source .venv/bin/activate

docker pull qdrant/qdrant


docker run -p 6333:6333 -p 6334:6334 \
  -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
  qdrant/qdrant

REST API → http://localhost:6333
gRPC     → localhost:6334
Dashboard → http://localhost:6333/dashboard

docker start ip_sakti_qdrant

PYTHONPATH=src ./venv/bin/python -m uvicorn api:app --reload --port 8000

cd sih_frontend_antigrav
npm run dev
