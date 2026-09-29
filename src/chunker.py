import re

from legal_structure import (
    classify_legal_line,
    build_legal_reference,
    heading_has_dash,
    is_form_or_schedule_banner,
)


def _section_sort_key(section: str | None):
    """Numeric ordering key for a provision number like "24", "24A", "161-A".

    Returns None when the number cannot be parsed, which callers treat as
    "don't apply the monotonicity rule".
    """

    if not section:
        return None
    match = re.match(r"^(\d+)", str(section))
    if not match:
        return None
    return int(match.group(1))


def split_into_paragraphs(text: str):

    lines = text.splitlines()

    paragraphs = []

    current = []

    for line in lines:

        line = line.strip()

        if not line:

            if current:
                paragraphs.append(
                    "\n".join(current)
                )

                current = []

            continue

        current.append(line)

    if current:
        paragraphs.append(
            "\n".join(current)
        )

    return paragraphs


def add_legal_metadata(
    text: str,
    section=None,
    clause=None,
    is_rules=False,
):
    """
    is_rules: True for "rules"-type documents (e.g. The Patents Rules,
    2003), so numbered provisions are labelled "Rule N" and stored
    under the "rule" field, not "Section N" / "section" - otherwise a
    Rules document's own numbering gets mislabelled as statute
    sections.
    """

    kind = "Rule" if is_rules else "Section"

    legal_reference = build_legal_reference(
        section=section,
        clause=clause,
        kind=kind,
    )

    if is_rules:
        return {
            "rule": section,
            "clause": clause,
            "legal_reference": legal_reference,
        }

    return {
        "section": section,
        "clause": clause,
        "legal_reference": legal_reference,
    }


def document_metadata(page: dict) -> dict:
    """Document-level fields carried onto every chunk from that page."""

    return {
        "document_type": page.get("document_type"),
        "jurisdiction": page.get("jurisdiction"),
        "language": page.get("language"),
        "authority_weight": page.get("authority_weight"),
    }


# ----------------------------------------------------------------------
# Post-pass: consolidate clause fragments into section-sized chunks
# ----------------------------------------------------------------------
#
# create_chunks() flushes at every clause boundary, which is right for
# metadata precision but produces chunks far too small to retrieve: the
# Patents Act's Section 3 came out as 17 fragments, the heading ("What are
# not inventions") severed from its own clauses, and clause (p) reduced to a
# 170-character sentence with nothing in it that identifies the Act, the
# section, or the fact that it describes a patentability bar. Measured on
# bge-reranker-v2-m3, that fragment scored 0.0001 against the questions it
# is the correct answer to, so it never entered the top-k at any candidate_k.
#
# Merging a section's fragments back together and prefixing the citation
# raises the same content to ~0.09 on the same queries.

MERGE_TARGET_CHARS = 900     # keep accumulating until at least this long
MERGE_MAX_CHARS = 2400       # but never build a chunk larger than this
MIN_USEFUL_CHARS = 25        # below this a "chunk" is a page number or stray glyph


def _is_noise(text: str) -> bool:
    """Page numbers and stray glyphs the line-based pass emitted as chunks
    (the old corpus contained chunks whose entire text was "10" or "26")."""

    stripped = text.strip()
    if len(stripped) < MIN_USEFUL_CHARS and not re.search(r"[A-Za-z]{3}", stripped):
        return True
    return not stripped


def _citation_header(chunk: dict) -> str:
    """A factual one-line citation label for the chunk's own content.

    This is prepended to the chunk text (rather than kept in a parallel
    field) so that embedding, BM25 and the cross-encoder all see it without
    each retriever needing to know about it — and so the generator sees the
    provision's own identity next to its text when it writes the citation.
    """

    parts = [chunk.get("document") or chunk.get("document_id") or ""]

    reference = chunk.get("legal_reference")
    if reference:
        parts.append(reference)

    document_type = chunk.get("document_type")
    if document_type in ("statute", "rules"):
        parts.append("statutory provision")
    elif document_type:
        parts.append(document_type.replace("_", " "))

    jurisdiction = chunk.get("jurisdiction")
    if jurisdiction:
        parts.append(jurisdiction)

    return " — ".join(part for part in parts if part)


