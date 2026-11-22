"""
End-to-end answer grading — the automated version of the hand-graded
sprint reports in benchmark_results/.

eval_benchmark.py checks the retrieval and engine layers without an LLM.
This suite grades the *generated answer* against the authored benchmark
answers, which is the number that says whether a change actually helped a
user. It is the regression gate for every retrieval / prompt change.

Subcommands (each one resumable — it writes after every case and skips
cases already done, so a rate-limited run can be restarted):

  generate   POST every question to a running API (/api/chat/) and save
             the answer + citations, in the same schema as sprint*_raw.json.
  grade      LLM-as-judge PASS / PARTIAL / FAIL per case, plus failure tags
             (over_abstention, wrong_jurisdiction, invented_citation, ...).
  report     Verdict counts overall and per category; with --baseline, a
             per-case diff (improved / regressed) against another run or
             against the human verdicts (--baseline human).
  calibrate  Judge the existing hand-graded sprint answers and report
             agreement with the human verdicts. Run this once per judge
             model before trusting its numbers.

Question sets (benchmark_questions/):
  1-100     sprint 1 set (validation criteria included)
  101-200   sprint 2 set
  301-400   extended set; the file numbers its questions Q201-Q300, they
            are renumbered by +100 here so ids stay unique
  201-300 is skipped: those are judge questions about the system's own
            architecture ("why RAG instead of fine-tuning?"), not queries
            the chatbot should answer. For the same reason the default id
            set (DEFAULT_IDS) leaves out sections A and I-L of the extended
            set (301-308, 379-400) — scope, RAG, voice, privacy, demo.

Judge note: grading with the same model that generated the answers biases
the result upward. Pass --judge-model to use a different one.

Run with:
    PYTHONPATH=src python src/eval_answers.py generate --ids 1-200 --out benchmark_results/runs/baseline.json
    PYTHONPATH=src python src/eval_answers.py grade benchmark_results/runs/baseline.json
    PYTHONPATH=src python src/eval_answers.py report benchmark_results/runs/baseline.json --baseline human
    PYTHONPATH=src python src/eval_answers.py calibrate
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

QUESTIONS_DIR = Path("benchmark_questions")
RESULTS_DIR = Path("benchmark_results")

# Sprint 1 + sprint 2 + extended-set sections B-H (classification through
# international regimes).
DEFAULT_IDS = "1-200,309-378"

VERDICTS = ("PASS", "PARTIAL", "FAIL")
FAILURE_TAGS = (
    "over_abstention",       # declined although the answer was findable
    "wrong_conclusion",      # the core legal answer is wrong
    "missing_provision",     # right answer, governing provision not cited
    "invented_citation",     # cites a provision that does not exist / is mislabelled
    "wrong_jurisdiction",    # applies foreign law to an India question or vice versa
    "outdated_law",          # states a superseded rule (e.g. pre-2024 amendment)
    "incomplete",            # covers part of a multi-part question
    "truncated",             # answer cut off mid-sentence
)


# ----------------------------------------------------------------------
# Question parsing
# ----------------------------------------------------------------------


def _clean(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _parse_set_1_100(text: str) -> list[dict]:
    """### Test Case NNN: Title / * **Field:** value bullets."""

    cases = []
    for block in re.split(r"^### Test Case ", text, flags=re.M)[1:]:
        header, _, body = block.partition("\n")
        m = re.match(r"(\d+):\s*(.+)", header)
        if not m:
            continue

        # Split on the bullet field markers; values may span lines
        # (the benchmarked answer is an indented paragraph).
        fields = {}
        parts = re.split(r"^\* \*\*([^*]+?):?\*\*:?", body, flags=re.M)
        for name, value in zip(parts[1::2], parts[2::2], strict=True):
            value = value.split("\n---")[0]
            fields[name.strip().rstrip(":")] = _clean(value)

        query = next(
            (v for k, v in fields.items() if k.startswith("User Query")), ""
        ).strip()
        # Multilingual cases append an English gloss after the quoted query.
        quoted = re.match(r'["“](.+?)["”]', query, flags=re.S)
        if quoted:
            query = quoted.group(1)
        cases.append(
            {
                "id": int(m.group(1)),
                "title": m.group(2).strip(),
                "query": query.strip(),
                "jurisdiction": fields.get("Jurisdiction Toggle"),
                "category": fields.get("Formulation Category"),
                "ground_truth": fields.get("Benchmarked Answer", ""),
                "validation_criteria": fields.get("Validation Criteria", ""),
            }
        )
    return cases


