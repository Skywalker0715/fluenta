import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from services import llm

load_dotenv()

TEST_CASES = [
    ("en", False, "Yesterday I go to the market", "Past tense error"),
    ("en", False, "I have cat", "Article error"),
    ("en", False, "She go to school", "Subject-verb agreement error"),
    ("en", False, "Hello, how are you today?", "Correct sentence"),
    ("zh", False, "Ni hao ma?", "Mandarin 1"),
    ("ja", False, "Konnichiwa", "Japanese 1"),
    ("en", True, "aku mau order coffee, tapi gimana ya bilangnya?", "Code mixing"),
    ("en", False, "I am in Monday", "Preposition error"),
]

GROQ_EXTRA_RULES = (
    "ATURAN TAMBAHAN: Penjelasan pada baris Fix WAJIB berbahasa Indonesia, 1 sampai 2 kalimat lengkap, "
    "sebutkan aturan grammar-nya dan alasan kenapa kalimat awal salah. Dilarang menulis penjelasan dalam bahasa Inggris. "
    "Format baris Fix harus persis: Fix: <kalimat benar> || <penjelasan Indonesia> || <tag>. "
    "Jika kalimat pengguna sudah benar, JANGAN menulis baris Fix. "
    "Jika diminta membalas dalam bahasa lain (Mandarin/Jepang), balasan utama ditulis dalam bahasa itu, lalu tambahkan baris "
    "Pinyin/Romaji dan Arti sesuai format yang diminta."
)


def build_system_prompt(lang, level, mixed):
    prompt = llm._build_system_prompt(lang, level, mixed)
    return prompt + "\n" + GROQ_EXTRA_RULES


def call_groq_only(system_prompt, user_message):
    """Panggil langsung fungsi internal Groq, tanpa melalui Gemini."""
    history = [{"role": "user", "text": user_message}]
    return llm._ask_tutor_groq(history, "en", "intermediate", False)


def main():
    if not llm.GROQ_API_KEY or not llm.GROQ_MODEL:
        print("GROQ_API_KEY atau GROQ_MODEL belum diisi di .env")
        return

    results = []
    for lang, mixed, user_msg, desc in TEST_CASES:
        system_prompt = build_system_prompt(lang, "intermediate", mixed)
        try:
            text = call_groq_only(system_prompt, user_msg)
            provider = "groq"
            error = None
        except Exception as exc:
            provider = "groq"
            text = None
            error = str(exc)
        results.append({
            "lang": lang,
            "mixed": mixed,
            "user_message": user_msg,
            "description": desc,
            "provider": provider,
            "text": text,
            "error": error,
        })
        mark = "OK" if text else "ERROR"
        print(f"{desc}: {mark} | provider={provider} | {error or ''}")
        time.sleep(3)

    lines = []
    lines.append("# Evaluasi Model Cadangan Groq (Live)")
    lines.append("")
    lines.append("Hanya fungsi jalur Groq yang dipanggil (Gemini tidak disentuh). Maksimal 8 panggilan, jeda 3 detik.")
    lines.append("")
    lines.append("## Hasil per Kasus")
    lines.append("")
    for r in results:
        lines.append(f"### {r['description']}")
        lines.append(f"- Pesan: {r['user_message']}")
        lines.append(f"- Provider: {r['provider']}")
        if r["error"]:
            lines.append(f"- Error: {r['error']}")
        lines.append("```")
        lines.append(r["text"] or "")
        lines.append("```")
        lines.append("")

    lines.append("## Catatan")
    lines.append("- Tidak ada API key yang tercantum dalam laporan ini.")
    lines.append("- Semua panggilan menggunakan fungsi internal `_ask_tutor_groq` dari `services/llm.py`.")
    lines.append("- System prompt sama dengan Gemini, ditambah aturan tambahan untuk Groq.")

    os.makedirs("docs", exist_ok=True)
    with open("docs/eval_fallback_live.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\nLaporan ditulis ke docs/eval_fallback_live.md")


if __name__ == "__main__":
    main()