"""
Sanity checks for the Sprint 2 domain intelligence engines
(classifier, tk_engine, abs_engine, reg_engine, ipr_router).

Run with:
    PYTHONPATH=src python3 src/test_engines.py
"""

from engines.classifier import classify_product, IntendedUse, ClassificationError
from engines.ipr_router import advise_regime
from engines.tk_engine import analyze_tk_patentability
from engines.abs_engine import analyze_abs_compliance, EntityType, ActivityType
from engines.reg_engine import analyze_regulatory_pathway


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


print("\n" + "=" * 80)
print("ALL ENGINE SANITY CHECKS PASSED")
print("=" * 80)
