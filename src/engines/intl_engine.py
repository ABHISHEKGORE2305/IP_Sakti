"""
International IP & Export Market Access Engine.

Deterministic rule engine for market-specific regulatory pathways
(USA, EU, UK) and the GRATK genetic-resource/traditional-knowledge
disclosure obligation that applies to international patent filings
regardless of market.

This encodes the *structure* of each pathway exactly as specified in
implementation_plan.md Phase 4.2 (the only market facts available
without the underlying treaty/guidance text). It does not replace
corpus-backed RAG grounding — ingesting the WIPO GRATK Treaty, Nagoya
Protocol, and US FDA Botanical Guidance into data/raw/international/
is a separate, still-blocked Sprint 4 item (no source PDFs supplied yet).
"""

from enum import Enum


class Market(str, Enum):
    US = "US"
    EU = "EU"
    UK = "UK"


# ----------------------------------------------------------------------
# United States
# ----------------------------------------------------------------------

class USRoute(str, Enum):
    BOTANICAL_DRUG = "botanical_drug"
    DIETARY_SUPPLEMENT = "dietary_supplement"


def us_market_pathway(route: USRoute | str) -> dict:
    """FDA route determination for a botanical/Ayurvedic product entering the US market."""

    route = USRoute(route)

    if route == USRoute.BOTANICAL_DRUG:
        return {
            "market": Market.US.value,
            "route": route.value,
            "governing_framework": "US FDA Botanical Drug Guidance (2016)",
            "requirements": [
                "Multi-batch chemical fingerprinting of the botanical raw material/extract",
                "Documented raw-material sourcing consistency across batches",
                "Phase I-III clinical trial pathway — single-molecule isolation is NOT "
                "required, unlike a conventional new chemical entity",
            ],
            "finding": (
                "This route permits filing a botanical drug as a defined, standardized "
                "mixture rather than requiring isolation of a single active compound — "
                "the tradeoff is that batch-to-batch chemical consistency must be "
                "rigorously documented."
            ),
            "recommendation": None,
        }

    return {
        "market": Market.US.value,
        "route": route.value,
        "governing_framework": "Dietary Supplement Health and Education Act (DSHEA), 1994",
        "requirements": [
            "Structure/function claims only — disease diagnosis/cure/treatment/"
            "prevention claims are NOT permitted on this route (that requires the "
            "botanical drug pathway)",
            "New Dietary Ingredient (NDI) notification to FDA if the ingredient was "
            "not marketed in the US before October 15, 1994",
            "Current Good Manufacturing Practice compliance under 21 CFR Part 111",
        ],
        "finding": (
            "Faster and cheaper to market than the botanical drug route, but claims "
            "are legally constrained to structure/function language, not therapeutic claims."
        ),
        "recommendation": None,
    }


def uspto_patent_eligibility(
    claims_natural_product_as_is: bool,
    claims_markedly_different_characteristics: bool,
) -> dict:
    """
    35 U.S.C. § 101 subject-matter eligibility for a natural-product-derived
    claim, under the Alice/Mayo framework (Mayo v. Prometheus / Association
    for Molecular Pathology v. Myriad Genetics).
    """

    if claims_natural_product_as_is and not claims_markedly_different_characteristics:
        return {
            "market": Market.US.value,
            "topic": "USPTO Subject Matter Eligibility (35 U.S.C. § 101)",
            "risk": "high_risk",
            "finding": (
                "A claim to a natural product in a form not markedly different from "
                "how it exists in nature is a judicial exception (a 'product of "
                "nature') under the Alice/Mayo framework, and is not eligible subject "
                "matter regardless of novelty or inventive step under India's Section 2(1)(j)."
            ),
            "recommendation": (
                "Reframe the claim around a markedly different characteristic — e.g. "
                "an isolated/purified compound with a new utility, a synthetic "
                "analogue, a novel formulation, or a specific method of use/process — "
                "rather than the natural product itself."
            ),
        }

    return {
        "market": Market.US.value,
        "topic": "USPTO Subject Matter Eligibility (35 U.S.C. § 101)",
        "risk": "conditional",
        "finding": (
            "A claim reciting markedly different characteristics from the natural "
            "product is more likely to survive the Alice/Mayo two-step eligibility "
            "analysis, but eligibility is only step one — novelty (§102) and "
            "non-obviousness (§103) must still be separately satisfied."
        ),
        "recommendation": (
            "Document the specific markedly different characteristic in the "
            "specification and claims, and conduct a separate US prior-art search "
            "for novelty/obviousness — eligibility alone does not guarantee grant."
        ),
    }


# ----------------------------------------------------------------------
# European Union
# ----------------------------------------------------------------------

class EUEvidenceBasis(str, Enum):
    TRADITIONAL_USE = "traditional_use"
    WELL_ESTABLISHED_USE = "well_established_use"


