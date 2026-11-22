"""
Structured logging, request IDs and per-stage timing.

Every log line is one JSON object stamped with the id of the request that
produced it, so one slow or failed request can be followed through query
expansion, retrieval, reranking and generation with a single grep:

    {"ts": "2026-11-22T10:04:11.532+00:00", "level": "INFO", "logger": "observability",
     "msg": "stage complete", "request_id": "9c1e...", "stage": "retrieval", "duration_ms": 812.4}

The request middleware (server/middleware.py) opens a request context; code
anywhere below it wraps expensive work in `with stage("name"):`. Each stage is
logged as it finishes and also summed into the request's closing access-log
line and its Server-Timing response header.

LOG_FORMAT=text switches to readable single-line output for local development.
"""

import json
import logging
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone

import config

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# A mutable dict rather than an immutable value: sync endpoints run in a
# worker thread with a *copy* of the request's context, and a copied context
# still points at the same dict, so stages timed there reach the middleware.
_stage_timings: ContextVar[dict[str, float] | None] = ContextVar("stage_timings", default=None)

# Attributes every LogRecord has; anything else on a record came from `extra=`.
_RECORD_ATTRS = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime", "request_id"}

logger = logging.getLogger(__name__)


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        for key, value in record.__dict__.items():
            if key not in _RECORD_ATTRS and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        extras = {k: v for k, v in record.__dict__.items() if k not in _RECORD_ATTRS and not k.startswith("_")}
        request_id = getattr(record, "request_id", None)
        line = f"{record.levelname:<7} {record.name}: {record.getMessage()}"
        if extras:
            line += " " + " ".join(f"{k}={v}" for k, v in extras.items())
        if request_id:
            line += f" [req {request_id[:8]}]"
        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line


_configured = False


def configure_logging(level: str | None = None, fmt: str | None = None) -> None:
    """Install the root handler once. Safe to call from every entry point."""

    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.addFilter(_RequestIdFilter())
    handler.setFormatter(TextFormatter() if (fmt or config.LOG_FORMAT) == "text" else JsonFormatter())

    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel((level or config.LOG_LEVEL).upper())

    # Model-loading libraries are chatty at INFO.
    for noisy in ("httpx", "urllib3", "sentence_transformers", "transformers", "filelock"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True


# ----------------------------------------------------------------------
# Request context and stage timing
# ----------------------------------------------------------------------


@contextmanager
def request_context(request_id: str) -> Iterator[dict[str, float]]:
    """Bind a request id and a fresh stage-timing dict for the duration of a request."""

    id_token = request_id_var.set(request_id)
    timings: dict[str, float] = {}
    timings_token = _stage_timings.set(timings)
    try:
        yield timings
    finally:
        _stage_timings.reset(timings_token)
        request_id_var.reset(id_token)


@contextmanager
def stage(name: str, **fields) -> Iterator[None]:
    """Time a pipeline stage; log it and add it to the current request's totals.

    A stage that runs more than once in a request (e.g. the LLM called once
    per specialist) accumulates into one total.
    """

    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        timings = _stage_timings.get()
        if timings is not None:
            timings[name] = round(timings.get(name, 0.0) + duration_ms, 1)
        logger.info("stage complete", extra={"stage": name, "duration_ms": duration_ms, **fields})
