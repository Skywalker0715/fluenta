"""Evaluasi live ask_tutor_ex untuk bahasa Inggris (en), Mandarin (zh), dan Jepang (ja).

Usage (dari root repositori):
    python scripts/eval_3bahasa_live.py [--hanya ID1 ID2 ...] [--jeda DETIK] [--keluaran NAMA]

Skrip ini hanya membuat file baru (berkas laporan, default docs/eval_3bahasa_live.md, atau
berkas yang ditentukan dengan --keluaran) dan tidak mengubah kode yang ada. Tidak membuka dan tidak mencetak isi .env.
"""
import argparse
import os
import sys
import re
import time
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm import ask_tutor_ex, _penjelasan_bukan_indonesia
from services.fixparse import parse_fix, TAG_LABELS

MAX_PANGGILAN = 20
JEDA_DETIK = 3
LEVEL = "intermediate"

FIX_LINE = re.compile(r"^Fix:\s*", re.MULTILINE)
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")          # aksara Han
JA = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")  # kana atau kanji
LATIN = re.compile(r"[a-zA-Z]")
HURUF = re.compile(r"[^\W\d_]", re.UNICODE)

# id, bahasa, mixed, input, harapan (fix / nofix / ngawur)
CASES = [
    ("E1", "en", False, "Yesterday I go to the market.", "fix"),
    ("E2", "en", False, "I have a cat and two dog.", "fix"),
    ("E3", "en", False, "She don't like coffee.", "fix"),
    ("E4", "en", False, "I am agree with you.", "fix"),
    ("E5", "en", False, "I went to school yesterday.", "nofix"),
    ("E6", "en", False, "Can you recommend a good restaurant near here?", "nofix"),
    ("E7", "en", True, "aku mau order coffee, tapi gimana ya bilangnya?", "fix"),
    ("E8", "en", False, "asdf obama purple tomorrow", "ngawur"),
    ("Z1", "zh", False, "你好，我叫Roy，我想学中文。", "nofix"),
    ("Z2", "zh", False, "Wo xihuan chi fan.", "nofix"),
    ("Z3", "zh", False, "我去学校昨天。", "fix"),
    ("Z4", "zh", False, "我有三个书。", "fix"),
    ("Z5", "zh", False, "他是很高。", "fix"),
    ("Z6", "zh", False, "苹果 电脑 昨天 红色 啊", "ngawur"),
    ("J1", "ja", False, "Watashi wa gakusei desu.", "nofix"),
    ("J2", "ja", False, "今日はいい天気ですね。", "nofix"),
    ("J3", "ja", False, "私は学校を行きます。", "fix"),
    ("J4", "ja", False, "私は日本語を話すができます。", "fix"),
    ("J5", "ja", False, "昨日、友達と映画を見ます。", "fix"),
    ("J6", "ja", False, "りんご パソコン 昨日 赤い ね", "ngawur"),
]

if len(CASES) > MAX_PANGGILAN:
    raise SystemExit(f"Terlalu banyak kasus: {len(CASES)} (maksimal {MAX_PANGGILAN})")

try:
    from pypinyin import pinyin, Style
    PYPINYIN_OK = True
    PYPINYIN_ERR = None
except ImportError as exc:
    PYPINYIN_OK = False
    PYPINYIN_ERR = str(exc)
except Exception as exc:
    PYPINYIN_OK = False
    PYPINYIN_ERR = str(exc)

try:
    import cutlet
    _CUTLET = cutlet.Cutlet()
    CUTLET_OK = True
    CUTLET_ERR = None
except ImportError as exc:
    _CUTLET = None
    CUTLET_OK = False
    CUTLET_ERR = str(exc)
except Exception as exc:
    _CUTLET = None
    CUTLET_OK = False
    CUTLET_ERR = str(exc)

MAKRON = {"ā": "aa", "ē": "ee", "ī": "ii", "ō": "ou", "ū": "uu"}


def normalisasi(teks):
    """Huruf kecil, buang spasi dan tanda baca."""
    return "".join(
        ch for ch in teks.lower()
        if not ch.isspace() and unicodedata.category(ch)[0] != "P"
    )


def tanpa_nada(teks):
    """Hapus tanda nada (diacritics) dari teks yang sudah dinormalisasi."""
    return "".join(
        ch for ch in unicodedata.normalize("NFD", teks)
        if unicodedata.category(ch) != "Mn"
    )


def normalisasi_ja(teks):
    """Normalisasi romaji Jepang: kecilkan, makron jadi vokal ganda, wo -> o, buang spasi/tanda baca."""
    teks = teks.lower()
    for makron, ganda in MAKRON.items():
        teks = teks.replace(makron, ganda)
    teks = teks.replace("wo", "o")
    return normalisasi(teks)


