"""
Central configuration: Qdrant connection, model names, retrieval/fusion
tuning knobs, and confidence thresholds. Values here are defaults only —
every consumer still accepts constructor/call overrides, so tests and
one-off scripts can override without touching this file.
"""

# --------------------------------------------------------------------
# Qdrant
# --------------------------------------------------------------------
import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
COLLECTION_NAME = "medical_documents"
VECTOR_SIZE = 1024

CHUNKS_PATH = "data/processed/chunks.json"
WEB_CHUNKS_PATH = "data/processed/chunks_web.json"          # src/ingest_web.py output, merged in by hybrid_retriever.py
WEB_SOURCES_MANIFEST_PATH = "data/processed/web_sources_manifest.json"
WEB_SOURCE_STALE_AFTER_DAYS = 60                             # default; overridable per-source via web_sources.WEB_SOURCES

# --------------------------------------------------------------------
# Models
# --------------------------------------------------------------------
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"

# --------------------------------------------------------------------
# Retrieval & fusion
# --------------------------------------------------------------------
# Benchmark questions routinely span 3-4 regimes at once (e.g. classify the
# formulation under the D&C Act, then patentability under the Patents Act,
# then ABS duties under the BD Act). At top_k=6 the later regimes were being
# crowded out of the context entirely.
TOP_K = 12                   # final chunks returned to the LLM
# candidates pulled per retriever before fusion/rerank. On the 40-query
# retrieval suite (benchmark_retrieval_comparison.py), 12 -> 24 raised
# relevant chunks in the top 12 from 8.4 to 9.2 and hit@12 from 39 to 40, for
# +1.6s/query on an M4; 40 added 0.1 more at double the rerank time. The
# EC2 deployment ran 12 to stay inside its request timeout.
CANDIDATE_K = int(os.getenv("CANDIDATE_K", "24"))
RRF_K = 60                   # reciprocal-rank-fusion smoothing constant
# International-scope queries also search India-labelled sources (the TKDL
# factsheet, the Patents Act's PCT/Budapest provisions and the Trade Marks
# Act's Madrid chapter describe the international mechanisms), but rank them
# below international sources by this much on the 0-1 reranker scale. On the
# 26 International benchmark cases with findable evidence, a hard India
# exclusion found it in 12; this soft penalty in 16 (a strict superset) with
# ~0.6 of 12 slots going to India sources. India scope stays a hard filter.
OFF_JURISDICTION_PENALTY = 0.2
DEFAULT_AUTHORITY_WEIGHT = 0.50
# Groq free tier allows 8,000 tokens/min for gpt-oss-120b/20b (7,000 for qwen) and
# rejects (HTTP 413) any single request whose input + max_tokens exceeds that.
# The answer prompt is capped so input (~11k context chars + ~4.5k chars of
# instructions/query = ~5k tokens) + LLM_MAX_OUTPUT_TOKENS stays under it.
# See llm.py for the per-model enforcement. Raise both only on a paid Groq tier.
#
# The 3.0 chars/token estimate was far too cautious for gpt-oss: a real
# 15.8k-char answer prompt measured 3,636 prompt tokens (4.3 chars/token).
# At 3.6 the estimate still overcounts by ~20%, and the freed room goes to
# context: 14k chars fits ~11 of the 12 retrieved chunks instead of ~8.
MAX_CONTEXT_CHARS = 14000
LLM_MAX_OUTPUT_TOKENS = 2000   # hard ceiling on generated tokens (incl. reasoning)
LLM_CHARS_PER_TOKEN = 3.6      # still conservative; gpt-oss measures ~4.3 on this corpus
LLM_TOKEN_MARGIN = 300         # slack under each model's limit
LLM_MIN_OUTPUT_TOKENS = 600    # below this a model is skipped, not squeezed

# Score bonuses added on top of the cross-encoder score when the query
# names an explicit statutory provision (Section/Rule/Form).
EXACT_REFERENCE_BONUS = 2.0
SAME_SECTION_BONUS = 0.6
STATUTORY_SOURCE_BONUS = 0.5

# --------------------------------------------------------------------
# Confidence & safe abstention (Phase 1.4 formula)
# --------------------------------------------------------------------
HIGH_THRESHOLD = 0.75
MEDIUM_THRESHOLD = 0.50

# bge-reranker-v2-m3 empirically scores irrelevant query/passage pairs
# around ~0.0001-0.0004, not negative, so the sigmoid midpoint/steepness
# below are recalibrated for that (see guardrails/confidence.py).
RERANK_THRESHOLD = 0.15
RERANK_STEEPNESS = 12.0

# --------------------------------------------------------------------
# API server
# --------------------------------------------------------------------
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ALLOW_ORIGINS = ["*"]

# --------------------------------------------------------------------
# Persistence (src/db.py) — audit log, consent, corpus admin. No-login,
# session-id-scoped SQLite. See db.py's module docstring.
# --------------------------------------------------------------------
DB_PATH = "data/processed/app.db"

# winning_features.md item 19 — written by `eval_benchmark.py --out-json`,
# read by GET /api/eval-results.
EVAL_RESULTS_PATH = "data/processed/eval_results.json"
