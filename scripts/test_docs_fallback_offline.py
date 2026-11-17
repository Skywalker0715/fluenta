import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
from services import docs

results = []

sleeps = []


class FakeResponse:
    def __init__(self, status_code, payload, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{status}: {name}{detail}")


def reset():
    os.environ.pop("FLUENTA_FORCE_FALLBACK", None)


orig_post = requests.post
orig_sleep = time.sleep
orig_groq_key = os.environ.get("GROQ_API_KEY")
orig_groq_model = os.environ.get("GROQ_MODEL")


def set_groq_env():
    os.environ["GROQ_API_KEY"] = "test-key"
    os.environ["GROQ_MODEL"] = "openai/gpt-oss-120b"


def restore_env():
    if orig_groq_key is None:
        os.environ.pop("GROQ_API_KEY", None)
    else:
        os.environ["GROQ_API_KEY"] = orig_groq_key
    if orig_groq_model is None:
        os.environ.pop("GROQ_MODEL", None)
    else:
        os.environ["GROQ_MODEL"] = orig_groq_model


def restore():
    requests.post = orig_post
    time.sleep = orig_sleep
    restore_env()


# a) teks pendek -> 1 panggilan Groq
calls = []


def fake_post_ok(url, headers, json, timeout):
    calls.append(json)
    return FakeResponse(200, {"choices": [{"message": {"content": "terjemahan bagian"}}]})


reset()
set_groq_env()
requests.post = fake_post_ok
calls.clear()
try:
    result = docs.process_document_groq("Halo Dunia", "translate", "English")
    check(
        "a) teks pendek -> 1 panggilan Groq",
        len(calls) == 1 and result == "terjemahan bagian",
        f" | calls={len(calls)} result={result!r}",
    )
except Exception as exc:
    check("a) teks pendek -> 1 panggilan Groq", False, f" | error: {exc}")
finally:
    restore()


# b) teks 6000 karakter -> beberapa bagian, urutan hasil terjaga
calls = []


def fake_post_tag(url, headers, json, timeout):
    calls.append(json)
    user_text = json["messages"][1]["content"]
    return FakeResponse(200, {"choices": [{"message": {"content": f"hasil:{user_text[:3]}"}}]})


def fake_sleep(seconds):
    sleeps.append(seconds)


reset()
set_groq_env()
requests.post = fake_post_tag
time.sleep = fake_sleep
calls.clear()
try:
    teks6000 = "A" * 2000 + "B" * 2000 + "C" * 2000
    result = docs.process_document_groq(teks6000, "translate", "English")
    urutan_ok = result == "hasil:AAA\n\nhasil:BBB\n\nhasil:CCC"
    check(
        "b) teks 6000 karakter -> beberapa bagian, urutan terjaga",
        len(calls) == 3 and urutan_ok,
        f" | calls={len(calls)} result={result!r}",
    )
except Exception as exc:
    check("b) teks 6000 karakter -> beberapa bagian, urutan terjaga", False, f" | error: {exc}")
finally:
    restore()


# c) teks > 10000 karakter -> ValueError dan Groq tidak dipanggil
calls = []


def fake_post_should_not_be_called(url, headers, json, timeout):
    calls.append(json)
    return FakeResponse(200, {"choices": [{"message": {"content": "x"}}]})


reset()
set_groq_env()
requests.post = fake_post_should_not_be_called
calls.clear()
try:
    docs.process_document_groq("x" * 10001, "translate", "English")
    check("c) teks > 10000 karakter -> ValueError", False)
except ValueError as exc:
    check(
        "c) teks > 10000 karakter -> ValueError",
        str(exc) == "Dokumen terlalu panjang untuk model cadangan" and len(calls) == 0,
        f" | error: {exc} calls={len(calls)}",
    )
except Exception as exc:
    check("c) teks > 10000 karakter -> ValueError", False, f" | error: {type(exc).__name__}: {exc}")
finally:
    restore()


# d) teks kosong -> ValueError
calls = []
reset()
set_groq_env()
requests.post = fake_post_should_not_be_called
calls.clear()
try:
    docs.process_document_groq("", "translate", "English")
    check("d) teks kosong -> ValueError", False)
except ValueError as exc:
    check("d) teks kosong -> ValueError", "kosong" in str(exc).lower() and len(calls) == 0)
except Exception as exc:
    check("d) teks kosong -> ValueError", False, f" | error: {type(exc).__name__}: {exc}")
finally:
    restore()


# e) panggilan Groq gagal -> error dilempar
reset()
set_groq_env()
requests.post = lambda url, headers, json, timeout: (_ for _ in ()).throw(
    ConnectionError("jaringan putus")
)
try:
    docs.process_document_groq("Halo Dunia", "translate", "English")
    check("e) panggilan Groq gagal -> error dilempar", False)
except Exception as exc:
    check("e) panggilan Groq gagal -> error dilempar", "Gagal koneksi" in str(exc))
finally:
    restore()


# f) content kosong -> dianggap gagal
reset()
set_groq_env()
requests.post = lambda url, headers, json, timeout: FakeResponse(
    200, {"choices": [{"message": {"content": ""}}]}
)
try:
    docs.process_document_groq("Halo Dunia", "translate", "English")
    check("f) content kosong -> dianggap gagal", False)
except Exception as exc:
    check("f) content kosong -> dianggap gagal", "kosong" in str(exc).lower())
finally:
    restore()


# g) tag think dibuang dari konten respons
reset()
set_groq_env()
requests.post = lambda url, headers, json, timeout: FakeResponse(
    200, {"choices": [{"message": {"content": "```think\nSaya sedang berpikir\n```\nHasil akhir."}}]}
)
try:
    result = docs.process_document_groq("Halo Dunia", "translate", "English")
    check(
        "g) tag think dibuang dari konten respons",
        "think" not in result.lower() and result == "Hasil akhir.",
        f" | result={result!r}",
    )
except Exception as exc:
    check("g) tag think dibuang dari konten respons", False, f" | error: {exc}")
finally:
    restore()


# h) tugas Rangkuman -> ada panggilan penggabung di akhir
calls = []
reset()
set_groq_env()
requests.post = fake_post_tag
calls.clear()
try:
    teks6000 = "A" * 2000 + "B" * 2000 + "C" * 2000
    result = docs.process_document_groq(teks6000, "summarize", "English")
    terakhir = calls[-1]["messages"][1]["content"] if calls else ""
    check(
        "h) tugas Rangkuman -> ada panggilan penggabung di akhir",
        len(calls) == 4 and "hasil:AAA" in terakhir and "hasil:BBB" in terakhir,
        f" | calls={len(calls)} result={result!r}",
    )
except Exception as exc:
    check("h) tugas Rangkuman -> ada panggilan penggabung di akhir", False, f" | error: {exc}")
finally:
    restore()


# i) jeda antar panggilan dipanggil (mock sleep)
sleeps = []
reset()
set_groq_env()
requests.post = fake_post_tag
time.sleep = fake_sleep
calls.clear()
sleeps.clear()
try:
    teks6000 = "A" * 2000 + "B" * 2000 + "C" * 2000
    docs.process_document_groq(teks6000, "translate", "English")
    check(
        "i) jeda antar panggilan dipanggil",
        len(sleeps) == len(calls) - 1 and all(s == 3 for s in sleeps),
        f" | calls={len(calls)} sleeps={sleeps}",
    )
except Exception as exc:
    check("i) jeda antar panggilan dipanggil", False, f" | error: {exc}")
finally:
    restore()


# j) process_document asli tidak pernah memanggil Groq
post_called = [0]


def fake_post_watch(url, headers, json, timeout):
    post_called[0] += 1
    return FakeResponse(200, {"choices": [{"message": {"content": "groq"}}]})


def fake_generate_text(contents, system_instruction, timeout_ms=30000):
    return "hasil gemini"


reset()
set_groq_env()
docs.generate_text = fake_generate_text
requests.post = fake_post_watch
post_called[0] = 0
try:
    result = docs.process_document("dok.txt", b"isi teks contoh", "text/plain", "translate", "English")
    check(
        "j) process_document asli tidak pernah memanggil Groq",
        result == "hasil gemini" and post_called[0] == 0,
        f" | result={result!r} post_called={post_called[0]}",
    )
except Exception as exc:
    check("j) process_document asli tidak pernah memanggil Groq", False, f" | error: {exc}")
finally:
    restore()
    docs.generate_text = __import__("services.llm", fromlist=["generate_text"]).generate_text


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