def eu_market_pathway(
    evidence_basis: EUEvidenceBasis | str,
    years_traditional_use: int = 0,
    years_eu_use: int = 0,
    years_bibliographic_evidence: int = 0,
) -> dict:
    """EU market access route determination under Directive 2004/24/EC (THMPD)."""

    evidence_basis = EUEvidenceBasis(evidence_basis)

    if evidence_basis == EUEvidenceBasis.TRADITIONAL_USE:

        meets_total = years_traditional_use >= 30
        meets_eu = years_eu_use >= 15
        eligible = meets_total and meets_eu

        return {
            "market": Market.EU.value,
            "route": evidence_basis.value,
            "governing_framework": (
                "Traditional Herbal Medicinal Products Directive (THMPD), 2004/24/EC"
            ),
            "requirement": (
                "At least 30 years of documented traditional use, including at "
                "least 15 years within the European Union."
            ),
            "facts": {
                "years_traditional_use": years_traditional_use,
                "years_eu_use": years_eu_use,
            },
            "eligible": eligible,
            "finding": (
                "Traditional-use evidence meets the THMPD threshold."
                if eligible else
                "Traditional-use evidence does NOT yet meet the THMPD threshold "
                f"(need >=30 years total and >=15 years in the EU; have "
                f"{years_traditional_use} total / {years_eu_use} in the EU)."
            ),
            "recommendation": None if eligible else (
                "Consider the Well-Established Use route instead if 10+ years of EU "
                "clinical bibliographic evidence exists, or accumulate further "
                "documented traditional-use history before filing."
            ),
        }

    eligible = years_bibliographic_evidence >= 10

    return {
        "market": Market.EU.value,
        "route": evidence_basis.value,
        "governing_framework": "Well-Established Use route (Directive 2001/83/EC, Article 10a)",
        "requirement": (
            "At least 10 years of clinical bibliographic evidence of well-established "
            "use with recognised efficacy and an acceptable safety level within the EU."
        ),
        "facts": {"years_bibliographic_evidence": years_bibliographic_evidence},
        "eligible": eligible,
        "finding": (
            "Bibliographic evidence meets the well-established-use threshold."
            if eligible else
            "Bibliographic evidence does NOT yet meet the well-established-use "
            f"threshold (need >=10 years; have {years_bibliographic_evidence})."
        ),
        "recommendation": None if eligible else (
            "Consider the Traditional Use route instead if 30+ years of traditional "
            "use (15+ in the EU) can be documented, or accumulate further "
            "bibliographic evidence before filing."
        ),
    }


# ----------------------------------------------------------------------
# United Kingdom
# ----------------------------------------------------------------------

def uk_market_pathway() -> dict:
    """
    UK market access route for a traditional herbal medicinal product.

    The MHRA's Traditional Herbal Registration (THR) scheme was built
    on the same traditional-use evidentiary model as the EU THMPD and
    continues to apply post-Brexit under retained UK law. The
    implementation plan does not specify UK-particular thresholds
    beyond naming the scheme, so — unlike us_market_pathway/
    eu_market_pathway — this function states the general framework
    only, rather than inventing figures the plan doesn't provide.
    """

    return {
        "market": Market.UK.value,
        "governing_framework": "MHRA Traditional Herbal Registration (THR) scheme",
        "finding": (
            "The UK operates its own Traditional Herbal Registration scheme through "
            "the MHRA, modelled on the same traditional-use evidentiary approach as "
            "the EU THMPD. Product-specific evidentiary thresholds should be "
            "confirmed directly against current MHRA guidance rather than assumed "
            "to be identical to the EU figures."
        ),
        "recommendation": (
            "Consult the MHRA's current THR guidance for the specific traditional-use "
            "evidence period and safety-data requirements applicable to this product "
            "before relying on any EU-derived assumption."
        ),
    }


# ----------------------------------------------------------------------
# GRATK cross-market disclosure obligation
# ----------------------------------------------------------------------

def gratk_disclosure_requirement(uses_genetic_resource_or_traditional_knowledge: bool) -> dict:
    """
    WIPO Treaty on Intellectual Property, Genetic Resources and
    Associated Traditional Knowledge (GRATK, 2024) — mandatory
    disclosure obligation, applicable to patent filings in any
    contracting-state market, not only India.
    """

    if not uses_genetic_resource_or_traditional_knowledge:
        return {
            "topic": "GRATK Disclosure Obligation",
            "applicable": False,
            "finding": (
                "The claimed invention does not appear to be based on genetic "
                "resources or associated traditional knowledge; the GRATK "
                "disclosure obligation is not triggered."
            ),
            "recommendation": None,
        }

    return {
        "topic": "GRATK Disclosure Obligation",
        "applicable": True,
        "finding": (
            "Where a claimed invention is based on genetic resources and/or "
            "associated traditional knowledge, GRATK requires each contracting "
            "party's patent system to mandate disclosure of the country of "
            "origin (or source) of the genetic resources, and the indigenous "
            "peoples/local community that is the source of any associated "
            "traditional knowledge, where known to the applicant."
        ),
        "recommendation": (
            "Disclose the country of origin/source and, where applicable, the "
            "originating community in the patent application at filing — in every "
            "contracting-state jurisdiction where the application is filed, not "
            "only in India. Non-disclosure can be a ground for revocation/"
            "invalidation under national implementing law."
        ),
    }


def advise_market(market: Market | str, **kwargs) -> dict:
    """Dispatch to the market-specific pathway function by market code."""

    market = Market(market)

    if market == Market.US:
        return us_market_pathway(**kwargs)
    if market == Market.EU:
        return eu_market_pathway(**kwargs)
    return uk_market_pathway(**kwargs)
