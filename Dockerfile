# ============================================================
# IP-Sakti Backend — Optimized Dockerfile
# ============================================================
# Layer order is tuned for maximum Docker cache reuse:
#   1. System deps        (rarely change)
#   2. Python packages    (change occasionally)
#   3. ML model download  (change almost never)
#   4. Application code   (changes frequently)
#
# This means editing a Python file does NOT re-download
# 2+ GB of ML models or re-install pip packages.
# ============================================================

# --- Stage 1: Base image ---
FROM python:3.10-slim

WORKDIR /app

# --- Stage 2: Python dependencies (cached unless requirements.txt changes) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 3: Pre-download ML models (cached unless model names change) ---
# Without this step, sentence_transformers downloads these 2-3 GB models
# every single time the container starts. By baking them into the image,
# the app starts in seconds instead of minutes.
RUN python -c "\
from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('BAAI/bge-m3'); \
CrossEncoder('BAAI/bge-reranker-v2-m3')"

# --- Stage 4: Application code (rebuilt on every code change, but fast) ---
COPY src/ ./src/
COPY data/ ./data/

# Tell Python where to find our modules (e.g. import config, import llm)
ENV PYTHONPATH=/app/src

# Hugging Face Spaces requires port 7860
EXPOSE 7860

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "7860"]
