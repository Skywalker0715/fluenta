import os
import re
import time
import requests

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .fixparse import parse_fix, TAG_LABELS

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

GROQ_EXTRA_RULES = (
    "ATURAN TAMBAHAN: Penjelasan pada baris Fix WAJIB berbahasa Indonesia, 1 sampai 2 kalimat lengkap, "
    "sebutkan aturan grammar-nya dan alasan kenapa kalimat awal salah. Dilarang menulis penjelasan dalam bahasa Inggris. "
    "Format baris Fix harus persis: Fix: <kalimat benar> || <penjelasan Indonesia> || <tag>. "
    "Jika kalimat pengguna sudah benar, JANGAN menulis baris Fix. "
    "Jika diminta membalas dalam bahasa lain (Mandarin/Jepang), balasan utama ditulis dalam bahasa itu, lalu tambahkan baris "
    "Pinyin/Romaji dan Arti sesuai format yang diminta."
)

SYSTEM_PROMPT = (
    "You are a friendly English tutor and conversation partner for an Indonesian "
    "learner. Reply in simple English, maximum 3 short sentences, and end with one "
    "follow-up question. The user's message may come from speech transcription, so "
    "IGNORE punctuation, capitalization, and likely transcription glitches. Only "
    "correct real mistakes in grammar, tense, word choice, or unnatural phrasing. "
    "If the user's last message has a real mistake, add a final line starting "
    "exactly with 'Fix: ' in a single line: 'Fix: <corrected sentence> || "
    "<short explanation in Indonesian naming the rule> || <tag>', where tag is "
    "exactly one of: past_tense, present_tense, future_tense, articles, "
    "prepositions, subject_verb_agreement, plural_singular, word_order, "
    "word_choice, collocation, code_mixing, other. If there is no real "
    "mistake, do not add a Fix line."
)

_FIX_LINE = re.compile(r"^Fix:\s*", re.MULTILINE)

_MIXED_INSTRUCTION = (
    "The user may mix Indonesian words into the message. Do NOT treat the Indonesian "
    "words as mistakes. Reply naturally to what the user means. If the message "
    "contains Indonesian words, add the Fix line where the corrected sentence is the "
    "natural {language} version of the WHOLE message, the explanation says briefly "
    "in Indonesian how the Indonesian parts are said naturally, and the tag is "
    "code_mixing."
)


def _is_transient_error(exc: Exception) -> bool:
    code = getattr(exc, "code", None)
    if isinstance(code, int) and 500 <= code < 600:
        return True
    message = str(exc).lower()
    return "read timeout" in message or "deadline exceeded" in message


def _generate_with_retry(
    client: genai.Client, model: str, contents: list, config: types.GenerateContentConfig
):
    try:
        return client.models.generate_content(model=model, contents=contents, config=config)
    except Exception as exc:
        if not _is_transient_error(exc):
            raise
        time.sleep(2)
        return client.models.generate_content(model=model, contents=contents, config=config)


