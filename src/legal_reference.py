"""
Explicit legal-reference detection for queries.

Only used to give a targeted retrieval boost when the user names a
specific provision, e.g. "What is Section 3(p) of the Patents Act?"
or "Explain Rule 24B". For every other query this module is inert
and the semantic pipeline is left completely unchanged.
"""

import re


_SECTION_RE = re.compile(
    r"\bsection[s]?\s+(\d+[A-Za-z]?)\s*((?:\(\s*[0-9A-Za-z]+\s*\))*)",
    re.IGNORECASE,
)

_RULE_RE = re.compile(
    r"\brule[s]?\s+(\d+[A-Za-z]?)\s*((?:\(\s*[0-9A-Za-z]+\s*\))*)",
    re.IGNORECASE,
)

_PAREN_RE = re.compile(r"\(\s*([0-9A-Za-z]+)\s*\)")


def _canonical(kind: str, number: str, parens: str) -> dict:

    tokens = _PAREN_RE.findall(parens or "")

    if tokens:
        label = f"{kind} {number}" + "".join(f"({t})" for t in tokens)
    else:
        label = f"{kind} {number}"

    return {
        "kind": kind,          # "Section" or "Rule"
        "number": number,      # e.g. "3", "24B"
        "tokens": tokens,      # e.g. ["1", "j"] or ["p"]
        "label": label,        # e.g. "Section 3(p)"
    }


def extract_legal_references(query: str) -> list[dict]:
    """
    Return the explicit legal references named in the query.

    >>> [r["label"] for r in extract_legal_references(
    ...     "What is Section 3(p) of the Patents Act?")]
    ['Section 3(p)']
    >>> extract_legal_references("Can traditional knowledge be patented?")
    []
    """

    references = []

    for number, parens in _SECTION_RE.findall(query or ""):
        references.append(_canonical("Section", number, parens))

    for number, parens in _RULE_RE.findall(query or ""):
        references.append(_canonical("Rule", number, parens))

    # de-duplicate by label, keep order
    seen = set()
    unique = []
    for ref in references:
        if ref["label"] in seen:
            continue
        seen.add(ref["label"])
        unique.append(ref)

    return unique


def _chunk_reference_label(chunk: dict) -> str | None:

    label = chunk.get("legal_reference")
    if label:
        return label

    section = chunk.get("section")
    if section:
        clause = chunk.get("clause")
        if clause:
            return f"Section {section}({clause})"
        return f"Section {section}"

    rule = chunk.get("rule")
    if rule:
        return f"Rule {rule}"

    return None


def _normalise(label: str) -> str:
    return re.sub(r"\s+", "", (label or "")).lower()


def match_reference(ref: dict, chunk: dict) -> str | None:
    """
    Compare a detected query reference against a chunk.

    Returns:
        "exact"   - the chunk is exactly that provision
        "section" - the chunk belongs to the same section/rule
        None      - no relation
    """

    chunk_label = _chunk_reference_label(chunk)
    if not chunk_label:
        return None

    if _normalise(chunk_label) == _normalise(ref["label"]):
        return "exact"

    # same section/rule number, e.g. query "Section 3(p)" vs chunk
    # "Section 3" or "Section 3(d)"
    chunk_number = None
    m = re.match(
        r"(section|rule)\s+(\d+[A-Za-z]?)",
        chunk_label,
        re.IGNORECASE,
    )
    if m:
        chunk_number = m.group(2).lower()

    if (
        chunk_number is not None
        and chunk_number == ref["number"].lower()
        and chunk.get("document_type")
        in ("statute", "rules")
    ):
        return "section"

    return None
