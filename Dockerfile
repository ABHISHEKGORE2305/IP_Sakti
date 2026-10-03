# ============================================================
# IP-Sakti Backend (deployment branch) - CPU-only, cache-friendly
# Layer order: torch -> requirements -> model weights -> code
# so editing src/ rebuilds in seconds without re-downloading models.
# Build on the EC2 host itself (no registry push needed).
# ============================================================
FROM python:3.10-slim

# Unbuffered stdout so print() / [timing] lines reach `docker logs` immediately.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/opt/hf \
    PYTHONPATH=/app/src

WORKDIR /app

# CPU-only torch first: otherwise pip resolves the CUDA build (several GB of
# nvidia libraries this host can never use). Version matches the tested env.
RUN pip install --no-cache-dir torch==2.11.0 --extra-index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the model weights into the image (cached unless model names change).
RUN python -c "\
from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('BAAI/bge-m3'); \
CrossEncoder('BAAI/bge-reranker-v2-m3')"

COPY src/ ./src/
COPY healthcheck.py .

# chunks.json feeds BM25; it MUST be the same file that was synced to Qdrant
# (scripts/sync_qdrant.py), otherwise dense and BM25 retrieve different chunks.
RUN mkdir -p data/processed
COPY data/processed/chunks.json data/processed/

EXPOSE 7860

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