def _ask_tutor_gemini(
    history: list[dict], lang: str = "en", level: str = "intermediate", mixed: bool = False
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")
    if not api_key or not model:
        raise RuntimeError("GEMINI_API_KEY atau GEMINI_MODEL belum diisi di .env")

    contents = [
        {
            "role": "user" if item["role"] == "user" else "model",
            "parts": [{"text": item["text"]}],
        }
        for item in history
    ]
    config = types.GenerateContentConfig(
        system_instruction=_build_system_prompt(lang, level, mixed),
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )
    client = genai.Client(
        api_key=api_key, http_options=types.HttpOptions(timeout=30000)
    )
    try:
        response = _generate_with_retry(client, model, contents, config)
    except Exception as exc:
        if getattr(exc, "code", None) == 429:
            raise RuntimeError(
                "Kuota Gemini habis untuk saat ini. Coba lagi nanti atau ganti GEMINI_MODEL di .env."
            ) from exc
        raise RuntimeError(
            f"Gagal meminta bantuan tutor dari Gemini: "
            f"{type(exc).__name__}: {str(exc)[:200]}"
        ) from exc

    if not response.text:
        candidates = response.candidates or []
        reason = candidates[0].finish_reason if candidates else "tanpa kandidat"
        feedback = getattr(response, "prompt_feedback", None)
        raise RuntimeError(
            f"Gemini mengembalikan balasan kosong. finish_reason={reason}, "
            f"prompt_feedback={feedback}"
        )
    return response.text.strip()


def _should_fallback_to_groq(exc: Exception) -> bool:
    code = getattr(exc, "code", None)
    if isinstance(code, int):
        if code == 429:
            return True
        if 500 <= code < 600:
            return True
        return False
    message = str(exc).lower()
    if "timeout" in message or "deadline exceeded" in message:
        return True
    if "connection" in message or "connect" in message or "network" in message:
        return True
    return False


def _strip_think(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"</?think>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```think.*?```", "", text, flags=re.DOTALL)
    return text.strip()


def _ask_tutor_groq(
    history: list[dict], lang: str = "en", level: str = "intermediate", mixed: bool = False
) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")
    if not api_key or not model:
        raise RuntimeError("GROQ_API_KEY atau GROQ_MODEL belum diisi di .env")

    system_prompt = _build_system_prompt(lang, level, mixed) + "\n" + GROQ_EXTRA_RULES

    recent = history[-8:] if history else []
    messages = [{"role": "system", "content": system_prompt}]
    for item in recent:
        role = item["role"] if item["role"] in ("user", "assistant") else "user"
        messages.append({"role": role, "content": item["text"]})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(f"Timeout memanggil Groq: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Gagal koneksi ke Groq: {type(exc).__name__}") from exc

    if resp.status_code != 200:
        raise RuntimeError(f"Groq HTTP {resp.status_code}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError(f"Gagal parsing respons Groq: {exc}") from exc

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("Groq mengembalikan choices kosong")
    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    content = _strip_think(content).strip()
    if not content:
        raise RuntimeError("Groq mengembalikan content kosong")
    return content


def _groq_translate(contents: list, system_instruction: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")
    if not api_key or not model:
        raise RuntimeError("GROQ_API_KEY atau GROQ_MODEL belum diisi di .env")

    text_parts = []
    for item in contents:
        if item.get("role") == "user":
            for part in item.get("parts", []):
                if "text" in part:
                    text_parts.append(part["text"])
    text = "\n".join(text_parts)

    system_prompt = "Terjemahkan teks persis seperti diminta. Balas HANYA hasil terjemahan tanpa penjelasan."
    user_message = f"{system_instruction}\n\n{text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(f"Timeout memanggil Groq: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Gagal koneksi ke Groq: {type(exc).__name__}") from exc

    if resp.status_code != 200:
        raise RuntimeError(f"Groq HTTP {resp.status_code}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError(f"Gagal parsing respons Groq: {exc}") from exc

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("Groq mengembalikan choices kosong")
    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    content = _strip_think(content).strip()
    if not content:
        raise RuntimeError("Groq mengembalikan content kosong")
    return content


def ask_tutor_ex(
    history: list[dict], lang: str = "en", level: str = "intermediate", mixed: bool = False
) -> tuple[str, str]:
    force_fallback = os.getenv("FLUENTA_FORCE_FALLBACK", "0") == "1"
    groq_available = bool(GROQ_API_KEY and GROQ_MODEL)

    gemini_error = None

    if not force_fallback:
        try:
            text = _ask_tutor_gemini(history, lang, level, mixed)
            return text, "gemini"
        except Exception as exc:
            gemini_error = exc
            if not _should_fallback_to_groq(exc):
                raise
            if not groq_available:
                raise

    if groq_available:
        try:
            text = _ask_tutor_groq(history, lang, level, mixed)
            return text, "groq"
        except Exception as groq_exc:
            print(f"Gagal fallback ke Groq: {type(groq_exc).__name__}: {str(groq_exc)[:200]}")
            raise gemini_error from groq_exc

    raise gemini_error if gemini_error else RuntimeError("Tidak ada penyedia LLM yang tersedia")


def ask_tutor(
    history: list[dict], lang: str = "en", level: str = "intermediate", mixed: bool = False
) -> str:
    text, _provider = ask_tutor_ex(history, lang, level, mixed)
    return text

def split_correction(reply: str) -> tuple[str, str | None]:
    match = _FIX_LINE.search(reply)
    if not match:
        return reply.strip(), None
    return reply[: match.start()].strip(), reply[match.end():].strip()


def generate_text(contents: list, system_instruction: str, timeout_ms: int = 30000) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")
    if not api_key or not model:
        raise RuntimeError("GEMINI_API_KEY atau GEMINI_MODEL belum diisi di .env")

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )
    client = genai.Client(
        api_key=api_key, http_options=types.HttpOptions(timeout=timeout_ms)
    )
    try:
        response = _generate_with_retry(client, model, contents, config)
    except Exception as exc:
        if getattr(exc, "code", None) == 429:
            raise RuntimeError(
                "Kuota Gemini habis untuk saat ini. Coba lagi nanti atau ganti GEMINI_MODEL di .env."
            ) from exc
        raise RuntimeError(
            f"Gagal memanggil Gemini: {type(exc).__name__}: {str(exc)[:200]}"
        ) from exc

    if not response.text:
        candidates = response.candidates or []
        reason = candidates[0].finish_reason if candidates else "tanpa kandidat"
        feedback = getattr(response, "prompt_feedback", None)
        raise RuntimeError(
            f"Gemini mengembalikan balasan kosong. finish_reason={reason}, "
            f"prompt_feedback={feedback}"
        )
    return response.text.strip()


def generate_text_ex(
    contents: list, system_instruction: str, timeout_ms: int = 30000
) -> tuple[str, str]:
    force_fallback = os.getenv("FLUENTA_FORCE_FALLBACK", "0") == "1"
    groq_available = bool(GROQ_API_KEY and GROQ_MODEL)

    text_parts = []
    for item in contents:
        if item.get("role") == "user":
            for part in item.get("parts", []):
                if "text" in part:
                    text_parts.append(part["text"])
    text = "\n".join(text_parts)

    gemini_error = None

    if not force_fallback:
        try:
            result = generate_text(contents, system_instruction, timeout_ms)
            return result, "gemini"
        except Exception as exc:
            gemini_error = exc
            if not _should_fallback_to_groq(exc):
                raise
            if not groq_available:
                raise
            if len(text) > 3000:
                raise

    if groq_available:
        try:
            result = _groq_translate(contents, system_instruction)
            return result, "groq"
        except Exception as groq_exc:
            if gemini_error is not None:
                raise gemini_error from groq_exc
            raise

    raise gemini_error if gemini_error else RuntimeError("Tidak ada penyedia LLM yang tersedia")


def _build_system_prompt(lang: str, level: str, mixed: bool = False) -> str:
    if lang not in ("en", "zh", "ja") or level not in (
        "beginner",
        "intermediate",
        "advanced",
    ):
        raise RuntimeError("Bahasa atau level tidak didukung.")
    prompt = SYSTEM_PROMPT
    if level == "beginner":
        prompt += "\nUse very simple words and at most 2 short sentences."
    elif level == "advanced":
        prompt += (
            "\nUse natural, richer vocabulary and idioms, at most 4 sentences, "
            "and gently challenge the learner."
        )
    if lang == "zh":
        prompt += (
            "\nReply in Mandarin Chinese (Simplified). Add a line starting exactly with "
            "'Pinyin: ' and a line starting exactly with 'Arti: ' (Indonesian meaning). "
            "Place any Fix line last."
        )
    elif lang == "ja":
        prompt += (
            "\nReply in Japanese. Add a line starting exactly with 'Romaji: ' and a line "
            "starting exactly with 'Arti: ' (Indonesian meaning). Place any Fix line last."
        )
    if mixed:
        _nama_bahasa = {"en": "English", "zh": "Mandarin", "ja": "Japanese"}
        prompt += "\n" + _MIXED_INSTRUCTION.format(language=_nama_bahasa[lang])
    return prompt


def speakable(conversation: str) -> str:
    lines = conversation.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(("Pinyin:", "Romaji:", "Arti:")):
            return "\n".join(lines[:index]).strip()
    return conversation.strip()