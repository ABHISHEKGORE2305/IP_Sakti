"""
Deterministic legal engines (src/engines/): product classifier, Section 3
TK patentability, ABS compliance, regulator cross-walk, IP-regime router
and the knowledge graph. Same inputs must always give the same statutory
output, so these are exact-value assertions.
"""

import pytest

from engines.abs_engine import ActivityType, EntityType, analyze_abs_compliance
from engines.classifier import ClassificationError, IntendedUse, classify_product
from engines.ipr_router import advise_regime, plan_ip_route
from engines.knowledge_graph import build_graph
from engines.reg_engine import analyze_regulatory_pathway
from engines.tk_engine import analyze_tk_patentability, misappropriation_risk

# ----------------------------------------------------------------------
# classifier.py
# ----------------------------------------------------------------------


@pytest.mark.parametrize("kwargs, category", [
    ({"in_first_schedule": True, "formulation_modified": False}, "classical_ayurvedic_medicine"),
    ({"in_first_schedule": True, "formulation_modified": True}, "patent_or_proprietary_medicine"),
    ({"in_first_schedule": False, "intended_use": IntendedUse.THERAPEUTIC}, "new_ayurvedic_drug"),
    ({"in_first_schedule": False, "intended_use": "nutritional"}, "ayurveda_aahar"),
])
def test_classifier_categories(kwargs, category):
    result = classify_product(**kwargs)
    assert result["category"] == category
    assert result["classification_path"]


def test_classifier_missing_required_input_raises():
    with pytest.raises(ClassificationError):
        classify_product(in_first_schedule=True)


# ----------------------------------------------------------------------
# tk_engine.py
# ----------------------------------------------------------------------


def test_classical_formulation_is_barred_by_section_3p():
    assert analyze_tk_patentability(documented_in_classical_text=True)["overall_risk"] == "barred"


@pytest.mark.parametrize("kwargs", [
    {"is_combination_of_known_herbs": True, "has_synergistic_data": True},
    {"is_novel_extraction_process": True, "extraction_method_is_standard": False},
])
def test_differentiated_inventions_are_conditional(kwargs):
    assert analyze_tk_patentability(**kwargs)["overall_risk"] == "conditional"


def test_tkdl_citation_has_mitigation_advice():
    assert analyze_tk_patentability(cited_in_tkdl=True)["tkdl_mitigation"]["recommendation"]


@pytest.mark.parametrize("documented, in_tkdl, level", [
    (True, True, "high"),
    (True, False, "moderate"),
    (False, True, "moderate"),
    (False, False, "low"),
])
def test_misappropriation_risk_levels(documented, in_tkdl, level):
    assert misappropriation_risk(documented, in_tkdl)["level"] == level


def test_tk_report_includes_misappropriation_risk():
    result = analyze_tk_patentability(documented_in_classical_text=True, cited_in_tkdl=True)
    assert result["misappropriation_risk"]["level"] == "high"


# ----------------------------------------------------------------------
# abs_engine.py
# ----------------------------------------------------------------------


def test_foreign_entity_seeking_ipr_needs_nba_forms_i_and_iii():
    report = analyze_abs_compliance(
        entity_type=EntityType.FOREIGN_ENTITY,
        activity_type=ActivityType.COMMERCIAL_UTILIZATION,
        seeking_ipr_on_biological_invention=True,
    )
    assert report["entity_classification"]["governing_section"] == "Section 3"
    assert {a["form"] for a in report["required_approvals"]} == {"Form I", "Form III"}
    assert report["compliance_checklist"]


def test_indian_company_commercial_use_needs_sbb_intimation_only():
    report = analyze_abs_compliance(
        entity_type=EntityType.INDIAN_COMPANY,
        activity_type=ActivityType.COMMERCIAL_UTILIZATION,
    )
    assert report["sbb_intimation"]["required"] is True
    assert report["required_approvals"] == []


def test_vaidya_exemption():
    report = analyze_abs_compliance(
        entity_type=EntityType.INDIAN_INDIVIDUAL,
        activity_type=ActivityType.NON_COMMERCIAL_RESEARCH,
        is_traditional_practitioner=True,
    )
    assert report["exemptions"]


# ----------------------------------------------------------------------
# reg_engine.py
# ----------------------------------------------------------------------


def test_new_ayurvedic_drug_has_dual_regulators():
    report = analyze_regulatory_pathway("new_ayurvedic_drug")
    regulators = {r["regulator"] for r in report["crosswalk"]["regulators"]}
    assert regulators == {"ayush_state_licensing_authority", "cdsco"}


@pytest.mark.parametrize("category, risk", [
    ("general_food", "high_risk"),
    ("classical_ayurvedic_medicine", "conditional"),
])
def test_disease_cure_claim_advertising_risk(category, risk):
    report = analyze_regulatory_pathway(category, makes_disease_cure_claim=True)
    assert report["advertising_compliance"]["risk"] == risk


# ----------------------------------------------------------------------
# ipr_router.py
# ----------------------------------------------------------------------


def test_patent_filing_workflow_starts_with_form_1():
    assert "Form 1" in advise_regime("patent")["filing_workflow"][0]


def test_trademark_nice_class_and_descriptiveness():
    report = advise_regime("trademark", product_type="herbal_tea", is_generic_or_descriptive_ayurvedic_term=True)
    assert report["nice_class"]["nice_class"] == 30
    assert report["distinctiveness"]["risk"] == "high_risk"


def test_gi_registration():
    report = advise_regime("geographical_indication")
    assert "Navara Rice" in report["examples"]
    assert report["process"]


def test_remaining_regimes_resolve():
    assert advise_regime("industrial_design")["governing_law"] == "The Designs Act, 2000"
    assert "processing steps" in advise_regime("trade_secret")["candidates"][0]
    assert "literary work" in advise_regime("copyright")["protectable_assets"][0]
    assert advise_regime("ppv_fr", variety_category="novel")["category"] == "novel"


def test_unknown_regime_raises():
    with pytest.raises(ValueError):
        advise_regime("not_a_real_regime")


def test_route_plan_outlook_follows_tk_risk_and_region_linkage():
    plan = plan_ip_route(
        {"patent": "note", "trademark": "note", "geographical_indication": "note", "trade_secret": "note"},
        tk_risk="barred",
        is_region_linked=False,
    )
    by_regime = {p["regime"]: p for p in plan}
    assert by_regime["patent"]["outlook"] == "barred"
    assert by_regime["geographical_indication"]["outlook"] == "conditional"
    assert by_regime["trademark"]["outlook"] == "available"


def test_route_plan_only_includes_supplied_regimes():
    assert [p["regime"] for p in plan_ip_route({"patent": "note"})] == ["patent"]


# ----------------------------------------------------------------------
# knowledge_graph.py
# ----------------------------------------------------------------------


def test_full_multi_hop_graph():
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


def test_graph_never_fabricates_nodes_without_facts():
    assert build_graph(jurisdiction="India")["nodes"] == [
        {"id": "product", "kind": "Product", "label": "Ayurvedic Product / Formulation"},
        {"id": "jurisdiction", "kind": "Jurisdiction", "label": "India"},
    ]


def test_graph_skips_branch_on_invalid_engine_inputs():
    build_graph(tk_inputs={"documented_in_classical_text": "not_a_bool_but_engine_is_lenient"})
    graph = build_graph(abs_inputs={"entity_type": "not_a_real_type", "activity_type": "bio_survey"})
    assert not any(n["kind"] == "ABSObligation" for n in graph["nodes"])
