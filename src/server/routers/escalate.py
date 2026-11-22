"""Escalation: email the case brief to the IP facilitator inbox as a PDF."""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from case_brief_pdf import build_case_brief_pdf, case_brief_filename
from escalation import EscalationError, send_case_brief
from escalation import is_configured as escalation_is_configured
from server.security import escalate_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(tags=["escalate"])


class EscalateRequest(BaseModel):
    case_brief_markdown: str    # pre-built brief, e.g. lib/caseBrief.js's buildCaseBriefMarkdown()
    query: str | None = None
    reply_to: str | None = None  # user's email, set as Reply-To so the facilitator can respond directly


class EscalateResponse(BaseModel):
    sent: bool
    error: str | None = None


# Rate limited: each call sends a real email from our SMTP account.
@router.post("/api/escalate", response_model=EscalateResponse, dependencies=[Depends(escalate_rate_limit)])
def api_escalate(request: EscalateRequest) -> EscalateResponse:
    """Email the case brief to the configured IP facilitator inbox."""

    brief = (request.case_brief_markdown or "").strip()
    if not brief:
        return EscalateResponse(sent=False, error="empty_case_brief")

    subject_query = (request.query or "").strip()
    subject = f"IP-Sakti case escalation — {subject_query[:80]}" if subject_query else "IP-Sakti case escalation"

    # The facilitator gets the brief as a formatted PDF report; the message
    # body is a short covering note. If rendering fails for any reason the
    # escalation still goes out, with the markdown brief as the body.
    attachment = None
    try:
        attachment = (case_brief_filename(), build_case_brief_pdf(brief))
    except Exception:  # never block an escalation on layout
        logger.warning("case brief PDF rendering failed, sending markdown body", exc_info=True)

    if attachment:
        body_text = (
            "A case brief has been escalated from IP-Sakti for human review.\n\n"
            f"Question: {subject_query or 'n/a'}\n"
            f"Reply-To: {request.reply_to or 'not provided'}\n\n"
            f"The full brief is attached as {attachment[0]}.\n\n"
            "This brief is informational only and is not legal advice."
        )
    else:
        body_text = brief

    try:
        send_case_brief(
            subject=subject,
            body_markdown=brief,
            reply_to=request.reply_to,
            attachment=attachment,
            body_text=body_text,
        )
    except EscalationError as exc:
        return EscalateResponse(sent=False, error=str(exc))

    return EscalateResponse(sent=True)


@router.get("/api/escalate/status")
def api_escalate_status() -> dict:
    return {"configured": escalation_is_configured()}
