import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services import llm

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


CONTENTS = [{"role": "user", "parts": [{"text": "Halo, apa kabar?"}]}]
INSTRUCTION = "Translate the user's text into English. Output only the translation."

orig_groq_translate = llm._groq_translate


# a) Gemini sukses -> provider gemini, Groq tidak dipanggil
def gemini_ok(*args, **kwargs):
    return "Halo, apa kabar? (translated)"


def groq_not_called(*args, **kwargs):
    raise AssertionError("Groq tidak boleh dipanggil")


reset()
llm.generate_text = gemini_ok
llm._groq_translate = groq_not_called
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("a) Gemini sukses -> provider gemini, Groq tidak dipanggil",
          provider == "gemini" and text == "Halo, apa kabar? (translated)")
except Exception as exc:
    check("a) Gemini sukses -> provider gemini, Groq tidak dipanggil", False, f" | error: {exc}")


# b) Gemini 429 -> groq
groq_called = False


def gemini_429(*args, **kwargs):
    raise GeminiError("Kuota habis", code=429)


def groq_ok(*args, **kwargs):
    global groq_called
    groq_called = True
    return "Halo, apa kabar? (groq)"


reset()
llm.generate_text = gemini_429
llm._groq_translate = groq_ok
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("b) Gemini 429 -> provider groq",
          provider == "groq" and groq_called and text == "Halo, apa kabar? (groq)")
except Exception as exc:
    check("b) Gemini 429 -> provider groq", False, f" | error: {exc}")


# c1) Gemini 503 -> groq
groq_called = False


def gemini_503(*args, **kwargs):
    raise GeminiError("Server error", code=503)


reset()
llm.generate_text = gemini_503
llm._groq_translate = groq_ok
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("c1) Gemini 503 -> provider groq",
          provider == "groq" and groq_called)
except Exception as exc:
    check("c1) Gemini 503 -> provider groq", False, f" | error: {exc}")


# c2) Gemini timeout -> groq
groq_called = False


def gemini_timeout(*args, **kwargs):
    raise TimeoutError("read timeout")


reset()
llm.generate_text = gemini_timeout
llm._groq_translate = groq_ok
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("c2) Gemini timeout -> provider groq",
          provider == "groq" and groq_called)
except Exception as exc:
    check("c2) Gemini timeout -> provider groq", False, f" | error: {exc}")


# d1) Gemini 400 -> tidak fallback, error muncul
def gemini_400(*args, **kwargs):
    raise GeminiError("Bad request", code=400)


reset()
llm.generate_text = gemini_400
llm._groq_translate = groq_not_called
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("d1) Gemini 400 -> tidak fallback, error muncul", False)
except Exception as exc:
    check("d1) Gemini 400 -> tidak fallback, error muncul",
          "Bad request" in str(exc) or "400" in str(exc), f" | error: {exc}")


# d2) Gemini 404 -> tidak fallback, error muncul
def gemini_404(*args, **kwargs):
    raise GeminiError("Not found", code=404)


reset()
llm.generate_text = gemini_404
llm._groq_translate = groq_not_called
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("d2) Gemini 404 -> tidak fallback, error muncul", False)
except Exception as exc:
    check("d2) Gemini 404 -> tidak fallback, error muncul",
          "Not found" in str(exc) or "404" in str(exc), f" | error: {exc}")


# e) Groq juga gagal -> error Gemini asli
def gemini_429_e(*args, **kwargs):
    raise GeminiError("Kuota habis asli", code=429)


def groq_fail(*args, **kwargs):
    raise RuntimeError("Groq juga gagal")


reset()
llm.generate_text = gemini_429_e
llm._groq_translate = groq_fail
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("e) Groq juga gagal -> error Gemini asli dilempar", False)
except GeminiError as exc:
    check("e) Groq juga gagal -> error Gemini asli dilempar",
          str(exc) == "Kuota habis asli")
except Exception as exc:
    check("e) Groq juga gagal -> error Gemini asli dilempar", False,
          f" | error: {type(exc).__name__}: {exc}")


# f) content Groq kosong -> gagal (error Gemini asli)
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
llm.generate_text = gemini_429_f
llm._groq_translate = orig_groq_translate
requests.post = fake_post_empty
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
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
llm.generate_text = gemini_429
llm._groq_translate = groq_ok
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("g) GROQ_API_KEY kosong -> tidak fallback", False)
except GeminiError as exc:
    check("g) GROQ_API_KEY kosong -> tidak fallback",
          str(exc) == "Kuota habis")
except Exception as exc:
    check("g) GROQ_API_KEY kosong -> tidak fallback", False,
          f" | error: {type(exc).__name__}: {exc}")

llm.GROQ_API_KEY = orig_groq_key
llm.GROQ_MODEL = orig_groq_model


# h) teks > 3000 karakter -> tidak fallback
long_text = "x" * 3500
long_contents = [{"role": "user", "parts": [{"text": long_text}]}]


def gemini_429_h(*args, **kwargs):
    raise GeminiError("Kuota habis", code=429)


reset()
llm.generate_text = gemini_429_h
llm._groq_translate = groq_not_called
try:
    text, provider = llm.generate_text_ex(long_contents, INSTRUCTION)
    check("h) teks > 3000 karakter -> tidak fallback", False)
except GeminiError as exc:
    check("h) teks > 3000 karakter -> tidak fallback",
          str(exc) == "Kuota habis")
except Exception as exc:
    check("h) teks > 3000 karakter -> tidak fallback", False,
          f" | error: {type(exc).__name__}: {exc}")


# i) generate_text lama tidak pernah memanggil Groq
groq_call_count = [0]


def groq_counting(*args, **kwargs):
    groq_call_count[0] += 1
    return "groq result"


def gemini_ok_i(*args, **kwargs):
    return "gemini result"


reset()
llm.generate_text = gemini_ok_i
llm._groq_translate = groq_counting
try:
    text, provider = llm.generate_text_ex(CONTENTS, INSTRUCTION)
    check("i) generate_text lama tidak pernah memanggil Groq",
          provider == "gemini" and groq_call_count[0] == 0,
          f" | groq_called={groq_call_count[0]}")
except Exception as exc:
    check("i) generate_text lama tidak pernah memanggil Groq", False,
          f" | error: {exc}")


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