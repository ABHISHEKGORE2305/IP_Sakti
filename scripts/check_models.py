"""
Verify the LLM models listed in src/llm.py are actually served for YOUR keys.

    python scripts/check_models.py

Lists the provider catalogs, then sends a 1-token request to every model in
GROQ_FALLBACK_MODELS / GEMINI_FALLBACK_MODELS. Read-only apart from those tiny
completions. Exit code 1 if any model in a list is unusable.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import llm  # noqa: E402

bad = 0

key = os.getenv("GROQ_API_KEY")
if key:
    from groq import Groq

    client = Groq(api_key=key)
    served = {m.id for m in client.models.list().data}
    for model in dict.fromkeys([llm.GROQ_DEFAULT_MODEL, *llm.GROQ_FALLBACK_MODELS]):
        if model not in served:
            print(f"[groq]   FAIL {model}: not in catalog")
            bad += 1
            continue
        try:
            client.chat.completions.create(
                model=model, max_tokens=16,
                messages=[{"role": "user", "content": "Reply with: ok"}],
            )
            print(f"[groq]   ok   {model}")
        except Exception as exc:  # noqa: BLE001
            print(f"[groq]   FAIL {model}: {str(exc)[:120]}")
            bad += 1
else:
    print("[groq]   GROQ_API_KEY not set - skipped")

key = os.getenv("GEMINI_API_KEY")
if key:
    from google import genai

    client = genai.Client(api_key=key)
    served = {m.name.split("/")[-1] for m in client.models.list()}
    for model in dict.fromkeys([llm.GEMINI_DEFAULT_MODEL, *llm.GEMINI_FALLBACK_MODELS]):
        try:
            client.models.generate_content(model=model, contents="Reply with: ok")
            print(f"[gemini] ok   {model}")
        except Exception as exc:  # noqa: BLE001
            note = "" if model in served else " (not in catalog)"
            print(f"[gemini] FAIL {model}{note}: {str(exc)[:120]}")
            bad += 1
else:
    print("[gemini] GEMINI_API_KEY not set - skipped")

sys.exit(1 if bad else 0)
