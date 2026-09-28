"""
Biological Diversity & Access and Benefit Sharing (ABS) Compliance Engine.

Deterministic rule engine over the Biological Diversity Act, 2002 (as
amended in 2023) entity/activity classification and National
Biodiversity Authority (NBA) / State Biodiversity Board (SBB) approval
requirements.

This module encodes the *structure* of the compliance pathway — who
needs which approval, in what order — as specified in the
implementation plan. It intentionally does not hardcode statutory
timelines or fees; those must be sourced from the ingested Biological
Diversity Rules text and cited from retrieval, not fabricated here.
"""

from enum import Enum


class EntityType(str, Enum):
    INDIAN_INDIVIDUAL = "indian_individual"
    INDIAN_COMPANY = "indian_company"    # wholly Indian-owned/controlled
    NRI = "nri"
    FOREIGN_ENTITY = "foreign_entity"    # includes foreign-controlled Indian entities


class ActivityType(str, Enum):
    COMMERCIAL_UTILIZATION = "commercial_utilization"
    NON_COMMERCIAL_RESEARCH = "non_commercial_research"
    BIO_SURVEY = "bio_survey"


_FOREIGN_ENTITY_TYPES = {EntityType.NRI, EntityType.FOREIGN_ENTITY}


def classify_entity(entity_type: EntityType | str) -> dict:
    """Section 3 (foreign) vs. Section 7 (Indian) jurisdiction determination."""

    entity_type = EntityType(entity_type)

    if entity_type in _FOREIGN_ENTITY_TYPES:
        return {
            "entity_type": entity_type.value,
            "governing_section": "Section 3",
            "finding": (
                "Foreign entities, NRIs, and body corporates/associations "
                "not registered in India, or having non-Indian "
                "participation in share capital or management, require "
                "prior National Biodiversity Authority (NBA) approval "
                "before obtaining any biological resource occurring in "
                "India for research, commercial utilisation, or "
                "bio-survey/bio-utilisation."
            ),
        }

    return {
        "entity_type": entity_type.value,
        "governing_section": "Section 7",
        "finding": (
            "Indian citizens and Indian-owned/controlled entities do not "
            "need NBA prior approval to access biological resources for "
            "their own use, but must give prior intimation to the State "
            "Biodiversity Board (SBB) before obtaining the resource for "
            "commercial utilisation."
        ),
    }


def sourcing_exemptions(
    is_normally_traded_commodity: bool,
    is_traditional_practitioner: bool,
) -> list[dict]:
    """Statutory exemptions from ABS approval requirements."""

    exemptions = []

    if is_normally_traded_commodity:
        exemptions.append({
            "exemption": "Normally Traded Commodity (NTC)",
            "finding": (
                "Biological resources notified as Normally Traded "
                "Commodities are exempt from NBA/SBB approval when "
                "accessed as a commodity, except where accessed for "
                "research, bio-survey, or commercial utilisation outside "
                "the scope of normal trade."
            ),
        })

    if is_traditional_practitioner:
        exemptions.append({
            "exemption": "Traditional Indian medicine practitioner (Vaidya)",
            "finding": (
                "Local people and communities — including growers and "
                "cultivators of biodiversity, and vaids and hakims "
                "practising indigenous medicine — are exempt from prior "
                "NBA/SBB approval for their traditional practice."
            ),
        })

    return exemptions


_FORM_CATALOG = {
    "form_i": {
        "form": "Form I",
        "purpose": "NBA approval for access to biological resources by a foreign entity",
        "governing_section": "Section 3",
        "trigger": (
            "entity_type is foreign/NRI and access to a biological "
            "resource occurring in India is sought"
        ),
    },
    "form_ii": {
        "form": "Form II",
        "purpose": "NBA approval for transfer of research results to a foreign entity",
        "governing_section": "Section 4",
        "trigger": (
            "research results (including specimens) obtained from Indian "
            "biological resources are to be transferred to a person/"
            "entity outside India"
        ),
    },
    "form_iii": {
        "form": "Form III",
        "purpose": (
            "NBA approval to apply for intellectual property rights based "
            "on research on a biological resource obtained from India"
        ),
        "governing_section": "Section 6",
        "trigger": (
            "an IPR application (e.g. a patent) is to be filed anywhere in "
            "the world claiming an invention based on biological material "
            "accessed from India"
        ),
        "note": (
            "Must be obtained BEFORE the patent is granted — approval can "
            "be sought after filing, but the patent must not proceed to "
            "grant without it."
        ),
    },
    "form_iv": {
        "form": "Form IV",
        "purpose": (
            "NBA approval for third-party transfer of biological "
            "resources/knowledge already accessed"
        ),
        "governing_section": "Section 20",
        "trigger": (
            "biological resources or associated knowledge already "
            "accessed under NBA approval are to be transferred to a third party"
        ),
    },
}


