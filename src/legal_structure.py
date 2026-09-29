import re


# Prefixes that mark an amendment / footnote line rather than a
# real statutory section heading. Footnote lines in the Patents
# Act PDF are numbered too (they restart per page), e.g.
#   3. Subs by s. 31, ibid., for section 39 (w.e.f. 1-1-2005).
#   3. The word "Appellate Board" omitted by Act 33 of 2021...
#   3. Sub-section (2) omitted by s. 30, ibid. (w.e.f. 20-5-2003).
_AMENDMENT_PREFIX = re.compile(
    r"^(?:"
    r"Ins\.?\b|"
    r"Subs?\.?\b|"
    r"Sub-clause\b|"
    r"Sub-section\b|"
    r"Sub-sections\b|"
    r"Omitted\b|"
    r"The word\b|"
    r"The words\b|"
    r"The bracket|"
    r"The figure|"
    r"The proviso\b|"
    r"Certain words\b|"
    r"Clause\b|"
    r"Renumbered\b|"
    r"Earlier\b|"
    r"Added\b"
    r")",
    re.IGNORECASE,
)

# Content fingerprints of an amendment / footnote line. Genuine
# section headings never carry these (the heading line only holds
# the short title; the provision body follows on later lines).
_AMENDMENT_BODY = re.compile(
    r"\(w\.e\.f\.|"
    r"\bibid\.|"
    r"\bomitted by\b|"
    r"\bby Act\s+\d+\s+of\s+\d{4}\b|"
    r"\bins\. by\b|"
    r"\bsubs?\.? by\b|"
    r"\bvide notification\b",
    re.IGNORECASE,
)

# Commencement-date footnotes, e.g.
#   1. 1-4-1978, vide notification No. S.O. 799, dated 10-3-1978, ...
# The leading token is a date, not a section title - genuine section
# headings never start this way.
_DATE_LEADING = re.compile(r"^\d{1,2}-\d{1,2}-\d{4}\b")


def strip_amendment_marker(line: str) -> str:
    """
    Remove a leading amendment-bracket marker.

    The India Code PDFs render amended passages as ``N[ ... ]``
    where ``N`` is an inline superscript footnote reference, e.g.

        6[(d) the mere discovery of a new form of a known substance ...
        3[25. Opposition to the patent.—(1) Where an application ...

    Without stripping the ``6[`` / ``3[`` prefix the section and
    clause detectors miss every amended provision - including
    Section 3(b), 3(d), 3(j) and the Section 25 heading.
    """

    return re.sub(r"^\d+\[", "", line.strip())


def detect_section_heading(line: str):
    """
    Detect actual statutory section headings.

    Examples:
        1. Short title, extent and commencement.
        3. What are not inventions.—
        117A. Appeals to High Court.

    Reject amendment / footnote lines such as:
        3. Sub-clause (B) omitted by Act 33 of 2021...
        4. Subs. by Act 38 of 2002...
        3. Subs by s. 31, ibid., for section 39 (w.e.f. 1-1-2005).
        3. The word "Appellate Board" omitted by Act 33 of 2021...
    """

    line = strip_amendment_marker(line)

    match = re.match(
        r"^(\d+[A-Za-z]?)\.\s+(.+)$",
        line
    )

    if not match:
        return None

    section_number = match.group(1)
    title = match.group(2).strip()

    if not title:
        return None

    # These are amendment / footnote indicators,
    # NOT statutory section headings.
    if _AMENDMENT_PREFIX.match(title):
        return None

    if _AMENDMENT_BODY.search(title):
        return None

    if _DATE_LEADING.match(title):
        return None

    if len(title) < 5:
        return None

    return section_number


# A genuine heading in the India Code PDFs runs the provision straight on
# from its own title, separated by an em/en dash:
#     23. Import licences.–An import licence in Form 10 shall be required...
#     3. What are not inventions.—The following are not inventions...
# Numbered *form fields* ("1. Name of the applicant") never do. The dash is
# therefore a strong positive signal, used to override the monotonicity check
# in chunker.create_chunks when numbering legitimately restarts.
_HEADING_DASH = re.compile(r"^.{5,120}?[—–]")

# Standalone FORM / SCHEDULE banners. The Drugs and Cosmetics volume is
# roughly two-thirds Forms and Schedules, whose numbered fields and list items
# would otherwise be read as rule headings — that mislabelled 330 chunks as
# "Rule 2" and 317 as "Rule 1", which is worse than no label at all because
# retrieval's exact-reference fast path trusts it.
_FORM_OR_SCHEDULE_BANNER = re.compile(
    r"^(?:"
    r"\d*\s*\[?\s*FORM\s+\d+[A-Z-]*\b"
    r"|(?:THE\s+)?(?:[A-Z]+\s+)?SCHEDULE\b\.?"
    r")",
)


def heading_has_dash(line: str) -> bool:
    """True when the line carries the title—body dash of a real heading."""

    return bool(_HEADING_DASH.match(strip_amendment_marker(line)))


def is_form_or_schedule_banner(line: str) -> bool:
    """True for a standalone FORM n / SCHEDULE banner line."""

    stripped = strip_amendment_marker(line).strip()
    if not _FORM_OR_SCHEDULE_BANNER.match(stripped):
        return False
    # A banner is a short standalone line; prose that merely mentions a form
    # ("...shall be required in Form 10 for import") is not a banner.
    return len(stripped) <= 60


def detect_clause(line: str):
    """
    Detect lowercase top-level clauses:

        (a)
        (b)
        (p)

    Do NOT detect uppercase nested items:

        (A)
        (B)
    """

    line = strip_amendment_marker(line)

    # Intentionally NO re.IGNORECASE
    match = re.match(
        r"^\(([a-z])\)\s+",
        line
    )

    if match:
        return match.group(1)

    return None


def detect_subsection(line: str):
    """
    Detect subsections:

        (1)
        (2)
        (3)
    """

    line = strip_amendment_marker(line)

    match = re.match(
        r"^\((\d+[A-Za-z]?)\)\s+",
        line
    )

    if match:
        return match.group(1)

    return None


def build_legal_reference(
    section=None,
    clause=None,
    kind="Section",
):
    """
    Build references such as:

        Section 3
        Section 3(p)
        Rule 6(a)          (kind="Rule", for Rules-type documents)
    """

    if section is None:
        return None

    if clause:
        return f"{kind} {section}({clause})"

    return f"{kind} {section}"


def classify_legal_line(line: str):

    section = detect_section_heading(line)

    if section:
        return {
            "type": "section",
            "section": section
        }

    clause = detect_clause(line)

    if clause:
        return {
            "type": "clause",
            "clause": clause
        }

    subsection = detect_subsection(line)

    if subsection:
        return {
            "type": "subsection",
            "subsection": subsection
        }

    return {
        "type": "other"
    }