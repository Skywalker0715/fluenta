import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

SYSTEM_PROMPT = (
    "You are a friendly English tutor and conversation partner for an Indonesian "
    "learner. Reply in simple English, maximum 3 short sentences, and end with one "
    "follow-up question. The user's message may come from speech transcription, so "
    "IGNORE punctuation, capitalization, and likely transcription glitches. Only "
    "correct real mistakes in grammar, tense, word choice, or unnatural phrasing. "
    "If the user's last message has a real mistake, add a final line starting "
    "exactly with 'Fix: ' containing the corrected sentence, then a short "
    "explanation in Indonesian that names the rule (for example past tense or "
    "articles). If there is no real mistake, do not add a Fix line."
)

_FIX_LINE = re.compile(r"^Fix:\s*", re.MULTILINE)


def ask_tutor(history: list[dict], lang: str = "en", level: str = "intermediate") -> str:
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
        system_instruction=_build_system_prompt(lang, level),
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )
    client = genai.Client(
        api_key=api_key, http_options=types.HttpOptions(timeout=20000)
    )
    try:
        response = client.models.generate_content(
            model=model, contents=contents, config=config
        )
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

def split_correction(reply: str) -> tuple[str, str | None]:
    match = _FIX_LINE.search(reply)
    if not match:
        return reply.strip(), None
    return reply[: match.start()].strip(), reply[match.end():].strip()


def generate_text(contents: list, system_instruction: str, timeout_ms: int = 20000) -> str:
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
        response = client.models.generate_content(
            model=model, contents=contents, config=config
        )
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


def _build_system_prompt(lang: str, level: str) -> str:
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
    return prompt


def speakable(conversation: str) -> str:
    lines = conversation.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(("Pinyin:", "Romaji:", "Arti:")):
            return "\n".join(lines[:index]).strip()
    return conversation.strip()