def consolidate_chunks(chunks: list[dict]) -> list[dict]:
    """Merge consecutive same-section fragments up to MERGE_TARGET_CHARS and
    prefix each result with its citation header. Drops noise chunks.

    Merging is only ever done within one (document, section/rule) group and
    only across *consecutive* fragments, so a merged chunk never splices two
    different provisions together and its metadata stays true to its text.
    """

    merged: list[dict] = []
    buffer: dict | None = None

    def flush():
        nonlocal buffer
        if buffer is None:
            return
        body = buffer.pop("_body")
        header = _citation_header(buffer)
        buffer["text"] = f"{header}\n{body}" if header else body
        merged.append(buffer)
        buffer = None

    for chunk in chunks:
        text = (chunk.get("text") or "").strip()

        if _is_noise(text):
            continue

        # Deliberately not keyed on page: a provision that runs across a page
        # break (Patents Act s.3 spans pp.9-10) must still merge. The merged
        # chunk keeps the page its first fragment came from, which is where a
        # citation should point.
        key = (
            chunk.get("document_id"),
            chunk.get("section"),
            chunk.get("rule"),
        )

        if (
            buffer is not None
            and buffer["_key"] == key
            and len(buffer["_body"]) < MERGE_TARGET_CHARS
            and len(buffer["_body"]) + len(text) + 1 <= MERGE_MAX_CHARS
        ):
            buffer["_body"] += "\n" + text
            buffer["merged_fragments"] += 1
            # The merged chunk spans its group's clauses, so the single-clause
            # label on the first fragment would misdescribe it.
            if buffer.get("clause") is not None:
                buffer["clause"] = None
                buffer["legal_reference"] = build_legal_reference(
                    section=buffer.get("section") or buffer.get("rule"),
                    clause=None,
                    kind="Rule" if buffer.get("rule") else "Section",
                )
            continue

        flush()
        buffer = dict(chunk)
        buffer["_key"] = key
        buffer["_body"] = text
        buffer["merged_fragments"] = 1

    flush()

    for chunk in merged:
        chunk.pop("_key", None)

    return merged


