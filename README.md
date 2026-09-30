# IP-Sakti (आयुरX) — Ayurveda IPR & Regulatory Intelligence

A citation-grounded AI assistant for Ayurvedic intellectual property and regulatory
law. Ask whether a formulation is patentable, which regulator owns it, or what
Access-and-Benefit-Sharing duties it triggers — and get back an answer where every
claim carries the Act, section and page it came from, plus a formal case brief PDF
you can send to an IP facilitator.

Built for Smart India Hackathon 2026, problem statement **26045**.

---

## The problem

Commercialising an Ayurvedic formulation in India means satisfying four regimes at
once, and they disagree with each other:

| Regime | What it decides |
|---|---|
| **Patents Act, 1970** | s.3(p) traditional knowledge, s.3(e) mere admixture, s.3(d) efficacy |
| **Biological Diversity Act, 2002 / 2023** | SBB intimation, NBA approval, benefit-sharing levies |
| **D&C Act, 1940 + FSSAI 2022** | Classical medicine vs. proprietary medicine vs. phytopharmaceutical vs. Ayurveda-Aahar |
| **International** | WIPO GRATK, US FDA (DSHEA vs. botanical-drug IND), EU THMPD |

General-purpose LLMs answer these questions confidently and wrongly — inventing
section numbers, conflating US and Indian provisions, and missing mandatory NBA
filings. IP-Sakti's design premise is that **the citation is the product**: an
answer that cannot name its source is worse than no answer.

---

## What is implemented

### Retrieval pipeline

```
query → PII sanitize → injection filter → query expansion
      → hybrid retrieval (dense + BM25) → RRF fusion
      → cross-encoder rerank + authority weighting → context builder
      → LLM → grounded answer → citation verification → confidence band
```

- **Corpus** — 21 primary legal/pharmacopoeial PDFs in `data/raw/` (Patents Act 1970,
  Biological Diversity Act 2002 + Rules 2024, D&C Act 1940 & Rules 1945, FSSAI
  Ayurveda Aahara Regulations 2022, WIPO GRATK Treaty, TKDL guidance and more),
  ingested with PyMuPDF and legal-aware chunking that preserves Act / Chapter /
  Section / Rule / page metadata → **3,078 indexed chunks** (`data/processed/chunks.json`),
  plus 9 chunks from live web sources (`ingest_web.py`, staleness-tracked in
  `web_sources_manifest.json`).
- **Dual retrieval** — `BAAI/bge-m3` dense vectors in Qdrant, combined with BM25
  sparse keyword search, merged by Reciprocal Rank Fusion (`RRF_K = 60`).
- **Reranking** — `BAAI/bge-reranker-v2-m3` cross-encoder, plus authority weighting
  and score bonuses when the query names an explicit Section / Rule / Form
  (`EXACT_REFERENCE_BONUS`, `SAME_SECTION_BONUS`, `STATUTORY_SOURCE_BONUS` in `src/config.py`).
- **LLM** — provider-agnostic: Groq (`openai/gpt-oss-120b` by default) or Gemini
  (`gemini-flash-latest`), each with a fallback model chain (`src/llm.py`).

### Deterministic legal engines (`src/engines/`)

These are rule engines, not prompts — the same inputs always produce the same
statutory output, with zero hallucination surface.

| Engine | What it decides |
|---|---|
| `classifier.py` | Statutory product identity under D&C Act Ch. IVA and FSSAI 2022 |
| `tk_engine.py` | Section 3(p)/3(e)/3(d) patentability analysis, TKDL prior-art risk |
| `abs_engine.py` | BD Act entity classification, exemptions, NBA/SBB approvals, Form I–IV |
| `reg_engine.py` | AYUSH / FSSAI / CDSCO regulator cross-walk, advertising compliance |
| `intl_engine.py` | US / EU / UK market pathways and the GRATK disclosure obligation |
| `ipr_router.py` | Route across 7 IP regimes: patent, trademark, GI, design, trade secret, copyright, PPV&FR |
| `knowledge_graph.py` | Product → Ingredient → Biological Resource → TK → Regulation → IP Type → Authority |

### Multi-agent orchestration (`src/agents/`)

A LangGraph state machine:

```
InputSanitizer → SupervisorRouter → {specialist} → VerificationGuardrail
              → OutputSynthesizer | FallbackHandler
```

Six specialists: `patent_agent`, `tm_gi_agent`, `abs_agent`, `reg_agent`,
`intl_agent`, `classifier_agent`. Routing is deliberately **keyword-based, not an
LLM call**, so it stays auditable and free. `citation_agent.py` re-checks every
citation in the draft answer against the retrieved chunks and reports a
verified/total count.

### Guardrails (`src/guardrails/`)

- **`pii_sanitizer.py`** — DPDP Act 2023 data minimisation: strips PII from the
  query *before* it is embedded or sent to the LLM.