def cek_bahasa_balasan(balasan, lang):
    """(a) Apakah bahasa balasan sesuai harapan. Informasi saja."""
    if lang == "zh":
        return "benar" if HAN.search(balasan) else "salah"
    if lang == "ja":
        return "benar" if JA.search(balasan) else "salah"
    if lang == "en":
        huruf = HURUF.findall(balasan)
        if not huruf:
            return "salah"
        latin = len(LATIN.findall(balasan))
        return "benar" if latin >= len(huruf) / 2 else "salah"
    return "-"


def ambil_baris(balasan, awalan):
    for line in balasan.splitlines():
        if line.startswith(awalan):
            return line[len(awalan):].strip()
    return None


def teks_utama(balasan):
    """Teks balasan sebelum baris Pinyin:/Romaji:/Arti:."""
    bagian = []
    for line in balasan.splitlines():
        if line.startswith(("Pinyin:", "Romaji:", "Arti:")):
            break
        bagian.append(line)
    return " ".join(bagian)


def teks_target(balasan, lang):
    """Teks dalam skrip target bahasa (Han untuk zh, kana/kanji untuk ja)."""
    if lang == "zh":
        return "".join(HAN.findall(teks_utama(balasan)))
    if lang == "ja":
        return "".join(JA.findall(teks_utama(balasan)))
    return ""


def cek_baris_pendukung(balasan, lang):
    """(b) Apakah baris Pinyin/Romaji dan Arti ada sesuai format bahasa."""
    if lang == "zh":
        pinyin = any(line.startswith("Pinyin:") for line in balasan.splitlines())
        arti = any(line.startswith("Arti:") for line in balasan.splitlines())
        return "benar" if (pinyin and arti) else f"salah (Pinyin={pinyin}, Arti={arti})"
    if lang == "ja":
        romaji = any(line.startswith("Romaji:") for line in balasan.splitlines())
        arti = any(line.startswith("Arti:") for line in balasan.splitlines())
        return "benar" if (romaji and arti) else f"salah (Romaji={romaji}, Arti={arti})"
    return "-"


def ambil_baris_fix(balasan):
    """Ambil isi setelah awalan 'Fix:' pada baris Fix pertama yang ditemukan."""
    match = FIX_LINE.search(balasan)
    if not match:
        return None
    baris = balasan[match.start():].split("\n", 1)[0]
    return baris[len("Fix:"):].strip()


def cek_fix(balasan, harapan):
    """(c) Apakah baris Fix muncul sesuai harapan. Informasi saja."""
    ada = FIX_LINE.search(balasan) is not None
    if harapan == "fix":
        if not ada:
            return "tidak ada (harapan: ada)"
        isi = ambil_baris_fix(balasan)
        hasil = parse_fix(isi)
        if hasil["structured"] and hasil["tag"] in TAG_LABELS:
            return f"ada, tag valid ({hasil['tag']})"
        return "ada, tapi gagal parse atau tag tidak valid"
    if harapan == "nofix":
        return "tidak ada (sesuai harapan)" if not ada else "ada (harapan: tidak ada)"
    return "ada" if ada else "tidak ada"


def pypinyin_teks(teks_han):
    if not teks_han:
        return ""
    hasil = pinyin(teks_han, style=Style.TONE)
    return "".join(bagian for kata in hasil for bagian in kata)


def bandingkan_pinyin(llm_line, teks_han):
    """Bandingkan Pinyin LLM dengan pypinyin, dengan dan tanpa nada."""
    lib = pypinyin_teks(teks_han)  # keluaran mentah pypinyin (dengan nada)
    if not llm_line or not lib:
        return "tidak dapat dihitung"
    a = normalisasi(llm_line)      # bentuk ternormalisasi LLM
    b = normalisasi(lib)           # bentuk ternormalisasi pustaka
    a_tanpa = tanpa_nada(a)
    b_tanpa = tanpa_nada(b)
    detail = f"pustaka={lib!r} norma_pustaka={b!r} norma_llm={a!r}"
    if a == b:
        return f"cocok ({detail})"
    if a_tanpa == b_tanpa:
        return f"beda nada saja ({detail})"
    return f"beda ({detail})"


def romaji_teks(teks_ja):
    if not teks_ja or _CUTLET is None:
        return ""
    return _CUTLET.romaji(teks_ja)