def create_chunks(
    pages: list[dict],
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
):

    chunks = []

    current_section = None
    current_clause = None

    in_schedule = False

    legal_parsing_enabled = False

    chunk_counter = 0

    for page in pages:

        page_number = page["page"]
        source = page["source"]
        toc_skip_pages = page.get("toc_skip_pages", 0) or 0

        lines = page["text"].splitlines()

        current_text = []

        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                continue

            # -------------------------------------------------
            # ENABLE LEGAL PARSING ONLY AFTER TABLE OF CONTENTS
            # -------------------------------------------------
            #
            # Some source PDFs (confirmed by inspection: the Patents
            # Act, 1970) open with an ARRANGEMENT OF SECTIONS / Table
            # of Contents whose lines - e.g. "3. What are not
            # inventions." or "THE SCHEDULE." - would otherwise be
            # mistaken for a real section heading / the real Schedule.
            # `toc_skip_pages` (per-document metadata, default 0) is
            # how many leading pages to treat as front matter before
            # legal classification begins. Defaulting to 0 means every
            # other document is parsed from page 1, rather than
            # silently inheriting a page-7 cutoff that only made sense
            # for that one PDF.

            if page_number > toc_skip_pages:

                legal_parsing_enabled = True

            # -------------------------------------------------
            # BEFORE LEGAL PARSING
            # -------------------------------------------------

            if not legal_parsing_enabled:

                current_text.append(line)

                continue

            # -------------------------------------------------
            # SCHEDULE DETECTION
            # -------------------------------------------------
            #
            # Only after legal parsing has started. Match a
            # standalone uppercase "THE SCHEDULE" heading line
            # (optionally followed by a period) - NOT prose
            # such as "... specified in the Schedule." which
            # otherwise triggered schedule mode one page early.

            if re.match(
                r"^THE\s+SCHEDULE\b\.?\s*$",
                line,
            ) or is_form_or_schedule_banner(line):

                in_schedule = True

                current_section = None
                current_clause = None

                current_text.append(line)

                continue

            # -------------------------------------------------
            # LEGAL CLASSIFICATION
            # -------------------------------------------------

            classification = classify_legal_line(line)

            line_type = classification["type"]

            # -------------------------------------------------
            # NEW SECTION
            # -------------------------------------------------

            # Statutory numbering ascends. A "heading" numbered at or below the
            # provision we are already inside is a numbered list item or form
            # field, not a new rule — unless it carries a real heading's
            # title-body dash, which is reliable enough to trust over the
            # ordering (and is how a genuine restart, e.g. a fresh Part, is
            # recognised). Without this the Drugs and Cosmetics Rules churned
            # between "Rule 1" and "Rule 9" across 597 pages.
            dash_heading = line_type == "section" and heading_has_dash(line)

            if line_type == "section" and not dash_heading:
                incoming = _section_sort_key(classification.get("section"))
                current = _section_sort_key(current_section)
                if (
                    incoming is not None
                    and current is not None
                    and incoming <= current
                ):
                    current_text.append(line)
                    continue

            # A real dash-style heading means the Forms/Schedules run is over.
            if dash_heading and in_schedule:
                in_schedule = False

            if (
                line_type == "section"
                and not in_schedule
            ):

                if current_text:

                    text = " ".join(
                        current_text
                    ).strip()

                    if text:

                        chunk_counter += 1

                        metadata = add_legal_metadata(
                            text=text,
                            section=current_section,
                            clause=current_clause,
                            is_rules=(page.get("document_type") == "rules"),
                        )

                        chunks.append({

                            "chunk_id": (
                                f"{page['document_id']}_"
                                f"{chunk_counter:06d}"
                            ),

                            "text": text,

                            "page": page_number,

                            "source": source,

                            "document_id": (
                                page["document_id"]
                            ),

                            "document": page.get(
                                "document",
                                page["document_id"]
                            ),

                            **metadata,
                            **document_metadata(page),
                        })

                    current_text = []

                current_section = (
                    classification["section"]
                )

                current_clause = None

                current_text.append(line)

                continue

            # -------------------------------------------------
            # NEW CLAUSE
            # -------------------------------------------------

            if line_type == "clause":

                if current_text:

                    text = " ".join(
                        current_text
                    ).strip()

                    if text:

                        chunk_counter += 1

                        metadata = add_legal_metadata(
                            text=text,
                            section=current_section,
                            clause=current_clause,
                            is_rules=(page.get("document_type") == "rules"),
                        )

                        chunks.append({

                            "chunk_id": (
                                f"{page['document_id']}_"
                                f"{chunk_counter:06d}"
                            ),

                            "text": text,

                            "page": page_number,

                            "source": source,

                            "document_id": (
                                page["document_id"]
                            ),

                            "document": page.get(
                                "document",
                                page["document_id"]
                            ),

                            **metadata,
                            **document_metadata(page),
                        })

                    current_text = []

                current_clause = (
                    classification["clause"]
                )

                current_text.append(line)

                continue

            # -------------------------------------------------
            # NORMAL TEXT
            # -------------------------------------------------

            current_text.append(line)

        # -----------------------------------------------------
        # END OF PAGE
        # -----------------------------------------------------

        if current_text:

            text = " ".join(
                current_text
            ).strip()

            if text:

                chunk_counter += 1

                metadata = add_legal_metadata(
                    text=text,
                    section=current_section,
                    clause=current_clause,
                    is_rules=(page.get("document_type") == "rules"),
                )

                chunks.append({

                    "chunk_id": (
                        f"{page['document_id']}_"
                        f"{chunk_counter:06d}"
                    ),

                    "text": text,

                    "page": page_number,

                    "source": source,

                    "document_id": (
                        page["document_id"]
                    ),

                    "document": page.get(
                        "document",
                        page["document_id"]
                    ),

                    **metadata,
                    **document_metadata(page),
                })

    return chunks