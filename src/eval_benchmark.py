"""
Golden Benchmark Evaluation Suite — 50 questions across the 10
categories named in implementation_plan.md Phase 6.2.

Design note on scope (read before assuming this calls the LLM):
Gemini's free tier allows roughly 20 requests/day per model (see
llm.py). Running full LLM generation for 50 questions is neither
reliably repeatable nor something this suite should silently burn the
daily quota on. So by default this suite runs three *deterministic,
LLM-free* checks per question, chosen per category to match what
actually exists in the corpus/engines today:

  retrieval   - does the expected document/legal_reference actually
                surface in top-k hybrid retrieval? (tests Sprint 1)
  engine      - does the relevant Sprint 2/4 deterministic engine
                (classifier/tk/abs/reg/intl) return the expected
                field? (tests Sprint 2/4, zero hallucination risk)
  confidence  - does guardrails.confidence.evaluate_confidence()
                correctly score this query low/abstain, using only
                retrieval signals (no generation)? Used both for
                genuine "safe abstention" questions (category 10) and
                for categories 7/8 (trademark, GI) where the
                corresponding statutory corpus was never ingested -
                the correct behavior there IS abstention, not a
                hallucinated answer, so that's what's tested.

Pass `--full` to additionally run a small sample through the real
agents.graph.run() pipeline (LLM + citation verification) - opt-in
because of the quota above.

Run with:
    PYTHONPATH=src python3 src/eval_benchmark.py
    PYTHONPATH=src python3 src/eval_benchmark.py --full --full-sample 5
"""

import argparse
import sys

from engines.abs_engine import ActivityType, EntityType, analyze_abs_compliance
from engines.classifier import IntendedUse, classify_product
from engines.intl_engine import us_market_pathway, uspto_patent_eligibility
from engines.reg_engine import analyze_regulatory_pathway
from engines.tk_engine import analyze_tk_patentability
from final_retriever import AyurvedicIPRetriever
from guardrails.confidence import evaluate_confidence


# ----------------------------------------------------------------------
# Check primitives
# ----------------------------------------------------------------------

_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = AyurvedicIPRetriever()
    return _retriever


def check_retrieval(query, expect_document_contains, expect_ref_contains=None, top_k=5):
    """Pass if a top-k result's document (and optionally legal_reference) matches."""

    results = _get_retriever().search(query, top_k=top_k)

    for r in results:
        doc = (r.get("document") or "")
        ref = (r.get("legal_reference") or "")
        if expect_document_contains.lower() in doc.lower():
            if expect_ref_contains is None or expect_ref_contains.lower() in ref.lower():
                return True, f"matched: {doc} | {ref}"

    top = [(r.get("document"), r.get("legal_reference")) for r in results[:3]]
    return False, f"no match in top {top_k}; top 3 were: {top}"


def check_engine(compute, predicate, label):
    """Pass if predicate(compute()) is True."""

    try:
        result = compute()
    except Exception as exc:  # noqa: BLE001
        return False, f"{label} raised: {exc}"

    ok = predicate(result)
    return ok, f"{label} -> {result if not ok else 'ok'}"


def check_confidence_low(query, top_k=6):
    """Pass if the retrieval-only confidence gate correctly abstains."""

    results = _get_retriever().search(query, top_k=top_k)
    report = evaluate_confidence(query, results)
    ok = report["band"] == "low"
    return ok, f"band={report['band']} confidence={report['confidence']:.3f}"


# ----------------------------------------------------------------------
# 50 golden questions, 5 per Phase 6.2 category
# ----------------------------------------------------------------------

GOLDEN_QUESTIONS = []


def _q(category, query, check_type, **kwargs):
    GOLDEN_QUESTIONS.append({
        "id": len(GOLDEN_QUESTIONS) + 1,
        "category": category,
        "query": query,
        "check_type": check_type,
        "kwargs": kwargs,
    })


# --- 1. Classical single-plant formulations vs Section 3(p) ---
_q(1, "What is Section 3(p) of the Patents Act, 1970?", "retrieval",
   expect_document_contains="Patents Act", expect_ref_contains="3(p)")
