"""
Consent, audit log, privacy (winning_features.md items 15/16/17) — all
session-scoped via src/db.py, never global. This is a demo-grade,
no-login store (see db.py's module docstring), not a production
multi-tenant privacy system.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

import db
from server.state import session_id

router = APIRouter(tags=["privacy"])


class ConsentRequest(BaseModel):
    consent_type: str    # e.g. "paid_source_premium_patent_db"
    granted: bool


@router.post("/api/consent")
def api_set_consent(request: ConsentRequest, http_request: Request) -> dict:
    sid = session_id(http_request)
    db.set_consent(sid, request.consent_type, request.granted)
    return {"session_id": sid, "consent": db.get_consent(sid)}


@router.get("/api/consent")
def api_get_consent(http_request: Request) -> dict:
    sid = session_id(http_request)
    return {"session_id": sid, "consent": db.get_consent(sid)}


@router.get("/api/audit-log")
def api_audit_log(http_request: Request, limit: int = 200) -> dict:
    sid = session_id(http_request)
    return {"session_id": sid, "entries": db.get_audit_log(sid, limit=limit)}


@router.get("/api/privacy/summary")
def api_privacy_summary(http_request: Request) -> dict:
    sid = session_id(http_request)
    return {"session_id": sid, **db.privacy_summary(sid)}


@router.post("/api/privacy/delete")
def api_privacy_delete(http_request: Request) -> dict:
    """DPDP "delete my data" — wipes every row for this session_id.
    Session-scoped by construction (db.delete_session_data takes only a
    session_id, never a global wipe), so one user can never delete
    another's data even accidentally."""

    sid = session_id(http_request)
    return {"session_id": sid, **db.delete_session_data(sid)}
