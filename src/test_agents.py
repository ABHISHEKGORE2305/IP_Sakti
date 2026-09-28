"""
Sanity checks for the Sprint 3/4 multi-agent pipeline (AgentState/graph,
supervisor routing incl. the Sprint 4 jurisdiction toggle, citation_agent,
confidence, and the Sprint 4 international market engine).

Deterministic checks only — no Gemini calls, no Qdrant dependency —
so this can run without any external services up.

Run with:
    PYTHONPATH=src python3 src/test_agents.py
"""

from agents import specialists
from agents.citation_agent import extract_citations, strip_unverified_citations, verify_citations
from agents.graph import supervisor_router
from agents.supervisor import route
from engines.intl_engine import (
    eu_market_pathway,
    gratk_disclosure_requirement,
    uk_market_pathway,
    us_market_pathway,
    uspto_patent_eligibility,
)
from agents.graph import input_sanitizer
from guardrails.confidence import evaluate_confidence
from guardrails.pii_sanitizer import sanitize_pii


def _header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# ----------------------------------------------------------------------
# supervisor.py
# ----------------------------------------------------------------------

_header("SUPERVISOR: domain routing")

cases = {
    "Do I need NBA Form I approval as a foreign company?": "abs_agent",
    "What FSSAI license do I need for an Ayurveda-Aahar supplement?": "reg_agent",
    "Can I register a trademark for my Ayurvedic brand?": "tm_gi_agent",
    "What is the process to file a PCT application in the US?": "intl_agent",
    "Is this an aggregation of known properties barred by Section 3(p)?": "patent_agent",
    "Completely unrelated query about nothing legal at all": "patent_agent",  # default
}

for query, expected in cases.items():
    result = route(query)
    assert expected in result["selected_agents"], (query, result)
    print(f"OK  {expected:<16} <- {query}")


# ----------------------------------------------------------------------
# citation_agent.py
# ----------------------------------------------------------------------

_header("CITATION AGENT: comma-in-document-name parsing")

answer = (
    "Per [The Patents Act, 1970, Section 3(p), p.10] this is barred. "
    "Also see [Fake Act, Section 99, p.1]."
)
sources = [{"document": "The Patents Act, 1970", "legal_reference": "Section 3(p)", "page": 10}]

citations = extract_citations(answer)
assert citations[0]["document"] == "The Patents Act, 1970", citations
assert citations[0]["reference"] == "Section 3(p)"
assert citations[0]["page"] == 10
print("Parsed:", citations)

report = verify_citations(answer, sources)
assert report["total_citations"] == 2
assert report["verified_citations"] == 1
assert report["citation_precision"] == 0.5
print("Verified:", report["verified_citations"], "/", report["total_citations"])

stripped = strip_unverified_citations(answer, report)
assert "Fake Act" not in stripped
assert "The Patents Act, 1970, Section 3(p), p.10" in stripped
print("Stripped:", stripped)

_header("CITATION AGENT: no citations at all -> zero precision")

report = verify_citations("This answer cites nothing.", sources)
assert report["total_citations"] == 0
assert report["citation_precision"] == 0.0
print("OK — uncited answer correctly scored as zero precision, not vacuous pass")


# ----------------------------------------------------------------------
# guardrails/confidence.py
# ----------------------------------------------------------------------

_header("CONFIDENCE: no retrieval results -> low / abstain")

report = evaluate_confidence("anything", [])
assert report["band"] == "low"
assert report["abstain"] is True
assert report["abstention_message"]
print("OK — empty retrieval abstains:", report["band"])

_header("CONFIDENCE: strong, dense, high-authority retrieval -> high")

strong_results = [
    {
        "reranker_score": 3.0,
        "authority_weight": 1.0,
        "text": "traditional knowledge section 3p patent invention aggregation",
    },
    {
        "reranker_score": 2.5,
        "authority_weight": 0.9,
        "text": "traditional knowledge patent aggregation known properties",
    },
]
report = evaluate_confidence("traditional knowledge patent aggregation", strong_results)
assert report["band"] == "high", report
print("OK — strong retrieval scores high:", report["band"], round(report["confidence"], 3))

_header("CONFIDENCE: unverified citation caps a high band at medium")

citation_report = {
    "citation_precision": 0.8,
    "has_unverified_citations": True,
}
report = evaluate_confidence(
    "traditional knowledge patent aggregation", strong_results, citation_report
)
assert report["band"] == "medium", report
print("OK — capped by unverified citation:", report["band"])

_header("CONFIDENCE: citation precision below 0.5 forces abstention")

citation_report = {"citation_precision": 0.3, "has_unverified_citations": True}
report = evaluate_confidence(
    "traditional knowledge patent aggregation", strong_results, citation_report
)
assert report["band"] == "low" and report["abstain"], report
print("OK — low citation precision forces abstention:", report["band"])


