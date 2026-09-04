"""
Automated tests for legal-aware chunking.

Every test here corresponds to a concrete bug that was found in the
legal parser / chunker while processing ``data/raw/patents_act_1970.pdf``:

    Bug #1  Table of Contents (pages 1-6) was parsed as if it were the
            statute, so the TOC line "3. What are not inventions." became
            Section 3.
    Bug #2  The TOC entry "THE SCHEDULE." switched the chunker into
            schedule mode before legal parsing had even started, which
            permanently disabled section detection for the whole Act.
    Bug #3  Per-page amendment footnotes ("3. Subs by s. 31, ibid. ...",
            "3. The word ... omitted by Act 33 of 2021 ...") were mistaken
            for real Section 3 headings and reset the current section.
    Bug #4  Upper-case nested items such as "(A)" were treated as the
            lower-case clause "(a)".
    Bug #5  Amended provisions carry an inline superscript-footnote marker
            "N[" ("6[(d) ...", "3[25. Opposition ..."). Without stripping
            it, Section 3(b)/(d)/(j) and the Section 25 heading were missed.

Run directly:      python src/tests/test_legal_chunking.py
Run with pytest:   pytest src/tests/test_legal_chunking.py
"""

import os
import sys

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

REPO_ROOT = os.path.dirname(SRC_DIR)
PDF_PATH = os.path.join(REPO_ROOT, "data", "raw", "patents_act_1970.pdf")

from legal_structure import (  # noqa: E402
    classify_legal_line,
    strip_amendment_marker,
)
from document_loader import load_pdf  # noqa: E402
from chunker import create_chunks  # noqa: E402


# ------------------------------------------------------------------
# Shared fixture: chunk the real Patents Act PDF exactly once.
# ------------------------------------------------------------------

_CHUNK_CACHE = {}


def patents_act_chunks():

    if "chunks" not in _CHUNK_CACHE:

        pages = load_pdf(
            PDF_PATH,
            metadata={
                "document": "The Patents Act, 1970",
                "document_type": "statute",
                "jurisdiction": "India",
                "language": "en",
            },
        )

        _CHUNK_CACHE["chunks"] = create_chunks(pages)

    return _CHUNK_CACHE["chunks"]


def section_chunks(section):
    return [
        c
        for c in patents_act_chunks()
        if c.get("section") == section
    ]


def reference_chunks(legal_reference):
    return [
        c
        for c in patents_act_chunks()
        if c.get("legal_reference") == legal_reference
    ]


# ==================================================================
# Pure parser tests (no PDF) - fast, target legal_structure.py
# ==================================================================


def test_real_section_3_heading_is_a_section():
    result = classify_legal_line(
        "3. What are not inventions.—The following are not "
        "inventions within the meaning of this Act,—"
    )
    assert result == {"type": "section", "section": "3"}, result


def test_section_transition_headings():
    # Bug context G/H/I - Section 4, 6, 7 must be recognised.
    assert classify_legal_line(
        "4. Inventions relating to atomic energy not patentable.—"
        "No patent shall be granted ..."
    ) == {"type": "section", "section": "4"}

    assert classify_legal_line(
        "6. Persons entitled to apply for patents.—(1) Subject ..."
    ) == {"type": "section", "section": "6"}

    assert classify_legal_line(
        "7. Form of application.—(1) Every application for a patent ..."
    ) == {"type": "section", "section": "7"}


def test_amendment_footnotes_are_not_sections():
    # Bug #3 - every one of these starts with "3." but is a footnote.
    footnotes = [
        "3. Sub-clause (B) omitted by Act 33 of 2021, s. 13 "
        "(w.e.f. 4-4-2021).",
        "3. Subs by s. 31, ibid., for section 39 (w.e.f. 1-1-2005).",
        "3. Subs. by Act 38 of 2002, s. 10, for “specification "
        "relating thereto” (w.e.f. 20-5-2003).",
        "3. Ins. by Act 15 of 2005, s. 2 (w.e.f. 1-1-2005).",
        "3. The word “Appellate Board” omitted by Act 33 of "
        "2021, s. 13 (w.e.f. 4-4-2021).",
        "3. The words “or plants” omitted by s. 4, ibid. "
        "(w.e.f. 20-5-2003).",
        "3. Sub-section (2) omitted by s. 30, ibid. (w.e.f. 20-5-2003).",
        "3. The brackets and words “(including payments by way of "
        "minimum royalty)” omitted by s. 42, ibid.",
    ]

    for line in footnotes:
        assert classify_legal_line(line)["type"] != "section", line


def test_clause_p_is_detected():
    # Bug context C - the traditional-knowledge clause.
    result = classify_legal_line(
        "(p) an invention which, in effect, is traditional knowledge "
        "or which is an aggregation or duplication of known properties "
        "of traditionally known component or components."
    )
    assert result == {"type": "clause", "clause": "p"}, result


