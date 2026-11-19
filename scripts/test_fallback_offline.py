import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services import llm

_orig_ask_tutor_groq = llm._ask_tutor_groq

HISTORY = [{"role": "user", "text": "Hello, how are you?"}]

results = []


class GeminiError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{status}: {name}{detail}")


def reset():
    os.environ.pop("FLUENTA_FORCE_FALLBACK", None)
    os.environ["FLUENTA_GEMINI_COOLDOWN_S"] = "0"
    llm._gemini_cooldown_until = 0.0


# a) Gemini sukses -> Groq tidak dipanggil, provider "gemini"
def gemini_ok(*args, **kwargs):
    return "Balasan Gemini"


def groq_not_called(*args, **kwargs):
    raise AssertionError("Groq tidak boleh dipanggil")


reset()
llm._ask_tutor_gemini = gemini_ok
llm._ask_tutor_groq = groq_not_called
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("a) Gemini sukses -> provider gemini, Groq tidak dipanggil",
          provider == "gemini" and text == "Balasan Gemini")
except Exception as exc:
    check("a) Gemini sukses -> provider gemini, Groq tidak dipanggil", False, f" | error: {exc}")


# b) Gemini 429 -> Groq dipanggil, provider "groq"
groq_called = False


def gemini_429(*args, **kwargs):
    raise GeminiError("Kuota habis", code=429)


def groq_ok(*args, **kwargs):
    global groq_called
    groq_called = True
    return "Balasan Groq"


reset()
llm._ask_tutor_gemini = gemini_429
llm._ask_tutor_groq = groq_ok
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("b) Gemini 429 -> provider groq",
          provider == "groq" and groq_called and text == "Balasan Groq")
except Exception as exc:
    check("b) Gemini 429 -> provider groq", False, f" | error: {exc}")


# c1) Gemini 503 -> Groq dipanggil
groq_called = False


def gemini_503(*args, **kwargs):
    raise GeminiError("Server error", code=503)


reset()
llm._ask_tutor_gemini = gemini_503
llm._ask_tutor_groq = groq_ok
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("c1) Gemini 503 -> provider groq",
          provider == "groq" and groq_called)
except Exception as exc:
    check("c1) Gemini 503 -> provider groq", False, f" | error: {exc}")


# c2) Gemini timeout -> Groq dipanggil
groq_called = False


def gemini_timeout(*args, **kwargs):
    raise TimeoutError("read timeout")


reset()
llm._ask_tutor_gemini = gemini_timeout
llm._ask_tutor_groq = groq_ok
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("c2) Gemini timeout -> provider groq",
          provider == "groq" and groq_called)
except Exception as exc:
    check("c2) Gemini timeout -> provider groq", False, f" | error: {exc}")


# d1) Gemini 400 -> TIDAK fallback, error muncul
def gemini_400(*args, **kwargs):
    raise GeminiError("Bad request", code=400)


reset()
llm._ask_tutor_gemini = gemini_400
llm._ask_tutor_groq = groq_not_called
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("d1) Gemini 400 -> tidak fallback, error muncul", False)
except Exception as exc:
    check("d1) Gemini 400 -> tidak fallback, error muncul",
          "Bad request" in str(exc) or "400" in str(exc), f" | error: {exc}")


# d2) Gemini 404 -> TIDAK fallback, error muncul
def gemini_404(*args, **kwargs):
    raise GeminiError("Not found", code=404)


reset()
llm._ask_tutor_gemini = gemini_404
llm._ask_tutor_groq = groq_not_called
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("d2) Gemini 404 -> tidak fallback, error muncul", False)
except Exception as exc:
    check("d2) Gemini 404 -> tidak fallback, error muncul",
          "Not found" in str(exc) or "404" in str(exc), f" | error: {exc}")


# e) Groq juga gagal -> error Gemini asli yang dilempar
def gemini_429_e(*args, **kwargs):
    raise GeminiError("Kuota habis asli", code=429)


def groq_fail(*args, **kwargs):
    raise RuntimeError("Groq juga gagal")


