# Root-Cause Analysis — Why the Chatbot Scored 11% and 22% on Sprints 1–2

Analysis of the 200 graded benchmark answers (test cases 1–200), traced back to
specific defects in the retrieval pipeline and corpus. Every root cause below
was confirmed by direct measurement, not inferred from the failure text.

## Summary of measured causes

| # | Root cause | How it was confirmed | Failures it explains |
|---|---|---|---|
| 1 | Vocabulary gap between user phrasing and statutory text | Same §3(p) content scored **0.995** against a statute-worded query vs **0.0005** against a user-worded one | The dominant "sources are insufficient" mode across both sprints |
| 2 | Five source PDFs present on disk but never ingested | Absent from `document_config.DOCUMENTS`; 0 chunks in `chunks.json` | Entire clusters at 0% (labeling/advertising, trade marks, GI, PVP, FSSAI) |
| 3 | Statutes shredded into unretrievable fragments | Patents Act §3 = 17 chunks; 37.5% of all chunks under 200 chars; some chunks were 2-character page numbers | §3(p) never retrieved at any `candidate_k`, including 150 |
| 4 | `jurisdiction_filter` never passed on the chat path | `api.py:_run_query` accepted the field and dropped it | US FDA guidance answering India-only questions; failed jurisdiction-switch test |
| 5 | `TOP_K = 6` | — | Multi-regime questions could not fit 3–4 governing statutes in context |
| 6 | Prompt mandated blanket refusal | `prompt.py` instructed abstention with no graded fallback | Refusals even where the governing test was retrievable |

## 1. The vocabulary gap (primary cause)

The reranker was never broken — it scores a clean match at 0.999 and a clean
mismatch at 0.000016. The problem is that user questions and statutory drafting
share almost no surface:

| Query phrasing | Passage | Reranker score |
|---|---|---|
| "Which section of the Patents Act bars patents on traditional knowledge?" | Prose naming and explaining §3(p) | **0.9947** |
| "Can I patent a classical Ayurvedic formulation from a Samhita text?" | The raw text of §3(p) | **0.000452** |

Identical law, ~2,200x difference. Statutes never restate their own subject
matter in the words a user would use, so dense retrieval and the cross-encoder
both miss them, and verbose guidance prose wins the top-k instead.

Measured effect of the two fixes on test case 001 (Chyawanprash → §3(p)):

| Configuration | Reranker score | vs baseline |
|---|---|---|
| Baseline (bare chunk, raw query) | 0.000125 | 1x |
| Chunk enriched with citation header | 0.090367 | 721x |
| Query expanded into statutory vocabulary | 0.065166 | 520x |
| **Both** | **0.924907** | **7381x** |

For reference, the irrelevant guidance chunks that were beating the statute
scored 0.03–0.07 — so either fix alone clears the bar, and both together put
the correct provision decisively first.

## 2. Five documents were never ingested

Present in `data/raw/`, absent from `document_config.DOCUMENTS`, therefore
absent from the corpus entirely:

| Document | Size | Benchmark impact |
|---|---|---|
| Drugs & Cosmetics Act 1940 + Rules 1945 | 635 pages | The classification question that gates nearly every IP answer (§3(a) classical vs §3(h) proprietary vs Rule 2(eb) phytopharmaceutical), plus Schedule T, Rule 161, Schedule E(1) |
| FSS (Ayurveda Aahara) Regulations 2022 | 27 pages | Every food-supplement-vs-drug question |
| Trade Marks Act 1999 | 56 pages | All trade mark questions (sprint 2, IDs 146–172) |
| PPV&FR Act 2001 | 38 pages | Plant-variety protection questions |
| WIPO GRATK Treaty (full text) | 10 pages | Only the 2-page summary was indexed |

This is why whole clusters scored 0% while patents/ABS questions scored 20–80%:
the bot was not reasoning badly, it had no text to reason from.

## 3. Fragmentation

