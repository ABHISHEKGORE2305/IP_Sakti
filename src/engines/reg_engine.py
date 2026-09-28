"""
AYUSH / FSSAI / CDSCO Regulatory Cross-Walk Engine.

Given a product's statutory classification (see engines.classifier)
and whether therapeutic claims are being made in its marketing, this
engine determines the governing regulator(s), the licensing pathway,
and flags any Drugs and Magic Remedies (Objectionable Advertisements)
Act, 1954 (DMR(OA)) advertising risk from the claims used.
"""

from enum import Enum


class Regulator(str, Enum):
    AYUSH_STATE_LICENSING_AUTHORITY = "ayush_state_licensing_authority"
    CDSCO = "cdsco"
    FSSAI = "fssai"


_REGULATOR_BY_CATEGORY = {
    "classical_ayurvedic_medicine": [Regulator.AYUSH_STATE_LICENSING_AUTHORITY],
    "patent_or_proprietary_medicine": [Regulator.AYUSH_STATE_LICENSING_AUTHORITY],
    "new_ayurvedic_drug": [Regulator.AYUSH_STATE_LICENSING_AUTHORITY, Regulator.CDSCO],
    "ayurveda_aahar": [Regulator.FSSAI],
    "general_food": [Regulator.FSSAI],
    "ayurvedic_cosmetic": [Regulator.AYUSH_STATE_LICENSING_AUTHORITY],
}

_REGULATOR_DETAILS = {
    Regulator.AYUSH_STATE_LICENSING_AUTHORITY: {
        "name": "State Licensing Authority (AYUSH), under Ministry of AYUSH oversight",
        "governing_law": "Drugs and Cosmetics Act, 1940 (Chapter IVA) & Rules, 1945",
        "typical_forms": [
            "Form 24D (manufacturing licence)",
            "Form 25D (safety/efficacy proof, where applicable)",
        ],
    },
    Regulator.CDSCO: {
        "name": "Central Drugs Standard Control Organisation (CDSCO)",
        "governing_law": (
            "Drugs and Cosmetics Act, 1940 — phytopharmaceutical drug "
            "provisions; New Drugs and Clinical Trials Rules, 2019"
        ),
        "typical_forms": [
            "Clinical trial application",
            "New drug / phytopharmaceutical approval application",
        ],
    },
    Regulator.FSSAI: {
        "name": "Food Safety and Standards Authority of India (FSSAI)",
        "governing_law": (
            "Food Safety and Standards Act, 2006; FSSAI (Ayurveda Aahar) "
            "Regulations, 2022, where applicable"
        ),
        "typical_forms": [
            "FSSAI Central/State Licence application",
            "Product approval (Ayurveda Aahar category, where applicable)",
        ],
    },
}


def regulatory_crosswalk(product_category: str) -> dict:
    """Map a classifier.py product_category to its governing regulator(s)."""

    regulators = _REGULATOR_BY_CATEGORY.get(product_category)

    if regulators is None:
        return {
            "product_category": product_category,
            "regulators": [],
            "finding": (
                f"Unrecognised product category '{product_category}' — run "
                "engines.classifier.classify_product first to establish "
                "the statutory category."
            ),
        }

    detail = [
        dict(_REGULATOR_DETAILS[regulator], regulator=regulator.value)
        for regulator in regulators
    ]

    finding = (
        "This product category falls under a single regulator."
        if len(regulators) == 1
        else (
            "This product category straddles multiple regulators — dual "
            "compliance (or a jurisdictional determination of which "
            "regulator has primary authority) is required."
        )
    )

    return {
        "product_category": product_category,
        "regulators": detail,
        "finding": finding,
    }


_LICENSED_DRUG_CATEGORIES = {
    "classical_ayurvedic_medicine",
    "patent_or_proprietary_medicine",
    "new_ayurvedic_drug",
}


def advertising_compliance_check(
    makes_disease_cure_claim: bool,
    product_category: str,
) -> dict:
    """
    Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954 check.

    The DMR(OA) Act prohibits advertisements claiming that a product can
    diagnose, cure, mitigate, treat, or prevent specified diseases/
    disorders, regardless of which regulator otherwise governs the product.
    """

    if not makes_disease_cure_claim:
        return {
            "risk": "clear",
            "finding": "No disease-cure/prevention claim identified in the advertising copy.",
            "recommendation": None,
        }

    if product_category in _LICENSED_DRUG_CATEGORIES:
        return {
            "risk": "conditional",
            "finding": (
                "Disease-cure/prevention claims are being made for a "
                "licensed Ayurvedic drug. Such claims must stay within the "
                "approved labelling/therapeutic indications for the "
                "licence and must not fall within the DMR(OA) Act's "
                "scheduled-disease restrictions or use prohibited language "
                "(e.g. 'guaranteed cure', 'miracle')."
            ),
            "recommendation": (
                "Have advertising copy reviewed against the DMR(OA) Act "
                "and the product's approved licence indications before publication."
            ),
        }

    return {
        "risk": "high_risk",
        "finding": (
            "A disease-cure/prevention claim is being made for a product "
            "classified outside the licensed-drug categories (e.g. a "
            "food, supplement, or cosmetic). Such claims are prohibited "
            "under the DMR(OA) Act and the applicable FSSAI/D&C Act "
            "labelling rules for this category, regardless of scientific merit."
        ),
        "recommendation": (
            "Remove the disease-cure/prevention language, or re-route the "
            "product through the appropriate drug-licensing pathway "
            "(new_ayurvedic_drug) before making such claims."
        ),
    }


def analyze_regulatory_pathway(
    product_category: str,
    makes_disease_cure_claim: bool = False,
) -> dict:
    """Combined AYUSH/FSSAI/CDSCO cross-walk plus DMR(OA) advertising check."""

    return {
        "crosswalk": regulatory_crosswalk(product_category),
        "advertising_compliance": advertising_compliance_check(
            makes_disease_cure_claim, product_category
        ),
    }
