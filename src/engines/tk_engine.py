"""
Traditional Knowledge & Section 3(p) Patentability Analysis Engine.

Analyzes an innovation claim against the traditional-knowledge-specific
patent exclusions in the Indian Patents Act, 1970:

    Section 3(p)    — traditional knowledge / aggregation of known properties
    Section 3(e)    — mere admixture of known substances
    Section 3(d)    — new use of a known substance
    Section 2(1)(j) — "invention" (novelty + inventive step), applied here
                       to novel extraction/isolation processes

This is a deterministic rule engine over structured facts about the
claim; it does not itself search the corpus or TKDL — callers should
establish the facts first (e.g. via retrieval, TKDL search, or user
input) and pass them in.
"""

from enum import Enum


class Risk(str, Enum):
    BARRED = "barred"              # statutory exclusion applies — essentially unpatentable
    HIGH_RISK = "high_risk"        # likely excluded absent strong differentiation
    CONDITIONAL = "conditional"    # patentable only if specific evidence is on record
    CLEAR = "clear"                # statutory exclusion does not appear to apply


def analyze_section_3p(documented_in_classical_text: bool) -> dict:
    """Section 3(p): traditional knowledge / aggregation of known properties."""

    if documented_in_classical_text:
        return {
            "section": "Section 3(p)",
            "risk": Risk.BARRED,
            "finding": (
                "The formulation is documented traditional knowledge, or an "
                "aggregation or duplication of known properties of "
                "traditionally known components. Section 3(p) squarely "
                "excludes it from patentability as claimed."
            ),
            "recommendation": (
                "Do not claim the classical formulation itself. Redirect "
                "claims to a genuinely novel element — a process, an "
                "isolated active molecule with a demonstrated new or "
                "enhanced property, or a new therapeutic use — that is not "
                "disclosed in the classical text."
            ),
        }

    return {
        "section": "Section 3(p)",
        "risk": Risk.CLEAR,
        "finding": (
            "No classical-text disclosure identified for this formulation "
            "as claimed; Section 3(p) does not appear to bar the claim on "
            "its face."
        ),
        "recommendation": (
            "Conduct a TKDL and classical-literature prior art search to "
            "confirm no undisclosed traditional-knowledge anticipation "
            "exists before filing."
        ),
    }


def analyze_section_3e(
    is_combination_of_known_herbs: bool,
    has_synergistic_data: bool,
) -> dict:
    """Section 3(e): mere admixture vs. synergistic interaction."""

    if not is_combination_of_known_herbs:
        return {
            "section": "Section 3(e)",
            "risk": Risk.CLEAR,
            "finding": "Not a combination of known substances; Section 3(e) is not implicated.",
            "recommendation": None,
        }

    if has_synergistic_data:
        return {
            "section": "Section 3(e)",
            "risk": Risk.CONDITIONAL,
            "finding": (
                "A combination of known herbs is presumed to be a mere "
                "admixture under Section 3(e), but documented synergistic "
                "data (e.g. isobologram analysis, enhanced bioavailability, "
                "or efficacy surprising to a person skilled in the art) can "
                "rebut the presumption."
            ),
            "recommendation": (
                "Ensure the specification explicitly presents the synergy "
                "data (quantified, not merely additive) and frame the claims "
                "around the surprising combined effect, not the individual "
                "components."
            ),
        }

    return {
        "section": "Section 3(e)",
        "risk": Risk.HIGH_RISK,
        "finding": (
            "A combination of known herbs without documented synergistic "
            "data is presumed a mere admixture — the properties are "
            "presumed to be a simple aggregation of the components' known "
            "properties, which Section 3(e) excludes."
        ),
        "recommendation": (
            "Generate experimental synergy data (e.g. isobolographic "
            "analysis) before filing, or reframe the claim around a "
            "non-admixture innovation, such as a novel process or a "
            "ratio-specific unexpected effect."
        ),
    }


def analyze_process_patent_eligibility(
    is_novel_extraction_process: bool,
    extraction_method_is_standard: bool,
) -> dict:
    """Section 2(1)(j): novel extraction/isolation process patent eligibility."""

    if extraction_method_is_standard:
        return {
            "section": "Section 2(1)(j)",
            "risk": Risk.HIGH_RISK,
            "finding": (
                "The extraction/isolation method matches a standard "
                "classical Ayurvedic process (e.g. Swarasa, Kwatha, Sneha "
                "Kalpana). Standard processes are not novel or inventive "
                "within the meaning of Section 2(1)(j) and will not support "
                "a process claim."
            ),
            "recommendation": (
                "Identify specific novel process parameters — e.g. "
                "temperature, pressure, solvent system, or purification "
                "steps — that depart from the standard method and produce a "
                "technical advance."
            ),
        }

    if is_novel_extraction_process:
        return {
            "section": "Section 2(1)(j)",
            "risk": Risk.CONDITIONAL,
            "finding": (
                "A non-standard extraction/isolation process may satisfy "
                "the 'invention' definition — novelty, inventive step, and "
                "industrial application — under Section 2(1)(j), provided "
                "the process parameters are demonstrably novel and non-obvious."
            ),
            "recommendation": (
                "Document the specific novel process parameters and any "
                "unexpected yield, purity, or activity improvement over the "
                "standard method to support the inventive step argument."
            ),
        }

    return {
        "section": "Section 2(1)(j)",
        "risk": Risk.CLEAR,
        "finding": (
            "No process claim asserted; the Section 2(1)(j) "
            "process-eligibility analysis is not applicable."
        ),
        "recommendation": None,
    }