`create_chunks()` flushes a chunk at every clause boundary, and its
`chunk_size`/`chunk_overlap` parameters were accepted but never used. Result
for the single most-cited provision in the benchmark:

- Patents Act Section 3 → **17 separate chunks**
- The heading ("3. What are not inventions.—") isolated in its own 93-char chunk,
  severed from every clause it governs
- Clause (p) reduced to 170 characters containing no mention of the Act, the
  section, or that it states a patentability bar
- Chunks whose entire text was `"10"` or `"26"` — page numbers captured as corpus

No chunk anywhere in the corpus contained both "what are not inventions" and
"traditional knowledge", so no phrasing of the question could retrieve the rule.

## 4–6. Configuration and prompt defects

- **Jurisdiction:** the frontend sent `jurisdiction`, `ChatRequest` accepted it,
  and `_run_query` silently dropped it. With 59 US FDA chunks in an
  otherwise-Indian corpus and no filter, India-scoped questions were answered
  under the US FD&C Act.
- **`TOP_K = 6`:** benchmark questions routinely span classification + patent +
  ABS + export regimes. Six chunks cannot hold four statutes.
- **Prompt:** required a blanket "sources are insufficient" refusal with no
  option to answer the covered part, state the governing test, or name the
  regime — converting every retrieval miss into a total non-answer.

## Fixes applied

1. **`src/query_expansion.py`** (new) — expands the query into statutory
   vocabulary for retrieval and reranking only; the user's wording is still
   what gets answered. Falls back to the raw query whenever the expansion
   model is unavailable, so retrieval cannot break because of it.
2. **`src/chunker.py`** — added `consolidate_chunks()`: merges consecutive
   same-section fragments to ~900–2400 chars, drops page-number noise, and
   prefixes each chunk with its citation header. Patents Act §3: 17 → 3 chunks;
   corpus-wide, chunks under 200 chars fell from 37.5% to 6.0%, median chunk
   size 298 → 970 chars.
3. **`src/document_config.py`** — registered the five missing documents. The
   D&C volume is registered twice with page ranges (Act pp.1–38, Rules pp.39+)
   so its numbered provisions are labelled "Rule N" rather than "Section N".
   Also fixed a filename case mismatch that would have broken ingestion on a
   case-sensitive filesystem.
4. **`src/document_loader.py`** — `page_range` support for PDFs bundling two
   instruments.
5. **`src/api.py`** — `_normalize_jurisdiction()` maps UI/caller labels onto the
   retriever's filter values and threads it through `/api/chat/`. Dual-scope or
   unrecognized labels widen the search rather than narrowing it wrongly.
6. **`src/config.py`** — `TOP_K` 6 → 12, `CANDIDATE_K` 20 → 40,
   `MAX_CONTEXT_CHARS` 12000 → 24000.
7. **`src/prompt.py`** — replaced blanket refusal with a graded fallback:
   answer the supported part and name what is not covered; else state the
   governing legal test; else name the regime as an explicitly uncited pointer.
   Hard bar on inventing section numbers, deadlines, fees or limits is retained.

Corpus after re-ingestion: **2,173 → 4,656 chunks**, 22 documents.

## What these fixes do not address

- **Stale statutory state** (Form 27 annual vs 3-year under the 2024 Rules;
  Form 3 deadlines). The 2024 amendment PDFs *are* in the corpus, so this is a
  retrieval-precedence problem between an amending instrument and the
  unamended parent text, not a coverage gap. Needs amendment-aware ranking.
- **Reversed conclusions** on questions whose answer turns on an exemption
  (e.g. registered AYUSH practitioners' ABS exemption). Worth re-measuring
  after these fixes before treating it as a separate defect — several of these
  answers were reasoning from the wrong retrieved provision.
- **Self-knowledge questions** (sprints 3–4 territory: "what is your
  architecture", "what is your abstention policy"). These are not in any
  statute and will keep failing until the system is given a description of
  itself to retrieve from.
