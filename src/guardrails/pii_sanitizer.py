"""
DPDP Act, 2023-aligned PII Sanitizer.

Data minimization: strips personally identifiable information from a
user's query BEFORE it is embedded (vectorized) or sent to the LLM, so
no Aadhaar number, PAN, phone number, email, or street address ever
reaches the vector store, the retrieval logs, or a third-party LLM
provider. Applied by agents.graph.input_sanitizer, the first node in
the pipeline.

Regex-based, not a full NER model — it catches the structured PII
formats the implementation plan names explicitly (Aadhaar, PAN, phone,
address) plus email as a standard addition. It will not catch PII in
free-form prose that doesn't match these shapes (e.g. a name on its
own); that is a known limitation, not a gap to be silently assumed away.
"""

import re


REDACTION_TAG = {
    "aadhaar": "[REDACTED-AADHAAR]",
    "pan": "[REDACTED-PAN]",
    "phone": "[REDACTED-PHONE]",
    "email": "[REDACTED-EMAIL]",
    "pin_code": "[REDACTED-PIN-CODE]",
}

# Order matters: PAN (10 alphanumeric) must be checked before looser
# patterns; Aadhaar (12 digits, optionally grouped) before phone
# numbers so a 12-digit Aadhaar isn't partially eaten by the 10-digit
# phone pattern first.
#
# Known limitation: a bare 12-digit number (e.g. a patent application
# number) is indistinguishable from an Aadhaar number by shape alone,
# and will be redacted as "aadhaar" too. For a DPDP data-minimization
# filter that is the safer failure direction - over-redacting a
# non-sensitive number costs a little precision; under-redacting a
# real Aadhaar number is the actual compliance risk - but it is a
# real, known false-positive, not a solved problem.
_PATTERNS = [
    ("pan", re.compile(r"\b[A-Za-z]{5}[0-9]{4}[A-Za-z]\b")),
    ("aadhaar", re.compile(r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(r"(?<!\d)\+?(?:91[\s-]?)?[6-9]\d{9}(?!\d)")),
    # A bare 6-digit Indian PIN code is the one structured, reliably
    # detectable fragment of a street address; free-text addresses
    # otherwise need real NER, which is out of scope here.
    ("pin_code", re.compile(r"(?<!\d)\d{6}(?!\d)")),
]


def sanitize_pii(text: str) -> dict:
    """
    Redact PII from `text`.

    Returns:
        {
          "sanitized_text": str,      # safe to embed / send to the LLM
          "redactions": [{"type": "aadhaar", "original": "..."}],
          "had_pii": bool,
        }

    `redactions` carries the original matched value so a caller can log
    *that PII was found and its type* for DPDP audit purposes, without
    ever needing to log or persist the original query text itself.
    """

    sanitized = text or ""
    redactions = []

    for pii_type, pattern in _PATTERNS:

        def _redact(match, _type=pii_type):
            redactions.append({"type": _type, "original": match.group(0)})
            return REDACTION_TAG[_type]

        sanitized = pattern.sub(_redact, sanitized)

    return {
        "sanitized_text": sanitized,
        "redactions": redactions,
        "had_pii": bool(redactions),
    }