_q(1, "Is traditional knowledge patentable in India?", "retrieval",
   # The TK-specific guidelines are the more on-point authority here
   # than the bare Patents Act text - retrieval correctly prefers them.
   expect_document_contains="Traditional Knowledge")
_q(1, "A classical single-herb Ashwagandha churna documented unchanged in a "
      "First Schedule text is claimed as a new invention.", "engine",
   compute=lambda: analyze_tk_patentability(documented_in_classical_text=True),
   predicate=lambda r: r["overall_risk"] == "barred")
_q(1, "A formulation with no classical-text disclosure is claimed as an invention.",
   "engine",
   compute=lambda: analyze_tk_patentability(documented_in_classical_text=False),
   predicate=lambda r: r["overall_risk"] == "clear")
_q(1, "What does the TKDL factsheet say about traditional knowledge documentation?",
   "retrieval", expect_document_contains="Traditional Knowledge Digital Library")

# --- 2. Novel synergistic herbal extracts vs Section 3(e) ---
_q(2, "What is Section 3(e) mere admixture exclusion under the Patents Act?",
   "retrieval", expect_document_contains="Patents Act", expect_ref_contains="3(e)")
_q(2, "Can a combination of known herbs be patented without synergistic data?",
   "retrieval", expect_document_contains="Guidelines for Examination of Ayush")
_q(2, "A combination of known herbs is claimed with no synergy data.", "engine",
   compute=lambda: analyze_tk_patentability(is_combination_of_known_herbs=True, has_synergistic_data=False),
   predicate=lambda r: r["overall_risk"] == "high_risk")
_q(2, "A combination of known herbs is claimed WITH documented isobolographic "
      "synergy data.", "engine",
   compute=lambda: analyze_tk_patentability(is_combination_of_known_herbs=True, has_synergistic_data=True),
   predicate=lambda r: r["overall_risk"] == "conditional")
_q(2, "What do the TK processing guidelines say about admixtures of known herbs?",
   "retrieval", expect_document_contains="Traditional Knowledge and Biological Material")

# --- 3. Process patents for traditional preparation methods ---
_q(3, "What is the definition of invention under Section 2(1)(j) of the Patents Act?",
   "retrieval", expect_document_contains="Patents Act", expect_ref_contains="2(j)")
_q(3, "Is a novel extraction process for herbal medicine patentable?", "retrieval",
   expect_document_contains="Guidelines for Examination of Ayush")
_q(3, "A Swarasa (standard classical juice-extraction) process is claimed as novel.",
   "engine",
   compute=lambda: analyze_tk_patentability(is_novel_extraction_process=True, extraction_method_is_standard=True),
   predicate=lambda r: r["overall_risk"] == "high_risk")
_q(3, "A non-standard, parameter-optimized extraction process is claimed.", "engine",
   compute=lambda: analyze_tk_patentability(is_novel_extraction_process=True, extraction_method_is_standard=False),
   predicate=lambda r: r["overall_risk"] == "conditional")
_q(3, "What does the Manual of Patent Office Practice say about process claims?",
   "retrieval", expect_document_contains="Manual of Patent Office")

# --- 4. ABS compliance triggers for foreign equity holders ---
_q(4, "What NBA approval does a foreign company need to access biological "
      "resources in India?", "retrieval", expect_document_contains="Biological Diversity")
_q(4, "What does the Biological Diversity (Amendment) Act, 2023 say about "
      "foreign entities?", "retrieval", expect_document_contains="Biological Diversity (Amendment) Act")
_q(4, "A foreign entity seeks to patent an invention based on an Indian "
      "biological resource.", "engine",
   compute=lambda: analyze_abs_compliance(
       entity_type=EntityType.FOREIGN_ENTITY,
       activity_type=ActivityType.COMMERCIAL_UTILIZATION,
       seeking_ipr_on_biological_invention=True,
   ),
   predicate=lambda r: {a["form"] for a in r["required_approvals"]} == {"Form I", "Form III"})
