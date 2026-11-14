import json
import os
import time
import requests
from dotenv import load_dotenv

from services.llm import _build_system_prompt
from services.fixparse import parse_fix, TAG_LABELS

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

API_URL = "https://api.groq.com/openai/v1/chat/completions"

VALID_TAGS = set(TAG_LABELS.keys())

INDONESIAN_MARKERS = ["yang", "kamu", "karena", "seharusnya", "ini", "itu", "dan", "atau"]

TEST_CASES = [
    ("E1", "en", False, "Yesterday I go to the market", True, "past_tense", "Past tense error"),
    ("E2", "en", False, "I have cat", True, "articles", "Article error"),
    ("E3", "en", False, "I am in Monday", True, "prepositions", "Preposition error"),
    ("E4", "en", False, "She go to school", True, "subject_verb_agreement", "Subject-verb agreement error"),
    ("E5", "en", False, "I have two book", True, "plural_singular", "Plural/singular error"),
    ("E6", "en", False, "I like very much coffee", True, "word_order", "Word order error"),
    ("C1", "en", False, "Hello, how are you today?", False, None, "Correct sentence 1"),
    ("C2", "en", False, "I am going to the library to study.", False, None, "Correct sentence 2"),
    ("C3", "en", False, "The weather is very nice today.", False, None, "Correct sentence 3"),
    ("Z1", "zh", False, "Ni hao ma?", False, None, "Mandarin 1"),
    ("Z2", "zh", False, "Wo xihuan chi fan", False, None, "Mandarin 2"),
    ("J1", "ja", False, "Konnichiwa", False, None, "Japanese 1"),
    ("J2", "ja", False, "Watashi wa gakusei desu", False, None, "Japanese 2"),
    ("M1", "en", True, "aku mau order coffee, tapi gimana ya bilangnya?", True, "code_mixing", "Code mixing"),
]


def has_indonesian(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in INDONESIAN_MARKERS)


def call_groq(system_prompt: str, user_message: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
    }
    start = time.time()
    status = None
    error = None
    raw = None
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        status = resp.status_code
        raw = resp.text
    except requests.exceptions.Timeout as exc:
        error = str(exc)
    except Exception as exc:
        error = str(exc)
    latency = time.time() - start
    return raw, latency, status, error


def evaluate_case(case):
    case_id, lang, mixed, user_msg, expect_fix, expected_tag, desc = case
    system_prompt = _build_system_prompt(lang, "intermediate", mixed)
    raw, latency, status, error = call_groq(system_prompt, user_msg)

    result = {
        "id": case_id,
        "lang": lang,
        "mixed": mixed,
        "user_message": user_msg,
        "description": desc,
        "expect_fix": expect_fix,
        "expected_tag": expected_tag,
        "raw": raw,
        "latency": round(latency, 3),
        "status": status,
        "error": error,
        "checks": {},
        "passed": False,
        "reason": "",
    }

    model_name = None
    answer_content = None
    if raw:
        try:
            data = json.loads(raw)
            model_name = data.get("model")
            choices = data.get("choices") or []
            if choices:
                answer_content = (choices[0].get("message") or {}).get("content")
        except (ValueError, TypeError):
            pass
    result["model"] = model_name
    result["answer_content"] = answer_content

    if error:
        result["passed"] = False
        result["reason"] = f"API error: {error}"
        return result

    if status != 200:
        result["passed"] = False
        result["reason"] = f"HTTP {status}"
        return result

    has_think = ("<|think|>" in raw) or ("```think" in raw) or ("</think>" in raw)
    result["checks"]["no_think"] = not has_think

    has_fix = "Fix:" in raw
    result["checks"]["has_fix"] = has_fix

    parsed = parse_fix(raw)
    result["checks"]["parse_structured"] = parsed["structured"]
    result["checks"]["tag_valid"] = parsed["tag"] in VALID_TAGS
    result["checks"]["tag"] = parsed["tag"]

    if expect_fix:
        reasons = []
        if not has_fix:
            reasons.append("tidak ada baris Fix")
        if not parsed["structured"]:
            reasons.append("parse_fix tidak terstruktur")
        if parsed["tag"] not in VALID_TAGS:
            reasons.append(f"tag tidak valid: {parsed['tag']}")
        if not has_indonesian(parsed["explanation"]):
            reasons.append("penjelasan bukan bahasa Indonesia")
        if has_think:
            reasons.append("mengandung think tags")
        result["passed"] = len(reasons) == 0
        result["reason"] = "; ".join(reasons) if reasons else "PASS"
    else:
        reasons = []
        if has_fix:
            reasons.append("kalimat benar tapi ada baris Fix")
        if has_think:
            reasons.append("mengandung think tags")
        result["passed"] = len(reasons) == 0
        result["reason"] = "; ".join(reasons) if reasons else "PASS"

    if lang == "zh":
        extra = []
        if "Pinyin:" not in raw:
            extra.append("tidak ada Pinyin:")
        if "Arti:" not in raw:
            extra.append("tidak ada Arti:")
        if extra:
            result["passed"] = False
            result["reason"] = "; ".join(extra) + ("; " if result["reason"] else "") + result["reason"]

    if lang == "ja":
        extra = []
        if "Romaji:" not in raw:
            extra.append("tidak ada Romaji:")
        if "Arti:" not in raw:
            extra.append("tidak ada Arti:")
        if extra:
            result["passed"] = False
            result["reason"] = "; ".join(extra) + ("; " if result["reason"] else "") + result["reason"]

    return result


