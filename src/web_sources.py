"""
left_to_do.md item 8/9 — periodic web-sourced corpus registry.

Parallel in shape to document_config.py's DOCUMENTS list, but for pages
fetched over HTTP instead of local PDFs (src/web_loader.py, src/
ingest_web.py). Every entry needs a "source_id" (used as document_id —
there's no file stem to derive one from) and a "url".

`content_selector` is REQUIRED for fetch_method="html" — a curated CSS
selector per site, not an automatic "readability" extractor, since a
heuristic extractor silently truncating or mangling statutory/treaty
text is worse than no text at all for this platform's citation-grounding
guarantee.

VERIFICATION STATUS (live-checked with `requests`/`BeautifulSoup`, not
guessed — see implementation_plan.md's web-corpus section for the
session this was done in):

WORKING — real, static, selector-confirmed content:
    wipo_gratk_treaty_2024, pct_texts, madrid_legal_texts,
    hague_legal_texts, budapest_treaty, cdsco_home
  IMPORTANT caveat: the WIPO pages above are each that treaty's overview
  /landing page (1-2KB of prose), NOT the full treaty text — WIPO hosts
  the actual legal text as a linked PDF from each of these pages. Treat
  these as "treaty overview" reference material (see document_type
  below), not a substitute for the full text. Getting the full text
  requires either manually finding the PDF's direct URL and adding it as
  a separate `fetch_method: "pdf_link"` entry, or a follow-up two-stage
  crawler (fetch page -> parse out the PDF link -> fetch that) which is
  NOT built here (see implementation_plan.md's "not attempted" list).

SUPERSEDED by user-supplied full-text PDFs (registered in
document_config.py's DOCUMENTS, ingested via the normal PDF pipeline —
see implementation_plan.md):
    cbd_convention_text — real CBD domain, but this specific URL 404d;
      no longer needed anyway — cbd-en.pdf (full Convention text) is
      registered as a "treaty" document.
    nagoya_protocol_text (cbd.int/abs landing page) — removed; superseded
      by nagoya-protocol-en.pdf (full protocol text).
    us_fda_botanical_guidance (was blocked — see below) — superseded by
      Botanical-Drug-Development--Guidance-for-Industry.pdf (full text).
    wipo_gratk_treaty_2024's full legal text still isn't available as a
      clean PDF — gratk_dc_exsum.pdf (WIPO's own 2-page informal summary)
      and gratk.pdf (a ratification-status excerpt) are registered as
      "treaty_overview" documents; the web-fetched landing page below
      remains as a third, complementary overview.

BROKEN / NOT FETCHABLE via static requests — confirmed, not guessed:
    trips_agreement — the WTO URL redirects to their own 404 page
      (returns HTTP 200 with 404 content — a trap for a naive status
      check). Correct URL not found in this pass.
    us_fda_botanical_guidance — fda.gov returns an anti-bot/"abuse
      detection" page for this request pattern; needs a different
      fetch approach (real browser headers/session, or manual PDF).
    eu_thmpd_directive — eur-lex.europa.eu returns an empty 202
      response to a plain GET; likely requires cookies/JS.
    uk_mhra_thr_scheme — gov.uk genuinely 404s; the guidance may have
      moved or been renamed. Not found in this pass.
    ayush_home, fssai_home — both are JavaScript-rendered single-page
      apps; a plain HTTP GET returns an near-empty app shell with no
      real content in the initial HTML. Needs a headless browser
      (Playwright/Selenium) to render — explicitly out of scope for
      the v1 static fetcher (see implementation_plan.md).
    ipindia_patents_overview — this specific deep link 404s; ipindia.gov.in's
      site structure has likely changed since references.py was written.

The BROKEN entries are commented out below rather than deleted, so
they're easy to find and fix once a corrected URL/fetch approach exists
— DO NOT uncomment and run one without re-verifying it first (a 200
status with wrong/boilerplate content is worse than a skipped source).
"""

