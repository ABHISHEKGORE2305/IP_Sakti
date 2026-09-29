"""
Central configuration: Qdrant connection, model names, retrieval/fusion
tuning knobs, and confidence thresholds. Values here are defaults only —
every consumer still accepts constructor/call overrides, so tests and
one-off scripts can override without touching this file.
"""

import os

# --------------------------------------------------------------------
# Qdrant
# --------------------------------------------------------------------
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
CANDIDATE_K = 40             # candidates pulled per retriever before fusion/rerank
RRF_K = 60                   # reciprocal-rank-fusion smoothing constant
DEFAULT_AUTHORITY_WEIGHT = 0.50
MAX_CONTEXT_CHARS = 24000

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
API_PORT = int(os.getenv("PORT", "8000"))
_frontend_url = os.getenv("FRONTEND_URL")
if _frontend_url and _frontend_url.strip():
    # Browsers send Origin headers without trailing slashes. 
    # If the user accidentally included one in their HF secret, this strips it to prevent CORS errors.
    CORS_ALLOW_ORIGINS = [_frontend_url.strip().rstrip("/")]
else:
    CORS_ALLOW_ORIGINS = ["*"]

# --------------------------------------------------------------------
# Persistence (src/db.py) — audit log, consent, corpus admin. No-login,
# session-id-scoped SQLite. See db.py's module docstring.
# --------------------------------------------------------------------
DB_PATH = "data/processed/app.db"

# winning_features.md item 19 — written by `eval_benchmark.py --out-json`,
# read by GET /api/eval-results.
EVAL_RESULTS_PATH = "data/processed/eval_results.json"
