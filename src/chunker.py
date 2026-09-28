import re

from legal_structure import (
    classify_legal_line,
    build_legal_reference,
)


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
            ):

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