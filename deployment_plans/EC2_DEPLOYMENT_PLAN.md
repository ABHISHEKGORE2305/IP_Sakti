# IP-Sakti — Backend Redeployment Plan (EC2 + Docker + Caddy)

Supersedes `FINAL_DEPLOYMENT_ARCHITECTURE.md` (ECS Express, now torn down).
Written 2026-10-03 against the `deployment` branch. Nothing in this plan has been executed yet except where marked **DONE**.

---

## 0. What we learned (why the old deployment failed)

| Finding | Evidence |
|---|---|
| **Chat 504s were CPU starvation, not memory or Qdrant.** | Live test: `/health` 200 in 1.9 s; `/api/chat/` → 504 at 60.7 s (ALB idle timeout). CPU 0.1 % idle → 99.8 % of the single vCPU during the request. Memory only 17.6 % → 20 % of 8 GB. |
| One 1-vCPU container ran bge-m3 query embedding + cross-encoder rerank + several sequential LLM calls. | `final_retriever.py` wraps all torch inference in a `threading.Lock()` (single-concurrency). |
| **Qdrant Cloud held a different chunking than `chunks.json`.** | Cloud: 2,504 points. Local `chunks.json`: 3,078. Only 920 point IDs overlap and **907 of those hold different text**. 10 documents (e.g. `drugs_and_cosmetics_rules_1945`, 1,165 chunks) were absent from Qdrant. BM25 (local file) and dense search (cloud) were retrieving from different corpora. |
| Dead fallback models on `deployment` (`gemini-1.5-*`, old Groq names). | `src/llm.py` — **DONE**: replaced with the tested `main` version (staged, uncommitted). |
| Logs were empty/useless. | No `PYTHONUNBUFFERED`; zero request lines for a request that ran > 3 min. |
| Orphan sprawl. | 12 task defs, 15 ECR image entries (~7.3 GB each), 3 log groups, 2 target groups. **DONE**: service, task defs, ECR repo, log groups removed. ALB/target groups should disappear with the service (verify). |

Vectors in `chunks.json` are valid: re-embedding 5 random chunks with local bge-m3 gave cosine **1.0000** vs the stored vectors. No re-embedding needed.

## 1. Decisions

| Topic | Decision | Reason |
|---|---|---|
| Compute | **One EC2 instance, Docker (Compose), Caddy for HTTPS** | You can SSH in and read `docker logs`; no ECS/ALB/task-def sprawl; stop the instance when idle to save credits. |
| Region | **`us-east-1`** (N. Virginia), same region as the Qdrant cluster, so every query avoids a cross-ocean hop. Cheapest region for EC2 too. | |
| Size | Start **4 vCPU / 8 GB compute-optimised** (c-family `xlarge`). Move to `2xlarge` only if the benchmark in §6 misses target. | Memory observed ≈ 1.6 GB for both models; CPU is the bottleneck. Confirm the family is offered in your region (§5.1). |
| Qdrant | **Stay on Qdrant Cloud** (cluster is in `us-east-1`). | Already provisioned; 3,078 × 1024-dim vectors is ≈ 15 MB of vectors, well inside the free tier. |
| LLM | Primary/fallback models from `main`'s `llm.py` (see §3). | Tested locally by you. |
| Frontend | Stays on Vercel, `VITE_API_URL` → new HTTPS backend URL. | Works today. |
| Build | **Build on the EC2 instance** from the `deployment` branch. | No 7 GB image pushes from your home connection, no registry to clean up. |
| Admin/ops | Create an IAM user (not root) for day-to-day CLI use. | CLI is currently signed in as root. |

**Honest latency expectation:** retrieval should drop from "minutes" to a few seconds on 4 vCPU. End-to-end answer time is then dominated by the LLM calls in the LangGraph pipeline, so expect roughly **5–20 s** per answer, not instant. §4.4 measures each stage so we tune facts, not guesses.

---

## 2. Phase A — Fix the Qdrant data (do this first; independent of AWS)

Script (**written, dry-run verified**): `scripts/sync_qdrant.py`.
It reads `.env` (`QDRANT_URL`, `QDRANT_API_KEY`), never writes without `--apply`, never deletes without `--prune`.

```bash
python scripts/sync_qdrant.py                  # dry run: what differs (read-only)
python scripts/sync_qdrant.py --verify 5       # re-embed 5 chunks locally, compare vectors
python scripts/sync_qdrant.py --apply --prune  # upsert all 3,078, delete orphans, ensure indexes
```

Expected after `--apply --prune`: `Qdrant now has 3078 points (expected 3078)`.