# ----------------------------------------------------------------------
# engines/intl_engine.py (Sprint 4)
# ----------------------------------------------------------------------

_header("INTL ENGINE: US botanical drug vs. dietary supplement routes")

pathway = us_market_pathway("botanical_drug")
assert pathway["governing_framework"] == "US FDA Botanical Drug Guidance (2016)"
pathway = us_market_pathway("dietary_supplement")
assert pathway["governing_framework"].startswith("Dietary Supplement")
print("OK — both US routes resolve with distinct governing frameworks")

_header("INTL ENGINE: EU THMPD 30/15-year traditional-use threshold")

eligible = eu_market_pathway("traditional_use", years_traditional_use=35, years_eu_use=20)
assert eligible["eligible"] is True
ineligible = eu_market_pathway("traditional_use", years_traditional_use=10, years_eu_use=5)
assert ineligible["eligible"] is False
print("OK — 35y/20y eligible, 10y/5y not")

_header("INTL ENGINE: EU Well-Established Use 10-year threshold")

report = eu_market_pathway("well_established_use", years_bibliographic_evidence=12)
assert report["eligible"] is True
print("OK —", report["facts"])

_header("INTL ENGINE: UK THR — general framework, no invented thresholds")

report = uk_market_pathway()
assert "MHRA" in report["governing_framework"]
assert "recommendation" in report and report["recommendation"]
print("OK —", report["governing_framework"])

_header("INTL ENGINE: USPTO Alice/Mayo eligibility")

report = uspto_patent_eligibility(
    claims_natural_product_as_is=True, claims_markedly_different_characteristics=False
)
assert report["risk"] == "high_risk"
report = uspto_patent_eligibility(
    claims_natural_product_as_is=False, claims_markedly_different_characteristics=True
)
assert report["risk"] == "conditional"
print("OK — bare natural-product claim high_risk, markedly-different claim conditional")

_header("INTL ENGINE: GRATK disclosure obligation")

report = gratk_disclosure_requirement(True)
assert report["applicable"] is True and report["recommendation"]
report = gratk_disclosure_requirement(False)
assert report["applicable"] is False
print("OK — disclosure triggers only when a genetic resource/TK basis is present")


# ----------------------------------------------------------------------
# agents/graph.py — Sprint 4 jurisdiction toggle & structured routing
# ----------------------------------------------------------------------

_header("GRAPH: target_market routes straight to intl_agent, bypassing keywords")

result = supervisor_router({
    "sanitized_query": "unrelated text with no domain keywords",
    "target_market": "US",
})
assert result["selected_agents"] == ["intl_agent"]
print("OK —", result["routing_reason"])

_header("GRAPH: jurisdiction=International defaults to intl_agent, not patent_agent")

result = supervisor_router({"sanitized_query": "no domain keywords here", "jurisdiction": "International"})
assert result["selected_agents"] == ["intl_agent"]
print("OK —", result["routing_reason"])

_header("GRAPH: jurisdiction=India (or unset) keeps the patent_agent default")

result = supervisor_router({"sanitized_query": "no domain keywords here", "jurisdiction": "India"})
assert result["selected_agents"] == ["patent_agent"]
result = supervisor_router({"sanitized_query": "no domain keywords here"})
assert result["selected_agents"] == ["patent_agent"]
print("OK — India/unset jurisdiction unaffected by the toggle")


# ----------------------------------------------------------------------
# guardrails/pii_sanitizer.py (Sprint 6)
# ----------------------------------------------------------------------

_header("PII SANITIZER: Aadhaar, PAN, phone, email, PIN code redacted")

cases = {
    "My Aadhaar is 1234 5678 9012, can I file a patent?": "aadhaar",
    "My PAN is ABCDE1234F and I need help with Section 3(p).": "pan",
    "Call me at 9876543210 about my formulation.": "phone",
    "Email me at test.user@example.com with the checklist.": "email",
    "I live in Neemuch, Madhya Pradesh 458441.": "pin_code",
}
for query, expected_type in cases.items():
    result = sanitize_pii(query)
    assert result["had_pii"], query
    assert any(r["type"] == expected_type for r in result["redactions"]), result
    print(f"OK  {expected_type:<10} <- {query}")

_header("PII SANITIZER: legitimate legal query is untouched")

clean = "What is Section 3(p) of the Patents Act, 1970?"
result = sanitize_pii(clean)
assert result["sanitized_text"] == clean
assert not result["had_pii"]
print("OK — no false positive on a plain statutory citation")

_header("GRAPH: input_sanitizer redacts PII and never stores the raw value in state")

