"""Tes offline pemeriksa penjelasan bahasa Indonesia pada baris Fix (Bagian 2).

Tidak memanggil API live. _ask_tutor_gemini dan _ask_tutor_groq di-mock.
Kunci yang digunakan hanyalah nilai tiruan dalam proses tes ini (bukan isi .env).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services import llm

results = []

HISTORY = [{"role": "user", "text": "Hello, how are you?"}]


def check(nama, kondisi, detail=""):
    status = "PASS" if kondisi else "FAIL"
    results.append((nama, status))
    print(f"{status}: {nama}{detail}")


def reset_cooldown():
    os.environ["FLUENTA_GEMINI_COOLDOWN_S"] = "0"
    llm._gemini_cooldown_until = 0.0


# Pastikan jalur Groq tersedia di lingkungan tes (nilai tiruan, tidak dicetak).
orig_groq_key = llm.GROQ_API_KEY
orig_groq_model = llm.GROQ_MODEL
llm.GROQ_API_KEY = "tes-kunci-groq"
llm.GROQ_MODEL = "openai/gpt-oss-120b"

orig_gemini = llm._ask_tutor_gemini
orig_groq = llm._ask_tutor_groq


def restore():
    llm._ask_tutor_gemini = orig_gemini
    llm._ask_tutor_groq = orig_groq
    llm.GROQ_API_KEY = orig_groq_key
    llm.GROQ_MODEL = orig_groq_model


def gemini_gagal(*args, **kwargs):
    exc = RuntimeError("Kuota Gemini habis")
    exc.code = 429
    raise exc


# (a) penjelasan Indonesia lolos pemeriksa -> False
reset_cooldown()
check(
    "a) penjelasan Indonesia lolos pemeriksa",
    llm._penjelasan_bukan_indonesia(
        "Fix: Saya pergi ke sekolah. || Kata kerja harus menggunakan simple past. || past_tense"
    )
    is False,
)

# (b) penjelasan Jepang dinyatakan pelanggaran -> True
reset_cooldown()
check(
    "b) penjelasan Jepang dinyatakan pelanggaran",
    llm._penjelasan_bukan_indonesia(
        "Fix: 私は学校へ行きます。 || をは目的語に使い、... || prepositions"
    )
    is True,
)

# (c) penjelasan Inggris dinyatakan pelanggaran -> True
reset_cooldown()
check(
    "c) penjelasan Inggris dinyatakan pelanggaran",
    llm._penjelasan_bukan_indonesia(
        "Fix: I go to school. || Use the particle e or ni for direction, not o. || prepositions"
    )
    is True,
)

# (d) kata Mandarin dalam kutipan di penjelasan Indonesia tidak dianggap pelanggaran -> False
reset_cooldown()
check(
    "d) kata Mandarin dalam kutipan tidak pelanggaran",
    llm._penjelasan_bukan_indonesia(
        'Fix: Saya suka makan nasi. || "Nasi" adalah makanan Indonesia yang enak. || word_choice'
    )
    is False,
)


# (e) pelanggaran Groq memicu tepat satu percobaan ulang (mock)
reset_cooldown()
panggilan_groq = {"n": 0}


def groq_pelanggaran_lalu_benar(*args, **kwargs):
    panggilan_groq["n"] += 1
    if panggilan_groq["n"] == 1:
        return (
            "Balasan pembuka.\n"
            "Fix: 私は学校へ行きます。 || をは目的語に使い、... || prepositions"
        )
    return "Balasan pembuka.\nFix: Saya pergi ke sekolah. || Kata kerja harus menggunakan simple past. || past_tense"


reset_cooldown()
llm._ask_tutor_gemini = gemini_gagal
llm._ask_tutor_groq = groq_pelanggaran_lalu_benar
try:
    teks, provider = llm.ask_tutor_ex(HISTORY)
    check(
        "e) pelanggaran Groq -> tepat satu percobaan ulang (2 panggilan)",
        provider == "groq"
        and panggilan_groq["n"] == 2
        and "simple past" in teks,
        f" | provider={provider} panggilan={panggilan_groq['n']} teks={teks!r}",
    )
except Exception as exc:
    check(
        "e) pelanggaran Groq -> tepat satu percobaan ulang (2 panggilan)",
        False,
        f" | error: {exc}",
    )
finally:
    restore()


# (f) tidak ada pelanggaran berarti tanpa percobaan ulang (1 panggilan)
reset_cooldown()
panggilan_groq = {"n": 0}


def groq_indonesia_benar(*args, **kwargs):
    panggilan_groq["n"] += 1
    return "Balasan pembuka.\nFix: Saya pergi ke sekolah. || Kata kerja harus menggunakan simple past. || past_tense"


reset_cooldown()
llm._ask_tutor_gemini = gemini_gagal
llm._ask_tutor_groq = groq_indonesia_benar
try:
    teks, provider = llm.ask_tutor_ex(HISTORY)
    check(
        "f) tanpa pelanggaran -> tidak ada percobaan ulang (1 panggilan)",
        provider == "groq"
        and panggilan_groq["n"] == 1
        and "simple past" in teks,
        f" | provider={provider} panggilan={panggilan_groq['n']}",
    )
except Exception as exc:
    check(
        "f) tanpa pelanggaran -> tidak ada percobaan ulang (1 panggilan)",
        False,
        f" | error: {exc}",
    )
finally:
    restore()


# (g) jalur Gemini tidak ikut percobaan ulang (Groq nol panggilan)
reset_cooldown()
panggilan_groq = {"n": 0}


def groq_never(*args, **kwargs):
    panggilan_groq["n"] += 1
    raise AssertionError("Groq tidak boleh dipanggil pada jalur Gemini")


def gemini_sukses(*args, **kwargs):
    return (
        "Balasan Gemini.\n"
        "Fix: Saya pergi ke sekolah. || をは目的語に使い、... || prepositions"
    )


reset_cooldown()
llm._ask_tutor_gemini = gemini_sukses
llm._ask_tutor_groq = groq_never
try:
    teks, provider = llm.ask_tutor_ex(HISTORY)
    check(
        "g) jalur Gemini -> tanpa percobaan ulang, Groq nol panggilan",
        provider == "gemini" and panggilan_groq["n"] == 0 and "Balasan Gemini" in teks,
        f" | provider={provider} panggilan={panggilan_groq['n']}",
    )
except Exception as exc:
    check(
        "g) jalur Gemini -> tanpa percobaan ulang, Groq nol panggilan",
        False,
        f" | error: {exc}",
    )
finally:
    restore()


# (h) parse_fix menangani pemisah tanpa spasi (kasus J3)
reset_cooldown()
from services.fixparse import parse_fix  # noqa: E402

hasil = parse_fix("…表す。|| prepositions")
check(
    "h) parse_fix pemisah tanpa spasi terstruktur dengan benar",
    hasil["structured"] is True
    and hasil["corrected"] == "…表す。"
    and hasil["explanation"] == "prepositions"
    and hasil["tag"] == "other",
    f" | hasil={hasil!r}",
)


# Ringkasan
print("\n=== Ringkasan Tes Penjelasan Offline ===")
lulus = sum(1 for _, s in results if s == "PASS")
gagal = sum(1 for _, s in results if s == "FAIL")
for nama, status in results:
    print(f"  {status}: {nama}")
print(f"\nLulus: {lulus}/{len(results)}")
if gagal:
    print(f"Gagal: {gagal}")
    sys.exit(1)