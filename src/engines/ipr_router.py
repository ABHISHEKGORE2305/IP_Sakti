"""
Multi-Regime IPR Decision Engine.

Deterministic routing/guidance across the 7 IP regimes named in
implementation_plan.md Phase 2.4: Patents, Trademarks, Geographical
Indications, Industrial Designs, Trade Secrets, Copyright, and Plant
Variety Protection (PPV&FR). Each regime function returns structured,
regime-specific procedural guidance — this is a *complement* to
engines.classifier (which gives a one-line IP-regime-availability
blurb per product category), not a duplicate of it.

No dedicated corpus (Trade Marks Act, GI Act, Designs Act, Copyright
Act, PPV&FR Act) has been ingested, so — like engines.intl_engine —
this encodes the structural/procedural facts stated directly in the
implementation plan, not generated legal interpretation.
"""

from enum import Enum


class Regime(str, Enum):
    PATENT = "patent"
    TRADEMARK = "trademark"
    GEOGRAPHICAL_INDICATION = "geographical_indication"
    INDUSTRIAL_DESIGN = "industrial_design"
    TRADE_SECRET = "trade_secret"
    COPYRIGHT = "copyright"
    PPV_FR = "ppv_fr"


# ----------------------------------------------------------------------
# Patents
# ----------------------------------------------------------------------

def patent_guidance() -> dict:
    """High-level patent filing workflow (detailed patentability analysis is engines.tk_engine)."""

    return {
        "regime": Regime.PATENT.value,
        "governing_law": "The Patents Act, 1970 & The Patents Rules, 2003 (as amended)",
        "filing_workflow": [
            "Form 1 — Application for grant of patent",
            "Form 2 — Provisional/complete specification",
            "Form 3 — Statement and undertaking regarding foreign applications",
            "Form 5 — Declaration as to inventorship",
            "Form 18 — Request for examination",
            "Form 27 — Statement regarding the working of the patented invention (post-grant, annual)",
        ],
        "note": (
            "For the substantive patentability question — novelty, inventive step, "
            "Section 3(p)/3(e)/3(d) traditional-knowledge exclusions — use "
            "engines.tk_engine.analyze_tk_patentability, not this router."
        ),
    }


# ----------------------------------------------------------------------
# Trademarks
# ----------------------------------------------------------------------

# NICE Classification guidance the plan calls out explicitly (Phase 2.4).
_NICE_CLASS_BY_PRODUCT_TYPE = {
    "medicine": {"class": 5, "description": "Pharmaceuticals, medicinal preparations, dietary supplements for medical use"},
    "supplement": {"class": 5, "description": "Pharmaceuticals, medicinal preparations, dietary supplements for medical use"},
    "cosmetic": {"class": 3, "description": "Cosmetics, non-medicated toiletry preparations"},
    "herbal_tea": {"class": 30, "description": "Tea, herbal infusions (non-medicinal), confections"},
    "confection": {"class": 30, "description": "Tea, herbal infusions (non-medicinal), confections"},
    "clinic_services": {"class": 44, "description": "Ayurvedic clinics, Panchakarma, medical/wellness services"},
}


def trademark_nice_class(product_type: str) -> dict:
    """NICE Classification guidance for a described product/service type."""

    entry = _NICE_CLASS_BY_PRODUCT_TYPE.get(product_type)

    if entry is None:
        return {
            "regime": Regime.TRADEMARK.value,
            "product_type": product_type,
            "finding": (
                f"No NICE class mapping for product_type='{product_type}'. Known types: "
                f"{', '.join(sorted(_NICE_CLASS_BY_PRODUCT_TYPE))}."
            ),
        }

    return {
        "regime": Regime.TRADEMARK.value,
        "product_type": product_type,
        "nice_class": entry["class"],
        "finding": f"NICE Class {entry['class']}: {entry['description']}.",
    }


