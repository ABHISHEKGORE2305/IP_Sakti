"""
Ayurvedic Product Classification Engine.

Deterministic decision tree that establishes the statutory product
identity of an Ayurvedic formulation, per the Drugs & Cosmetics Act,
1940 (Chapter IVA) and the FSSAI (Ayurveda Aahar) Regulations, 2022.

    Start -> Q1: In First Schedule authoritative texts?
      Yes -> Q2: Formulation modified or changed?
        Unchanged -> Classical Ayurvedic Medicine (D&C Act Sec 3(a))
        Modified   -> Patent or Proprietary Medicine (D&C Act Sec 3(h))
      No  -> Q3: Claims & intended use?
        Therapeutic / cure / disease treatment -> New Ayurvedic Drug / Phytopharmaceutical
        Nutritional / dietary supplement       -> Ayurveda-Aahar (FSSAI 2022)
        General food / beverage                -> General Food (FSSAI)
        Topical / beautification / cleansing   -> Ayurvedic Cosmetic (D&C Act Rules)
"""

from enum import Enum


class IntendedUse(str, Enum):
    THERAPEUTIC = "therapeutic"
    NUTRITIONAL = "nutritional"
    GENERAL_FOOD = "general_food"
    TOPICAL = "topical"


class ProductCategory(str, Enum):
    CLASSICAL_AYURVEDIC_MEDICINE = "classical_ayurvedic_medicine"
    PATENT_OR_PROPRIETARY_MEDICINE = "patent_or_proprietary_medicine"
    NEW_AYURVEDIC_DRUG = "new_ayurvedic_drug"
    AYURVEDA_AAHAR = "ayurveda_aahar"
    GENERAL_FOOD = "general_food"
    AYURVEDIC_COSMETIC = "ayurvedic_cosmetic"


class ClassificationError(ValueError):
    pass


_CLASSIFICATION_TABLE = {

    ProductCategory.CLASSICAL_AYURVEDIC_MEDICINE: {
        "label": "Classical Ayurvedic Medicine",
        "statutory_basis": "Drugs and Cosmetics Act, 1940 — Section 3(a)",
        "primary_regulator": "State Licensing Authority (AYUSH)",
        "licensing_route": [
            "Form 24D — manufacturing licence for classical / patent & "
            "proprietary Ayurvedic medicines",
            "No Form 25D safety/efficacy dossier required — the formulation "
            "is documented, unchanged, in a First Schedule authoritative text",
        ],
        "clinical_evidence": (
            "None beyond classical-text citation — safety/efficacy is "
            "presumed from documented traditional use per the First Schedule "
            "authoritative text."
        ),
        "ip_regimes": {
            "patent": (
                "Not available — the classical formulation is prior art / "
                "traditional knowledge (Patents Act Section 3(p) bars any "
                "claim over it as such)."
            ),
            "trademark": "Available for the brand name only (NICE Class 5), not the formula.",
            "geographical_indication": "Possible if tied to a specific region/community.",
            "trade_secret": "Not applicable — the formulation is published in a classical text.",
        },
        "abs_biodiversity_triggers": (
            "Low — but sourcing the classical ingredients still triggers "
            "Biological Diversity Act obligations if resources are accessed "
            "for commercial use."
        ),
    },

    ProductCategory.PATENT_OR_PROPRIETARY_MEDICINE: {
        "label": "Patent or Proprietary Medicine",
        "statutory_basis": "Drugs and Cosmetics Act, 1940 — Section 3(h)",
        "primary_regulator": "State Licensing Authority (AYUSH)",
        "licensing_route": [
            "Form 25D — safety and efficacy proof (literature-backed, or "
            "clinical if the modification is substantial) for the modified formulation",
            "Form 24D — manufacturing licence",
        ],
        "clinical_evidence": (
            "Rule 158B: proof of safety/efficacy required — may be "
            "satisfied by citing published Ayurvedic literature for each "
            "modified ingredient/process, or by clinical data if the "
            "modification is substantial."
        ),
        "ip_regimes": {
            "patent": (
                "Possible for the modified formulation/process if the "
                "modification produces a demonstrable, non-obvious, "
                "synergistic effect beyond the classical formulation (see the "
                "Section 3(e) admixture analysis)."
            ),
            "trademark": "Available (NICE Class 5).",
            "geographical_indication": "Not typically applicable to a modified proprietary product.",
            "trade_secret": "Available for the specific modification/process parameters.",
        },
        "abs_biodiversity_triggers": (
            "Moderate to High — modified formulations often involve new "
            "sourcing, extraction, or novel biological material use; ABS Form "
            "III is mandatory before any patent filing on the biological "
            "invention."
        ),
    },

    ProductCategory.NEW_AYURVEDIC_DRUG: {
        "label": "New Ayurvedic Drug / Phytopharmaceutical",
        "statutory_basis": (
            "Drugs and Cosmetics Act, 1940 — Chapter IVA / "
            "phytopharmaceutical drug provisions"
        ),
        "primary_regulator": (
            "CDSCO (phytopharmaceuticals) / Ministry of AYUSH (new Ayurvedic drugs)"
        ),
        "licensing_route": [
            "Form 25D, or the New Drugs and Clinical Trials Rules, 2019 route, "
            "depending on classification as a new Ayurvedic drug vs. a phytopharmaceutical",
            "Clinical trial approval where a phytopharmaceutical pathway applies",
        ],
        "clinical_evidence": (
            "Substantial — pre-clinical toxicology and clinical "
            "safety/efficacy data are required; literature citation alone is "
            "not sufficient for new therapeutic claims."
        ),
        "ip_regimes": {
            "patent": (
                "Strong candidate — a new therapeutic use / novel extract "
                "may satisfy novelty and inventive step, subject to Section "
                "3(d)/3(e)/3(p) scrutiny."
            ),
            "trademark": "Available (NICE Class 5).",
            "geographical_indication": "Not applicable.",
            "trade_secret": "Available for process/manufacturing know-how.",
        },
        "abs_biodiversity_triggers": (
            "High — novel extraction/isolation from biological resources "
            "triggers Biological Diversity Act Form I/III obligations before "
            "commercialisation or patent filing."
        ),
    },

    ProductCategory.AYURVEDA_AAHAR: {
        "label": "Ayurveda-Aahar (Nutritional / Dietary Supplement)",
        "statutory_basis": "FSSAI (Ayurveda Aahar) Regulations, 2022",
        "primary_regulator": "FSSAI",
        "licensing_route": [
            "FSSAI Central/State Licence, depending on production scale",
            "Product approval under the Ayurveda Aahar category (not a drug licence)",
        ],
        "clinical_evidence": (
            "Not required as a drug — must not carry disease "
            "prevention/cure/treatment claims, only structure/function or "
            "nutritional claims."
        ),
        "ip_regimes": {
            "patent": (
                "Possible only for a genuinely novel formulation/process, not "
                "the traditional recipe itself."
            ),
            "trademark": "Available (NICE Class 29/30/32, depending on the food form).",
            "geographical_indication": "Possible if tied to a specific region.",
            "trade_secret": "Available for proprietary blend ratios/process.",
        },
        "abs_biodiversity_triggers": (
            "Low to Moderate — standard Normally Traded Commodity (NTC) "
            "exemptions may apply."
        ),
    },

    ProductCategory.GENERAL_FOOD: {
        "label": "General Food / Beverage",
        "statutory_basis": "Food Safety and Standards Act, 2006",
        "primary_regulator": "FSSAI",
        "licensing_route": [
            "Standard FSSAI Central/State Licence",
        ],
        "clinical_evidence": "Not applicable — standard food safety compliance only.",
        "ip_regimes": {
            "patent": (
                "Not typically applicable, unless a novel food-processing "
                "technique is involved."
            ),
            "trademark": "Available (NICE Class 29/30/32).",
            "geographical_indication": "Possible if tied to a specific region.",
            "trade_secret": "Available for recipe/process.",
        },
        "abs_biodiversity_triggers": "Low — generally exempt as a Normally Traded Commodity.",
    },

    ProductCategory.AYURVEDIC_COSMETIC: {
        "label": "Ayurvedic Cosmetic",
        "statutory_basis": "Drugs and Cosmetics Act, 1940 — Cosmetic Rules",
        "primary_regulator": "State Licensing Authority (Cosmetics)",
        "licensing_route": [
            "Manufacturing licence for cosmetics under the D&C Rules",
            "BIS / product-standard compliance where applicable",
        ],
        "clinical_evidence": (
            "Safety data (e.g. patch testing / toxicology) required; "
            "therapeutic claims are not permitted without drug licensing."
        ),
        "ip_regimes": {
            "patent": "Possible for a novel formulation or delivery mechanism.",
            "trademark": "Available (NICE Class 3).",
            "geographical_indication": "Not typically applicable.",
            "trade_secret": "Available for the formulation/process.",
            "industrial_design": "Available for novel packaging/applicator design.",
        },
        "abs_biodiversity_triggers": (
            "Moderate — biological ingredient sourcing for cosmetic use "
            "still triggers ABS obligations."
        ),
    },
}


