"""Container healthcheck: exit 0 only when /health reports status == "ok".

api.py swallows startup errors into _STATE["error"] and keeps serving, so
HTTP 200 alone does not mean the RAG pipeline is alive.
"""
import json
import sys
import urllib.request

try:
    body = json.load(urllib.request.urlopen("http://127.0.0.1:7860/health", timeout=8))
    sys.exit(0 if body.get("status") == "ok" else 1)
except Exception:
    sys.exit(1)