def _parse_set_101_200(text: str) -> list[dict]:
    """QNNN / Jurisdiction Focus: / Domain: / Question: / Benchmark Answer:"""

    cases = []
    for block in re.split(r"^Q(?=\d+\s*$)", text, flags=re.M)[1:]:
        header, _, body = block.partition("\n")
        # A trailing "Section N: ..." heading belongs to the next block.
        body = re.split(r"^Section \d+:", body, flags=re.M)[0]

        def field(name: str) -> str:
            m = re.search(rf"^{name}:\s*(.*)$", body, flags=re.M)  # noqa: B023 - called within this iteration
            return m.group(1).strip() if m else ""

        answer = body.split("Benchmark Answer:", 1)[1] if "Benchmark Answer:" in body else ""
        domain = field("Domain")
        cases.append(
            {
                "id": int(header.strip()),
                "title": domain,
                "query": field("Question"),
                "jurisdiction": field("Jurisdiction Focus") or None,
                "category": domain,
                "ground_truth": _clean(answer),
                "validation_criteria": "",
            }
        )
    return cases


def _parse_set_301_400(text: str) -> list[dict]:
    """### Q2NN. Question / **Benchmark answer:** / **Must cite:** / **Tag:**"""

    cases = []
    sections = re.split(r"^## ([A-L]\. .+)$", text, flags=re.M)
    for section, section_body in zip(sections[1::2], sections[2::2], strict=True):
        for block in re.split(r"^### Q", section_body, flags=re.M)[1:]:
            header, _, body = block.partition("\n")
            m = re.match(r"(\d+)\.\s*(.+)", header)
            if not m:
                continue

            def field(name: str) -> str:
                fm = re.search(
                    rf"^\*\*{name}:\*\*\s*(.*?)(?=^\*\*[A-Z][\w ]+:\*\*|\Z)",
                    body,  # noqa: B023 - called within this iteration
                    flags=re.M | re.S,
                )
                return _clean(fm.group(1)) if fm else ""

            must_cite = field("Must cite")
            tag = field("Tag")
            criteria = "; ".join(
                p for p in (f"Must cite: {must_cite}" if must_cite else "",
                            f"Behaviour tag: {tag}" if tag else "") if p
            )
            question = m.group(2).strip()
            cases.append(
                {
                    "id": int(m.group(1)) + 100,
                    "title": question[:80],
                    "query": question,
                    "jurisdiction": None,
                    "category": section.strip(),
                    "ground_truth": field("Benchmark answer"),
                    "validation_criteria": criteria,
                }
            )
    return cases


_PARSERS = {
    "benchmark_questions1-100.md": _parse_set_1_100,
    "benchmark_questions101-200.md": _parse_set_101_200,
    "benchmark_questions301-400.md": _parse_set_301_400,
}


def load_questions(questions_dir: Path = QUESTIONS_DIR) -> list[dict]:
    cases = []
    for filename, parser in _PARSERS.items():
        path = questions_dir / filename
        if path.exists():
            cases.extend(parser(path.read_text(encoding="utf-8")))
    return sorted(cases, key=lambda c: c["id"])


def parse_ids(spec: str | None) -> set[int] | None:
    """'1-100,150,301-310' -> set of ids. None means every question."""

    if not spec:
        return None
    ids: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            ids.update(range(int(lo), int(hi) + 1))
        elif part:
            ids.add(int(part))
    return ids


# ----------------------------------------------------------------------
# Human verdicts (sprint reports)
# ----------------------------------------------------------------------


def load_human_verdicts(results_dir: Path = RESULTS_DIR) -> dict[int, str]:
    """Per-case verdicts from the 'Full Results' tables of the sprint
    reports: | id | title | VERDICT | note |."""

    verdicts = {}
    for name in ("sprint1_report.md", "sprint2_report.md"):
        path = results_dir / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[0].isdigit() and cells[2] in VERDICTS:
                verdicts[int(cells[0])] = cells[2]
    return verdicts


# ----------------------------------------------------------------------
# Run files
# ----------------------------------------------------------------------


