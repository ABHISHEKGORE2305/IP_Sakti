"""
Tests for the end-to-end grading harness (src/eval_answers.py).

No LLM or API is called: the judge is a stub, and the question parsers run
against the real benchmark_questions/ files and the hand-graded sprint data.

Run directly:      python src/tests/test_eval_answers.py
Run with pytest:   pytest src/tests/test_eval_answers.py
"""

import json
import os
import sys

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

REPO_ROOT = os.path.dirname(SRC_DIR)
os.chdir(REPO_ROOT)

import eval_answers as ea  # noqa: E402


def _sprint_raw():
    cases = []
    for name in ("sprint1_raw.json", "sprint2_raw.json"):
        with open(os.path.join("benchmark_results", name), encoding="utf-8") as f:
            cases.extend(json.load(f))
    return cases


def _norm(text):
    return " ".join((text or "").replace("*", "").split()).strip('"“” ')


# ------------------------------------------------------------------
# Question parsing
# ------------------------------------------------------------------


def test_parses_every_question_in_the_three_answerable_sets():
    ids = {q["id"] for q in ea.load_questions()}
    expected = set(range(1, 201)) | set(range(301, 401))
    assert ids == expected, f"missing {sorted(expected - ids)[:10]}"


def test_every_question_has_a_query_and_benchmark_answer():
    for q in ea.load_questions():
        assert q["query"], f"case {q['id']} has no query"
        assert q["ground_truth"], f"case {q['id']} has no benchmark answer"


# Benchmark answers corrected after the sprint snapshots were taken.
# 26: Form 27 is due within six months of each three-year period, not three
#     (rule 131(2) as substituted by G.S.R. 211(E), 15 March 2024).
CORRECTED_GROUND_TRUTH = {26}


def test_parsed_questions_match_the_hand_graded_sprint_data():
    """The sprint raw files were built from the same markdown; any drift
    means the parser is reading the wrong field."""

    parsed = {q["id"]: q for q in ea.load_questions()}
    for raw in _sprint_raw():
        q = parsed[raw["id"]]
        assert _norm(q["query"]) == _norm(raw["query"]), raw["id"]
        assert q["jurisdiction"] == raw["jurisdiction"], raw["id"]
        if raw["id"] not in CORRECTED_GROUND_TRUTH:
            assert _norm(q["ground_truth"])[:150] == _norm(raw["ground_truth"])[:150], raw["id"]


def test_multilingual_query_drops_the_english_gloss():
    q = {c["id"]: c for c in ea.load_questions()}[94]
    assert "(Can I file" not in q["query"]
    assert q["query"].startswith("क्या")


def test_extended_set_is_renumbered_and_carries_must_cite():
    q = {c["id"]: c for c in ea.load_questions()}[311]
    assert "proprietary medicine" in q["query"]
    assert "Must cite:" in q["validation_criteria"]
    assert "TRAP" in q["validation_criteria"]


def test_parse_ids():
    assert ea.parse_ids("1-3,7") == {1, 2, 3, 7}
    assert ea.parse_ids(None) is None
    assert len(ea.parse_ids(ea.DEFAULT_IDS)) == 270


# ------------------------------------------------------------------
# Human verdicts
# ------------------------------------------------------------------


def test_human_verdicts_cover_both_sprints():
    human = ea.load_human_verdicts()
    assert set(human) == set(range(1, 201))
    # Totals published in the sprint report summaries: 11 + 22 PASS.
    assert sum(v == "PASS" for v in human.values()) == 33


# ------------------------------------------------------------------
# Judge parsing and grading
# ------------------------------------------------------------------


def test_parse_judgement_tolerates_prose_and_drops_unknown_tags():
    j = ea._parse_judgement(
        'Here you go:\n{"verdict": "partial", "tags": ["incomplete", "made_up"], '
        '"rationale": "Misses Sec 3(a)."}'
    )
    assert j == {"verdict": "PARTIAL", "tags": ["incomplete"], "rationale": "Misses Sec 3(a)."}


def test_parse_judgement_rejects_bad_verdict():
    try:
        ea._parse_judgement('{"verdict": "MAYBE"}')
    except ValueError:
        return
    raise AssertionError("expected ValueError")


class _StubLLM:
    def __init__(self, reply):
        self.reply = reply
        self.prompts = []

    def generate(self, prompt, max_tokens=None):
        self.prompts.append(prompt)
        return self.reply


