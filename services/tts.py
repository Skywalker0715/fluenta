import os

import requests
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID")
ELEVEN_MODEL_ID = os.getenv("ELEVEN_MODEL_ID", "eleven_turbo_v2_5")


def text_to_speech(text: str, lang: str = "en") -> bytes:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY belum diisi di .env")
    if not ELEVEN_VOICE_ID:
        raise RuntimeError("ELEVEN_VOICE_ID belum diisi di .env")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    payload = {"text": text, "model_id": ELEVEN_MODEL_ID, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.RequestException as exc:
        status_code = getattr(exc.response, "status_code", None)
        raise RuntimeError(f"Gagal mengirim teks ke ElevenLabs. Status: {status_code}") from exc
    return response.content