- **Why `--prune`:** the cloud holds a different chunking. Same-ID points have stale text and ~1,600 points match nothing in `chunks.json`; leaving them gives dense search stale text that BM25 never sees.
- **Indexes:** the cluster runs strict mode with `unindexed_filtering_retrieve=false`, so filtering on an unindexed field **errors**. `retriever.py` filters on `jurisdiction` and `document_id`; both are keyword-indexed (they exist now; the script re-creates them if missing). If you add a new filter field later, add it to `INDEXED_FIELDS` in the script.
- **Rollback:** before `--apply --prune`, take a Qdrant Cloud snapshot (Cloud console → cluster → Backups) or the REST call `POST {QDRANT_URL}/collections/medical_documents/snapshots` and download it. The prune is not undoable otherwise.
- **After:** `curl -H "api-key: …" $QDRANT_URL/collections/medical_documents` → `points_count: 3078`. Re-check that `chunks.json` is the file shipped in the image (§4.2); the image's BM25 and Qdrant must come from the same file.

## 3. Phase B — Port new code from `main` without merging

Do **not** merge. On `deployment`, bring over only what's new. From the diff (`git diff deployment main -- src`):

| File | Action | Why |
|---|---|---|
| `src/llm.py` | **DONE** (`git checkout main -- src/llm.py`) | Live Groq/Gemini model names. |
| `src/case_brief_pdf.py` | take from `main` | New; uses `pymupdf` (already in requirements). |
| `src/escalation.py` | take from `main` | PDF attachment support. |
| `src/api.py` | take from `main` | Escalate-with-PDF. Only that hunk differs. |
| `src/config.py` | **do not take** | `main` hard-codes `QDRANT_URL=localhost`, drops `QDRANT_API_KEY`, and sets `CANDIDATE_K=40` (the cause of earlier 504s). Keep deployment's. |
| `src/agents/state.py` | **do not take** | Deployment imports `NotRequired` from `typing_extensions` (Py 3.10 fix). |
| `src/retriever.py`, `src/vector_store.py` | **do not take** | Deployment's Qdrant `api_key` wiring. |
| `requirements.txt`, `Dockerfile`, `.dockerignore` | **never take** | Why you can't merge. |

```bash
git checkout deployment
git checkout main -- src/case_brief_pdf.py src/escalation.py src/api.py   # llm.py already staged
git diff --cached --stat        # expect only those 4 files
python -c "import ast,sys; [ast.parse(open(f,encoding='utf-8').read()) for f in ['src/api.py','src/llm.py','src/escalation.py','src/case_brief_pdf.py']]"
```

Fallback model matrix (from `main/src/llm.py`):

| Provider | Order | Env var |
|---|---|---|
| Groq (used first if `GROQ_API_KEY` is set) | `openai/gpt-oss-120b` → `openai/gpt-oss-20b` → `qwen/qwen3.8-27b` | `GROQ_API_KEY`, optional `GROQ_MODEL` |
| Gemini (fallback after all Groq models fail, or primary if no Groq key) | `gemini-flash-latest` → `gemini-3.5-flash` → `gemini-flash-lite-latest` | `GEMINI_API_KEY`, optional `GEMINI_MODEL` |

**Before deploying, validate both lists against your real keys** (names go stale). Add `scripts/check_models.py` that lists `GET https://api.groq.com/openai/v1/models` and `client.models.list()` for Gemini, then does a one-token completion on every model in the lists. Run it on the EC2 box with the production `.env`.

## 4. Phase C — Code & container changes on `deployment`

