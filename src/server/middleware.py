"""
Request middleware: assigns every request an id, times it, and writes one
structured access-log line with the per-stage breakdown.

The id is echoed as X-Request-Id and the stage totals as a standard
Server-Timing header, so browser devtools show where a slow answer spent
its time (retrieval vs. rerank vs. LLM) without opening the server logs.
"""

import logging
import re
import time
import uuid

from fastapi import Request

from observability import request_context

logger = logging.getLogger("access")

# A client may pass its own id to correlate with its logs, but it ends up in
# ours, so only accept something that cannot forge or break a log line.
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


async def request_logging_middleware(request: Request, call_next):
    incoming = request.headers.get("X-Request-Id", "")
    request_id = incoming if _VALID_REQUEST_ID.fullmatch(incoming) else uuid.uuid4().hex

    with request_context(request_id) as timings:
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            fields = {
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "duration_ms": duration_ms,
                "client": request.client.host if request.client else None,
            }
            if timings:
                fields["stages_ms"] = dict(timings)
            # /health is polled every 30s by the container healthcheck.
            level = logging.DEBUG if request.url.path == "/health" else logging.INFO
            logger.log(level, "request", extra=fields)

    response.headers["X-Request-Id"] = request_id
    server_timing = [f"{name};dur={ms}" for name, ms in timings.items()]
    server_timing.append(f"total;dur={duration_ms}")
    response.headers["Server-Timing"] = ", ".join(server_timing)
    return response
