"""Tes offline fallback Groq pada error asli (dan yang sudah dibungkus) SDK google-genai.

Tidak memanggil API live. _ask_tutor_gemini asli dijalankan dengan klien tiruan;
ask_tutor_ex dievaluasi, dan _ask_tutor_groq di-mock. Kunci yang digunakan hanyalah
nilai tiruan dalam proses tes ini (bukan isi .env, tidak dicetak).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services import llm

results = []

HISTORY = [{"role": "user", "text": "Hello, how are you?"}]

# Nilai tiruan agar jalur asli (bukan mock) dapat sampai ke pemanggilan klien.
env_cadangan = {
    "GEMINI_API_KEY": "tes-kunci-gemini",
    "GEMINI_MODEL": "tes-model-gemini",
}
env_lama = {}
for kunci, nilai in env_cadangan.items():
    env_lama[kunci] = os.environ.get(kunci)
    os.environ.setdefault(kunci, nilai)
os.environ.pop("FLUENTA_FORCE_FALLBACK", None)

llm.GROQ_API_KEY = "tes-kunci-groq"
llm.GROQ_MODEL = "openai/gpt-oss-120b"

try:
    from google.genai.errors import APIError as _APIError
except Exception:  # stand-in jika tipe SDK tidak tersedia
    _APIError = None


def sdk_error(kode, status, pesan):
    """Exception yang meniru SDK google-genai (APIError asli bila tersedia)."""
    if _APIError is not None:
        return _APIError(kode, {"error": {"message": pesan, "status": status}}, None)

    class _Standin(Exception):
        def __init__(self, message, kode, status):
            super().__init__(message)
            self.code = kode
            self.status = status
            self.status_code = kode

    return _Standin(f"{kode} {status}. {pesan}", kode, status)


def check(nama, kondisi, detail=""):
    status = "PASS" if kondisi else "FAIL"
    results.append((nama, status))
    print(f"{status}: {nama}{detail}")


class _ModelTiruan:
    def __init__(self, exc):
        self.exc = exc

    def generate_content(self, model, contents, config):
        raise self.exc


class _KlienTiruan:
    def __init__(self, api_key=None, http_options=None, **kwargs):
        self.models = _ModelTiruan(_pelembar[0])


_pelembar = [None]
_orig_client = llm.genai.Client
_orig_groq = llm._ask_tutor_groq
_orig_sleep = llm.time.sleep


def pasang(exc):
    _pelembar[0] = exc
    llm.genai.Client = _KlienTiruan
    llm.time.sleep = lambda _detik: None


def lepaskan():
    llm.genai.Client = _orig_client
    llm._ask_tutor_groq = _orig_groq
    llm.time.sleep = _orig_sleep


def jalankan(exc):
    """Jalankan _ask_tutor_gemini asli melalui ask_tutor_ex; Groq di-mock."""
    os.environ["FLUENTA_GEMINI_COOLDOWN_S"] = "0"
    llm._gemini_cooldown_until = 0.0
    pasang(exc)
    dipanggil_groq = {"terpanggil": False}

    def groq_mock(*args, **kwargs):
        dipanggil_groq["terpanggil"] = True
        return "Balasan Groq"

    llm._ask_tutor_groq = groq_mock
    try:
        teks, penyedia = llm.ask_tutor_ex(HISTORY)
        return penyedia, dipanggil_groq["terpanggil"], teks, None
    except Exception as exc_akhir:
        return None, dipanggil_groq["terpanggil"], None, exc_akhir
    finally:
        lepaskan()


# 1) 429 RESOURCE_EXHAUSTED sampai sebagai RuntimeError pembungkus
#    "Kuota Gemini habis..." dari _ask_tutor_gemini (baris 99-102).
penyedia, terpanggil, teks, error = jalankan(
    sdk_error(429, "RESOURCE_EXHAUSTED", "Kuota habis")
)
check(
    "1) 429 RESOURCE_EXHAUSTED -> fallback ke Groq",
    penyedia == "groq" and terpanggil and teks == "Balasan Groq" and error is None,
    f" | penyedia={penyedia} groq={terpanggil} error={error}",
)

# 1b) Detektor langsung pada pembungkus ramah dengan penyebab 429 di __cause__.
pembungkus = RuntimeError("Kuota Gemini habis untuk saat ini. Coba lagi nanti.")
try:
    raise pembungkus from sdk_error(429, "RESOURCE_EXHAUSTED", "Kuota habis")
except Exception as bundling:
    check(
        "1b) Detektor langsung pembungkus 'Kuota Gemini habis...' (cause 429) -> True",
        llm._should_fallback_to_groq(bundling),
    )

# 2) 503 UNAVAILABLE -> fallback ke Groq
penyedia, terpanggil, teks, error = jalankan(sdk_error(503, "UNAVAILABLE", "macet"))
check(
    "2) 503 UNAVAILABLE -> fallback ke Groq",
    penyedia == "groq" and terpanggil and error is None,
    f" | penyedia={penyedia} error={error}",
)

# 3) 504 DEADLINE_EXCEEDED (timeout) -> fallback ke Groq
penyedia, terpanggil, teks, error = jalankan(
    sdk_error(504, "DEADLINE_EXCEEDED", "deadline exceeded")
)
check(
    "3) 504 DEADLINE_EXCEEDED -> fallback ke Groq",
    penyedia == "groq" and terpanggil and error is None,
    f" | penyedia={penyedia} error={error}",
)

# 4) 400 BAD_REQUEST -> TIDAK fallback, error Gemini muncul
penyedia, terpanggil, teks, error = jalankan(sdk_error(400, "BAD_REQUEST", "Bad request"))
check(
    "4) 400 BAD_REQUEST -> tidak fallback, error muncul",
    penyedia is None and not terpanggil and error is not None and "400" in str(error),
    f" | penyedia={penyedia} error={error}",
)

# 5) 404 NOT_FOUND -> TIDAK fallback, error Gemini muncul
penyedia, terpanggil, teks, error = jalankan(sdk_error(404, "NOT_FOUND", "Not found"))
check(
    "5) 404 NOT_FOUND -> tidak fallback, error muncul",
    penyedia is None and not terpanggil and error is not None and "404" in str(error),
    f" | penyedia={penyedia} error={error}",
)

# 6) Detektor langsung: 4xx lain tidak memicu fallback
check(
    "6a) Detektor langsung 400 -> False",
    not llm._should_fallback_to_groq(sdk_error(400, "BAD_REQUEST", "Bad request")),
)
check(
    "6b) Detektor langsung 404 -> False",
    not llm._should_fallback_to_groq(sdk_error(404, "NOT_FOUND", "Not found")),
)

# Pemulihan environment
for kunci, nilai in env_lama.items():
    if nilai is None:
        os.environ.pop(kunci, None)
    else:
        os.environ[kunci] = nilai


print("\n=== Ringkasan Tes Fallback Error Asal (Offline) ===")
lulus = sum(1 for _, s in results if s == "PASS")
gagal = sum(1 for _, s in results if s == "FAIL")
for nama, status in results:
    print(f"  {status}: {nama}")
print(f"\nLulus: {lulus}/{len(results)}")
if gagal:
    print(f"Gagal: {gagal}")
    sys.exit(1)