def test_uppercase_nested_item_is_not_a_clause():
    # Bug #4 - "(A)" must NOT become clause "a".
    result = classify_legal_line(
        "(A) in relation to proceedings before a High Court, prescribed "
        "by rules made by the High Court;"
    )
    assert result["type"] != "clause", result


def test_amendment_bracket_marker_is_stripped():
    # Bug #5 - "N[" prefix on amended provisions.
    assert strip_amendment_marker("6[(d) the mere discovery of a new "
                                  "form") == "(d) the mere discovery of a new form"
    assert strip_amendment_marker("3[25. Opposition to the patent.—"
                                  "(1)") == "25. Opposition to the patent.—(1)"
    # A normal line is untouched.
    assert strip_amendment_marker("(p) an invention ...") == \
        "(p) an invention ..."


def test_amended_clause_behind_bracket_marker_is_detected():
    # Bug #5 - Section 3(d) is written as "6[(d) ...".
    assert classify_legal_line(
        "6[(d) the mere discovery of a new form of a known substance "
        "which does not result in the enhancement of the known "
        "efficacy of that substance ...]"
    ) == {"type": "clause", "clause": "d"}

    # Section 3(j) is written as "2[(j) ...".
    assert classify_legal_line(
        "2[(j) plants and animals in whole or any part thereof other "
        "than micro-organisms ...]"
    ) == {"type": "clause", "clause": "j"}


def test_amended_section_heading_behind_bracket_marker_is_detected():
    # Bug #5 - Section 25 heading is written as "3[25. Opposition ...".
    assert classify_legal_line(
        "3[25. Opposition to the patent.—(1) Where an application "
        "for a patent has been published but a patent has not been "
        "granted ..."
    ) == {"type": "section", "section": "25"}


# ==================================================================
# Integration tests against the real Patents Act PDF
# ==================================================================


def test_toc_section_3_is_ignored():
    # Bug #1 - pages 1-6 are the Table of Contents.
    toc_section_3 = [
        c for c in section_chunks("3") if c["page"] <= 6
    ]
    assert toc_section_3 == [], toc_section_3


def test_actual_section_3_is_detected_on_page_9():
    on_page_9 = [c for c in section_chunks("3") if c["page"] == 9]
    assert on_page_9, "no Section 3 chunk found on page 9"

    heading = on_page_9[0]
    assert "what are not inventions" in heading["text"].lower()
    assert heading["legal_reference"] == "Section 3"


def test_section_3p_chunk_exists_with_tk_provision():
    # The headline success condition from prompt.md.
    matches = reference_chunks("Section 3(p)")
    assert len(matches) >= 1, "no Section 3(p) chunk"

    chunk = matches[0]
    assert chunk["section"] == "3"
    assert chunk["clause"] == "p"

    text = chunk["text"].lower()
    assert "traditional knowledge" in text
    assert "known properties" in text


def test_section_3_survives_page_9_to_10_boundary():
    # Bug context F - state must not reset at the page boundary.
    pages = {c["page"] for c in section_chunks("3")}
    assert 9 in pages and 10 in pages, sorted(pages)


def test_no_bogus_section_3_elsewhere_in_the_act():
    # Bug #3 - amendment footnotes must not resurrect Section 3.
    stray = sorted(
        {c["page"] for c in section_chunks("3") if c["page"] not in (9, 10)}
    )
    assert stray == [], f"unexpected Section 3 chunks on pages {stray}"


def test_section_4_6_7_start_after_the_statute_begins():
    # Bug context G/H/I on the real document.
    for number in ("4", "6", "7"):
        chunks = section_chunks(number)
        assert chunks, f"Section {number} not detected"
        assert min(c["page"] for c in chunks) >= 7


def test_important_section_3_clauses_are_present():
    for clause in ("b", "d", "e", "i", "j", "p"):
        ref = f"Section 3({clause})"
        assert reference_chunks(ref), f"missing {ref}"


def test_schedule_mode_suppresses_sections_in_the_real_schedule():
    # Bug #2 - the REAL "THE SCHEDULE" (page 67) must still switch the
    # chunker into schedule mode, so no section headings are emitted
    # from the schedule pages.
    tagged_pages = [
        c["page"] for c in patents_act_chunks() if c.get("section")
    ]
    assert tagged_pages, "no section-tagged chunks at all"
    assert max(tagged_pages) < 67, max(tagged_pages)


# ==================================================================
# Minimal runner so the file works without pytest installed.
# ==================================================================


def _run_standalone():

    tests = [
        (name, obj)
        for name, obj in sorted(globals().items())
        if name.startswith("test_") and callable(obj)
    ]

    passed = 0
    failed = 0

    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {name}\n      {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {name}\n      {type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"ok    {name}")

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_standalone())
