"""
left_to_do.md item 13 — "source freshness checking" for the citation
system. The retrieval pipeline does not persist a `version_date` on
chunks (document_config.DOCUMENTS never set one — see the implementation
plan's audit), and re-deriving one for every statute/rule would mean
asserting enactment/amendment dates from memory, which risks stamping
an incorrect legal date on a citation. Instead this maps only the years
already stated in each document's own title/filename in
document_config.py (a fact already asserted elsewhere in the corpus,
not a new claim), and is applied post-hoc at the API layer so it never
touches chunking/embedding/ingestion.

Document types with no confirmed year (e.g. "Guidelines for Ayush.pdf",
which carries no year in its title) are left unflagged rather than
guessed.
"""

import datetime

import config

# document_id -> year asserted in that document's own title/filename in
# document_config.py. Statutes/rules/guidelines only; reference material
# (tkdl_factsheet, an_overview_of_ayurveda) is intentionally excluded —
# it's background material, not a primary legal source with a version to
# go stale.
KNOWN_YEAR_BY_DOCUMENT_ID = {
    "patents_act_1970": 1970,
    "patent_rules_2003": 2003,
    "3_Patents_Amendment_Rules_2024_16-03-2024": 2024,
    "pharmaceuticals_guidelines_2014": 2014,
    "traditional_knowledge_guidelines_2012": 2012,
    "26_Biological_Diversity_Act_2002_IndiaCode": 2023,  # labelled "2023 Amendment" in document_config.py
    "27_Biological_Diversity_Rules_2024": 2024,
    "patent_office_manual_2019": 2019,
}

# Primary legal sources older than this many years get a "confirm
# currency" note — a statute or rule set can of course still be in
# force at any age, this is a prompt to check for later amendments,
# not a claim that the source is invalid.
STALE_AFTER_YEARS = 10


def freshness_note(document_id: str | None) -> str | None:
    if not document_id:
        return None

    year = KNOWN_YEAR_BY_DOCUMENT_ID.get(document_id)
    if year is None:
        return None

    age = datetime.date.today().year - year
    if age < STALE_AFTER_YEARS:
        return None

    return (
        f"This source is from {year} ({age} years old) — confirm no later "
        "amendment or notification has superseded it."
    )


def web_freshness_note(fetched_at: str | None, stale_after_days: int = config.WEB_SOURCE_STALE_AFTER_DAYS) -> str | None:
    """
    Parallel check for web-sourced chunks (src/web_loader.py, src/
    ingest_web.py) — those carry a `fetched_at` ISO date instead of a
    title-asserted enactment year, and go stale on a much shorter
    (days, not years) horizon since the underlying page can change at
    any time without a new "amendment" being announced the way a
    statute's is.
    """

    if not fetched_at:
        return None

    try:
        fetched_date = datetime.date.fromisoformat(fetched_at)
    except ValueError:
        return None

    age_days = (datetime.date.today() - fetched_date).days
    if age_days < stale_after_days:
        return None

    return (
        f"This web source was last fetched {age_days} days ago (on {fetched_at}) "
        "— it may have changed since; re-run the corpus update or check the "
        "source directly."
    )
