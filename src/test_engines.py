"""
Sanity checks for the Sprint 2 domain intelligence engines
(classifier, tk_engine, abs_engine, reg_engine, ipr_router).

Run with:
    PYTHONPATH=src python3 src/test_engines.py
"""

from engines.classifier import classify_product, IntendedUse, ClassificationError
from engines.ipr_router import advise_regime, plan_ip_route
from engines.tk_engine import analyze_tk_patentability, misappropriation_risk
from engines.abs_engine import analyze_abs_compliance, EntityType, ActivityType
from engines.reg_engine import analyze_regulatory_pathway
from engines.knowledge_graph import build_graph


def _header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# ----------------------------------------------------------------------
# classifier.py
# ----------------------------------------------------------------------

_header("CLASSIFIER: unchanged classical formulation")
result = classify_product(in_first_schedule=True, formulation_modified=False)
assert result["category"] == "classical_ayurvedic_medicine"
print(result["label"], "->", result["classification_path"])

_header("CLASSIFIER: modified classical formulation")
result = classify_product(in_first_schedule=True, formulation_modified=True)
assert result["category"] == "patent_or_proprietary_medicine"
print(result["label"], "->", result["classification_path"])

_header("CLASSIFIER: new formulation, therapeutic claim")
result = classify_product(in_first_schedule=False, intended_use=IntendedUse.THERAPEUTIC)
assert result["category"] == "new_ayurvedic_drug"
print(result["label"], "->", result["classification_path"])

_header("CLASSIFIER: new formulation, dietary supplement")
result = classify_product(in_first_schedule=False, intended_use="nutritional")
assert result["category"] == "ayurveda_aahar"
print(result["label"], "->", result["classification_path"])

_header("CLASSIFIER: missing required input raises")
try:
    classify_product(in_first_schedule=True)
    raise AssertionError("expected ClassificationError")
except ClassificationError as exc:
    print("Correctly raised:", exc)


# ----------------------------------------------------------------------
# tk_engine.py
# ----------------------------------------------------------------------

_header("TK ENGINE: classical formulation, no differentiation (Section 3(p) bar)")
report = analyze_tk_patentability(documented_in_classical_text=True)
assert report["overall_risk"] == "barred"
for f in report["findings"]:
    print(f["section"], "->", f["risk"])

_header("TK ENGINE: novel synergistic combination with data")
report = analyze_tk_patentability(
    is_combination_of_known_herbs=True,
    has_synergistic_data=True,
)
assert report["overall_risk"] == "conditional"
for f in report["findings"]:
    print(f["section"], "->", f["risk"])

_header("TK ENGINE: novel non-standard extraction process")
report = analyze_tk_patentability(
    is_novel_extraction_process=True,
    extraction_method_is_standard=False,
)
assert report["overall_risk"] == "conditional"

_header("TK ENGINE: TKDL citation mitigation")
report = analyze_tk_patentability(cited_in_tkdl=True)
print(report["tkdl_mitigation"]["recommendation"][:120], "...")


# ----------------------------------------------------------------------
# abs_engine.py
# ----------------------------------------------------------------------

_header("ABS ENGINE: foreign entity seeking IPR on biological invention")
report = analyze_abs_compliance(
    entity_type=EntityType.FOREIGN_ENTITY,
    activity_type=ActivityType.COMMERCIAL_UTILIZATION,
    seeking_ipr_on_biological_invention=True,
)
assert report["entity_classification"]["governing_section"] == "Section 3"
forms = {a["form"] for a in report["required_approvals"]}
assert forms == {"Form I", "Form III"}
for step in report["compliance_checklist"]:
    print("-", step)

_header("ABS ENGINE: Indian company, commercial utilisation")
report = analyze_abs_compliance(
    entity_type=EntityType.INDIAN_COMPANY,
    activity_type=ActivityType.COMMERCIAL_UTILIZATION,
)
assert report["sbb_intimation"]["required"] is True
assert report["required_approvals"] == []
for step in report["compliance_checklist"]:
    print("-", step)

_header("ABS ENGINE: Vaidya exemption")
report = analyze_abs_compliance(
    entity_type=EntityType.INDIAN_INDIVIDUAL,
    activity_type=ActivityType.NON_COMMERCIAL_RESEARCH,
    is_traditional_practitioner=True,
)
assert report["exemptions"]
for step in report["compliance_checklist"]:
    print("-", step)


# ----------------------------------------------------------------------
# reg_engine.py
# ----------------------------------------------------------------------

_header("REG ENGINE: new Ayurvedic drug dual regulator")
report = analyze_regulatory_pathway("new_ayurvedic_drug")
regulators = {r["regulator"] for r in report["crosswalk"]["regulators"]}
assert regulators == {"ayush_state_licensing_authority", "cdsco"}
print(report["crosswalk"]["finding"])

_header("REG ENGINE: disease-cure claim on a food product (high risk)")
report = analyze_regulatory_pathway("general_food", makes_disease_cure_claim=True)
assert report["advertising_compliance"]["risk"] == "high_risk"
print(report["advertising_compliance"]["finding"])

_header("REG ENGINE: disease-cure claim on a licensed drug (conditional)")
report = analyze_regulatory_pathway(
    "classical_ayurvedic_medicine", makes_disease_cure_claim=True
)
assert report["advertising_compliance"]["risk"] == "conditional"
print(report["advertising_compliance"]["finding"])


