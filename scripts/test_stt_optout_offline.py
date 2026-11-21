"""Tes offline opt-out Deepgram Model Improvement Program (STT).

Tidak memanggil API live. Memalsukan requests.post dan memeriksa parameter
yang dikirim.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

import services.stt as stt

results = []


def check(nama, kondisi, detail=""):
    status = "PASS" if kondisi else "FAIL"
    results.append((nama, status))
    print(f"{status}: {nama}{detail}")


class FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text

    def json(self):
        return {
            "results": {
                "channels": [
                    {"alternatives": [{"transcript": "hi"}]}
                ]
            }
        }

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


captured = {}


def fake_post(url, params, headers, data, timeout):
    captured["url"] = url
    captured["params"] = dict(params)
    captured["headers"] = dict(headers)
    captured["data"] = data
    captured["timeout"] = timeout
    return FakeResponse()


orig_post = requests.post

# Hindari RuntimeError saat DEEPGRAM_API_KEY kosong di lingkungan tes.
stt.DEEPGRAM_API_KEY = "test-key"


def reset_env():
    os.environ.pop("DEEPGRAM_MIP_OPT_OUT", None)


# (a) Default: mip_opt_out=true dikirim, bahasa dan model tidak berubah.
reset_env()
captured.clear()
requests.post = fake_post
try:
    stt.speech_to_text(b"audio", lang="en")
    p = captured["params"]
    check(
        "a) default mip_opt_out=true terkirim",
        p.get("mip_opt_out") == "true",
        f" | params={p}",
    )
    check(
        "a) model tetap nova-2",
        p.get("model") == "nova-2",
        f" | params={p}",
    )
    check(
        "a) language tetap en",
        p.get("language") == "en",
        f" | params={p}",
    )
    check(
        "a) smart_format tetap true",
        p.get("smart_format") == "true",
        f" | params={p}",
    )
finally:
    requests.post = orig_post


# (b) DEEPGRAM_MIP_OPT_OUT=false -> mip_opt_out tidak terkirim.
os.environ["DEEPGRAM_MIP_OPT_OUT"] = "false"
captured.clear()
requests.post = fake_post
try:
    stt.speech_to_text(b"audio", lang="id")
    p = captured["params"]
    check(
        "b) env=false -> mip_opt_out tidak ada",
        "mip_opt_out" not in p,
        f" | params={p}",
    )
    check(
        "b) language tetap id saat env=false",
        p.get("language") == "id",
        f" | params={p}",
    )
    check(
        "b) model tetap nova-2 saat env=false",
        p.get("model") == "nova-2",
        f" | params={p}",
    )
finally:
    requests.post = orig_post
    os.environ.pop("DEEPGRAM_MIP_OPT_OUT", None)


# Ringkasan
print("\n=== Ringkasan Tes Opt-Out Deepgram Offline ===")
passed = sum(1 for _, s in results if s == "PASS")
failed = sum(1 for _, s in results if s == "FAIL")
for name, status in results:
    print(f"  {status}: {name}")
print(f"\nLulus: {passed}/{len(results)}")
if failed:
    print(f"Gagal: {failed}")
    sys.exit(1)
