"""
"Escalate to IP Facilitator" — emails the generated case brief.

Reads delivery config from the environment (same .env pattern as
GEMINI_API_KEY in llm.py):

    SMTP_HOST               e.g. smtp.gmail.com
    SMTP_PORT               default 587 (STARTTLS)
    SMTP_USER               account used to authenticate/send
    SMTP_PASSWORD           app password / API key
    SMTP_FROM               From: address (defaults to SMTP_USER)
    ESCALATION_EMAIL_TO     facilitator inbox the brief is sent to

Credentials are intentionally not required at import time — until they
are set, `send_case_brief` raises EscalationError with a message telling
the operator exactly which variable is missing, mirroring llm.py's
GEMINI_API_KEY error.
"""

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:  # noqa: BLE001 - some interpreters lack a caller frame
    pass


class EscalationError(RuntimeError):
    """Raised when the case brief cannot be emailed."""


_REQUIRED_VARS = ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "ESCALATION_EMAIL_TO")


def _missing_vars() -> list[str]:
    return [name for name in _REQUIRED_VARS if not os.getenv(name)]


def is_configured() -> bool:
    return not _missing_vars()


def send_case_brief(
    subject: str,
    body_markdown: str,
    reply_to: str | None = None,
) -> None:
    """
    Email `body_markdown` (already-formatted case brief text) to
    ESCALATION_EMAIL_TO. Raises EscalationError on missing config or any
    SMTP failure — callers should surface that as a clean error field,
    not a 500, the same way LLMError is handled elsewhere in api.py.
    """

    missing = _missing_vars()
    if missing:
        raise EscalationError(
            "Escalation email is not configured. Set "
            f"{', '.join(missing)} in .env to enable it."
        )

    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM") or user
    recipient = os.getenv("ESCALATION_EMAIL_TO")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(body_markdown)

    try:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        raise EscalationError(f"Failed to send escalation email: {exc}") from exc