state = input_sanitizer({"query": "My Aadhaar is 1234 5678 9012. What is Section 3(p)?"})
assert "[REDACTED-AADHAAR]" in state["sanitized_query"]
assert "1234" not in state["sanitized_query"]
assert state["pii_redactions"] == [{"type": "aadhaar"}]
assert "original" not in str(state["pii_redactions"])
print("OK — sanitized_query:", state["sanitized_query"])
print("OK — pii_redactions carries only the type:", state["pii_redactions"])


# ----------------------------------------------------------------------
# specialists.py: every specialist wired to its Sprint 2/4 engine
# (audit finding: only classifier_agent/intl_agent were wired before;
# patent_agent/tm_gi_agent/abs_agent/reg_agent were pure RAG-only
# despite tk_engine/ipr_router/abs_engine/reg_engine already existing)
# ----------------------------------------------------------------------

_header("SPECIALISTS: patent_agent runs tk_engine when tk_inputs given")

result = specialists.patent_agent({"tk_inputs": {"documented_in_classical_text": True}})
assert result["engine_results"]["tk_patentability"]["overall_risk"] == "barred"
assert result["draft_answer"] is None
print("OK — bypasses RAG entirely:", result["engine_results"]["tk_patentability"]["overall_risk"])

_header("SPECIALISTS: tm_gi_agent runs ipr_router when ipr_inputs given")

result = specialists.tm_gi_agent({
    "ipr_inputs": {"regime": "geographical_indication"},
})
assert "Navara Rice" in result["engine_results"]["ipr_guidance"]["examples"]
print("OK —", result["engine_results"]["ipr_guidance"]["governing_law"])

_header("SPECIALISTS: abs_agent runs abs_engine when abs_inputs given")

result = specialists.abs_agent({
    "abs_inputs": {"entity_type": "foreign_entity", "activity_type": "commercial_utilization"},
})
assert result["engine_results"]["abs_compliance"]["entity_classification"]["governing_section"] == "Section 3"
print("OK —", result["engine_results"]["abs_compliance"]["entity_classification"]["governing_section"])

_header("SPECIALISTS: reg_agent runs reg_engine when reg_inputs given")

result = specialists.reg_agent({"reg_inputs": {"product_category": "ayurveda_aahar"}})
regulators = {r["regulator"] for r in result["engine_results"]["regulatory_pathway"]["crosswalk"]["regulators"]}
assert regulators == {"fssai"}
print("OK —", regulators)

_header("GRAPH: structured-input fast path routes every specialist correctly")

cases = [
    ({"sanitized_query": "x", "tk_inputs": {"documented_in_classical_text": True}}, "patent_agent"),
    ({"sanitized_query": "x", "ipr_inputs": {"regime": "copyright"}}, "tm_gi_agent"),
    ({"sanitized_query": "x", "abs_inputs": {"entity_type": "indian_company", "activity_type": "commercial_utilization"}}, "abs_agent"),
    ({"sanitized_query": "x", "reg_inputs": {"product_category": "general_food"}}, "reg_agent"),
]
for state, expected_agent in cases:
    result = supervisor_router(state)
    assert result["selected_agents"] == [expected_agent], result
    print(f"OK  {expected_agent:<14} <- {[k for k in state if k.endswith('_inputs')][0]}")

_header("SPECIALISTS: invalid enum-string inputs are caught, not left to crash")

# Audit finding: analyze_abs_compliance/classify_product convert their
# string inputs to EntityType/ActivityType/IntendedUse enums
# internally and raise ValueError for an unrecognised value - only
# TypeError was being caught, so a malformed request (e.g. a stale
# frontend dropdown value) would crash the whole graph run uncaught.

result = specialists.abs_agent({
    "abs_inputs": {"entity_type": "not_a_real_type", "activity_type": "commercial_utilization"},
})
assert result.get("error") and "not a valid EntityType" in result["error"]
print("OK — abs_agent: invalid entity_type handled, not raised:", result["error"])

result = specialists.abs_agent({
    "abs_inputs": {"entity_type": "indian_company", "activity_type": "not_a_real_activity"},
})
assert result.get("error") and "not a valid ActivityType" in result["error"]
print("OK — abs_agent: invalid activity_type handled, not raised:", result["error"])

result = specialists.classifier_agent({
    "sanitized_query": "x",
    "classification_inputs": {"in_first_schedule": False, "intended_use": "not_a_real_use"},
})
assert result.get("error") and "not a valid IntendedUse" in result["error"]
print("OK — classifier_agent: invalid intended_use handled, not raised:", result["error"])


print("\n" + "=" * 80)
print("ALL AGENT/GUARDRAIL SANITY CHECKS PASSED")
print("=" * 80)
