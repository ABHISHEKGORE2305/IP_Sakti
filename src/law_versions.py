"""
winning_features.md item 9 — "Version-tracked corpus with a 'Law
changed' timeline."

A full old-vs-new side-by-side text diff isn't honestly buildable from
the current corpus: for the Biological Diversity family we only have the
2023 Amendment Act and the 2024 Rules ingested, not the original 2002
Act or 2004 Rules text (see freshness.py / document_config.py's own
notes on this) — diffing against text we don't have would mean
fabricating one side of the comparison. Patents Rules is the one family
where both a full original text and a full amendment text are actually
ingested.

So this is scoped to what the corpus genuinely supports: a timeline of
known law versions (document_id + year, both already asserted elsewhere
in document_config.py — not new claims), each independently queryable
via retriever.combined_query_filter's document_id_filter, so a user can
literally "ask the same question under the old law vs the current law"
(the doc's own suggested demo moment) with the answer retrieval-scoped
to exactly one version — not a fabricated diff.
"""

LAW_FAMILIES = [
    {
        "family_id": "patents_rules",
        "label": "Patents Rules",
        "versions": [
            {"document_id": "patent_rules_2003", "year": 2003, "label": "The Patents Rules, 2003"},
            {
                "document_id": "3_Patents_Amendment_Rules_2024_16-03-2024",
                "year": 2024,
                "label": "The Patents (Amendment) Rules, 2024",
            },
        ],
        "note": None,
    },
    {
        "family_id": "biological_diversity",
        "label": "Biological Diversity Act / Rules",
        "versions": [
            {
                "document_id": "26_Biological_Diversity_Act_2002_IndiaCode",
                "year": 2023,
                "label": "The Biological Diversity (Amendment) Act, 2023",
            },
            {
                "document_id": "27_Biological_Diversity_Rules_2024",
                "year": 2024,
                "label": "The Biological Diversity Rules, 2024",
            },
        ],
        "note": (
            "Only the 2023 amendment and the 2024 rules are ingested — the "
            "original 2002 Act and 2004 Rules text is not, so this is not a "
            "full old-vs-new comparison, just what's actually in the corpus."
        ),
    },
]


def get_law_families() -> list[dict]:
    return LAW_FAMILIES


def find_version(document_id: str) -> dict | None:
    for family in LAW_FAMILIES:
        for version in family["versions"]:
            if version["document_id"] == document_id:
                return version
    return None
