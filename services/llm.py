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

# Cooldown Gemini untuk jalur chat tutor (ask_tutor_ex). time.monotonic-based.
_gemini_cooldown_until = 0.0


def _cooldown_aktif() -> bool:
    detik = float(os.getenv("FLUENTA_GEMINI_COOLDOWN_S", "0") or "0")
    if detik <= 0:
        return False
    return time.monotonic() < _gemini_cooldown_until


def _aktifkan_cooldown() -> None:
    global _gemini_cooldown_until
    detik = float(os.getenv("FLUENTA_GEMINI_COOLDOWN_S", "0") or "0")
    if detik > 0:
        _gemini_cooldown_until = time.monotonic() + detik


GROQ_EXTRA_RULES = (
    "ATURAN TAMBAHAN: Penjelasan pada baris Fix WAJIB berbahasa Indonesia, 1 sampai 2 kalimat lengkap, "
    "sebutkan aturan grammar-nya dan alasan kenapa kalimat awal salah. Dilarang menulis penjelasan dalam bahasa Inggris. "
    "Dilarang juga menulis penjelasan dalam bahasa yang sedang dipelajari (Mandarin atau Jepang). "
    "Format baris Fix harus persis: Fix: <kalimat benar> || <penjelasan Indonesia> || <tag>. "
    "Jika kalimat pengguna sudah benar, JANGAN menulis baris Fix. "
    "Jika diminta membalas dalam bahasa lain (Mandarin/Jepang), balasan utama ditulis dalam bahasa itu, lalu tambahkan baris "
    "Pinyin/Romaji dan Arti sesuai format yang diminta. "
    "Contoh baris Fix Mandarin: Fix: 我昨天去学校。 || Keterangan waktu 昨天 diletakkan sebelum kata kerja. || word_order. "
    "Contoh baris Fix Jepang: Fix: 私は学校へ行きます。 || Gunakan partikel へ atau に untuk tujuan, bukan を. || prepositions."
    " Bila pesan pengguna adalah sapaan, ucapan terima kasih, kata tunggal, "
    "atau frasa pendek yang bermakna (contoh: hello, thank you, Konnichiwa, "
    "Ni hao, coffee please), anggap itu normal bagi pemula; balas dengan ramah "
    "dan lanjutkan percakapan, JANGAN meminta menulis ulang. Terapkan penolakan "
    "hanya bila pesan terdiri dari kata-kata acak tanpa makna yang bisa "
    "dipahami. Dilarang mengarang riwayat percakapan atau mengklaim sudah "
    "membahas sesuatu sebelumnya."
)

SYSTEM_PROMPT = (
    "You are a friendly English tutor and conversation partner for an Indonesian "
    "learner. Reply in simple English, maximum 3 short sentences, and end with one "
    "follow-up question. The user's message may come from speech transcription, so "
    "IGNORE punctuation, capitalization, and likely transcription glitches. Only "
    "correct real mistakes in grammar, tense, word choice, or unnatural phrasing. "
    "If the user's last message has a real mistake, add a final line starting "
    "exactly with 'Fix: ' in a single line: 'Fix: <corrected sentence> || "
    "<short explanation in Indonesian ONLY. The explanation MUST be in Indonesian, never in English and never in the language being learned (Mandarin or Japanese).> || <tag>', where tag is "
    "exactly one of: past_tense, present_tense, future_tense, articles, "
    "prepositions, subject_verb_agreement, plural_singular, word_order, "
    "word_choice, collocation, code_mixing, other. If there is no real "
    "mistake, do not add a Fix line."
    "If the user's message is a greeting, thanks, a single word, or a short "
    "meaningful phrase (for example: hello, thank you, Konnichiwa, Ni hao, "
    "coffee please), treat it as normal for a beginner; reply friendly and "
    "continue the conversation, do not ask the user to rewrite. Only refuse to "
    "treat it as meaningful if the message consists of random words without "
    "understandable meaning. Do not invent conversation history or claim to "
    "have discussed something before."
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
    client: genai.Client,
    model: str,
    contents: list,
    config: types.GenerateContentConfig,
    retry: bool = True,
):
    try:
        return client.models.generate_content(model=model, contents=contents, config=config)
    except Exception as exc:
        if not retry or not _is_transient_error(exc):
            raise
        time.sleep(2)
        return client.models.generate_content(model=model, contents=contents, config=config)