def _load_run(path: Path) -> list[dict]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _save_run(path: Path, cases: list[dict], answers_win: bool = False) -> None:
    """Merge `cases` into the run file rather than overwrite it, so a
    `generate` and a `grade` working on the same file concurrently cannot
    erase each other's results. answers_win=True (generate) replaces the
    stored answer; otherwise (grade) a judgement is only stored against the
    exact answer it was given for."""

    merged = {c["id"]: c for c in _load_run(path)}
    for case in cases:
        stored = merged.get(case["id"])
        if stored is None:
            merged[case["id"]] = case
        elif answers_win:
            same = stored.get("actual_answer") == case.get("actual_answer")
            keep = stored.get("judge") if same and not case.get("judge") else case.get("judge")
            merged[case["id"]] = dict(case, **({"judge": keep} if keep else {}))
        elif case.get("judge") and stored.get("actual_answer") == case.get("actual_answer"):
            merged[case["id"]] = dict(stored, judge=case["judge"])

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    out = sorted(merged.values(), key=lambda c: c["id"])
    tmp.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


# ----------------------------------------------------------------------
# generate
# ----------------------------------------------------------------------


def generate(args) -> None:
    import requests

    wanted = parse_ids(args.ids)
    questions = [q for q in load_questions() if wanted is None or q["id"] in wanted]
    out = Path(args.out)
    done = {c["id"]: c for c in _load_run(out) if not c.get("api_error")}

    url = args.api_url.rstrip("/") + "/api/chat/"
    print(f"Generating {len(questions)} answers via {url} ({len(done)} already done)")

    for q in questions:
        if q["id"] in done:
            continue
        for attempt in range(args.retries + 1):
            started = time.perf_counter()
            case = dict(q, actual_answer="", actual_citations=[], api_error=None)
            try:
                resp = requests.post(
                    url,
                    json={"query": q["query"], "jurisdiction": q["jurisdiction"]},
                    timeout=args.timeout,
                )
                resp.raise_for_status()
                body = resp.json()
                case["actual_answer"] = body.get("answer", "")
                case["actual_citations"] = body.get("citations", [])
                case["api_error"] = body.get("error")
            except Exception as exc:  # network error, 5xx, timeout
                case["api_error"] = f"{type(exc).__name__}: {exc}"
            case["latency_s"] = round(time.perf_counter() - started, 2)
            # An LLM failure on a free tier is almost always a per-minute
            # token limit; waiting for the bucket to refill beats recording
            # the fallback message as the answer.
            if not _retryable(case["api_error"]) or attempt == args.retries:
                break
            print(f"  [{q['id']:>3}] {case['api_error'][:60]} - retrying in {args.backoff:.0f}s")
            time.sleep(args.backoff)
        done[q["id"]] = case
        _save_run(out, [case], answers_win=True)
        status = case["api_error"] or "ok"
        print(f"  [{q['id']:>3}] {case['latency_s']:>6.1f}s  {status}")
        if args.delay:
            time.sleep(args.delay)


def _retryable(error: str | None) -> bool:
    if not error:
        return False
    e = error.lower()
    return any(t in e for t in ("llm_failed", "not_ready", "rate", "429", "timeout", "unavailable"))


# ----------------------------------------------------------------------
# grade
# ----------------------------------------------------------------------

JUDGE_PROMPT = """You are grading an AI legal-research assistant for Ayurvedic IP and
regulatory law (India + international). Compare its answer with the benchmark.

Grade on substance, not style or length:
- PASS: the core legal conclusion matches the benchmark, the governing
  provision(s) are named correctly, and nothing material is wrong.
- PARTIAL: the conclusion is broadly right but a key provision, requirement
  or part of a multi-part question is missing, OR the answer correctly
  answers part and transparently scopes out the rest.
- FAIL: wrong conclusion; blanket refusal / "sources insufficient" when the
  benchmark shows a specific answer exists; foreign law applied to an
  India-scoped question (or vice versa); or a material provision, deadline,
  fee or limit that is invented or misattributed.

If the benchmark itself expects abstention, escalation or a clarifying
question, then doing that is a PASS and confidently answering is a FAIL.
Treat the benchmark as the reference; where it says a fact must be verified,
do not penalise a different but clearly-sourced statement of that fact.

Failure tags (zero or more): {tags}

QUESTION (jurisdiction: {jurisdiction}):
{query}

BENCHMARK ANSWER:
{ground_truth}

VALIDATION CRITERIA:
{criteria}

ASSISTANT ANSWER:
{answer}

Reply with JSON only, no prose before or after:
{{"verdict": "PASS|PARTIAL|FAIL", "tags": ["..."], "rationale": "<one sentence>"}}"""


