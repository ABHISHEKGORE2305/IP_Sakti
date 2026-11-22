"""
FastAPI application for the IP-Sakti Ayurvedic / Indian IP RAG backend.

Run:
    PYTHONPATH=src python -m uvicorn api:app --reload --reload-dir src --port 8000 --app-dir src
    # or
    PYTHONPATH=src python src/api.py

This module only assembles the app: model loading at startup, middleware,
and the routers. The endpoints live in server/routers/, one module per
product area:

    system         GET  /health, /api/eval-results, /api/references
    chat           POST /ask, /api/chat/
    agent          POST /api/agent (multi-agent graph), /api/ip-route-plan, /api/knowledge-graph
    language       POST /api/translate, /api/tts, /api/stt; GET /api/bhashini/status
    escalate       POST /api/escalate (case brief PDF by email); GET /api/escalate/status
    law_versions   GET  /api/law-versions; POST /api/law-version-query
    privacy        /api/consent, /api/audit-log, /api/privacy/summary, /api/privacy/delete
    admin          /api/admin/corpus, /api/admin/corpus/upload (X-Admin-Key required)

Interactive API docs are served at /docs.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from agents import specialists as agent_specialists
from observability import configure_logging
from rag_pipeline import AyurvedicIPRAG
from server.middleware import request_logging_middleware
from server.routers import admin, agent, chat, escalate, language, law_versions, privacy, system
from server.state import STATE

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models / clients once at startup.
    try:
        rag = AyurvedicIPRAG()
        STATE["rag"] = rag

        # Reuse the already-loaded retriever/reranker/LLM for the agent
        # graph too, instead of it lazily loading a second copy on its
        # first request.
        agent_specialists.configure(
            retriever=rag.retriever,
            llm=rag.llm,
            context_builder=rag.context_builder,
        )
    except Exception as exc:
        # Keep serving so /health can report "degraded" with the reason.
        STATE["error"] = str(exc)
        logger.exception("RAG initialization failed")
    yield
    STATE.update(rag=None, error=None)


app = FastAPI(title="Ayurvedic IP RAG", version=system.SERVICE_VERSION, lifespan=lifespan)

# The static frontend is opened from file:// or a different port during the
# demo, so allow any origin. No credentials are used.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-Id", "Server-Timing", "Retry-After"],
)
app.middleware("http")(request_logging_middleware)

for module in (system, chat, agent, language, escalate, law_versions, privacy, admin):
    app.include_router(module.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
