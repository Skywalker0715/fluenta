import os

import requests
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


def speech_to_text(audio_bytes: bytes, lang: str = "en", content_type: str = "audio/wav") -> str:
    if not DEEPGRAM_API_KEY:
        raise RuntimeError("DEEPGRAM_API_KEY belum diisi di .env")
    url = "https://api.deepgram.com/v1/listen"
    params = {"model": "nova-2", "language": lang, "smart_format": "true"}
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": content_type,
    }
    try:
        response = requests.post(url, params=params, headers=headers, data=audio_bytes, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        status_code = getattr(exc.response, "status_code", None)
        raise RuntimeError(f"Gagal mengirim audio ke Deepgram. Status: {status_code}") from exc
    try:
        data = response.json()
        results = data.get("results", {})
        channels = results.get("channels", [])
        if channels:
            return channels[0].get("alternatives", [{}]) [0].get("transcript", "")
    except ValueError:
        pass
    return ""