def _ask_tutor_gemini(
    history: list[dict],
    lang: str = "en",
    level: str = "intermediate",
    mixed: bool = False,
    retry: bool = True,
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
        response = _generate_with_retry(
            client, model, contents, config, retry=retry
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


def _should_fallback_to_groq(exc: Exception) -> bool:
    """Deteksi error yang layak diganti ke Groq.

    Telusuri rantai pengecuali (__cause__ dan __context__) karena pemanggil
    dapat menerima RuntimeError pembungkus dengan exception asli SDK
    (misal google.genai.errors.APIError, code 429) tersembunyi di dalamnya.
    Kode 4xx selain 429 (400, 401, 403, 404) tidak memicu fallback.
    """

    def norm(teks: str) -> str:
        return teks.lower().replace("_", "").replace("-", "").replace(" ", "")

    penanda = ("429", "resourceexhausted", "quota", "kuotageminihabis",
               "503", "unavailable", "504", "deadlineexceeded", "timeout")
    status_penanda = ("resourceexhausted", "unavailable", "deadlineexceeded")
    seen = set()
    node: Exception | None = exc
    while node is not None and id(node) not in seen:
        seen.add(id(node))
        kode = getattr(node, "code", None)
        if not isinstance(kode, int):
            kode = getattr(node, "status_code", None)
        if not isinstance(kode, int):
            kode = getattr(node, "status", None)
        if isinstance(kode, int):
            if kode == 429 or 500 <= kode < 600:
                return True
        else:
            status_teks = getattr(node, "status", None)
            if isinstance(status_teks, str) and any(
                p in norm(status_teks) for p in status_penanda
            ):
                return True
        if any(
            p in (norm(str(node)) + norm(type(node).__name__)) for p in penanda
        ):
            return True
        node = getattr(node, "__cause__", None) or getattr(
            node, "__context__", None
        )
    return False


def _strip_think(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"</?think>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```think.*?```", "", text, flags=re.DOTALL)
    return text.strip()


_HAN_KANA = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")
_HURUF = re.compile(r"[^\W\d_]", re.UNICODE)
_PENNANTA_ID = ("yang", "dan", "untuk", "karena", "harus", "gunakan",
                "kata", "dengan", "atau", "bukan", "di", "ke")


def _penjelasan_bukan_indonesia(teks_fix: str) -> bool:
    """True jika penjelasan di baris Fix terindikasi bukan bahasa Indonesia.

    Ambil bagian kedua di antara '||', hapus teks dalam tanda kutip terlebih
    dahulu, lalu nyatakan pelanggaran bila rasio aksara Han/kana terhadap
    seluruh huruf > 20% atau tidak ada kata penanda Indonesia sama sekali.
    """
    if not teks_fix:
        return False
    hasil = parse_fix(teks_fix)
    if not hasil["structured"]:
        return False
    penjelasan = hasil["explanation"]
    bersih = re.sub(r"「[^」]*」", "", penjelasan)
    bersih = re.sub(r"\u201c[^\u201d]*\u201d", "", bersih)
    bersih = re.sub(r"\u2018[^\u2019]*\u2019", "", bersih)
    bersih = re.sub(r'"[^"]*"', "", bersih)
    bersih = re.sub(r"'[^']*'", "", bersih)
    huruf = _HURUF.findall(bersih)
    if huruf:
        han_kana = len(_HAN_KANA.findall(bersih))
        if han_kana / len(huruf) > 0.20:
            return True
    for kata in _PENNANTA_ID:
        if re.search(r"\b" + re.escape(kata) + r"\b", bersih.lower()):
            return False
    return True


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


def _groq_chat(system_prompt: str, user_text: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")
    if not api_key or not model:
        raise RuntimeError("GROQ_API_KEY atau GROQ_MODEL belum diisi di .env")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
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
        if groq_available and not _cooldown_aktif():
            # Satu percobaan Gemini tanpa retry transient; langsung ke Groq saat gagal.
            try:
                text = _ask_tutor_gemini(history, lang, level, mixed, retry=False)
                return text, "gemini"
            except Exception as exc:
                gemini_error = exc
                if not _should_fallback_to_groq(exc):
                    raise
        elif not groq_available:
            # Perilaku lama: Gemini dengan retry transient, tidak ada fallback ke Groq.
            try:
                text = _ask_tutor_gemini(history, lang, level, mixed, retry=True)
                return text, "gemini"
            except Exception as exc:
                gemini_error = exc
                if not _should_fallback_to_groq(exc):
                    raise
                raise
        # groq tersedia tetapi cooldown aktif -> langsung ke Groq di bawah.

    if groq_available:
        try:
            text = _ask_tutor_groq(history, lang, level, mixed)
            if gemini_error is not None:
                _aktifkan_cooldown()
            # BAGIAN 2c: satu kali percobaan ulang ke Groq bila penjelasan Fix bukan Indonesia
            match = _FIX_LINE.search(text)
            if match:
                baris_fix = text[match.start():].split("\n", 1)[0]
                if _penjelasan_bukan_indonesia(baris_fix):
                    ulang_history = list(history) + [
                        {"role": "user", "text": "Tulis ulang. Penjelasan di baris Fix WAJIB bahasa Indonesia."}
                    ]
                    text = _ask_tutor_groq(ulang_history, lang, level, mixed)
            return text, "groq"
        except Exception as groq_exc:
            print(f"Gagal fallback ke Groq: {type(groq_exc).__name__}: {str(groq_exc)[:200]}")
            if gemini_error is not None:
                raise gemini_error from groq_exc
            raise

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
            "\nReply in Mandarin Chinese (Simplified). ALL Mandarin text in your reply, "
            "including the follow-up question, MUST be written before the 'Pinyin: ' and "
            "'Arti: ' lines. Both lines MUST cover the entire Mandarin text, including "
            "the follow-up question. Do NOT write any Mandarin text after the 'Arti: ' "
            "line. Add a line starting exactly with 'Pinyin: ' and a line starting "
            "exactly with 'Arti: ' (Indonesian meaning). Place any Fix line last. "
            "Contoh baris Fix Mandarin: Fix: 我昨天去学校。 || Keterangan waktu 昨天 diletakkan sebelum kata kerja. || word_order."
        )
    elif lang == "ja":
        prompt += (
            "\nReply in Japanese. ALL Japanese text in your reply, including the "
            "follow-up question, MUST be written before the 'Romaji: ' and 'Arti: ' "
            "lines. Both lines MUST cover the entire Japanese text, including the "
            "follow-up question. Do NOT write any Japanese text after the 'Arti: ' "
            "line. Add a line starting exactly with 'Romaji: ' and a line starting "
            "exactly with 'Arti: ' (Indonesian meaning). Place any Fix line last. "
            "Contoh baris Fix Jepang: Fix: 私は学校へ行きます。 || Gunakan partikel へ atau に untuk tujuan, bukan を. || prepositions."
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