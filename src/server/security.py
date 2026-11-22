"""
Admin authentication, upload validation and per-client rate limiting.

Admin routes fail closed: with ADMIN_API_KEY unset they answer 503 rather
than becoming open. Keys are compared in constant time.

The rate limiter is an in-memory sliding window keyed by client IP. That is
correct for the single-worker deployment (Dockerfile runs one uvicorn
worker); with several workers each would keep its own window, so move the
counters to Redis before scaling out. Behind Caddy the client IP comes from
X-Forwarded-For via uvicorn's --proxy-headers.
"""

import hmac
import math
import re
import threading
import time
from collections import deque
from pathlib import PurePath

from fastapi import Header, HTTPException, Request

import config

# ----------------------------------------------------------------------
# Admin authentication
# ----------------------------------------------------------------------


def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    expected = config.ADMIN_API_KEY
    if not expected:
        raise HTTPException(status_code=503, detail="admin_disabled: set ADMIN_API_KEY to enable admin endpoints")
    if not x_admin_key or not hmac.compare_digest(x_admin_key.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="invalid_admin_key")


# ----------------------------------------------------------------------
# Upload validation
# ----------------------------------------------------------------------

_SAFE_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._,()'&-]{0,150}\.pdf$", re.IGNORECASE)
PDF_MAGIC = b"%PDF-"


def safe_upload_filename(raw_name: str | None) -> str | None:
    """Reduce a client-supplied filename to a bare, safe PDF name, or None.

    The client controls this string completely. Keeping only the final path
    component (under both / and \\ separators) defeats "../../src/x.pdf"
    traversal, and the allow-list rejects control characters, leading dots
    and anything that is not a .pdf.
    """

    if not raw_name:
        return None
    name = PurePath(raw_name.replace("\\", "/")).name
    if not _SAFE_FILENAME.fullmatch(name):
        return None
    return name


# ----------------------------------------------------------------------
# Rate limiting
# ----------------------------------------------------------------------


class RateLimiter:
    """FastAPI dependency allowing `limit` requests per `window_s` seconds per client IP."""

    _PRUNE_AT = 10_000   # distinct clients tracked before idle ones are dropped

    def __init__(self, name: str, limit: int, window_s: float):
        self.name = name
        self.limit = limit
        self.window_s = window_s
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def __call__(self, request: Request) -> None:
        if self.limit <= 0:
            return
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        cutoff = now - self.window_s

        with self._lock:
            hits = self._hits.setdefault(client, deque())
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.limit:
                retry_after = max(1, math.ceil(hits[0] + self.window_s - now))
                raise HTTPException(
                    status_code=429,
                    detail=f"rate_limited: {self.name} allows {self.limit} requests per {int(self.window_s)}s",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)
            if len(self._hits) > self._PRUNE_AT:
                self._prune(cutoff)

    def _prune(self, cutoff: float) -> None:
        for key in [k for k, v in self._hits.items() if not v or v[-1] <= cutoff]:
            del self._hits[key]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


llm_rate_limit = RateLimiter("llm", config.RATE_LIMIT_LLM_PER_MIN, 60)
escalate_rate_limit = RateLimiter("escalate", config.RATE_LIMIT_ESCALATE_PER_HOUR, 3600)
admin_rate_limit = RateLimiter("admin", config.RATE_LIMIT_ADMIN_PER_MIN, 60)

ALL_LIMITERS = (llm_rate_limit, escalate_rate_limit, admin_rate_limit)
