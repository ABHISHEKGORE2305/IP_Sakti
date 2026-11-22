"""
Tests for explicit-reference detection and instrument scoping
(src/legal_reference.py). Pure text, no models.

Run: pytest tests/test_legal_reference.py
"""


from legal_reference import extract_legal_references, instrument_families, match_reference


def _chunk(document, reference, document_type="statute"):
    return {"document": document, "legal_reference": reference, "document_type": document_type}


def test_year_in_a_rules_title_is_not_a_rule_number():
    assert extract_legal_references("What changed in the Patents (Amendment) Rules 2024?") == []
    assert [r["label"] for r in extract_legal_references("Explain Rule 24B")] == ["Rule 24B"]


def test_instrument_families_from_common_phrasings():
    assert instrument_families("Section 84 of the Patents Act") == ["patents"]
    assert instrument_families("NBA approval under Section 4 of BDA") == ["biodiversity"]
    assert instrument_families("Rule 170 of the Drugs Rules") == ["drugs_cosmetics"]
    assert instrument_families("Rule 161 of D&C Act") == ["drugs_cosmetics"]
    assert instrument_families("a Section 11 trademark objection") == ["trade_marks"]
    assert instrument_families("How does Section 3(e) apply?") == []


def test_named_instrument_scopes_the_exact_match():
    """Case 127: 'Section 8' must not match Section 8 of the BD or D&C Acts
    when the question is about the Patents Rules."""

    ref = extract_legal_references(
        "How do the Patents (Amendment) Rules, 2024 affect obligations under Section 8 (Form 3)?"
    )[0]
    assert match_reference(ref, _chunk("The Patents Act, 1970", "Section 8")) == "exact"
    assert match_reference(ref, _chunk("The Drugs and Cosmetics Act, 1940", "Section 8")) is None
    assert match_reference(ref, _chunk("The Biological Diversity (Amendment) Act, 2023", "Section 8")) is None


def test_ayush_examination_guidelines_count_as_patent_documents():
    ref = extract_legal_references("Patent Office objection under Section 3(p)")[0]
    chunk = _chunk("Guidelines for Examination of Ayush Related Inventions", "Section 3(p)",
                   "ayush_examination_guidelines")
    assert match_reference(ref, chunk) == "exact"


def test_no_named_instrument_matches_every_instrument():
    ref = extract_legal_references("How does Section 3(e) apply to a polyherbal formulation?")[0]
    assert match_reference(ref, _chunk("The Patents Act, 1970", "Section 3(e)")) == "exact"
    assert match_reference(ref, _chunk("The Drugs and Cosmetics Act, 1940", "Section 3(e)")) == "exact"


# ------------------------------------------------------------------