def _parse_judgement(text: str) -> dict:
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError(f"no JSON in judge output: {text[:200]!r}")
    data = json.loads(m.group(0))
    verdict = str(data.get("verdict", "")).upper().strip()
    if verdict not in VERDICTS:
        raise ValueError(f"bad verdict {verdict!r}")
    tags = [t for t in data.get("tags", []) if t in FAILURE_TAGS]
    return {"verdict": verdict, "tags": tags, "rationale": str(data.get("rationale", ""))}


def judge_case(llm, case: dict, max_answer_chars: int = 9000) -> dict:
    answer = (case.get("actual_answer") or "").strip()
    if not answer:
        return {"verdict": "FAIL", "tags": [], "rationale": "No answer returned."}
    prompt = JUDGE_PROMPT.format(
        tags=", ".join(FAILURE_TAGS),
        jurisdiction=case.get("jurisdiction") or "unspecified",
        query=case["query"],
        ground_truth=case.get("ground_truth") or "(none)",
        criteria=case.get("validation_criteria") or "(none)",
        answer=answer[:max_answer_chars],
    )
    return _parse_judgement(llm.generate(prompt, max_tokens=400))


def _make_judge(model: str | None):
    from dotenv import load_dotenv

    load_dotenv(".env")
    from llm import GroqLLM

    return GroqLLM(model=model)


def _grade_cases(cases: list[dict], llm, save, delay: float, force: bool,
                 retries: int = 3, backoff: float = 60) -> None:
    for case in cases:
        if case.get("judge") and not force:
            continue
        if case.get("api_error"):
            continue  # generation failed; regenerate rather than grade
        for attempt in range(retries + 1):
            try:
                case["judge"] = judge_case(llm, case)
                break
            except Exception as exc:
                print(f"  [{case['id']:>3}] judge error: {str(exc)[:100]}")
                if attempt < retries and _retryable(str(exc)):
                    time.sleep(backoff)
        if not case.get("judge"):
            continue
        save()
        j = case["judge"]
        print(f"  [{case['id']:>3}] {j['verdict']:<7} {','.join(j['tags'])}")
        if delay:
            time.sleep(delay)


def grade(args) -> None:
    path = Path(args.run)
    cases = _load_run(path)
    llm = _make_judge(args.judge_model)
    print(f"Grading {len(cases)} cases in {path}")
    _grade_cases(cases, llm, lambda: _save_run(path, cases), args.delay, args.force)
    _print_summary(cases)


# ----------------------------------------------------------------------
# report
# ----------------------------------------------------------------------


def _verdicts(cases: list[dict]) -> dict[int, str]:
    return {c["id"]: c["judge"]["verdict"] for c in cases if c.get("judge")}


def _pct(n: int, total: int) -> str:
    return f"{100 * n / total:.1f}%" if total else "-"


