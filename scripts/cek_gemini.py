import os, time
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types

c = genai.Client(api_key=os.getenv("GEMINI_API_KEY"),
                 http_options=types.HttpOptions(timeout=60000))
m = os.getenv("GEMINI_MODEL")

def coba(nama, tc):
    t = time.time()
    try:
        r = c.models.generate_content(model=m, contents="Say hi in one short sentence.",
            config=types.GenerateContentConfig(thinking_config=tc))
        u = r.usage_metadata
        print(nama, "OK", round(time.time() - t, 2), "detik | token pikir:",
              getattr(u, "thoughts_token_count", None))
    except Exception as e:
        print(nama, "ERROR", round(time.time() - t, 2), "detik:", type(e).__name__, str(e)[:150])

coba("budget=0", types.ThinkingConfig(thinking_budget=0))
for level in ("minimal", "low"):
    try:
        coba("level=" + level, types.ThinkingConfig(thinking_level=level))
    except Exception as e:
        print("level=" + level, "tidak didukung SDK:", type(e).__name__, str(e)[:120])
