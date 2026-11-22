"""
Line-level tests for the legal structure parser (src/legal_structure.py).

Every test here corresponds to a concrete bug that was found in the
legal parser / chunker while processing ``data/raw/patents_act_1970.pdf``
(the same bugs are checked end to end against the real PDF in
tests/integration/test_patents_act_chunking.py):

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

Run: pytest tests/test_legal_structure.py
"""

from legal_structure import classify_legal_line, strip_amendment_marker

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