WEB_SOURCES = [
    # --- Treaties / international instruments (verified: overview pages, not full text) ---
    {
        "source_id": "wipo_gratk_treaty_2024",
        "url": "https://www.wipo.int/en/web/treaties/ip/gratk/index",
        "document": "WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (GRATK), 2024 — overview",
        "document_type": "treaty_overview",
        "jurisdiction": "International",
        "language": "en",
        "fetch_method": "html",
        "content_selector": "#main-content",
        "stale_after_days": 90,
    },
    # nagoya_protocol_text (cbd.int/abs landing page) removed — superseded
    # by the full-text nagoya-protocol-en.pdf now registered in
    # document_config.py's DOCUMENTS and ingested via the normal PDF
    # pipeline. Keeping both would mean a lower-quality landing-page
    # summary sitting alongside the real text for no benefit.
    {
        "source_id": "pct_texts",
        "url": "https://www.wipo.int/en/web/pct-system/texts/index",
        "document": "Patent Cooperation Treaty (PCT) — texts and regulations, overview",
        "document_type": "treaty_overview",
        "jurisdiction": "International",
        "language": "en",
        "fetch_method": "html",
        "content_selector": "#main-content",
        "stale_after_days": 180,
    },
    {
        "source_id": "madrid_legal_texts",
        "url": "https://www.wipo.int/en/web/madrid-system/legal_texts/index",
        "document": "Madrid System — legal texts overview (international trademark registration)",
        "document_type": "treaty_overview",
        "jurisdiction": "International",
        "language": "en",
        "fetch_method": "html",
        "content_selector": "#main-content",
        "stale_after_days": 180,
    },
    {
        "source_id": "hague_legal_texts",
        "url": "https://www.wipo.int/en/web/hague-system/legal-texts",
        "document": "Hague System — legal texts overview (international design registration)",
        "document_type": "treaty_overview",
        "jurisdiction": "International",
        "language": "en",
        "fetch_method": "html",
        "content_selector": "#main-content",
        "stale_after_days": 180,
    },
    {
        "source_id": "budapest_treaty",
        "url": "https://www.wipo.int/en/web/treaties/registration/budapest/index",
        "document": "Budapest Treaty on the International Recognition of the Deposit of Microorganisms — overview",
        "document_type": "treaty_overview",
        "jurisdiction": "International",
        "language": "en",
        "fetch_method": "html",
        "content_selector": "#main-content",
        "stale_after_days": 365,
    },

    # --- Indian regulatory portals ---
    {
        "source_id": "cdsco_home",
        "url": "https://cdsco.gov.in",
        "document": "CDSCO — Central Drugs Standard Control Organisation",
        "document_type": "regulatory_notice",
        "jurisdiction": "India",
        "language": "en",
        "fetch_method": "html",
        "content_selector": "body",
        "stale_after_days": 30,
    },

    # ------------------------------------------------------------------
    # NOT FETCHABLE as of this verification pass — see module docstring
    # for exactly what's wrong with each. Left here, commented out, as
    # the record of what was tried rather than silently dropped.
    # ------------------------------------------------------------------

    # {
    #     "source_id": "trips_agreement",
    #     "url": "https://www.wto.org/english/tratop_e/trips_e/t_agm0_e.htm",  # redirects to WTO's own 404 page
    #     "document": "Agreement on Trade-Related Aspects of Intellectual Property Rights (TRIPS)",
    #     "document_type": "treaty_overview",
    #     "jurisdiction": "International",
    #     "language": "en",
    #     "fetch_method": "html",
    #     "content_selector": "main",  # UNVERIFIED — URL itself is broken
    #     "stale_after_days": 365,
    # },
    # {
    #     "source_id": "us_fda_botanical_guidance",
    #     "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/botanical-drug-development-guidance-industry",  # FDA anti-bot page
    #     "document": "US FDA — Botanical Drug Development, Guidance for Industry",
    #     "document_type": "international_guidance",
    #     "jurisdiction": "United States",
    #     "language": "en",
    #     "fetch_method": "html",
    #     "content_selector": "main",  # UNVERIFIED — blocked before reaching content
    #     "stale_after_days": 180,
    # },
    # {
    #     "source_id": "eu_thmpd_directive",
    #     "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32004L0024",  # empty 202 response to plain GET
    #     "document": "Directive 2004/24/EC (Traditional Herbal Medicinal Products Directive, THMPD)",
    #     "document_type": "international_guidance",
    #     "jurisdiction": "European Union",
    #     "language": "en",
    #     "fetch_method": "html",
    #     "content_selector": "main",  # UNVERIFIED — site returned no content
    #     "stale_after_days": 365,
    # },
    # {
    #     "source_id": "uk_mhra_thr_scheme",
    #     "url": "https://www.gov.uk/guidance/traditional-herbal-medicines-registration-scheme",  # genuine 404
    #     "document": "UK MHRA — Traditional Herbal Medicines Registration (THR) Scheme",
    #     "document_type": "international_guidance",
    #     "jurisdiction": "United Kingdom",
    #     "language": "en",
    #     "fetch_method": "html",
    #     "content_selector": "main",  # UNVERIFIED — page not found, needs a corrected URL
    #     "stale_after_days": 180,
    # },
    # {
    #     "source_id": "ipindia_patents_overview",
    #     "url": "https://ipindia.gov.in/patents.htm",  # 404 as of this pass
    #     "document": "IP India — Patents overview",
    #     "document_type": "regulatory_notice",
    #     "jurisdiction": "India",
    #     "language": "en",
    #     "fetch_method": "html",
    #     "content_selector": "main",  # UNVERIFIED — URL itself is broken
    #     "stale_after_days": 60,
    # },
    # {
    #     "source_id": "ayush_home",
    #     "url": "https://ayush.gov.in",  # JS-rendered SPA — empty on plain GET
    #     "document": "Ministry of AYUSH",
    #     "document_type": "regulatory_notice",
    #     "jurisdiction": "India",
    #     "language": "en",
    #     "fetch_method": "html",
    #     "content_selector": "body",  # would need a headless browser, not a static fetch
    #     "stale_after_days": 30,
    # },
    # {
    #     "source_id": "fssai_home",
    #     "url": "https://fssai.gov.in",  # JS-rendered SPA — empty on plain GET
    #     "document": "FSSAI — Food Safety and Standards Authority of India",
    #     "document_type": "regulatory_notice",
    #     "jurisdiction": "India",
    #     "language": "en",
    #     "fetch_method": "html",
    #     "content_selector": "body",  # would need a headless browser, not a static fetch
    #     "stale_after_days": 30,
    # },
]