_q(4, "An Indian company commercially utilises a biological resource.", "engine",
   compute=lambda: analyze_abs_compliance(
       entity_type=EntityType.INDIAN_COMPANY, activity_type=ActivityType.COMMERCIAL_UTILIZATION,
   ),
   predicate=lambda r: r["sbb_intimation"]["required"] is True)
_q(4, "What do the Biological Diversity Rules, 2024 say about NBA procedure?",
   "retrieval", expect_document_contains="Biological Diversity Rules")

# --- 5. Ayurvedic cosmetics vs Ayurvedic drugs regulatory boundaries ---
_q(5, "A new, non-classical formulation is marketed for topical beautification.",
   "engine",
   compute=lambda: classify_product(in_first_schedule=False, intended_use=IntendedUse.TOPICAL),
   predicate=lambda r: r["category"] == "ayurvedic_cosmetic")
_q(5, "A new, non-classical formulation claims to cure a disease.", "engine",
   compute=lambda: classify_product(in_first_schedule=False, intended_use=IntendedUse.THERAPEUTIC),
   predicate=lambda r: r["category"] == "new_ayurvedic_drug")
_q(5, "What regulator governs an Ayurvedic cosmetic vs a new Ayurvedic drug?",
   "engine",
   compute=lambda: (
       analyze_regulatory_pathway("ayurvedic_cosmetic")["crosswalk"]["regulators"][0]["regulator"],
       analyze_regulatory_pathway("new_ayurvedic_drug")["crosswalk"]["regulators"],
   ),
   predicate=lambda r: r[0] == "ayush_state_licensing_authority" and len(r[1]) == 2)
_q(5, "A cosmetic product's advertisement claims it cures a skin disease.", "engine",
   compute=lambda: analyze_regulatory_pathway("ayurvedic_cosmetic", makes_disease_cure_claim=True),
   predicate=lambda r: r["advertising_compliance"]["risk"] == "high_risk")
_q(5, "A classical, unmodified formulation is manufactured as-is.", "engine",
   compute=lambda: classify_product(in_first_schedule=True, formulation_modified=False),
   predicate=lambda r: r["category"] == "classical_ayurvedic_medicine")

# --- 6. FSSAI Ayurveda-Aahar classification and health claims ---
_q(6, "A new, non-classical formulation is marketed as a dietary supplement.",
   "engine",
   compute=lambda: classify_product(in_first_schedule=False, intended_use=IntendedUse.NUTRITIONAL),
   predicate=lambda r: r["category"] == "ayurveda_aahar")
_q(6, "What regulator governs Ayurveda-Aahar products?", "engine",
   compute=lambda: analyze_regulatory_pathway("ayurveda_aahar")["crosswalk"]["regulators"][0]["regulator"],
   predicate=lambda r: r == "fssai")
_q(6, "An Ayurveda-Aahar product's advertisement claims it cures a disease.",
   "engine",
   compute=lambda: analyze_regulatory_pathway("ayurveda_aahar", makes_disease_cure_claim=True),
   predicate=lambda r: r["advertising_compliance"]["risk"] == "high_risk")
_q(6, "A general food/beverage product with no medicinal claim.", "engine",
   compute=lambda: classify_product(in_first_schedule=False, intended_use=IntendedUse.GENERAL_FOOD),
   predicate=lambda r: r["category"] == "general_food")
_q(6, "Does an Ayurveda-Aahar product need drug clinical trial evidence?", "engine",
   compute=lambda: classify_product(in_first_schedule=False, intended_use=IntendedUse.NUTRITIONAL),
   predicate=lambda r: "Not required as a drug" in r["clinical_evidence"])

# --- 7. Trademark distinctiveness for Sanskrit herbal terms ---
# No Trade Marks Act corpus has been ingested - correct behavior is
# abstention, not a hallucinated answer, so these test the gate itself.
_q(7, "Can I trademark the Sanskrit word 'Ashwagandha' as a brand name for "
      "my supplement?", "confidence")
