"""Tes offline aturan pesan fragmen / kata acak (Bagian 1).

Tidak memanggil API live. Hanya membaca konstanta dan fungsi di services/llm.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm import (
    GROQ_EXTRA_RULES,
    SYSTEM_PROMPT,
    _build_system_prompt,
    _penjelasan_bukan_indonesia,
)

results = []


def check(nama, kondisi, detail=""):
    status = "PASS" if kondisi else "FAIL"
    results.append((nama, status))
    print(f"{status}: {nama}{detail}")


# Aturan fragmen, versi bahasa Inggris (prompt utama) dan Indonesia (GROQ_EXTRA_RULES).
ATURAN_EN = (
    "If the user's message is a greeting, thanks, a single word, or a short "
    "meaningful phrase (for example: hello, thank you, Konnichiwa, Ni hao, "
    "coffee please), treat it as normal for a beginner; reply friendly and "
    "continue the conversation, do not ask the user to rewrite. Only refuse to "
    "treat it as meaningful if the message consists of random words without "
    "understandable meaning. Do not invent conversation history or claim to "
    "have discussed something before."
)
ATURAN_ID = (
    "Bila pesan pengguna adalah sapaan, ucapan terima kasih, kata tunggal, "
    "atau frasa pendek yang bermakna (contoh: hello, thank you, Konnichiwa, "
    "Ni hao, coffee please), anggap itu normal bagi pemula; balas dengan ramah "
    "dan lanjutkan percakapan, JANGAN meminta menulis ulang. Terapkan penolakan "
    "hanya bila pesan terdiri dari kata-kata acak tanpa makna yang bisa "
    "dipahami. Dilarang mengarang riwayat percakapan atau mengklaim sudah "
    "membahas sesuatu sebelumnya."
)


def fix_baris(penjelasan, tag="prepositions"):
    return f"Fix: Saya pergi ke sekolah. || {penjelasan} || {tag}"


# (a) Teks aturan fragmen ada di prompt utama untuk en, zh, dan ja.
for bahasa in ("en", "zh", "ja"):
    prompt = _build_system_prompt(bahasa, "intermediate")
    check(
        f"(a) aturan fragmen ada di prompt utama ({bahasa})",
        ATURAN_EN in prompt,
        f" | bahasa={bahasa}",
    )

# (b) Teks yang sama ada di GROQ_EXTRA_RULES.
check("(b) aturan fragmen sama ada di GROQ_EXTRA_RULES", ATURAN_ID in GROQ_EXTRA_RULES)

# (c) Contoh "hello" dan "Konnichiwa" ada di prompt utama dan di GROQ_EXTRA_RULES.
check("(c) 'hello' dan 'Konnichiwa' ada di SYSTEM_PROMPT dan GROQ_EXTRA_RULES",
      "hello" in SYSTEM_PROMPT and "Konnichiwa" in SYSTEM_PROMPT
      and "hello" in GROQ_EXTRA_RULES and "Konnichiwa" in GROQ_EXTRA_RULES)

# (d) Penjelasan partikel Jepang dalam kalimat Indonesia bukan pelanggaran.
check(
    "(c) 'Tujuan (ke sekolah) menggunakan partikel へ atau に, bukan を.' bukan pelanggaran",
    _penjelasan_bukan_indonesia(
        fix_baris("Tujuan (ke sekolah) menggunakan partikel へ atau に, bukan を.")
    )
    is False,
)

# (d) Penjelasan Indonesia dengan partikel Jepang bukan pelanggaran.
check(
    "(d) 'Subjek dan predikat harus lengkap, gunakan partikel が untuk subjek dan "
    "ありました untuk menyatakan keberadaan di masa lalu.' bukan pelanggaran",
    _penjelasan_bukan_indonesia(
        fix_baris(
            "Subjek dan predikat harus lengkap, gunakan partikel が untuk subjek "
            "dan ありました untuk menyatakan keberadaan di masa lalu."
        )
    )
    is False,
)

# (e) Penjelasan berbahasa Jepang murni adalah pelanggaran.
check(
    "(e) penjelasan berbahasa Jepang murni adalah pelanggaran",
    _penjelasan_bukan_indonesia(
        fix_baris("へは方向を表す助詞です。には存在を示します。")
    )
    is True,
)

# Ringkasan
print("\n=== Ringkasan Tes Aturan Fragmen Offline ===")
lulus = sum(1 for _, s in results if s == "PASS")
gagal = sum(1 for _, s in results if s == "FAIL")
for nama, status in results:
    print(f"  {status}: {nama}")
print(f"\nLulus: {lulus}/{len(results)}")
if gagal:
    print(f"Gagal: {gagal}")
    sys.exit(1)