reset()
llm._ask_tutor_gemini = gemini_429_e
llm._ask_tutor_groq = groq_fail
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("e) Groq juga gagal -> error Gemini asli dilempar", False)
except GeminiError as exc:
    check("e) Groq juga gagal -> error Gemini asli dilempar",
          str(exc) == "Kuota habis asli")
except Exception as exc:
    check("e) Groq juga gagal -> error Gemini asli dilempar", False,
          f" | error: {type(exc).__name__}: {exc}")


# f) content Groq kosong -> dianggap gagal (error Gemini asli dilempar)
def gemini_429_f(*args, **kwargs):
    raise GeminiError("Kuota habis", code=429)


orig_groq_key_f = llm.GROQ_API_KEY
orig_groq_model_f = llm.GROQ_MODEL
llm.GROQ_API_KEY = "test-key-f"
llm.GROQ_MODEL = "openai/gpt-oss-120b"

import requests

orig_post = requests.post


class FakeEmptyResponse:
    def __init__(self):
        self.status_code = 200
        self.text = ""

    def json(self):
        return {"id": "x", "object": "chat.completion", "model": "m",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": ""}}]}


def fake_post_empty(url, headers, json, timeout):
    return FakeEmptyResponse()


reset()
llm._ask_tutor_gemini = gemini_429_f
requests.post = fake_post_empty
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("f) content Groq kosong -> dianggap gagal", False)
except Exception as exc:
    check("f) content Groq kosong -> dianggap gagal",
          "Kuota habis" in str(exc), f" | error: {exc}")
finally:
    requests.post = orig_post
    llm.GROQ_API_KEY = orig_groq_key_f
    llm.GROQ_MODEL = orig_groq_model_f


# g) GROQ_API_KEY kosong -> tidak fallback
orig_groq_key = llm.GROQ_API_KEY
orig_groq_model = llm.GROQ_MODEL
llm.GROQ_API_KEY = None
llm.GROQ_MODEL = None

reset()
llm._ask_tutor_gemini = gemini_429
llm._ask_tutor_groq = groq_ok
try:
    text, provider = llm.ask_tutor_ex(HISTORY)
    check("g) GROQ_API_KEY kosong -> tidak fallback", False)
except GeminiError as exc:
    check("g) GROQ_API_KEY kosong -> tidak fallback",
          str(exc) == "Kuota habis")
except Exception as exc:
    check("g) GROQ_API_KEY kosong -> tidak fallback", False,
          f" | error: {type(exc).__name__}: {exc}")

llm.GROQ_API_KEY = orig_groq_key
llm.GROQ_MODEL = orig_groq_model


# h) Teks 	... dibuang, field reasoning tidak pernah dipakai
class FakeThinkResponse:
    def __init__(self):
        self.status_code = 200
        self.text = ""

    def json(self):
        return {"id": "x", "object": "chat.completion", "model": "openai/gpt-oss-120b",
                "choices": [{"index": 0, "message": {
                    "role": "assistant",
                    "content": "Balasan asli.\n\n```think\nSaya sedang berpikir dalam biasa.\n```\nAkhir dari balasan.",
                    "reasoning": "Ini adalah field reasoning yang JANGAN boleh digunakan"
                }}]}


def fake_post_think(url, headers, json, timeout):
    return FakeThinkResponse()


llm._ask_tutor_groq = _orig_ask_tutor_groq
reset()
requests.post = fake_post_think
try:
    text = llm._ask_tutor_groq(HISTORY, "en", "intermediate", False)
    print(f"DEBUG h: {repr(text)}")
    check("h) 	... dibuang, reasoning tidak dipakai",
          "think" not in text.lower() and "Saya sedang berpikir" not in text
          and "Balasan asli" in text and "Akhir dari balasan" in text)
except Exception as exc:
    check("h) 	... dibuang, reasoning tidak dipakai", False, f" | error: {exc}")
finally:
    requests.post = orig_post


# Ringkasan
print("\n=== Ringkasan Tes Offline ===")
passed = sum(1 for _, s in results if s == "PASS")
failed = sum(1 for _, s in results if s == "FAIL")
for name, status in results:
    print(f"  {status}: {name}")
print(f"\nLulus: {passed}/{len(results)}")
if failed:
    print(f"Gagal: {failed}")
    sys.exit(1)