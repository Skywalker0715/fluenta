"""Tes offline cooldown Gemini pada jalur chat tutor (ask_tutor_ex).

Waktu (time.monotonic / time.sleep) di-stub, tanpa memanggil API live.
_ask_tutor_gemini dan _ask_tutor_groq asli diganti dengan tiruan yang dapat
dikontrol. Kunci yang digunakan hanyalah nilai tiruan dalam proses tes ini
(bukan isi .env, tidak dicetak).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services import llm

results = []

HISTORY = [{"role": "user", "text": "Hello, how are you?"}]

# Nilai tiruan agar jalur asli (bukan mock ask_tutor_ex) dapat berjalan.
env_cadangan = {
    "GEMINI_API_KEY": "tes-kunci-gemini",
    "GEMINI_MODEL": "tes-model-gemini",
    "FLUENTA_GEMINI_COOLDOWN_S": "120",
}
env_lama = {}
for kunci, nilai in env_cadangan.items():
    env_lama[kunci] = os.environ.get(kunci)
    os.environ[kunci] = nilai
os.environ.pop("FLUENTA_FORCE_FALLBACK", None)

orig_groq_key = llm.GROQ_API_KEY
orig_groq_model = llm.GROQ_MODEL
llm.GROQ_API_KEY = "tes-kunci-groq"
llm.GROQ_MODEL = "openai/gpt-oss-120b"

# Variabel waktu yang dikontrol tes.
_waktu = [0.0]


def now_monotonic():
    return _waktu[0]


def sleep_stub(_detik):
    pass


orig_monotonic = llm.time.monotonic
orig_sleep = llm.time.sleep
llm.time.monotonic = now_monotonic
llm.time.sleep = sleep_stub

orig_ask_gemini = llm._ask_tutor_gemini
orig_ask_groq = llm._ask_tutor_groq


class Gemini429(Exception):
    def __init__(self):
        super().__init__("429 RESOURCE_EXHAUSTED. Kuota habis")
        self.code = 429
        self.status = "RESOURCE_EXHAUSTED"
        self.status_code = 429


class Gemini503(Exception):
    def __init__(self):
        super().__init__("503 Server error")
        self.code = 503
        self.status = "UNAVAILABLE"
        self.status_code = 503


class Gemini400(Exception):
    def __init__(self):
        super().__init__("400 Bad request")
        self.code = 400
        self.status = "BAD_REQUEST"
        self.status_code = 400


class Gemini404(Exception):
    def __init__(self):
        super().__init__("404 Not found")
        self.code = 404
        self.status = "NOT_FOUND"
        self.status_code = 404


def check(nama, kondisi, detail=""):
    status = "PASS" if kondisi else "FAIL"
    results.append((nama, status))
    print(f"{status}: {nama}{detail}")


def reset_modul():
    llm._gemini_cooldown_until = 0.0
    _waktu[0] = 0.0
    llm.GROQ_API_KEY = "tes-kunci-groq"
    llm.GROQ_MODEL = "openai/gpt-oss-120b"


def pasang(gemini_hasil, groq_hasil):
    """gemini_hasil: teks (sukses) atau Exception. groq_hasil: teks atau Exception."""
    panggilan = {"gemini": 0, "groq": 0}

    def gemini_tiruan(*args, **kwargs):
        panggilan["gemini"] += 1
        if isinstance(gemini_hasil, Exception):
            raise gemini_hasil
        return gemini_hasil

    def groq_tiruan(*args, **kwargs):
        panggilan["groq"] += 1
        if isinstance(groq_hasil, Exception):
            raise groq_hasil
        return groq_hasil

    llm._ask_tutor_gemini = gemini_tiruan
    llm._ask_tutor_groq = groq_tiruan
    return panggilan


def lepaskan():
    llm._ask_tutor_gemini = orig_ask_gemini
    llm._ask_tutor_groq = orig_ask_groq


def panggil():
    try:
        teks, provider = llm.ask_tutor_ex(HISTORY)
        return provider, teks, None
    except Exception as exc:
        return None, None, exc


# (a) Gemini 429 lalu Groq sukses mengaktifkan cooldown;
#     panggilan berikutnya langsung Groq tanpa memanggil Gemini.
reset_modul()
p = pasang(Gemini429(), "Balasan Groq")
provider, _, error = panggil()
check(
    "a) Gemini 429 + Groq sukses -> provider groq, cooldown aktif",
    provider == "groq" and p["gemini"] == 1 and p["groq"] == 1 and error is None,
    f" | provider={provider} gemini={p['gemini']} groq={p['groq']} error={error}",
)
provider2, _, error2 = panggil()  # waktu masih 0, cooldown masih aktif
check(
    "a2) selama cooldown -> langsung Groq, Gemini tidak dipanggil",
    provider2 == "groq" and p["gemini"] == 1 and p["groq"] == 2 and error2 is None,
    f" | provider={provider2} gemini={p['gemini']} groq={p['groq']} error={error2}",
)
lepaskan()

# (b) setelah cooldown habis (waktu 200 > 120) Gemini dipanggil lagi.
reset_modul()
_waktu[0] = 200.0
p = pasang("Balasan Gemini", "Balasan Groq")
provider, _, error = panggil()
check(
    "b) setelah cooldown habis -> Gemini dipanggil lagi",
    provider == "gemini" and p["gemini"] == 1 and error is None,
    f" | provider={provider} gemini={p['gemini']} error={error}",
)
lepaskan()


# (c) Groq tersedia -> hanya SATU percobaan Gemini (tanpa retry transient).
reset_modul()
p = pasang(Gemini503(), "Balasan Groq")
provider, _, error = panggil()
check(
    "c) Groq tersedia -> satu percobaan Gemini (tanpa retry)",
    provider == "groq" and p["gemini"] == 1 and p["groq"] == 1 and error is None,
    f" | provider={provider} gemini={p['gemini']} groq={p['groq']} error={error}",
)
lepaskan()

# (d) Groq tidak tersedia -> perilaku retry lama (transient dipanggil 2x).
reset_modul()
llm.GROQ_API_KEY = None
llm.GROQ_MODEL = None
p = pasang(Gemini503(), "Balasan Groq")
try:
    provider, _, error = panggil()
    check(
        "d) Groq tidak tersedia -> tidak fallback ke Groq, error Gemini muncul",
        provider is None and p["groq"] == 0 and error is not None and "503" in str(error),
        f" | provider={provider} groq={p['groq']} gemini={p['gemini']} error={error}",
    )
except Exception as exc:
    check(
        "d) Groq tidak tersedia -> tidak fallback ke Groq, error Gemini muncul",
        p["groq"] == 0,
        f" | exception: {exc}",
    )
lepaskan()
llm.GROQ_API_KEY = orig_groq_key
llm.GROQ_MODEL = orig_groq_model


# (e) cooldown=0 -> tidak ada cooldown (panggilan berikutnya masih Gemini).
reset_modul()
os.environ["FLUENTA_GEMINI_COOLDOWN_S"] = "0"
p = pasang(Gemini429(), "Balasan Groq")
provider, _, error = panggil()
check(
    "e) cooldown=0 -> fallback pertama ke Groq",
    provider == "groq" and p["gemini"] == 1 and p["groq"] == 1 and error is None,
    f" | provider={provider} gemini={p['gemini']} groq={p['groq']} error={error}",
)
provider2, _, error2 = panggil()  # cooldown nonaktif meski waktu masih 0
check(
    "e2) cooldown=0 -> coba Gemini lagi (tidak ada cooldown yang mencegah)",
    p["gemini"] == 2 and error2 is None,
    f" | provider={provider2} gemini={p['gemini']} error={error2}",
)
os.environ["FLUENTA_GEMINI_COOLDOWN_S"] = "120"
lepaskan()

# (f) Gemini sukses tidak mengaktifkan cooldown.
reset_modul()
p = pasang("Balasan Gemini", "Balasan Groq")
provider, _, error = panggil()
check(
    "f) Gemini sukses -> provider gemini, cooldown tidak aktif",
    provider == "gemini" and p["gemini"] == 1 and p["groq"] == 0 and error is None,
    f" | provider={provider} gemini={p['gemini']} groq={p['groq']} error={error}",
)
provider2, _, error2 = panggil()  # cooldown tidak aktif (until=0)
check(
    "f2) Gemini sukses -> panggilan berikutnya tetap Gemini",
    provider2 == "gemini" and p["gemini"] == 2 and error2 is None,
    f" | provider={provider2} gemini={p['gemini']} error={error2}",
)
lepaskan()


# (g) error 400 dan 404 tidak fallback dan tidak memicu cooldown.
reset_modul()
p = pasang(Gemini400(), "Balasan Groq")
try:
    provider, _, error = panggil()
    check(
        "g1) 400 -> tidak fallback, error muncul, Groq tidak dipanggil",
        provider is None and p["gemini"] == 1 and p["groq"] == 0 and error is not None,
        f" | provider={provider} error={error}",
    )
except Exception as exc:
    check(
        "g1) 400 -> tidak fallback, error muncul, Groq tidak dipanggil",
        p["gemini"] == 1 and p["groq"] == 0,
        f" | exception: {exc}",
    )
provider2, _, error2 = panggil()  # tidak ada cooldown, Gemini dipanggil lagi
check(
    "g2) 400 -> tidak cooldown, Gemini dipanggil lagi",
    provider2 is None and p["gemini"] == 2,
    f" | provider={provider2} gemini={p['gemini']} error={error2}",
)
lepaskan()

reset_modul()
p = pasang(Gemini404(), "Balasan Groq")
try:
    provider, _, error = panggil()
    check(
        "g3) 404 -> tidak fallback, error muncul, Groq tidak dipanggil",
        provider is None and p["gemini"] == 1 and p["groq"] == 0 and error is not None,
        f" | provider={provider} error={error}",
    )
except Exception as exc:
    check(
        "g3) 404 -> tidak fallback, error muncul, Groq tidak dipanggil",
        p["gemini"] == 1 and p["groq"] == 0,
        f" | exception: {exc}",
    )
lepaskan()

# (h) Groq juga gagal -> melempar error Gemini asli, tanpa cooldown.
reset_modul()
p = pasang(Gemini429(), RuntimeError("Gagal Groq"))
try:
    provider, _, error = panggil()
    check(
        "h) Groq gagal -> error Gemini dilempar, tanpa cooldown",
        provider is None and p["gemini"] == 1 and p["groq"] == 1 and error is not None,
        f" | provider={provider} error={error}",
    )
except Exception as exc:
    check(
        "h) Groq gagal -> error Gemini dilempar, tanpa cooldown",
        p["gemini"] == 1 and p["groq"] == 1 and "429" in str(exc),
        f" | exception: {exc}",
    )
provider2, _, error2 = panggil()  # tidak cooldown, Gemini dipanggil lagi
check(
    "h2) Groq gagal -> tidak cooldown, Gemini dipanggil lagi",
    provider2 is None and p["gemini"] == 2,
    f" | provider={provider2} gemini={p['gemini']} error={error2}",
)
lepaskan()

# Pemulihan environment.
llm.GROQ_API_KEY = orig_groq_key
llm.GROQ_MODEL = orig_groq_model
llm.time.monotonic = orig_monotonic
llm.time.sleep = orig_sleep
for kunci, nilai in env_lama.items():
    if nilai is None:
        os.environ.pop(kunci, None)
    else:
        os.environ[kunci] = nilai


print("\n=== Ringkasan Tes Cooldown Gemini (Offline) ===")
lulus = sum(1 for _, s in results if s == "PASS")
gagal = sum(1 for _, s in results if s == "FAIL")
for nama, status in results:
    print(f"  {status}: {nama}")
print(f"\nLulus: {lulus}/{len(results)}")
if gagal:
    print(f"Gagal: {gagal}")
    sys.exit(1)