def trademark_distinctiveness_risk(is_generic_or_descriptive_ayurvedic_term: bool) -> dict:
    """
    Section 9 (absolute grounds) / Section 11 (relative grounds) distinctiveness
    screen for a proposed Ayurvedic brand term.
    """

    if is_generic_or_descriptive_ayurvedic_term:
        return {
            "regime": Regime.TRADEMARK.value,
            "topic": "Distinctiveness (Trade Marks Act, 1999, Section 9)",
            "risk": "high_risk",
            "finding": (
                "A generic or merely descriptive Ayurvedic/Sanskrit term (e.g. the "
                "plain name of a classical formulation or a common ingredient) is "
                "liable to objection under Section 9 as devoid of distinctive "
                "character, unless acquired distinctiveness (secondary meaning "
                "through extensive prior use) can be shown."
            ),
            "recommendation": (
                "Coin a distinctive/suggestive mark instead of the generic term "
                "itself, or gather evidence of long, extensive, exclusive prior use "
                "to argue acquired distinctiveness."
            ),
        }

    return {
        "regime": Regime.TRADEMARK.value,
        "topic": "Distinctiveness (Trade Marks Act, 1999, Section 9)",
        "risk": "clear",
        "finding": "Not flagged as a generic/descriptive term on the facts given.",
        "recommendation": (
            "Still run a clearance search against the Trade Marks Registry for "
            "conflicting prior marks (Section 11 relative grounds) before filing."
        ),
    }


# ----------------------------------------------------------------------
# Geographical Indications
# ----------------------------------------------------------------------

def gi_guidance() -> dict:
    """GI Act, 1999 registration process for a region-linked product."""

    return {
        "regime": Regime.GEOGRAPHICAL_INDICATION.value,
        "governing_law": "Geographical Indications of Goods (Registration and Protection) Act, 1999",
        "ownership_model": (
            "Collective/community ownership — a GI is registered in the name of an "
            "association of persons, producers, or an organisation representing "
            "their interests, not an individual proprietor."
        ),
        "process": [
            "File the GI application (Form GI-1) with the Geographical Indications Registry, Chennai",
            "Examination and publication in the GI Journal for opposition",
            "Registration of the Geographical Indication itself",
            "Separate Authorized User registration (Form GI-3) for each producer entitled to use the GI",
        ],
        "examples": ["Navara Rice", "Nilambur Teak", "Malabar Pepper"],
        "note": (
            "Registering the GI protects the community's right to the name; each "
            "individual producer still needs their own Authorized User registration "
            "to use it commercially."
        ),
    }


# ----------------------------------------------------------------------
# Industrial Designs
# ----------------------------------------------------------------------

def industrial_design_guidance() -> dict:
    """Designs Act, 2000 protection for novel packaging/applicator/device shape."""

    return {
        "regime": Regime.INDUSTRIAL_DESIGN.value,
        "governing_law": "The Designs Act, 2000",
        "finding": (
            "A novel, non-functional visual shape, configuration, pattern, or "
            "ornamentation of a bottle, packaging, applicator, or device — as "
            "applied to the finished article — can be registered as a design, "
            "separately from any patent or trademark protection on the same product."
        ),
        "requirement": "The design must be new/original and not previously published or used anywhere.",
        "not_covered": (
            "Purely functional features dictated solely by the article's function "
            "are not protectable as a design."
        ),
    }


# ----------------------------------------------------------------------
# Trade Secrets
# ----------------------------------------------------------------------

def trade_secret_guidance() -> dict:
    """Non-disclosure strategy for proprietary process know-how (no registration regime in India)."""

    return {
        "regime": Regime.TRADE_SECRET.value,
        "governing_law": (
            "No dedicated Indian trade secret statute — protected via contract "
            "(NDAs, confidentiality clauses) and common-law breach-of-confidence claims."
        ),
        "candidates": [
            "Proprietary processing steps and their sequence",
            "Extraction temperatures, pressures, and durations",
            "Precise ingredient proportions/ratios",
            "Supplier/sourcing relationships not otherwise disclosed",
        ],
        "recommendation": (
            "Use trade secret protection for process know-how you do NOT want to "
            "disclose in a patent specification (which becomes public). This is "
            "mutually exclusive with patenting the same specific detail — a patent "
            "requires enabling disclosure, a trade secret requires it stay confidential."
        ),
    }