- **`injection_filter.py`** — deterministic prompt-injection phrase/pattern matching.
- **`confidence.py`** — multi-factor score and safe abstention:
  `0.40·rerank + 0.30·retrieval_density + 0.20·authority + 0.10·query_term_coverage`,
  banded High (≥0.75) / Medium (≥0.50) / Low.

### Frontend (`sih_frontend_antigrav/`)

React 19 + Vite, dark/light themed, deep-green-and-gold Ayurvedic design system
(`src/index.css`).

- **`/`** — marketing landing page (hero with animated Sanskrit mantra rings, problem,
  how-it-works, use cases, testimonials).
- **`/auth`** — mock login → `/app`.
- **`/app`** — the product shell:
  - **Analysis** — the 6-step guided wizard: Jurisdiction → Classification →
    Issue Routing → Analysis → Sources → Action Plan, with persona modes
    (Practitioner / Researcher / Startup-MSME / Cultivator) that adjust tone and
    depth only, never which legal facts get cited.
  - **Chat** — free-form follow-up Q&A. Non-blocking: every message carries its own
    pending/done/error state, so you can keep sending while replies are in flight.
    Prior turns are resent as `history` so follow-ups have context.
  - **Export Markets**, **Law Version Timeline**, **Privacy & Audit**,
    **Corpus Admin**, **Evaluation** panels.

Recent frontend work:

- **Case brief preview renders as a document**, not raw markdown — the brief now goes
  through the shared `<Markdown>` component with a letterhead treatment.
- **`preserveLineBreaks`** in `Markdown.jsx` — engine answers are one fact per line,
  and markdown collapses single newlines; hard breaks are inserted everywhere that
  does not already open a new block (fenced code, lists, tables and headings are left alone).
- **GFM task lists** render as real checkboxes across chat, analysis and the brief.
- **"Continue in Chat"** — hands the wizard's question and answer to the chat tab as a
  completed turn, so follow-ups build on the analysis instead of starting cold. The
  transcript lives in the app shell, so it survives switching tabs.
- **Invisible-text fix** — `.step__card` is a `<button>`, and the global button reset
  cleared background/border but never `color`, so cards inherited the UA's black
  `buttontext` against a dark surface.

### Export and escalation

- **Case brief** — built from real wizard state and backend results (never placeholder
  data) as Markdown, JSON, or a print-formatted PDF (`src/lib/caseBrief.js` +
  `markdownToHtml.js`), with A4 page rules, letterhead, page-break control and a colophon.
- **ABS compliance checklist** — a separate, narrower export of just the biodiversity
  obligations and their citations.
- **Escalate to IP Facilitator** — `POST /api/escalate` renders the brief server-side
  into a **PDF report** (`src/case_brief_pdf.py`, built on PyMuPDF's `Story` engine —
  no extra PDF dependency) and emails it as an attachment with a short covering note.
  If rendering ever fails, the escalation still goes out with the markdown body.

### Persistence and privacy (`src/db.py`)

No-login, session-scoped SQLite (`X-Session-Id` header from a localStorage UUID).
Powers the audit log, consent record, corpus admin, and a real DPDP-style
"delete my data" primitive. Every read is session-scoped, never global.

### Multilingual

10 languages (English, Hindi, Marathi, Tamil, Telugu, Kannada, Bengali, Gujarati,
Malayalam, Punjabi). `bhashini_client.py` wraps Bhashini TTS/STT when credentials are
present; `/api/translate` falls back to the Gemini client already in use and preserves
bracketed statutory citations in English.

---

## API

Base URL `http://127.0.0.1:8000`. Full docstrings at the top of `src/api.py`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Service status |
| `POST` | `/ask` | Plain RAG question |
| `POST` | `/api/chat/` | Chat with `history` |
| `POST` | `/api/agent` | Full multi-agent graph — jurisdiction, forced agent, classification/market/ABS/regulatory inputs, confidence + citation reports |
| `POST` | `/api/translate` | Translate an answer, citations preserved |
| `GET` | `/api/bhashini/status` · `POST` `/api/tts` · `POST` `/api/stt` | Speech |
| `POST` | `/api/escalate` · `GET` `/api/escalate/status` | Email the case brief as a PDF |
| `GET` | `/api/law-versions` · `POST` `/api/law-version-query` | Law version timeline |
| `POST` | `/api/ip-route-plan` | Multi-regime IP filing strategy |
| `POST` | `/api/knowledge-graph` | Multi-hop relational graph |
| `GET` | `/api/eval-results` | Benchmark dashboard data |
| `GET` | `/api/references` | Deep links to official portals (IP India, WIPO, GI Registry, TKDL, AYUSH, FSSAI, NBA) |
| `GET`/`POST` | `/api/consent` · `/api/audit-log` · `/api/privacy/summary` · `/api/privacy/delete` | DPDP dashboard |
| `GET`/`POST` | `/api/admin/corpus` · `/api/admin/corpus/upload` | Corpus admin |

---

## Running it