def _print_summary(cases: list[dict]) -> None:
    graded = [c for c in cases if c.get("judge")]
    counts = Counter(c["judge"]["verdict"] for c in graded)
    print(f"\nGraded {len(graded)}/{len(cases)}")
    for v in VERDICTS:
        print(f"  {v:<8} {counts[v]:>4}  {_pct(counts[v], len(graded))}")

    tags = Counter(t for c in graded for t in c["judge"]["tags"])
    if tags:
        print("\nFailure tags:")
        for tag, n in tags.most_common():
            print(f"  {tag:<20} {n:>4}")

    by_cat: defaultdict[str, Counter] = defaultdict(Counter)
    for c in graded:
        by_cat[c.get("category") or "-"][c["judge"]["verdict"]] += 1
    print("\nBy category (PASS / PARTIAL / FAIL):")
    for cat, cnt in sorted(by_cat.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {cnt['PASS']:>3} / {cnt['PARTIAL']:>3} / {cnt['FAIL']:>3}  {cat[:70]}")


_RANK = {"FAIL": 0, "PARTIAL": 1, "PASS": 2}


def diff_verdicts(new: dict[int, str], old: dict[int, str]) -> dict[str, list]:
    shared = sorted(set(new) & set(old))
    out: dict[str, list] = {"improved": [], "regressed": [], "same": []}
    for cid in shared:
        delta = _RANK[new[cid]] - _RANK[old[cid]]
        key = "improved" if delta > 0 else "regressed" if delta < 0 else "same"
        out[key].append((cid, old[cid], new[cid]))
    return out


def report(args) -> None:
    cases = _load_run(Path(args.run))
    _print_summary(cases)
    if not args.baseline:
        return

    if args.baseline == "human":
        old = load_human_verdicts()
        label = "human sprint verdicts"
    else:
        old = _verdicts(_load_run(Path(args.baseline)))
        label = args.baseline
    d = diff_verdicts(_verdicts(cases), old)
    shared = sum(len(v) for v in d.values())
    print(f"\nVs {label} ({shared} shared cases): "
          f"{len(d['improved'])} improved, {len(d['regressed'])} regressed, "
          f"{len(d['same'])} unchanged")
    for cid, before, after in d["regressed"]:
        print(f"  REGRESSED [{cid:>3}] {before} -> {after}")
    if args.verbose:
        for cid, before, after in d["improved"]:
            print(f"  improved  [{cid:>3}] {before} -> {after}")


# ----------------------------------------------------------------------
# calibrate
# ----------------------------------------------------------------------


def agreement(judge: dict[int, str], human: dict[int, str]) -> dict:
    shared = sorted(set(judge) & set(human))
    exact = sum(judge[i] == human[i] for i in shared)
    within_one = sum(abs(_RANK[judge[i]] - _RANK[human[i]]) <= 1 for i in shared)
    confusion = Counter((human[i], judge[i]) for i in shared)
    return {
        "n": len(shared),
        "exact": exact,
        "within_one": within_one,
        "confusion": confusion,
    }


def calibrate(args) -> None:
    human = load_human_verdicts()
    out = Path(args.out)
    cases = _load_run(out)
    if not cases:
        for name in ("sprint1_raw.json", "sprint2_raw.json"):
            cases.extend(_load_run(RESULTS_DIR / name))
    wanted = parse_ids(args.ids)
    todo = [c for c in cases if c["id"] in human and (wanted is None or c["id"] in wanted)]

    llm = _make_judge(args.judge_model)
    print(f"Calibrating judge on {len(todo)} hand-graded answers -> {out}")
    _grade_cases(todo, llm, lambda: _save_run(out, cases), args.delay, args.force)

    a = agreement(_verdicts(cases), human)
    print(f"\nJudge vs human on {a['n']} cases: exact {_pct(a['exact'], a['n'])}, "
          f"within one grade {_pct(a['within_one'], a['n'])}")
    print("Rows = human, columns = judge:")
    print("           " + "".join(f"{v:>9}" for v in VERDICTS))
    for h in VERDICTS:
        print(f"  {h:<8} " + "".join(f"{a['confusion'][(h, j)]:>9}" for j in VERDICTS))


# ----------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate")
    p.add_argument("--ids", default=DEFAULT_IDS, help=f"e.g. 1-100,150 (default: {DEFAULT_IDS})")
    p.add_argument("--out", required=True)
    p.add_argument("--api-url", default=os.getenv("EVAL_API_URL", "http://127.0.0.1:8000"))
    p.add_argument("--timeout", type=float, default=180)
    p.add_argument("--delay", type=float, default=0, help="seconds between requests")
    p.add_argument("--retries", type=int, default=4, help="retries after an LLM/rate-limit failure")
    p.add_argument("--backoff", type=float, default=60, help="seconds to wait before a retry")
    p.set_defaults(func=generate)

    p = sub.add_parser("grade")
    p.add_argument("run")
    p.add_argument("--judge-model")
    p.add_argument("--delay", type=float, default=0)
    p.add_argument("--force", action="store_true", help="re-grade graded cases")
    p.set_defaults(func=grade)

    p = sub.add_parser("report")
    p.add_argument("run")
    p.add_argument("--baseline", help="another run file, or 'human'")
    p.add_argument("--verbose", "-v", action="store_true")
    p.set_defaults(func=report)

    p = sub.add_parser("calibrate")
    p.add_argument("--out", default=str(RESULTS_DIR / "runs" / "judge_calibration.json"))
    p.add_argument("--ids")
    p.add_argument("--judge-model")
    p.add_argument("--delay", type=float, default=0)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=calibrate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
