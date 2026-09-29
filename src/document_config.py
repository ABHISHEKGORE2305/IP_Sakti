import config

# Authority weight by document_type, per the retrieval fusion
# formula: Score(d) = RRF(d) * Authority(d) * ExactRefBoost(d).
# Statutes carry the most legal weight; reference/educational
# material the least.
AUTHORITY_WEIGHTS = {
    "statute": 1.0,
    "rules": 0.9,
    "patent_guidelines": 0.85,
    "traditional_knowledge_guidelines": 0.85,
    "ayush_examination_guidelines": 0.85,
    "patent_office_manual": 0.75,
    "tkdl_reference": 0.50,
    "ayurvedic_reference": 0.50,
    # src/web_sources.py document types (periodic URL ingestion, src/ingest_web.py)
    "treaty": 0.95,                # full treaty text (CBD, Nagoya, GRATK)
    "treaty_overview": 0.65,       # what's currently fetchable — a treaty-body's own summary page, not the full text
    "international_guidance": 0.80,
    "regulatory_notice": 0.75,
}

DEFAULT_AUTHORITY_WEIGHT = config.DEFAULT_AUTHORITY_WEIGHT


DOCUMENTS = [
    {
        "filename": "patents_act_1970.pdf",
        "document": "The Patents Act, 1970",
        "document_type": "statute",
        "jurisdiction": "India",
        "language": "en",
        # Pages 1-6 of this specific PDF are the Arrangement of
        # Sections / Table of Contents - see chunker.py.
        "toc_skip_pages": 6,
    },

    {
        "filename": "patent_rules_2003.pdf",
        "document": "The Patents Rules, 2003",
        "document_type": "rules",
        "jurisdiction": "India",
        "language": "en",
    },

    {
        "filename": "3_Patents_Amendment_Rules_2024_16-03-2024.pdf",
        "document": "The Patents (Amendment) Rules, 2024",
        "document_type": "rules",
        "jurisdiction": "India",
        # Bilingual Gazette notification (Hindi pp.1-5, English pp.6-9).
        # Only the English pages structure-parse into section/clause
        # metadata; the Hindi pages still embed and are searchable, just
        # without that precision.
        "language": "en",
    },

    {
        "filename": "pharmaceuticals_guidelines_2014.pdf",
        "document": "Guidelines for Examination of Patent Applications in the Field of Pharmaceuticals",
        "document_type": "patent_guidelines",
        "jurisdiction": "India",
        "language": "en",
    },

    {
        "filename": "traditional_knowledge_guidelines_2012.pdf",
        "document": "Guidelines for Processing of Patent Applications Relating to Traditional Knowledge and Biological Material",
        "document_type": "traditional_knowledge_guidelines",
        "jurisdiction": "India",
        "language": "en",
    },

    {
        "filename": "Guidelines for Ayush.pdf",
        "document": "Guidelines for Examination of Ayush Related Inventions",
        "document_type": "ayush_examination_guidelines",
        "jurisdiction": "India",
        "language": "en",
        # Page 4 is this document's own "Table of Content" - without
        # skipping it, its "1. Introduction......1" line gets
        # misread as a real Section 1 heading (same TOC trap as
        # patents_act_1970.pdf). Real content starts page 5.
        "toc_skip_pages": 4,
    },

    {
        "filename": "26_Biological_Diversity_Act_2002_IndiaCode.pdf",
        # Confirmed by content inspection: this file is the 2023
        # AMENDMENT act only (15 pages of "In section N of the
        # principal Act, ... substitute" text), NOT the full 2002
        # principal Act. Labelling it as the principal Act would
        # misattribute citations - the full original Biological
        # Diversity Act, 2002 text has not been ingested.
        "document": "The Biological Diversity (Amendment) Act, 2023",
        "document_type": "statute",
        "jurisdiction": "India",
        "language": "en",
    },

    {
        "filename": "27_Biological_Diversity_Rules_2024.pdf",
        # Confirmed by content inspection: a full, freshly-notified
        # rule set (definitions, authority procedures, forms/schedules)
        # from the Ministry of Environment, Forest and Climate Change,
        # not merely a short amendment list - labelled as the Rules
        # in their own right rather than "Amendment Rules".
        "document": "The Biological Diversity Rules, 2024",
        "document_type": "rules",
        "jurisdiction": "India",
        # Predominantly Hindi (only the closing forms/schedules are in
        # English) - those pages still embed and are searchable, but
        # won't get section/clause structure metadata, since
        # legal_structure.py's patterns are English-only.
        "language": "hi",
    },

    {
        "filename": "patent_office_manual_2019.pdf",
        "document": "Manual of Patent Office Practice and Procedure",
        "document_type": "patent_office_manual",
        "jurisdiction": "India",
        "language": "en",
    },

    {
        "filename": "tkdl_factsheet.pdf",
        "document": "Traditional Knowledge Digital Library Factsheet",
        "document_type": "tkdl_reference",
        "jurisdiction": "India",
        "language": "en",
    },

    {
        "filename": "An_Overview_of_Ayurveda.pdf",
        "document": "An Overview of Ayurveda",
        "document_type": "ayurvedic_reference",
        "jurisdiction": "India",
        "language": "en",
    },

    # --- Regulatory / allied-regime corpus ---
    # The D&C Act + Rules govern the *classification* question that gates
    # almost every downstream IP answer (classical ASU medicine under s.3(a)
    # vs patent-and-proprietary under s.3(h) vs phytopharmaceutical under
    # Rule 2(eb)), so its absence propagated into wrong or refused answers
    # well beyond drug-licensing questions.
    # One PDF, two instruments: the Act runs to p.38, the Rules from p.39
    # (verified by the running header on each page). Registered separately so
    # the Rules' numbered provisions are labelled "Rule N", which is how the
    # benchmark — and a patent agent — cites them. document_id is set
    # explicitly because it otherwise derives from the shared filename.
    {
        "filename": "11.2_2016DrugsandCosmeticsAct1940Rules1945.pdf",
        "document_id": "drugs_and_cosmetics_act_1940",
        "document": "The Drugs and Cosmetics Act, 1940",
        "document_type": "statute",
        "jurisdiction": "India",
        "language": "en",
        "page_range": (1, 38),
    },
    {
        "filename": "11.2_2016DrugsandCosmeticsAct1940Rules1945.pdf",
        "document_id": "drugs_and_cosmetics_rules_1945",
        "document": "The Drugs and Cosmetics Rules, 1945",
        "document_type": "rules",
        "jurisdiction": "India",
        "language": "en",
        "page_range": (39, 635),
    },
    {
        "filename": "17_Food Safety and Standards (Ayurveda Aahara) Regulations, 2022.pdf",
        "document": "Food Safety and Standards (Ayurveda Aahara) Regulations, 2022",
        "document_type": "rules",
        "jurisdiction": "India",
        # Bilingual Gazette notification; the Hindi pages still embed and are
        # searchable, just without section/rule metadata precision.
        "language": "en",
    },
    {
        "filename": "4_Trade_Marks_Act_1999_IndiaCode_2026-06-01.pdf",
        "document": "The Trade Marks Act, 1999",
        "document_type": "statute",
        "jurisdiction": "India",
        "language": "en",
    },
    {
        "filename": "Protection of Plant Varieties and Farmers' Rights Act, 2001.pdf",
        "document": "The Protection of Plant Varieties and Farmers' Rights Act, 2001",
        "document_type": "statute",
        "jurisdiction": "India",
        "language": "en",
    },

    # --- International treaty corpus (user-supplied PDFs, full text where available) ---
    {
        "filename": "cbd-en.pdf",
        "document": "Convention on Biological Diversity (CBD), 1992 — Text and Annexes",
        "document_type": "treaty",
        "jurisdiction": "International",
        "language": "en",
    },
    {
        "filename": "nagoya-protocol-en.pdf",
        "document": "Nagoya Protocol on Access to Genetic Resources and the Fair and Equitable Sharing of Benefits Arising from their Utilization, 2010",
        "document_type": "treaty",
        "jurisdiction": "International",
        "language": "en",
    },
    {
        "filename": "Botanical-Drug-Development--Guidance-for-Industry.pdf",
        "document": "US FDA — Botanical Drug Development, Guidance for Industry",
        "document_type": "international_guidance",
        "jurisdiction": "United States",
        "language": "en",
    },
    {
        "filename": "37_WIPO GRATK Treaty.pdf",
        "document": "WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (GRATK), 2024",
        "document_type": "treaty",
        "jurisdiction": "International",
        "language": "en",
    },
    {
        "filename": "gratk_dc_exsum.pdf",
        # WIPO's own 2-page informal summary of the treaty, not the full
        # treaty text (that wasn't supplied as a clean standalone PDF —
        # see src/web_sources.py's wipo_gratk_treaty_2024 for the
        # complementary web-fetched overview page).
        "document": "WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (GRATK), 2024 — Informal Summary",
        "document_type": "treaty_overview",
        "jurisdiction": "International",
        "language": "en",
    },
    {
        "filename": "gratk.pdf",
        # Single-page excerpt from a WIPO General Assembly document
        # listing treaty ratification/accession status — not the treaty
        # text itself, but genuine, current (dated in the source) status
        # data. Confirmed by content inspection, not assumed from the
        # filename.
        "document": "WIPO GRATK Treaty — Ratification/Accession Status",
        "document_type": "treaty_overview",
        "jurisdiction": "International",
        "language": "en",
    },
]

for _doc in DOCUMENTS:
    _doc["authority_weight"] = AUTHORITY_WEIGHTS.get(
        _doc["document_type"], DEFAULT_AUTHORITY_WEIGHT
    )