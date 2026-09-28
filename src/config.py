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

# --------------------------------------------------------------------
# Models
# --------------------------------------------------------------------
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"

# --------------------------------------------------------------------
# Retrieval & fusion
# --------------------------------------------------------------------
TOP_K = 6                    # final chunks returned to the LLM
CANDIDATE_K = 20             # candidates pulled per retriever before fusion/rerank
RRF_K = 60                   # reciprocal-rank-fusion smoothing constant
DEFAULT_AUTHORITY_WEIGHT = 0.50
MAX_CONTEXT_CHARS = 12000

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
CORS_ALLOW_ORIGINS = [_frontend_url] if _frontend_url else ["*"]