def bandingkan_romaji(llm_line, teks_ja):
    """Bandingkan Romaji LLM dengan cutlet, bentuk ternormalisasi kedua sisi."""
    lib = romaji_teks(teks_ja)  # keluaran mentah cutlet
    if not llm_line or not lib:
        return "tidak dapat dihitung"
    a = normalisasi_ja(llm_line)  # bentuk ternormalisasi LLM
    b = normalisasi_ja(lib)       # bentuk ternormalisasi pustaka
    detail = f"pustaka={lib!r} norma_pustaka={b!r} norma_llm={a!r}"
    return f"cocok ({detail})" if a == b else f"beda ({detail})"


def _err_pustaka(nama, ok, err):
    if not ok:
        if isinstance(err, str) and err == "pustaka tidak terpasang":
            return f"{nama}: pustaka tidak terpasang"
        return f"{nama}: {err}"
    return None


def cek_pustaka(balasan, lang):
    """(d) Bandingkan baris Pinyin/Romaji LLM dengan pustaka. Informasi saja."""
    teks = teks_target(balasan, lang)
    if lang == "zh":
        baris = ambil_baris(balasan, "Pinyin:")
        err = _err_pustaka("pypinyin", PYPINYIN_OK, PYPINYIN_ERR)
        if err:
            return err
        if not baris or not teks:
            return "pypinyin: tidak dapat dihitung"
        return f"pypinyin: {bandingkan_pinyin(baris, teks)}"
    if lang == "ja":
        baris = ambil_baris(balasan, "Romaji:")
        err = _err_pustaka("cutlet", CUTLET_OK, CUTLET_ERR)
        if err:
            return err
        if not baris or not teks:
            return "cutlet: tidak dapat dihitung"
        return f"cutlet: {bandingkan_romaji(baris, teks)}"
    return "-"


def cek_target_setelah_arti(balasan, lang):
    """(f) zh/ja: apakah ada aksara target setelah baris 'Arti:' (ya/tidak)."""
    if lang not in ("zh", "ja"):
        return "-"
    baris = balasan.splitlines()
    arti_idx = None
    for index, line in enumerate(baris):
        if line.startswith("Arti:"):
            arti_idx = index
            break
    if arti_idx is None:
        return "-"
    target = HAN if lang == "zh" else JA
    for line in baris[arti_idx + 1:]:
        if line.startswith("Fix:"):
            continue
        if target.search(line):
            return "ya"
    return "tidak"


def cek_penjelasan_fix_mengandung_target(balasan, lang):
    """(f) Penjelasan Fix terindikasi bukan bahasa Indonesia (ya/tidak).

    Logika identik dengan _penjelasan_bukan_indonesia di services/llm.py:
    ambil penjelasan antara '||', abaikan teks dalam tanda kutip, lalu
    nyatakan pelanggaran bila rasio aksara Han/kana terhadap seluruh huruf
    > 20% atau tidak ada kata penanda Indonesia.
    """
    if lang == "en":
        return "-"
    match = FIX_LINE.search(balasan)
    if not match:
        return "-"
    baris = balasan[match.start():].split("\n", 1)[0]
    return "ya" if _penjelasan_bukan_indonesia(baris) else "tidak"


def fix_sesuai_harapan(hasil_c):
    if "sesuai harapan" in hasil_c:
        return True
    if hasil_c.startswith("ada, tag valid"):
        return True
    if "tidak ada (harapan: ada)" in hasil_c:
        return False
    if "ada (harapan: tidak ada)" in hasil_c:
        return False
    if hasil_c == "tidak ada (harapan: ada)":
        return False
    if hasil_c == "tidak ada (sesuai harapan)":
        return True
    return None


def panggil_kasus(lang, mixed, input_text):
    history = [{"role": "user", "text": input_text}]
    mulai = time.perf_counter()
    try:
        balasan, provider = ask_tutor_ex(history, lang=lang, level=LEVEL, mixed=mixed)
        return {
            "balasan": balasan,
            "provider": provider,
            "latensi": time.perf_counter() - mulai,
            "error": None,
        }
    except Exception as exc:
        return {
            "balasan": None,
            "provider": None,
            "latensi": time.perf_counter() - mulai,
            "error": str(exc),
        }


def bangun_result(case_id, lang, mixed, input_text, harapan):
    p = panggil_kasus(lang, mixed, input_text)
    balasan = p["balasan"] or ""
    return {
        "id": case_id,
        "lang": lang,
        "mixed": mixed,
        "input": input_text,
        "harapan": harapan,
        "provider": p["provider"],
        "latensi": p["latensi"],
        "error": p["error"],
        "balasan": balasan,
        "cek_a": cek_bahasa_balasan(balasan, lang),
        "cek_b": cek_baris_pendukung(balasan, lang),
        "cek_c": cek_fix(balasan, harapan),
        "cek_d": cek_pustaka(balasan, lang),
        "cek_e": cek_target_setelah_arti(balasan, lang),
        "cek_f": cek_penjelasan_fix_mengandung_target(balasan, lang),
        "fix_ok": (
            fix_sesuai_harapan(cek_fix(balasan, harapan))
            if harapan in ("fix", "nofix")
            else None
        ),
    }


