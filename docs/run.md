1. Qdrant (vector DB) — start once, it persists:
docker start ip_sakti_qdrant
# first time only, if the container doesn't exist yet:
# docker run -d --name ip_sakti_qdrant -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant

2. Backend API
source venv/bin/activate
PYTHONPATH=src python -m uvicorn api:app --reload --reload-dir src --port 8000 --app-dir src
Needs GEMINI_API_KEY in .env at repo root (already present).

--reload-dir src is not optional. --reload on its own watches the whole working
directory, which here is ~60,000 files (venv/ ~41k, node_modules/ ~18k) against
129 actual source files. The watcher re-walks that tree on every poll, pegs the
main thread, and starves the event loop — the API then stops answering even
/health. Scoping the watch to src/ is the difference between a responsive server
and one that appears hung.

3. Frontend (React app) — requires Node ≥22:
nvm use 22   # or: export NVM_DIR="$HOME/.nvm"; source "$NVM_DIR/nvm.sh"; nvm use 22
cd sih_frontend_antigrav
npm run dev
Open the printed URL and go to /app for the product wizard (/ is the marketing landing page, /auth → /app after mock login).

Sanity checks once both servers are up:
curl http://localhost:8000/health
curl http://localhost:6333/collections

Optional (backend-only, no servers needed):
PYTHONPATH=src python src/test_engines.py    # engine unit checks
PYTHONPATH=src python src/test_agents.py     # agent/guardrail checks
PYTHONPATH=src python src/eval_benchmark.py  # 50-question golden benchmark