### 4.1 Code changes
1. **Unbuffered logs (DONE):** `ENV PYTHONUNBUFFERED=1` in the Dockerfile.
2. **Health that tells the truth (DONE):** `/health` is now `async def`; `healthcheck.py` asserts `status == ok` so it isn't starved by the threadpool. Healthcheck must assert `"status":"ok"` in the body, not just HTTP 200 (`api.py` stores startup failures in `_STATE["error"]` and keeps serving).
3. **Timing logs (DONE):** `[timing] retrieval hybrid=… rerank=… candidates=…` in `final_retriever.py` and `[timing] llm.generate …` in `llm.py`. The agent path's total is the sum of these lines. Original idea: embed, dense search, BM25, fuse, rerank, each LLM call, total. One line per request, e.g. `[timing] embed=0.4s dense=0.2s bm25=0.1s rerank=3.1s llm=6.8s total=10.9s`.
4. **Threads:** torch already uses all cores by default; keep `--workers 1` (models are per process and the inference lock serialises anyway).
5. **Protect `/api/admin/*`:** `POST /api/admin/corpus/upload` has no auth and writes PDFs to disk. Block it in Caddy (basicauth) or reject unless an env token matches.
6. **CORS:** leave `["*"]` (no cookies used) or restrict to the Vercel URL.
7. **Keep `CANDIDATE_K = 12`** (deployment's value). Revisit only with timing data.

### 4.2 Requirements and Dockerfile
- **Pins (DONE, uncommitted):** 14 direct deps pinned to the versions in your local Python 3.10 env. `groq`, `google-genai`, `beautifulsoup4` are unpinned because that env doesn't have them. After the first good build run `docker run --rm ipsakti pip freeze > requirements.lock` and pin from that. **Do not copy pins from the old plan file** (`deployment-plan.md`): they came from `main`'s Python 3.14 venv.
- **CPU-only torch** installed first, otherwise pip pulls CUDA wheels (several GB, slower build/pull):
  ```dockerfile
  FROM python:3.10-slim
  ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 HF_HOME=/opt/hf
  WORKDIR /app
  RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
      SentenceTransformer('BAAI/bge-m3'); CrossEncoder('BAAI/bge-reranker-v2-m3')"
  COPY src/ ./src/
  RUN mkdir -p data/processed
  COPY data/processed/chunks.json data/processed/
  ENV PYTHONPATH=/app/src
  EXPOSE 7860
  CMD ["uvicorn","src.api:app","--host","0.0.0.0","--port","7860","--workers","1"]
  ```
  Layer order (torch → requirements → model download → code) keeps code-only rebuilds to seconds. This is the cache behaviour you wanted; it works only because `deployment` keeps its own requirements file.
- **Delete the `docker commit` hack** from the workflow: it layers patched images on top of each other and hides what's running. Always `docker compose build`.
- **Python version:** stay on 3.10 (what you've tested on `deployment`).
- **Smoke test the image locally before touching AWS:** `docker build -t ipsakti .`, run with `.env`, hit `/health`, then one `/api/chat/` call.

### 4.3 Compose and TLS (files to add to the repo, `deployment` branch only)
`docker-compose.yml`
```yaml
services:
  api:
    build: .
    env_file: .env
    restart: unless-stopped
    mem_limit: 6g
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request,sys;sys.exit(0 if b'\\\"status\\\":\\\"ok\\\"' in urllib.request.urlopen('http://localhost:7860/health').read() else 1)\""]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 180s
  caddy:
    image: caddy:2
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes: ["./Caddyfile:/etc/caddy/Caddyfile", "caddy_data:/data"]
    depends_on: [api]
volumes:
  caddy_data:
```
`Caddyfile` (replace host)
```
api.<your-host> {
    @admin path /api/admin/*
    respond @admin 403
    reverse_proxy api:7860 {
        transport http { response_header_timeout 180s }
    }
}
```
HTTPS is required: Vercel is HTTPS, so a plain-HTTP backend is blocked as mixed content. Hostname options: your own domain (A record → Elastic IP), or a free `<ip>.nip.io` / DuckDNS name; Let's Encrypt rate-limits shared domains, so don't loop on failed issuance.

### 4.4 Latency measurement (decides instance size)
After deploy, send the same 3 questions (one single-regime, one 3-regime like your Ashwagandha example, one follow-up) three times each and read the `[timing]` lines. Targets: retrieval (embed+search+rerank) ≤ 4 s; total ≤ 20 s. If rerank dominates → go `2xlarge` or cut candidates. If LLM calls dominate → reduce sequential agent calls or pick a faster primary model; more CPU won't help.

## 5. Phase D — AWS build-out

### 5.1 Before creating anything
1. Create an **IAM user** (or SSO) with EC2 permissions; stop using root. Delete any root access keys.
2. **Budget alerts** already exist at $20…$100; confirm they still do (Billing → Budgets).
3. **Region = `us-east-1`** (your Qdrant cluster's region). If most users are in India/Europe, the extra browser-to-backend latency (~150-250 ms) is small next to the LLM time; a Mumbai/Stockholm box would instead add a transatlantic hop to every Qdrant call.
4. Check the instance family exists there and its price:
   ```bash
   aws ec2 describe-instance-type-offerings --region <r> --filters Name=instance-type,Values=c7i.xlarge,c6i.xlarge,c7a.xlarge --query "InstanceTypeOfferings[].InstanceType"
   ```
   Use any available 4 vCPU / 8 GB compute-optimised type; confirm the hourly price in the pricing page. Do **not** use `t3`/`t4g`: burstable CPU credits run out under sustained torch inference.

### 5.2 Create
- AMI: Amazon Linux 2023. Storage: **40 GiB gp3** (image ≈ 6–8 GB with CPU torch, plus build cache; resize later if needed).
- Security group: 80/443 from anywhere; 22 from **your IP only** (or use SSM Session Manager and open no SSH). Never open Qdrant/7860.
- Elastic IP attached (stable URL across stop/start). Note: an EIP on a stopped instance is still billed hourly; that is the price of a stable address.
- Key pair downloaded once.

### 5.3 Provision
```bash
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user          # re-login
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose && sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
git clone -b deployment <your-repo-url> ~/ip-sakti && cd ~/ip-sakti
nano .env     # created on the box, never committed: GROQ_API_KEY, GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY, FRONTEND_URL, SMTP_*, ESCALATION_EMAIL_TO
docker compose build            # first build is slow (torch + ~2.7 GB of weights)
docker compose up -d
docker compose logs -f api      # wait for the model-load lines; /health flips starting → ok
```
Rotate any key that has appeared in a chat, log or commit; the earlier deployment doc stored raw keys in task definitions.

### 5.4 Frontend
- Vercel env `VITE_API_URL=https://api.<your-host>` then redeploy.
- `src/lib/api.js` fetch timeout: raise from 60 000 to 120 000 ms (kept as a safety margin even after the speed work).

## 6. Verification checklist (all must pass before you call it done)

1. `curl -s https://api.<host>/health` → `{"status":"ok",...}` (`starting`/`degraded` = broken even with HTTP 200).
2. `curl -H "api-key: …" $QDRANT_URL/collections/medical_documents` → `points_count: 3078`.
3. `python scripts/check_models.py` on the box: every listed Groq and Gemini model answers (or is flagged to remove).
4. `POST /api/chat/` with the Ashwagandha / Section 3(p) question returns non-empty `sources` and a confidence band, in the §4.4 target time. Repeat 3×.
5. `POST /api/agent` for a 3-regime question; check `[timing]` lines.
6. Browser: full chat from the Vercel site, no `Failed to fetch`; DevTools Network shows 200.
7. `/api/admin/*` returns 403 from outside.
8. `POST /api/escalate` to a test address → PDF attachment arrives (new `case_brief_pdf.py`).
9. `docker stats` while a query runs: CPU high, memory comfortably < `mem_limit`.
10. `docker compose restart api` and a full reboot of the instance → service returns to `ok` on its own (restart policy works).
11. A forced LLM failure test: set `GROQ_MODEL=bogus` in `.env`, restart, confirm the fallback chain answers and logs which model served it; then revert.

## 7. Cost and operations
- Compute bills only while the instance runs. `aws ec2 stop-instances` when idle; the volume (~$3–4/mo for 40 GiB) and EIP (~$3.6/mo) continue. At the typical ~$0.17–0.20/hour for a 4-vCPU compute instance, 24/7 uses ~$130–145/month, more than your $120 credits, so stop it outside demos or review days.
- Update flow: `git pull && docker compose build && docker compose up -d`; the heavy layers stay cached unless `requirements.txt` changes.
- Logs: `docker compose logs --tail 200 api`. Optional: `awslogs`/CloudWatch agent later.
- Do not use `docker commit` or push multi-GB images again.

## 8. Known risks and open items
- **Region/size/price are unverified** until §5.1 is run. Pick the instance after seeing offerings and your Qdrant region.
- **Single replica, single-concurrency inference:** two simultaneous users queue behind the inference lock. Fine for a demo; for real traffic, hosted embedding/rerank APIs (bge-m3 and bge-reranker-v2-m3 are served by several providers, which preserves the existing index) would remove local inference entirely. Evaluate only if §4.4 misses the target.
- **SQLite (`data/processed/app.db`)** lives inside the container. It is lost on rebuild unless `data/` is bind-mounted; if audit/consent records matter, add `volumes: ["./data/processed:/app/data/processed"]` — but then `chunks.json` must exist on the host (copy it from the repo) or the bind mount hides the baked-in file.
- **`git` hygiene:** `qdrant_storage/` (395 MB) is tracked on `deployment` and unused with Qdrant Cloud; `git rm -r --cached qdrant_storage` when convenient.
- `/api/admin/corpus/upload` writes a file but doesn't re-index; don't present it as a working feature.
- No CI yet. A GitHub Actions deploy-over-SSH job is the natural follow-up once this is stable.