def write_report(results, path):
    passed = [r for r in results if r["passed"]]
    failed = [r for r in results if not r["passed"]]
    total = len(results)
    avg_latency = sum(r["latency"] for r in results) / total if total else 0

    lines = []
    lines.append("# Evaluasi LLM Cadangan (Groq)")
    lines.append("")
    lines.append(f"Skor: {len(passed)}/{total}")
    lines.append(f"Rata-rata latensi: {avg_latency:.2f} detik")
    lines.append("")
    lines.append("## Tabel Hasil per Kasus")
    lines.append("")
    lines.append("| ID | Bahasa | Uji | PASS/FAIL | Alasan | Latensi (s) | Status HTTP |")
    lines.append("|----|--------|-----|-----------|--------|-------------|-------------|")
    for r in results:
        status_str = "PASS" if r["passed"] else "FAIL"
        http = r["status"] if r["status"] else "-"
        lines.append(
            f"| {r['id']} | {r['lang']} | {r['description']} | {status_str} | {r['reason']} | {r['latency']} | {http} |"
        )

    lines.append("")
    lines.append("## Ringkasan Skor")
    lines.append(f"- Total kasus: {total}")
    lines.append(f"- Lulus: {len(passed)}")
    lines.append(f"- Gagal: {len(failed)}")
    lines.append(f"- Rata-rata latensi: {avg_latency:.2f} detik")
    lines.append("")

    if failed:
        lines.append("## Daftar FAIL")
        for r in failed:
            lines.append(f"- {r['id']} ({r['description']}): {r['reason']}")
        lines.append("")

    sorted_by_bad = sorted(results, key=lambda r: (not r["passed"], -r["latency"]))
    worst = sorted_by_bad[:3]
    lines.append("## 3 Contoh Jawaban Mentah Paling Buruk")
    lines.append("")
    for r in worst:
        lines.append(f"### {r['id']} - {r['description']}")
        lines.append(f"- Pesan pengguna: {r['user_message']}")
        lines.append(f"- Status HTTP: {r['status']}")
        lines.append(f"- Error: {r['error'] or '-'}")
        lines.append(f"- Latensi: {r['latency']} detik")
        lines.append("```")
        lines.append((r["raw"] or "")[:1000])
        lines.append("```")
        lines.append("")

    lines.append("## Jawaban Lengkap Semua Kasus")
    lines.append("")
    for r in results:
        lines.append(f"### {r['id']} - {r['description']}")
        lines.append(f"- Pesan pengguna: {r['user_message']}")
        lines.append(f"- Model: {r['model'] or '-'}")
        lines.append("```")
        lines.append(r["answer_content"] or "")
        lines.append("```")
        lines.append("")

    lines.append("## Catatan")
    lines.append("- Tidak ada API key yang tercantum dalam laporan ini.")
    lines.append("- Semua pemanggilan API menggunakan `requests` ke endpoint Groq.")
    lines.append("- System prompt menggunakan `_build_system_prompt` dari `services/llm.py` yang sama dengan Gemini.")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    if not GROQ_API_KEY or not GROQ_MODEL:
        print("GROQ_API_KEY atau GROQ_MODEL belum diisi di .env")
        return

    results = []
    for case in TEST_CASES:
        result = evaluate_case(case)
        results.append(result)
        mark = "PASS" if result["passed"] else "FAIL"
        print(f"{result['id']}: {mark} | {result['description']} | {result['latency']}s | HTTP {result['status']} | {result['reason']}")
        if result["error"]:
            print(f"   error: {result['error']}")
        time.sleep(3)

    write_report(results, "docs/eval_groq.md")
    print("\nLaporan ditulis ke docs/eval_groq.md")

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_latency = sum(r["latency"] for r in results) / total if total else 0
    print(f"Skor: {passed}/{total}")
    print(f"Rata-rata latensi: {avg_latency:.2f} detik")


if __name__ == "__main__":
    main()