# KNOWN LIMITATION (documented, not silently skipped): this one still
# fails. legal_reference.py's exact-reference boost has no concept of
# *which* Act a cited section belongs to - "Section 9" here means
# Trade Marks Act Section 9, but the Patents Act, 1970 also happens to
# have its own Section 9, so the exact-match boost fires against that
# unrelated chunk and drives confidence artificially high. Fixing this
# properly needs extract_legal_references() to capture the named Act
# and match_reference() to require it match the chunk's `document`,
# which is a real but narrow fix left for future work rather than
# rushed in under this pass.
_q(7, "Is 'Triphala' too descriptive to register as a trademark under "
      "Section 9 of the Trade Marks Act?", "confidence")
_q(7, "What NICE class should I file a herbal tea trademark under?", "confidence")
_q(7, "Can a generic Ayurvedic term acquire secondary meaning as a trademark?",
   "confidence")
_q(7, "What distinguishes a suggestive mark from a descriptive mark for "
      "herbal products?", "confidence")

# --- 8. GI protection for regional medicinal crops ---
# No GI Act corpus has been ingested either - same rationale as category 7.
_q(8, "How do I register a Geographical Indication for Navara rice?",
   "confidence")
_q(8, "What is the Authorized User registration process under the GI Act, 1999?",
   "confidence")
_q(8, "Can a medicinal plant variety specific to one region get GI protection?",
   "confidence")
_q(8, "What is the difference between collective ownership and individual "
      "trademark rights for a GI-protected crop?", "confidence")
_q(8, "How long does GI registration last in India?", "confidence")

# --- 9. US FDA Botanical Drug guidance comparison ---
_q(9, "What does the US FDA Botanical Drug Guidance require for multi-batch "
      "products?", "engine",
   compute=lambda: us_market_pathway("botanical_drug"),
   predicate=lambda r: "fingerprinting" in " ".join(r["requirements"]).lower())
_q(9, "Can I make disease-cure claims under the DSHEA dietary supplement route?",
   "engine",
   compute=lambda: us_market_pathway("dietary_supplement"),
   predicate=lambda r: "NOT permitted" in " ".join(r["requirements"]))
_q(9, "Is a bare natural-product claim eligible under US 35 U.S.C. Section 101?",
   "engine",
   compute=lambda: uspto_patent_eligibility(
       claims_natural_product_as_is=True, claims_markedly_different_characteristics=False,
   ),
   predicate=lambda r: r["risk"] == "high_risk")
_q(9, "Is an isolated compound with markedly different characteristics "
      "eligible under 35 U.S.C. Section 101?", "engine",
   compute=lambda: uspto_patent_eligibility(
       claims_natural_product_as_is=False, claims_markedly_different_characteristics=True,
   ),
   predicate=lambda r: r["risk"] == "conditional")
_q(9, "Does the botanical drug route require single-molecule isolation?",
   "engine",
   compute=lambda: us_market_pathway("botanical_drug"),
   predicate=lambda r: "NOT required" in " ".join(r["requirements"]))

# --- 10. Safe abstention on ambiguous/unsupported queries ---
_q(10, "What is the capital of France and what's a good pizza recipe?", "confidence")
_q(10, "Will it rain in Mumbai tomorrow?", "confidence")
_q(10, "What is the meaning of life?", "confidence")
_q(10, "Recommend a good movie to watch this weekend.", "confidence")
_q(10, "How do I reset my email password?", "confidence")


assert len(GOLDEN_QUESTIONS) == 50, len(GOLDEN_QUESTIONS)


# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------

CATEGORY_NAMES = {
    1: "Classical single-plant formulations vs Section 3(p)",
    2: "Novel synergistic herbal extracts vs Section 3(e)",
    3: "Process patents for traditional preparation methods",
    4: "ABS compliance triggers for foreign equity holders",
    5: "Ayurvedic cosmetics vs Ayurvedic drugs regulatory boundaries",
    6: "FSSAI Ayurveda-Aahar classification and health claims",
    7: "Trademark distinctiveness for Sanskrit herbal terms",
    8: "GI protection for regional medicinal crops",
    9: "US FDA Botanical Drug guidance comparison",
    10: "Safe abstention on ambiguous/unsupported queries",
}


