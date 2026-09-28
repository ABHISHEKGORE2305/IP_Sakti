"""
Citation Verifier Agent — zero-hallucination guardrail.

Scans a generated answer for inline citations of the form
    [Document, Section/Rule, Page]
(as required by src/prompt.py's SYSTEM_PROMPT) and verifies each one
against the chunks actually retrieved for the query. Citations that do
not match any retrieved source are flagged as unverified/hallucinated,
and can be stripped from the answer text before it reaches the user.
"""

import re


_CITATION_RE = re.compile(r"\[([^\[\]]+?)\]")
_REFERENCE_MARKER_RE = re.compile(r"^(section|rule)\b", re.IGNORECASE)
_PAGE_RE = re.compile(r"(\d+)")


def _parse_citation(raw: str) -> dict | None:
    """
    Parse a bracketed citation body into (document, reference, page).

    Expected shape: "Document, Section/Rule, p.NN" (page optional).
    Document titles in this corpus routinely contain their own comma
    (e.g. "The Patents Act, 1970"), so the split can't just take
    parts[0] as the document — instead we locate the "Section"/"Rule"
    segment as the boundary and treat everything before it as the
    (possibly comma-containing) document name.
    """

    parts = [p.strip() for p in raw.split(",")]

    if len(parts) < 2:
        return None

    ref_index = next(
        (i for i, part in enumerate(parts) if _REFERENCE_MARKER_RE.match(part)),
        None,
    )

    if ref_index is None or ref_index == 0:
        return None

    document = ", ".join(parts[:ref_index])
    reference = parts[ref_index]

    page = None
    if len(parts) > ref_index + 1:
        match = _PAGE_RE.search(parts[ref_index + 1])
        if match:
            page = int(match.group(1))

    return {"document": document, "reference": reference, "page": page}


def extract_citations(answer_text: str) -> list[dict]:
    """Extract every [Document, Section/Rule, Page]-shaped citation from the answer."""

    citations = []

    for raw in _CITATION_RE.findall(answer_text or ""):
        parsed = _parse_citation(raw)
        if parsed:
            citations.append(parsed)

    return citations


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _source_reference(source: dict) -> str:
    return (
        source.get("legal_reference")
        or (f"section {source['section']}" if source.get("section") else "")
        or (f"rule {source['rule']}" if source.get("rule") else "")
        or ""
    )


def _matches_source(citation: dict, source: dict) -> bool:

    doc = _normalise(source.get("document") or "")
    ref = _normalise(_source_reference(source))

    cited_doc = _normalise(citation["document"])
    cited_ref = _normalise(citation["reference"])

    if not doc or not (cited_doc in doc or doc in cited_doc):
        return False

    if ref and cited_ref and not (cited_ref in ref or ref in cited_ref):
        return False

    if citation.get("page") is not None and source.get("page") is not None:
        if citation["page"] != source["page"]:
            return False

    return True


def verify_citations(answer_text: str, retrieved_sources: list[dict]) -> dict:
    """
    Verify every citation in `answer_text` against `retrieved_sources`
    (the chunks actually returned by the retriever for this query).

    Returns a report with per-citation verdicts and the citation
    precision (verified / total), consumed by guardrails.confidence.
    """

    citations = extract_citations(answer_text)

    verdicts = [
        {**citation, "verified": any(
            _matches_source(citation, source) for source in retrieved_sources
        )}
        for citation in citations
    ]

    total = len(verdicts)
    verified = sum(1 for v in verdicts if v["verified"])

    # No citations at all is itself a grounding failure for a system
    # whose prompt mandates inline citations for every legal claim, not
    # a vacuous pass — treat it as zero precision so it can't hide
    # behind an unearned "high confidence" score.
    precision = (verified / total) if total else 0.0

    return {
        "citations": verdicts,
        "total_citations": total,
        "verified_citations": verified,
        "citation_precision": precision,
        "has_unverified_citations": verified < total,
    }


def strip_unverified_citations(answer_text: str, report: dict) -> str:
    """
    Remove the bracketed span for every citation verdicted as
    unverified, leaving the surrounding prose intact.
    """

    cleaned = answer_text or ""

    for verdict in report["citations"]:

        if verdict["verified"]:
            continue

        page_part = f", p.{verdict['page']}" if verdict.get("page") is not None else ""
        original = f"[{verdict['document']}, {verdict['reference']}{page_part}]"

        cleaned = cleaned.replace(original, "[unverified citation removed]")

    return cleaned