def tulis_laporan(results, path="docs/eval_3bahasa_live.md", jeda=3, hanya=None):
    lines = []
    lines.append("# Evaluasi Live: Bahasa Inggris, Mandarin, dan Jepang")
    lines.append("")
    lines.append("Panggilan ke `services.llm.ask_tutor_ex` dengan `level='intermediate'` dan history satu pesan user per kasus.")
    lines.append(f"Maksimal {MAX_PANGGILAN} panggilan, jeda {jeda} detik, timeout bawaan layanan.")
    if hanya:
        lines.append(f"Hanya kasus yang dijalankan: {', '.join(sorted(hanya))}.")
    lines.append("Pemeriksaan otomatis (a) sampai (g) bersifat informasi pembantu, bukan penentu satu-satunya kualitas.")
    lines.append("Hasil pustaka (pypinyin/cutlet) bisa sendiri salah (misal polifon seperti 教 atau 得, atau 日本schaft dibaca \"Nippon go\"), jadi \"beda\" bukan otomatis berarti kesalahan LLM.")
    lines.append("Arti dan benarnya koreksi tidak dinilai secara otomatis.")
    lines.append("Laporan ini tidak mengandung kunci API.")
    lines.append("")

    lines.append("## Ringkasan per Kasus")
    lines.append("")
    lines.append("| ID | Bahasa | Input | Provider | Latensi (s) | (a) Bahasa balasan | (b) Pinyin/Romaji + Arti | (c) Fix vs harapan | (d) Pinyin/Romaji vs pustaka | (e) Target setelah Arti: | (f) Penjelasan Fix bukan Indonesia |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        provider = r["provider"] or "gagal"
        latensi = f"{r['latensi']:.2f}" if r["provider"] else "-"
        lines.append(
            f"| {r['id']} | {r['lang']} | {r['input']} | {provider} | {latensi} | "
            f"{r['cek_a']} | {r['cek_b']} | {r['cek_c']} | {r['cek_d']} | {r['cek_e']} | {r['cek_f']} |"
        )

    lines.append("")
    lines.append("## Statistik per Bahasa")
    for lang in ("en", "zh", "ja"):
        sub = [r for r in results if r["lang"] == lang]
        lines.append(f"### {lang.upper()} ({len(sub)} kasus)")
        fix_cek = [r for r in sub if r["fix_ok"] is not None]
        sesuai = sum(1 for r in fix_cek if r["fix_ok"])
        tidak_sesuai = len(fix_cek) - sesuai
        lines.append(f"- Fix sesuai harapan: {sesuai} dari {len(fix_cek)} kasus (fix/nofix).")
        lines.append(f"- Fix tidak sesuai harapan: {tidak_sesuai} kasus.")
        if lang in ("zh", "ja"):
            cocok = sum(
                1 for r in sub
                if r["cek_d"].startswith("pypinyin: cocok") or r["cek_d"].startswith("cutlet: cocok")
            )
            nada = sum(1 for r in sub if "beda nada saja" in r["cek_d"])
            beda = sum(
                1 for r in sub
                if (" pypinyin: beda" in r["cek_d"] or " cutlet: beda" in r["cek_d"])
                and "beda nada saja" not in r["cek_d"]
            )
            tidak_dapat = sum(
                1 for r in sub
                if "tidak dapat dihitung" in r["cek_d"] or "pustaka tidak terpasang" in r["cek_d"]
            )
            lines.append(
                f"- Pinyin/Romaji vs pustaka: cocok {cocok}, beda nada saja {nada}, "
                f"beda {beda}, tidak dapat dihitung {tidak_dapat}."
            )
            setelah_arti_ya = sum(1 for r in sub if r["cek_e"] == "ya")
            penjelasan_target = sum(1 for r in sub if r["cek_f"] == "ya")
            lines.append(f"- Aksara target setelah Arti: {setelah_arti_ya} kasus.")
            lines.append(f"- Penjelasan Fix bukan Indonesia: {penjelasan_target} kasus.")
        else:
            lines.append("- Pinyin/Romaji vs pustaka: tidak berlaku (bukan bahasa target pustaka).")
        lines.append("")

    lines.append("## Detail per Kasus")
    lines.append("")
    for r in results:
        lines.append(f"### {r['id']} — {r['lang']} ({r['harapan']})")
        lines.append("")
        lines.append(f"Input: {r['input']}")
        lines.append("")
        lines.append(f"Provider: {r['provider'] or 'gagal'} | Latensi: {r['latensi']:.2f} detik")
        if r["error"]:
            lines.append(f"Error: {r['error']}")
        lines.append("")
        lines.append("Jawaban Lengkap LLM:")
        lines.append("```")
        lines.append(r["balasan"] or "(tidak ada balasan)")
        lines.append("```")
        lines.append("")
        lines.append("Hasil pustaka:")
        lines.append(f"- {r['cek_d']}")
        lines.append("")
        lines.append(f"Target setelah Arti: {r['cek_e']}")
        lines.append(f"Penjelasan Fix bukan Indonesia: {r['cek_f']}")
        lines.append("")
        lines.append("| Pinyin/Romaji benar? | Arti benar? | Koreksi benar? |")
        lines.append("|---|---|---|")
        lines.append("| | | |")
        lines.append("")

    lines.append("## Catatan")
    lines.append("- Pemeriksaan otomatis (a) sampai (g) adalah informasi pembantu, bukan penentu satu-satunya kualitas.")
    lines.append("- Hasil pustaka (pypinyin/cutlet) bisa sendiri salah (misal polifon seperti 教 atau 得, atau 日本語 menjadi \"Nippon go\"), jadi \"beda\" bukan otomatis berarti kesalahan LLM.")
    lines.append("- Arti (baris 'Arti:') dan kebenaran koreksi ('Fix:') harus divalidasi secara manual di kolom yang disediakan.")
    lines.append("- Jika panggilan gagal (misal kunci API belum diisi atau jaringan mati), provider dan latensi ditulis sebagai gagal, dan kasus berikutnya tetap dipanggil.")
    lines.append("- Tidak ada kunci API yang dicetak atau disimpan dalam laporan ini.")

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nLaporan ditulis ke {path} ({len(results)} kasus)")


def parse_argv():
    parser = argparse.ArgumentParser(
        description="Evaluasi live ask_tutor_ex untuk bahasa Inggris (en), Mandarin (zh), dan Jepang (ja)."
    )
    parser.add_argument(
        "--hanya",
        nargs="*",
        metavar="ID",
        help="Hanya jalankan kasus dengan ID ini (contoh: --hanya E1 Z3 J5).",
    )
    parser.add_argument(
        "--jeda",
        type=float,
        default=3,
        metavar="DETIK",
        help="Jeda antar panggilan dalam detik (default 3).",
    )
    parser.add_argument(
        "--keluaran",
        default="docs/eval_3bahasa_live.md",
        metavar="NAMA",
        help="Nama berkas laporan evaluasi (default docs/eval_3bahasa_live.md).",
    )
    return parser.parse_args()


def main():
    args = parse_argv()

    if os.getenv("FLUENTA_FORCE_FALLBACK"):
        print(
            "Skrip dihentikan: variabel lingkungan FLUENTA_FORCE_FALLBACK diisi. "
            "Kosongkan variabel ini sebelum menjalankan evaluasi langsung."
        )
        sys.exit(1)

    ids = set(args.hanya) if args.hanya else None
    kasus = [c for c in CASES if ids is None or c[0] in ids]

    if ids:
        tidak_ditemukan = ids - {c[0] for c in CASES}
        if tidak_ditemukan:
            print(f"Peringatan: ID tidak ditemukan: {', '.join(sorted(tidak_ditemukan))}")
        if not kasus:
            print("Tidak ada kasus yang dijalankan untuk --hanya.")
            sys.exit(1)

    if len(kasus) > MAX_PANGGILAN:
        raise SystemExit(f"Terlalu banyak kasus: {len(kasus)} (maksimal {MAX_PANGGILAN})")

    results = []
    total = len(kasus)
    for index, (case_id, lang, mixed, input_text, harapan) in enumerate(kasus):
        print(f"[{index + 1}/{total}] {case_id} ({lang}): {input_text}")
        result = bangun_result(case_id, lang, mixed, input_text, harapan)
        results.append(result)
        mark = "OK" if result["balasan"] else "GAGAL"
        print(
            f"  {mark} | provider={result['provider'] or '-'} | "
            f"latensi={result['latensi']:.2f}s | {result['error'] or ''}"
        )
        if index < total - 1:
            time.sleep(args.jeda)

    tulis_laporan(results, path=args.keluaran, jeda=args.jeda, hanya=ids)


if __name__ == "__main__":
    main()