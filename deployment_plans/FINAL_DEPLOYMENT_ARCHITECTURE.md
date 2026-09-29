# IP-Sakti: Finalized Deployment Architecture

This document serves as the absolute ground truth for the IP-Sakti application deployment. Any AI agent reading this should use it to understand the current cloud infrastructure, exact configurations, historical bugs fixed, and pending architectural gaps.

---

## 1. System Overview
* **Frontend:** Vercel (Vite / SPA)
* **Backend:** AWS ECS Express Mode (Serverless Fargate Container)
* **Vector Database:** Qdrant Cloud (Free Tier)
* **LLM Engine:** Google Gemini API

---

## 2. Backend (AWS ECS Express Mode)
The backend is a FastAPI server running a heavily optimized PyTorch + LangGraph multi-agent RAG pipeline.

### Infrastructure Details
* **Region:** Europe - Stockholm (`eu-north-1`)
* **Service:** AWS Elastic Container Service (ECS) - Express Mode
* **Compute Specs:** 1 vCPU, 4 GB RAM. (Intentionally restricted to stay under the $100 hackathon credit limit. Estimated cost: ~$66/month).
* **Networking:** Application Load Balancer (ALB) attached with HTTPS auto-configured. Exposing Container Port **7860**.
* **Container Registry:** AWS ECR (`530702498762.dkr.ecr.eu-north-1.amazonaws.com/ip-sakti-backend:latest`)

### Environment Variables
* `GEMINI_API_KEY`: API Key for LLM.
* `QDRANT_URL`: URL to the Qdrant Cloud cluster.
* `QDRANT_API_KEY`: API Key for Qdrant Cloud.
* `FRONTEND_URL`: `https://sih-frontend-antigrav.vercel.app` (Crucial for FastAPI CORS Middleware).

### Crucial Hacks & Fixes Implemented
1. **Python 3.10 Compatibility:** The `Dockerfile` uses `python:3.10`. The LangGraph schema (`src/agents/state.py`) was failing with an `ImportError` on `NotRequired`. We hot-patched the file to import `NotRequired` from `typing_extensions` instead of `typing`.
2. **Docker Cache Preservation:** The `Dockerfile` pre-downloads 3GB of AI models in Stage 3. To avoid rebuilding and pushing a 7.3GB image over slow internet during code updates, future agents **MUST** use `docker commit` on a local container to append small code changes to the existing image before pushing to ECR.
3. **AWS Load Balancer Deadlock:** An earlier deployment failed and deadlocked the AWS account's Load Balancer limits. The fix was deleting the broken ECS service, waiting 5 minutes for the invisible ALB to terminate, and re-creating the Express Service.

### ⚠️ Pending Gaps for Future Agents
* **The Threadpool Health Check Death:** `api.py` currently has a synchronous health check (`def health()`). Because RAG queries are synchronous and take 10+ seconds, concurrent requests will exhaust the FastAPI threadpool. The ALB will be unable to reach `/health`, assuming the server is dead, and will terminate the container. **Future Agent Task: Change `def health()` to `async def health()`**.
* **OOM (Out Of Memory) Risk:** The server is running on 4GB of RAM. The `bge-m3` and `bge-reranker-v2-m3` models take ~4.2GB combined. If PyTorch spikes memory during heavy matrix multiplication, the container will instantly die. **Future Agent Task: If the server crashes, scale ECS compute to 8 GB RAM.**

---

## 3. Frontend (Vercel)
The frontend is a static Single Page Application (SPA) built with Vite.

### Infrastructure Details
* **Platform:** Vercel (Hobby Tier)
* **Production URL:** `https://sih-frontend-antigrav.vercel.app`
* **Root Directory:** `./` (Cleared from Vercel settings to allow direct GitHub/CLI deployment).

### Environment Variables
* `VITE_API_URL`: `https://ip-0550419baf1a49b4bba8957b30a6c91f.ecs.eu-north-1.on.aws` (Points directly to the AWS ALB).

### Crucial Hacks & Fixes Implemented
1. **SPA Routing 404 Fix:** Vercel was throwing `404 Not Found` when refreshing or directly linking to sub-pages like `/auth`. We added a `vercel.json` file in the frontend directory with a rewrite rule (`/(.*)` -> `/index.html`) to force Vercel to route everything to the JavaScript bundle.
2. **405 Method Not Allowed Fix:** The legacy code in `src/lib/api.js` was ignoring the Vercel cloud environment variables and attempting to send API requests to `window.location.origin` (Vercel itself). We modified `api.js` to strictly prioritize `import.meta.env.VITE_API_URL`.

### ⚠️ Pending Gaps for Future Agents
* **The 60-Second Fetch Timeout:** `src/lib/api.js` has a hardcoded `timeoutMs = 60000`. The LangGraph backend pipeline is highly complex and runs on a slow 1 vCPU Fargate instance; it will frequently take 75+ seconds to answer a query. At exactly 60 seconds, the frontend will violently abort the connection and show a "Failed to fetch" error. **Future Agent Task: Increase `timeoutMs` to `120000` (120 seconds).**

---

## 4. Financial Guardrails
* **Budget:** $120 AWS Credits.
* **Burn Rate:** ~$66 / month for the backend infrastructure.
* **AWS Budgets:** Configured at $20, $40, $60, $80, and $100 thresholds. Any spike in usage or undetected auto-scaling will trigger an immediate email alert.