# ----------------------------------------------------------------------
# Copyright
# ----------------------------------------------------------------------

def copyright_guidance() -> dict:
    """Copyright Act, 1957 protectable assets for an Ayurvedic business."""

    return {
        "regime": Regime.COPYRIGHT.value,
        "governing_law": "The Copyright Act, 1957",
        "protectable_assets": [
            "Original formulation reference books / compiled texts (literary work)",
            "Branding brochures, packaging artwork, and label designs (artistic work)",
            "Website text and marketing copy (literary work)",
            "Proprietary software / algorithms, e.g. a formulation database (literary work, as source code)",
        ],
        "note": (
            "Copyright protects the specific expression (the text, artwork, or "
            "code), not the underlying formulation, method, or idea itself — that "
            "requires patent or trade secret protection instead."
        ),
    }


# ----------------------------------------------------------------------
# Plant Variety Protection (PPV&FR)
# ----------------------------------------------------------------------

class PlantVarietyCategory(str, Enum):
    EXTANT = "extant"
    FARMERS = "farmers"
    NOVEL = "novel"


def ppvfr_guidance(variety_category: PlantVarietyCategory | str) -> dict:
    """PPV&FR Act, 2001 registration category for a medicinal plant variety."""

    category = PlantVarietyCategory(variety_category)

    descriptions = {
        PlantVarietyCategory.EXTANT: (
            "An already-notified, farmers', or common-knowledge variety in "
            "existence at the time of the Act — registrable to record and protect "
            "existing rights, not as a novelty claim."
        ),
        PlantVarietyCategory.FARMERS: (
            "A variety traditionally cultivated and evolved by farmers, or a wild "
            "relative/landrace they have selected — registrable in the name of the "
            "farmer(s)/community, with benefit-sharing obligations for commercial use."
        ),
        PlantVarietyCategory.NOVEL: (
            "A new variety meeting Novelty, Distinctiveness, Uniformity, and "
            "Stability (NDUS) criteria — the closest PPV&FR analogue to patent "
            "novelty, registrable in the breeder's name with exclusive rights."
        ),
    }

    return {
        "regime": Regime.PPV_FR.value,
        "governing_law": "Protection of Plant Varieties and Farmers' Rights Act, 2001",
        "category": category.value,
        "finding": descriptions[category],
    }


def advise_regime(regime: Regime | str, **kwargs) -> dict:
    """Dispatch to the regime-specific guidance function by regime code."""

    regime = Regime(regime)

    dispatch = {
        Regime.PATENT: lambda: patent_guidance(),
        Regime.GEOGRAPHICAL_INDICATION: lambda: gi_guidance(),
        Regime.INDUSTRIAL_DESIGN: lambda: industrial_design_guidance(),
        Regime.TRADE_SECRET: lambda: trade_secret_guidance(),
        Regime.COPYRIGHT: lambda: copyright_guidance(),
        Regime.PPV_FR: lambda: ppvfr_guidance(**kwargs),
    }

    if regime == Regime.TRADEMARK:
        # Trademark has two independent sub-checks; run whichever kwargs support.
        result = {"regime": Regime.TRADEMARK.value}
        if "product_type" in kwargs:
            result["nice_class"] = trademark_nice_class(kwargs["product_type"])
        if "is_generic_or_descriptive_ayurvedic_term" in kwargs:
            result["distinctiveness"] = trademark_distinctiveness_risk(
                kwargs["is_generic_or_descriptive_ayurvedic_term"]
            )
        return result

    return dispatch[regime]()
