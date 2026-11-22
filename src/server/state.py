"""
Process-wide state shared by the routers (the loaded RAG pipeline), plus the
request helpers more than one router needs.
"""

import logging
import uuid

from fastapi import Request

import db
from freshness import freshness_note, web_freshness_note

logger = logging.getLogger(__name__)

# Filled by api.lifespan once the models have loaded.
STATE: dict = {"rag": None, "error": None}


def get_rag():
    return STATE.get("rag")


def not_ready_message() -> str:
    return "The backend is not ready. " + (STATE.get("error") or "Models/services are still loading.")


def session_id(request: Request) -> str:
    """No-login session identity (src/db.py) — the frontend generates a
    UUID once, stores it in localStorage, and sends it as X-Session-Id.
    A caller without the header (e.g. a raw curl/test) still gets a
    fresh per-request id rather than a crash, it just won't accumulate
    audit-log history across requests."""

    return request.headers.get("X-Session-Id") or str(uuid.uuid4())


def audit_log_best_effort(request: Request, event_type: str, payload: dict) -> None:
    """A DB hiccup must never break the actual API response — this is
    best-effort observability, not a transactional requirement."""

    try:
        db.log_event(session_id(request), event_type, payload)
    except Exception:
        logger.warning("audit log write failed (non-fatal)", exc_info=True)


def resolve_freshness_note(item: dict) -> str | None:
    """
    fetched_at is only ever set on web-sourced chunks (src/web_loader.py,
    src/ingest_web.py) — use the days-since-fetch check for those,
    otherwise fall back to the title-year check used for PDFs.
    """

    fetched_at = item.get("fetched_at")
    if fetched_at:
        return web_freshness_note(fetched_at)
    return freshness_note(item.get("document_id"))


def citations_from_retrieved(retrieved: list) -> list:
    """Shape retrieved chunks into the {statute, section, title, page} form
    the frontend citation UI expects."""

    citations = []
    for item in retrieved:
        citations.append(
            {
                "statute": item.get("document") or "Source",
                "section": (
                    item.get("legal_reference")
                    or (f"p.{item.get('page')}" if item.get("page") else "")
                ),
                "title": item.get("snippet") or item.get("text", "")[:120],
                "page": item.get("page"),
                "chunk_id": item.get("chunk_id"),
                "reranker_score": item.get("reranker_score"),
                "freshness_note": resolve_freshness_note(item),
            }
        )
    return citations


def normalize_jurisdiction(value: str | None) -> str | None:
    """Map a UI/caller jurisdiction label onto the two filter values the
    retrievers understand ("India"/"International"), or None for no filter.

    Anything explicitly dual-scoped, unrecognized or absent returns None:
    an unknown label must widen the search rather than silently narrow it to
    the wrong regime.
    """

    if not value:
        return None

    text = value.strip().lower()
    if not text:
        return None

    if "both" in text or "dual" in text:
        return None
    # "India (National & International Multi-Step)" is a dual-scope question
    # despite leading with India, so check for a co-mention first.
    india = "india" in text
    international = any(
        term in text
        for term in ("international", "global", "wipo", "pct", "foreign", "export")
    )
    if india and international:
        return None
    if india:
        return "India"
    if international:
        return "International"
    return None