**Prerequisites:** Python 3.14 + `venv`, Node **≥ 22**, Docker (for Qdrant),
`GROQ_API_KEY` or `GEMINI_API_KEY` in `.env`.

```bash
# 1. Qdrant — start once, it persists
docker start ip_sakti_qdrant
# first time only:
# docker run -d --name ip_sakti_qdrant -p 6333:6333 -p 6334:6334 \
#   -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant

# 2. Backend
source venv/bin/activate
PYTHONPATH=src python -m uvicorn api:app --reload --reload-dir src --port 8000 --app-dir src

# 3. Frontend
nvm use 22
cd sih_frontend_antigrav && npm run dev
```

> **`--reload-dir src` is not optional.** Bare `--reload` watches the whole working
> directory — roughly 60,000 files (`venv/` ~41k, `node_modules/` ~18k) against 129
> actual source files. The watcher re-walks that tree every poll, pegs the main thread
> and starves the event loop, and the API stops answering even `/health`.

Sanity checks:

```bash
curl http://localhost:8000/health
curl http://localhost:6333/collections
```

### Environment variables

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` / `GEMINI_API_KEY` | At least one required |
| `GROQ_MODEL` / `GEMINI_MODEL` | Override the default model |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Escalation email |
| `ESCALATION_EMAIL_TO` | IP facilitator inbox |
| Bhashini credentials | Optional; TTS/STT degrade gracefully without them |

### Tests and evaluation

```bash
PYTHONPATH=src python src/test_engines.py     # deterministic engine checks
PYTHONPATH=src python src/test_agents.py      # agent + guardrail checks
PYTHONPATH=src python src/eval_benchmark.py   # 50-question golden benchmark
```

---

## Where it actually stands

Two evaluation tracks measure different things, and they disagree. Both are kept
in the repo on purpose.

**1. Golden benchmark — 49/50 (98%).** `src/eval_benchmark.py`, surfaced in the
Evaluation panel. This runs three *deterministic, LLM-free* checks per question:
does the expected document surface in top-k retrieval, does the relevant engine
return the expected field, and does the confidence guardrail correctly abstain
where it should. It measures the retrieval and engine layers, **not** answer quality.

**2. End-to-end answer grading — 26.5% PASS.** `benchmark_results/`, 400 authored
questions of which 200 have been graded PASS / PARTIAL / FAIL on the real generated
answer (sprint 1: cases 1–100, sprint 2: cases 101–200). The latest 49-case re-run
after the retrieval fixes:

| Verdict | Before | After |
|---|---|---|
| PASS | 16.3% | **26.5%** |
| PARTIAL | 16.3% | 36.7% |
| FAIL | 67.3% | 36.7% |

19 cases improved, 25 held, 5 regressed. That 49-case sample was pre-selected from
the failures and is not representative of the full 200 — it is valid only as a
same-case before/after comparison. The dominant remaining failure mode is
**over-abstention** — declining to answer where a correct, findable Indian statutory
citation exists. The FSSAI/D&C labelling, advertising and manufacturing-licensing
cluster is the weakest area.

Read the second number as the honest one for "will this answer my question well."
The system's guardrails are tuned to prefer silence over invention, which is the
right trade for legal work and is exactly why the first number is high and the
second is not.

---

## Repository layout

```
src/
  api.py                 FastAPI server, all endpoints
  rag_pipeline.py        query → retrieval → rerank → LLM → grounded answer
  final_retriever.py     hybrid retrieval + RRF + rerank + authority weighting
  hybrid_retriever.py    dense + BM25
  chunker.py             legal-aware chunking (Act/Chapter/Section/Rule/page)
  ingest.py, ingest_web.py, embed_chunks.py, qdrant_setup.py
  llm.py, prompt.py, query_expansion.py, context_builder.py
  case_brief_pdf.py      markdown → A4 PDF via PyMuPDF Story
  escalation.py          SMTP delivery with PDF attachment
  db.py, freshness.py, law_versions.py, references.py, bhashini_client.py
  agents/                LangGraph graph, supervisor, 6 specialists, citation agent
  engines/               7 deterministic legal engines
  guardrails/            PII sanitizer, injection filter, confidence scoring
  test_*.py              suite-per-layer checks
sih_frontend_antigrav/   React 19 + Vite frontend (landing + /app product shell)
frontend/                legacy static prototype, superseded
data/raw/                21 source PDFs
data/processed/          chunks.json (3,078), chunks_web.json, app.db, eval_results.json
benchmark_questions/     400 authored test questions
benchmark_results/       sprint reports, root-cause analysis, post-fix verification
docs/                    implementation plan, problem statement, feature analysis, run notes
brag-output/             generated 21s launch video, poster, plan and Hyperframes project
```

---

## Disclaimer

IP-Sakti is an AI-assisted research aid, **not legal advice**. Every answer is
grounded in retrieved statutory text and reports its own confidence, but the
retrieval and generation layers both make mistakes — see the numbers above. Verify
every statutory citation against its primary source, and consult an accredited IP
professional before filing.