def required_approvals(
    entity_type: EntityType | str,
    seeking_ipr_on_biological_invention: bool = False,
    transferring_results_to_foreign_entity: bool = False,
    transferring_resource_to_third_party: bool = False,
) -> list[dict]:
    """Determine which NBA Forms (I-IV) apply."""

    entity_type = EntityType(entity_type)

    approvals = []

    if entity_type in _FOREIGN_ENTITY_TYPES:
        approvals.append(dict(_FORM_CATALOG["form_i"]))

    if transferring_results_to_foreign_entity:
        approvals.append(dict(_FORM_CATALOG["form_ii"]))

    if seeking_ipr_on_biological_invention:
        approvals.append(dict(_FORM_CATALOG["form_iii"]))

    if transferring_resource_to_third_party:
        approvals.append(dict(_FORM_CATALOG["form_iv"]))

    return approvals


def sbb_intimation_required(
    entity_type: EntityType | str,
    activity_type: ActivityType | str,
) -> dict:
    """State Biodiversity Board prior-intimation requirement for Indian commercial actors."""

    entity_type = EntityType(entity_type)
    activity_type = ActivityType(activity_type)

    if (
        entity_type not in _FOREIGN_ENTITY_TYPES
        and activity_type == ActivityType.COMMERCIAL_UTILIZATION
    ):
        return {
            "required": True,
            "finding": (
                "Indian citizens/entities undertaking commercial "
                "utilisation of biological resources must give prior "
                "intimation to the State Biodiversity Board (SBB) of the "
                "state where the resource is accessed."
            ),
        }

    return {
        "required": False,
        "finding": (
            "SBB prior intimation applies specifically to commercial "
            "utilisation by Indian entities; it is not triggered on these facts."
        ),
    }


def analyze_abs_compliance(
    entity_type: EntityType | str,
    activity_type: ActivityType | str,
    is_normally_traded_commodity: bool = False,
    is_traditional_practitioner: bool = False,
    seeking_ipr_on_biological_invention: bool = False,
    transferring_results_to_foreign_entity: bool = False,
    transferring_resource_to_third_party: bool = False,
) -> dict:
    """
    Run the full ABS compliance analysis and return an interactive,
    filing-ordered checklist: entity classification, applicable
    exemptions, required NBA Form approvals, and SBB intimation status.
    """

    entity_classification = classify_entity(entity_type)
    exemptions = sourcing_exemptions(
        is_normally_traded_commodity, is_traditional_practitioner
    )
    approvals = required_approvals(
        entity_type,
        seeking_ipr_on_biological_invention,
        transferring_results_to_foreign_entity,
        transferring_resource_to_third_party,
    )
    sbb = sbb_intimation_required(entity_type, activity_type)

    checklist = []

    if exemptions:
        checklist.append(
            "Confirm and document the applicable exemption(s) before "
            "proceeding: " + "; ".join(e["exemption"] for e in exemptions)
        )

    for approval in approvals:
        checklist.append(f"File NBA {approval['form']} — {approval['purpose']}.")

    if sbb["required"]:
        checklist.append("Submit prior intimation to the State Biodiversity Board (SBB).")

    if seeking_ipr_on_biological_invention:
        checklist.append(
            "Do not allow the patent to proceed to grant until Form III "
            "approval is obtained — Section 6 approval must precede grant, "
            "not merely filing."
        )

    if not checklist:
        checklist.append(
            "No NBA/SBB approval identified as required on these facts — "
            "re-verify against the current Biological Diversity Rules "
            "before proceeding."
        )

    return {
        "entity_classification": entity_classification,
        "exemptions": exemptions,
        "required_approvals": approvals,
        "sbb_intimation": sbb,
        "compliance_checklist": checklist,
    }