def run_question(q):

    if q["check_type"] == "retrieval":
        return check_retrieval(q["query"], **q["kwargs"])

    if q["check_type"] == "engine":
        return check_engine(q["kwargs"]["compute"], q["kwargs"]["predicate"], f"Q{q['id']}")

    if q["check_type"] == "confidence":
        return check_confidence_low(q["query"], **q["kwargs"])

    raise ValueError(f"unknown check_type: {q['check_type']}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full", action="store_true",
        help="Also run a sample through the real agents.graph.run() pipeline (uses the Gemini quota).",
    )
    parser.add_argument("--full-sample", type=int, default=3)
    parser.add_argument(
        "--out-json", type=str, default=None,
        help="Write structured results (winning_features.md item 19's eval dashboard) to this path, "
             "e.g. data/processed/eval_results.json — served by GET /api/eval-results.",
    )
    args = parser.parse_args()

    print("=" * 80)
    print(f"GOLDEN BENCHMARK: {len(GOLDEN_QUESTIONS)} questions across {len(CATEGORY_NAMES)} categories")
    print("=" * 80)

    results_by_category = {c: [] for c in CATEGORY_NAMES}

    for q in GOLDEN_QUESTIONS:
        passed, detail = run_question(q)
        results_by_category[q["category"]].append(passed)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] Q{q['id']:>2} (cat {q['category']}, {q['check_type']:<10}) {q['query'][:70]}")
        if not passed:
            print(f"         -> {detail}")

    print("\n" + "=" * 80)
    print("RESULTS BY CATEGORY")
    print("=" * 80)

    total_passed = 0
    total = 0
    for cat, name in CATEGORY_NAMES.items():
        outcomes = results_by_category[cat]
        passed = sum(outcomes)
        total_passed += passed
        total += len(outcomes)
        print(f"  {passed}/{len(outcomes)}  Category {cat}: {name}")

    accuracy = total_passed / total if total else 0.0
    print("\n" + "=" * 80)
    print(f"OVERALL: {total_passed}/{total} ({accuracy:.1%})")
    print("=" * 80)

    if args.out_json:
        _write_json_results(args.out_json, results_by_category, total_passed, total, accuracy)

    if args.full:
        _run_full_sample(args.full_sample)

    return 0 if total_passed == total else 1


def _write_json_results(path, results_by_category, total_passed, total, accuracy):
    import datetime
    import json
    from pathlib import Path

    categories = []
    for cat, name in CATEGORY_NAMES.items():
        outcomes = results_by_category[cat]
        categories.append({
            "category": cat,
            "name": name,
            "passed": sum(outcomes),
            "total": len(outcomes),
        })

    payload = {
        "run_at": datetime.datetime.now().isoformat(),
        "total_passed": total_passed,
        "total": total,
        "accuracy": accuracy,
        "categories": categories,
    }

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote results to {out_path}")


def _run_full_sample(sample_size):
    """Opt-in: exercise the real agents.graph.run() pipeline end-to-end
    (LLM generation + citation verification) for a small sample, since
    this uses the Gemini free-tier daily quota."""

    from agents.graph import run as agent_run

    print("\n" + "=" * 80)
    print(f"FULL PIPELINE SAMPLE ({sample_size} questions, uses the LLM quota)")
    print("=" * 80)

    sample = [q for q in GOLDEN_QUESTIONS if q["check_type"] == "retrieval"][:sample_size]

    for q in sample:
        result = agent_run(q["query"])
        band = result.get("confidence_report", {}).get("band")
        citations = result.get("citation_report") or {}
        print(
            f"Q{q['id']}: band={band} "
            f"citations={citations.get('verified_citations')}/{citations.get('total_citations')}"
        )


if __name__ == "__main__":
    sys.exit(main())