def analyze_section_3d(
    is_new_therapeutic_use_of_known_substance: bool,
    enhanced_efficacy_demonstrated: bool,
) -> dict:
    """Section 3(d): new use / new form of a known substance."""

    if not is_new_therapeutic_use_of_known_substance:
        return {
            "section": "Section 3(d)",
            "risk": Risk.CLEAR,
            "finding": "Not a new use of a known substance; Section 3(d) is not implicated.",
            "recommendation": None,
        }

    if enhanced_efficacy_demonstrated:
        return {
            "section": "Section 3(d)",
            "risk": Risk.CONDITIONAL,
            "finding": (
                "A new therapeutic use of a known traditional plant/"
                "substance is patentable under Section 3(d) only on proof of "
                "enhancement of the known efficacy — comparative data "
                "against the known use/form is essential."
            ),
            "recommendation": (
                "Present head-to-head comparative efficacy data against the "
                "known substance/use in the specification, not merely a new "
                "indication claim."
            ),
        }

    return {
        "section": "Section 3(d)",
        "risk": Risk.HIGH_RISK,
        "finding": (
            "The mere discovery of a new use for a known substance, "
            "without demonstrated enhancement of known efficacy, falls "
            "within the Section 3(d) exclusion."
        ),
        "recommendation": (
            "Generate and disclose comparative efficacy data before "
            "filing — the claim as currently framed is likely to be "
            "rejected under Section 3(d)."
        ),
    }


def tkdl_mitigation_strategy(cited_in_tkdl: bool) -> dict:
    """Guidance for distinguishing claims from a TKDL prior-art citation."""

    if not cited_in_tkdl:
        return {
            "topic": "TKDL Prior Art Mitigation",
            "finding": "No TKDL citation identified for this claim on the facts given.",
            "recommendation": (
                "Run a TKDL search (via the Patent Office's TKDL access "
                "arrangement) before filing, to rule out an undisclosed citation."
            ),
        }

    return {
        "topic": "TKDL Prior Art Mitigation",
        "finding": (
            "A TKDL citation has been identified against this claim. TKDL "
            "entries document traditional knowledge and will be cited by "
            "the Examiner as prior art / Section 3(p) evidence."
        ),
        "recommendation": (
            "Distinguish the claim from the TKDL disclosure by: (1) "
            "narrowing claims to a specific novel process, isolated "
            "compound, or quantified synergy not disclosed in the TKDL "
            "entry; (2) submitting a technical rebuttal showing the claimed "
            "subject matter is not anticipated by, and involves an "
            "inventive step over, the cited traditional knowledge; and (3) "
            "avoiding claim language that reads directly on the classical "
            "formulation or use described in the TKDL entry."
        ),
    }


_RISK_PRECEDENCE = [Risk.BARRED, Risk.HIGH_RISK, Risk.CONDITIONAL, Risk.CLEAR]


def analyze_tk_patentability(
    documented_in_classical_text: bool = False,
    is_combination_of_known_herbs: bool = False,
    has_synergistic_data: bool = False,
    is_novel_extraction_process: bool = False,
    extraction_method_is_standard: bool = False,
    is_new_therapeutic_use_of_known_substance: bool = False,
    enhanced_efficacy_demonstrated: bool = False,
    cited_in_tkdl: bool = False,
) -> dict:
    """
    Run the full Section 3(p)/3(e)/3(d)/2(1)(j) traditional-knowledge
    patentability analysis for an innovation claim and return a combined
    report plus an overall risk rating (the worst risk across the four
    provisions).
    """

    findings = [
        analyze_section_3p(documented_in_classical_text),
        analyze_section_3e(is_combination_of_known_herbs, has_synergistic_data),
        analyze_process_patent_eligibility(
            is_novel_extraction_process, extraction_method_is_standard
        ),
        analyze_section_3d(
            is_new_therapeutic_use_of_known_substance,
            enhanced_efficacy_demonstrated,
        ),
    ]

    risks = {f["risk"] for f in findings}
    overall_risk = next(r for r in _RISK_PRECEDENCE if r in risks)

    # Normalise each finding's `risk` from the Risk enum to its plain
    # string value - Python 3.11+ changed str-mixin Enum.__str__() to
    # print "Risk.BARRED" instead of "barred", which otherwise leaks
    # into every rendered/serialized engine_results output (API
    # responses, agents.graph._format_engine_results, etc).
    for finding in findings:
        finding["risk"] = finding["risk"].value

    return {
        "overall_risk": overall_risk.value,
        "findings": findings,
        "tkdl_mitigation": tkdl_mitigation_strategy(cited_in_tkdl),
    }
