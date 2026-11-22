"""
End-to-end chunking checks against the real Patents Act PDF.

Each test pins one of the parser/chunker bugs described in
tests/test_legal_structure.py, this time on the actual document as
ingest.py chunks it. Needs data/raw/patents_act_1970.pdf (not in git), so
the module is marked integration and skips when the PDF is absent.

Run: pytest -m integration tests/integration/test_patents_act_chunking.py
"""

import os

import pytest

from chunker import create_chunks
from document_config import DOCUMENTS
from document_loader import load_pdf

pytestmark = pytest.mark.integration

PDF_PATH = os.path.join("data", "raw", "patents_act_1970.pdf")


@pytest.fixture(scope="module")
def patents_act_chunks():
    if not os.path.exists(PDF_PATH):
        pytest.skip(f"{PDF_PATH} not present (corpus PDFs are not in git)")

    # Use the production document_config entry rather than hand-written
    # metadata: it carries toc_skip_pages=6, without which the table of
    # contents ("3. What are not inventions.") is parsed as Section 3.
    entry = next(d for d in DOCUMENTS if d["filename"] == "patents_act_1970.pdf")
    return create_chunks(load_pdf(PDF_PATH, metadata=dict(entry)), chunk_size=1000, chunk_overlap=200)


def section_chunks(chunks, section):
    return [c for c in chunks if c.get("section") == section]


def reference_chunks(chunks, legal_reference):
    return [c for c in chunks if c.get("legal_reference") == legal_reference]


def test_toc_section_3_is_ignored(patents_act_chunks):
    # Bug #1 - pages 1-6 are the Table of Contents.
    toc_section_3 = [
        c for c in section_chunks(patents_act_chunks, "3") if c["page"] <= 6
    ]
    assert toc_section_3 == [], toc_section_3


def test_actual_section_3_is_detected_on_page_9(patents_act_chunks):
    on_page_9 = [c for c in section_chunks(patents_act_chunks, "3") if c["page"] == 9]
    assert on_page_9, "no Section 3 chunk found on page 9"

    heading = on_page_9[0]
    assert "what are not inventions" in heading["text"].lower()
    assert heading["legal_reference"] == "Section 3"


def test_section_3p_chunk_exists_with_tk_provision(patents_act_chunks):
    # The headline success condition from prompt.md.
    matches = reference_chunks(patents_act_chunks, "Section 3(p)")
    assert len(matches) >= 1, "no Section 3(p) chunk"

    chunk = matches[0]
    assert chunk["section"] == "3"
    assert chunk["clause"] == "p"

    text = chunk["text"].lower()
    assert "traditional knowledge" in text
    assert "known properties" in text


def test_section_3_survives_page_9_to_10_boundary(patents_act_chunks):
    # Bug context F - state must not reset at the page boundary.
    pages = {c["page"] for c in section_chunks(patents_act_chunks, "3")}
    assert 9 in pages and 10 in pages, sorted(pages)


def test_no_bogus_section_3_elsewhere_in_the_act(patents_act_chunks):
    # Bug #3 - amendment footnotes must not resurrect Section 3.
    stray = sorted(
        {c["page"] for c in section_chunks(patents_act_chunks, "3") if c["page"] not in (9, 10)}
    )
    assert stray == [], f"unexpected Section 3 chunks on pages {stray}"


def test_section_4_6_7_start_after_the_statute_begins(patents_act_chunks):
    # Bug context G/H/I on the real document.
    for number in ("4", "6", "7"):
        chunks = section_chunks(patents_act_chunks, number)
        assert chunks, f"Section {number} not detected"
        assert min(c["page"] for c in chunks) >= 7


def test_important_section_3_clauses_are_present(patents_act_chunks):
    for clause in ("b", "d", "e", "i", "j", "p"):
        ref = f"Section 3({clause})"
        assert reference_chunks(patents_act_chunks, ref), f"missing {ref}"


def test_schedule_mode_suppresses_sections_in_the_real_schedule(patents_act_chunks):
    # Bug #2 - the REAL "THE SCHEDULE" (page 67) must still switch the
    # chunker into schedule mode, so no section headings are emitted
    # from the schedule pages.
    tagged_pages = [
        c["page"] for c in patents_act_chunks if c.get("section")
    ]
    assert tagged_pages, "no section-tagged chunks at all"
    assert max(tagged_pages) < 67, max(tagged_pages)
