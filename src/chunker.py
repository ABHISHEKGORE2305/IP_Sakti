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
):

    legal_reference = build_legal_reference(
        section=section,
        clause=clause,
    )

    return {
        "section": section,
        "clause": clause,
        "legal_reference": legal_reference,
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
            # Pages 1-6 of the Patents Act PDF are confirmed
            # (by direct inspection) to be the ARRANGEMENT OF
            # SECTIONS / Table of Contents. The actual statute
            # starts on page 7. We must not run any legal
            # classification against the TOC, otherwise TOC
            # lines like "3. What are not inventions." and the
            # TOC entry "THE SCHEDULE." are mistaken for the
            # real section heading / the real Schedule.

            if page_number >= 7:

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
                })

    return chunks