# ----------------------------------------------------------------------
# ipr_router.py
# ----------------------------------------------------------------------

_header("IPR ROUTER: patent filing workflow")
report = advise_regime("patent")
assert "Form 1" in report["filing_workflow"][0]
print(report["filing_workflow"][0])

_header("IPR ROUTER: trademark NICE class + descriptiveness risk")
report = advise_regime(
    "trademark", product_type="herbal_tea", is_generic_or_descriptive_ayurvedic_term=True
)
assert report["nice_class"]["nice_class"] == 30
assert report["distinctiveness"]["risk"] == "high_risk"
print(report["nice_class"]["finding"])
print(report["distinctiveness"]["finding"])

_header("IPR ROUTER: GI registration process")
report = advise_regime("geographical_indication")
assert "Navara Rice" in report["examples"]
print(report["process"][0])

_header("IPR ROUTER: industrial design, trade secret, copyright, PPV&FR")
assert advise_regime("industrial_design")["governing_law"] == "The Designs Act, 2000"
assert "processing steps" in advise_regime("trade_secret")["candidates"][0]
assert "literary work" in advise_regime("copyright")["protectable_assets"][0]
assert advise_regime("ppv_fr", variety_category="novel")["category"] == "novel"
print("OK — all four regimes resolve")

_header("IPR ROUTER: unknown regime raises")
try:
    advise_regime("not_a_real_regime")
    raise AssertionError("expected ValueError")
except ValueError as exc:
    print("Correctly raised:", exc)


# ----------------------------------------------------------------------
# ipr_router.plan_ip_route / tk_engine.misappropriation_risk
# (winning_features.md items 6/8)
# ----------------------------------------------------------------------

_header("IPR ROUTER: plan_ip_route colors outlook by TK risk and region-linkage")
plan = plan_ip_route(
    {"patent": "note", "trademark": "note", "geographical_indication": "note", "trade_secret": "note"},
    tk_risk="barred",
    is_region_linked=False,
)
by_regime = {p["regime"]: p for p in plan}
assert by_regime["patent"]["outlook"] == "barred"
assert by_regime["geographical_indication"]["outlook"] == "conditional"
assert by_regime["trademark"]["outlook"] == "available"
print("OK —", [(p["regime"], p["outlook"]) for p in plan])

_header("IPR ROUTER: plan_ip_route omits regimes absent from ip_regimes")
plan = plan_ip_route({"patent": "note"})
assert [p["regime"] for p in plan] == ["patent"]
print("OK — only supplied regimes appear")

_header("TK ENGINE: misappropriation_risk levels")
assert misappropriation_risk(True, True)["level"] == "high"
assert misappropriation_risk(True, False)["level"] == "moderate"
assert misappropriation_risk(False, True)["level"] == "moderate"
assert misappropriation_risk(False, False)["level"] == "low"
print("OK — high/moderate/moderate/low")

result = analyze_tk_patentability(documented_in_classical_text=True, cited_in_tkdl=True)
assert result["misappropriation_risk"]["level"] == "high"
print("OK — analyze_tk_patentability includes misappropriation_risk")


# ----------------------------------------------------------------------
# knowledge_graph.py
# ----------------------------------------------------------------------

_header("KNOWLEDGE GRAPH: full multi-hop build (Product -> Ingredient -> "
        "Biological Resource -> TK -> IP Type -> ABS -> Jurisdiction)")
graph = build_graph(
    jurisdiction="India",
    ingredient="Withania somnifera (Ashwagandha)",
    biological_resource="Root extract sourced from Madhya Pradesh",
    classification_inputs={"in_first_schedule": False, "intended_use": "therapeutic"},
    tk_inputs={"documented_in_classical_text": True},
    abs_inputs={
        "entity_type": "foreign_entity",
        "activity_type": "commercial_utilization",
        "seeking_ipr_on_biological_invention": True,
    },
)
node_kinds = {n["kind"] for n in graph["nodes"]}
assert {"Product", "Ingredient", "BiologicalResource", "Classification", "TKFinding",
        "ABSObligation", "Jurisdiction"} <= node_kinds
assert any(e["relation"] == "sourced_from" for e in graph["edges"])
assert any(e["relation"] == "patent_issue" for e in graph["edges"])
print(f"OK — {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")

_header("KNOWLEDGE GRAPH: partial input (jurisdiction-only) still resolves")
graph = build_graph(jurisdiction="India")
assert graph["nodes"] == [
    {"id": "product", "kind": "Product", "label": "Ayurvedic Product / Formulation"},
    {"id": "jurisdiction", "kind": "Jurisdiction", "label": "India"},
]
print("OK — no fabricated nodes when no facts are supplied")

_header("KNOWLEDGE GRAPH: invalid engine inputs are caught, not left to crash")
graph = build_graph(tk_inputs={"documented_in_classical_text": "not_a_bool_but_engine_is_lenient"})
graph = build_graph(abs_inputs={"entity_type": "not_a_real_type", "activity_type": "bio_survey"})
assert not any(n["kind"] == "ABSObligation" for n in graph["nodes"])
print("OK — invalid abs_inputs skips that branch instead of raising")


print("\n" + "=" * 80)
print("ALL ENGINE SANITY CHECKS PASSED")
print("=" * 80)
