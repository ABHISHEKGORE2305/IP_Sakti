"""
left_to_do.md item 16 ("Official Database Access") — deep links to free,
official government/WIPO portals. Record lookup / application-reference
search on these portals is left to the user (each requires its own
CAPTCHA/session flow that a scraper would have to fight); this module
gives the assistant a verified, categorized set of destinations to point
users at, which is the free-tier scope item 16 actually asks for.

Paid/subscription databases (e.g. commercial patent-analytics
platforms) are deliberately not included — item 16 requires explicit
per-use user permission and access logging for those, which is a
separate feature this module does not attempt.
"""

REFERENCE_CATEGORIES = [
    {
        "category": "Patents (India)",
        "links": [
            {
                "title": "Indian Patent Search (InPASS)",
                "url": "https://ipindiaonline.gov.in/patentsearch/search/index.aspx",
                "description": "Search granted patents and published applications at the Indian Patent Office.",
            },
            {
                "title": "IP India — Patents",
                "url": "https://ipindia.gov.in/patents.htm",
                "description": "CGPDTM's patents portal: forms, fee schedules, manuals, and notifications.",
            },
        ],
    },
    {
        "category": "Trademarks (India)",
        "links": [
            {
                "title": "Trademark Public Search",
                "url": "https://ipindiaonline.gov.in/tmrpublicsearch/frmmain.aspx",
                "description": "Search registered and pending trademarks by word mark, class, or applicant.",
            },
            {
                "title": "IP India — Trade Marks",
                "url": "https://ipindia.gov.in/trade-marks.htm",
                "description": "NICE Classification, forms, and registry procedure.",
            },
        ],
    },
    {
        "category": "Geographical Indications",
        "links": [
            {
                "title": "GI Registry",
                "url": "https://ipindia.gov.in/registration-gi.htm",
                "description": "Registered GIs, authorized-user procedure, Geographical Indications Registry (Chennai).",
            },
        ],
    },
    {
        "category": "Designs",
        "links": [
            {
                "title": "Design Search",
                "url": "https://ipindiaonline.gov.in/designsearch/",
                "description": "Search registered industrial designs (packaging, containers, applicators, etc.).",
            },
        ],
    },
    {
        "category": "Traditional Knowledge",
        "links": [
            {
                "title": "Traditional Knowledge Digital Library (TKDL)",
                "url": "https://www.tkdl.res.in",
                "description": "Prior-art documentation of codified Ayurveda/Siddha/Unani/Yoga knowledge, used by patent examiners under Section 3(p).",
            },
        ],
    },
    {
        "category": "Biodiversity & ABS",
        "links": [
            {
                "title": "National Biodiversity Authority (NBA)",
                "url": "http://nbaindia.org",
                "description": "Form I/II/III/IV applications, ABS guidelines, and State Biodiversity Board contacts.",
            },
        ],
    },
    {
        "category": "AYUSH & Drug Regulation",
        "links": [
            {
                "title": "Ministry of AYUSH",
                "url": "https://ayush.gov.in",
                "description": "AYUSH licensing, GMP notifications, and Ayurveda examination guidelines.",
            },
            {
                "title": "CDSCO",
                "url": "https://cdsco.gov.in",
                "description": "Central Drugs Standard Control Organisation — phytopharmaceutical and new-drug approvals.",
            },
        ],
    },
    {
        "category": "Food & Nutraceuticals",
        "links": [
            {
                "title": "FSSAI",
                "url": "https://fssai.gov.in",
                "description": "Food Safety and Standards Authority — Ayurveda-Aahar regulations and licensing.",
            },
        ],
    },
    {
        "category": "International / WIPO",
        "links": [
            {
                "title": "WIPO",
                "url": "https://www.wipo.int",
                "description": "World Intellectual Property Organization — treaties, IP statistics, global services.",
            },
            {
                "title": "WIPO Lex",
                "url": "https://www.wipo.int/wipolex/",
                "description": "Full text of national IP laws and international treaties, including TRIPS and the Nagoya Protocol.",
            },
            {
                "title": "PCT (Patent Cooperation Treaty)",
                "url": "https://www.wipo.int/pct/en/",
                "description": "International patent filing system — national-phase entry deadlines and procedure.",
            },
            {
                "title": "Madrid System",
                "url": "https://www.wipo.int/madrid/en/",
                "description": "International trademark registration across member countries.",
            },
            {
                "title": "Hague System",
                "url": "https://www.wipo.int/hague/en/",
                "description": "International registration of industrial designs.",
            },
        ],
    },
]