def classify_product(
    in_first_schedule: bool,
    formulation_modified: bool | None = None,
    intended_use: IntendedUse | str | None = None,
) -> dict:
    """
    Run the statutory product classification decision tree.

    Args:
        in_first_schedule: Whether the formulation (ingredients,
            proportions, and method of preparation) is documented,
            unchanged, in one of the First Schedule authoritative
            Ayurvedic texts.
        formulation_modified: Required when in_first_schedule is True.
            Whether the ingredients, extracts, or dosage form have been
            changed from the classical text.
        intended_use: Required when in_first_schedule is False. One of
            "therapeutic", "nutritional", "general_food", "topical".

    Returns:
        The output contract: category, statutory_basis, primary_regulator,
        licensing_route, clinical_evidence, ip_regimes,
        abs_biodiversity_triggers, plus the decision path taken.
    """

    path = ["Q1: In First Schedule authoritative texts?"]

    if in_first_schedule:
        path.append("Yes")

        if formulation_modified is None:
            raise ClassificationError(
                "formulation_modified is required when in_first_schedule=True"
            )

        path.append("Q2: Formulation modified or changed?")

        if formulation_modified:
            path.append("Modified ingredients/extracts/dosage form")
            category = ProductCategory.PATENT_OR_PROPRIETARY_MEDICINE
        else:
            path.append("Unchanged")
            category = ProductCategory.CLASSICAL_AYURVEDIC_MEDICINE

    else:
        path.append("No")

        if intended_use is None:
            raise ClassificationError(
                "intended_use is required when in_first_schedule=False"
            )

        intended_use = IntendedUse(intended_use)
        path.append(f"Q3: Claims & intended use? -> {intended_use.value}")

        category = {
            IntendedUse.THERAPEUTIC: ProductCategory.NEW_AYURVEDIC_DRUG,
            IntendedUse.NUTRITIONAL: ProductCategory.AYURVEDA_AAHAR,
            IntendedUse.GENERAL_FOOD: ProductCategory.GENERAL_FOOD,
            IntendedUse.TOPICAL: ProductCategory.AYURVEDIC_COSMETIC,
        }[intended_use]

    result = dict(_CLASSIFICATION_TABLE[category])
    result["category"] = category.value
    result["classification_path"] = path

    return result