def test_judge_case_builds_prompt_and_parses_reply():
    llm = _StubLLM('{"verdict": "PASS", "tags": [], "rationale": "ok"}')
    case = {
        "id": 1,
        "query": "Can I patent Chyawanprash?",
        "jurisdiction": "India (National)",
        "ground_truth": "No - Section 3(p).",
        "validation_criteria": "Must cite 3(p).",
        "actual_answer": "No, barred by Section 3(p).",
    }
    assert ea.judge_case(llm, case)["verdict"] == "PASS"
    prompt = llm.prompts[0]
    for part in ("Can I patent Chyawanprash?", "No - Section 3(p).",
                 "Must cite 3(p).", "barred by Section 3(p)", "India (National)"):
        assert part in prompt


def test_empty_answer_fails_without_calling_the_judge():
    llm = _StubLLM("unused")
    j = ea.judge_case(llm, {"id": 1, "query": "q", "actual_answer": "  "})
    assert j["verdict"] == "FAIL" and not llm.prompts


def test_grade_cases_skips_graded_and_failed_generations():
    llm = _StubLLM('{"verdict": "FAIL", "tags": ["over_abstention"], "rationale": "x"}')
    cases = [
        {"id": 1, "query": "q", "actual_answer": "a", "judge": {"verdict": "PASS"}},
        {"id": 2, "query": "q", "actual_answer": "", "api_error": "Timeout"},
        {"id": 3, "query": "q", "actual_answer": "a"},
    ]
    ea._grade_cases(cases, llm, save=lambda: None, delay=0, force=False)
    assert len(llm.prompts) == 1
    assert cases[0]["judge"]["verdict"] == "PASS"
    assert "judge" not in cases[1]
    assert cases[2]["judge"]["tags"] == ["over_abstention"]


def test_concurrent_generate_and_grade_saves_do_not_erase_each_other():
    import tempfile
    from pathlib import Path

    path = Path(tempfile.mkdtemp()) / "run.json"
    # grade loaded the file when only case 1 existed ...
    stale = [{"id": 1, "actual_answer": "a1"}]
    ea._save_run(path, stale, answers_win=True)
    # ... generate adds case 2 meanwhile ...
    ea._save_run(path, [{"id": 2, "actual_answer": "a2"}], answers_win=True)
    # ... then grade saves its stale list with a verdict for case 1.
    stale[0]["judge"] = {"verdict": "PASS"}
    ea._save_run(path, stale)
    run = {c["id"]: c for c in ea._load_run(path)}
    assert set(run) == {1, 2}, "grade must not drop answers generated meanwhile"
    assert run[1]["judge"]["verdict"] == "PASS"

    # A regenerated answer drops the verdict given for the old one; a
    # verdict for a stale answer is not attached to the new one.
    ea._save_run(path, [{"id": 1, "actual_answer": "a1-new"}], answers_win=True)
    assert "judge" not in ea._load_run(path)[0]
    ea._save_run(path, [{"id": 1, "actual_answer": "a1", "judge": {"verdict": "FAIL"}}])
    assert "judge" not in ea._load_run(path)[0]


# ------------------------------------------------------------------
# Report / calibration maths
# ------------------------------------------------------------------


def test_diff_verdicts():
    d = ea.diff_verdicts({1: "PASS", 2: "FAIL", 3: "PARTIAL", 9: "PASS"},
                         {1: "FAIL", 2: "PARTIAL", 3: "PARTIAL"})
    assert d["improved"] == [(1, "FAIL", "PASS")]
    assert d["regressed"] == [(2, "PARTIAL", "FAIL")]
    assert d["same"] == [(3, "PARTIAL", "PARTIAL")]


def test_agreement():
    a = ea.agreement({1: "PASS", 2: "FAIL", 3: "PASS"}, {1: "PASS", 2: "PARTIAL", 3: "FAIL"})
    assert (a["n"], a["exact"], a["within_one"]) == (3, 1, 2)
    assert a["confusion"][("FAIL", "PASS")] == 1


# ------------------------------------------------------------------


def _run_standalone():
    tests = [
        (name, obj)
        for name, obj in sorted(globals().items())
        if name.startswith("test_") and callable(obj)
    ]

    passed = 0
    failed = 0

    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {name}\n      {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {name}\n      {type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"ok    {name}")

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_standalone())
