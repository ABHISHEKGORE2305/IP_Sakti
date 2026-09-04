"""
Minimal FastAPI server for the Ayurvedic / Indian patent RAG backend.

Run:
    PYTHONPATH=src python -m uvicorn api:app --port 8000
    # or
    PYTHONPATH=src python src/api.py

Endpoints:
    GET  /health     -> {"status": "ok", ...}
    POST /ask        -> {"answer", "sources", "retrieved", "error"}
    POST /api/chat/  -> {"answer", "citations", "retrieved", "sources", "error"}
                        (compatibility shape consumed by the web frontend)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_pipeline import AyurvedicIPRAG


SERVICE_NAME = "ayurvedic-ip-rag"
SERVICE_VERSION = "1.0"

_STATE: dict = {"rag": None, "error": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models / clients once at startup.
    try:
        _STATE["rag"] = AyurvedicIPRAG()
    except Exception as exc:  # noqa: BLE001
        _STATE["error"] = str(exc)
        print(f"[api] RAG initialization failed: {exc}")
    yield
    _STATE.clear()


app = FastAPI(title="Ayurvedic IP RAG", lifespan=lifespan)

# The static frontend is opened from file:// or a different port during the
# demo, so allow any origin. No credentials are used.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------


class AskRequest(BaseModel):
    query: str
    top_k: int | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list
    retrieved: list
    error: str | None = None


class ChatRequest(BaseModel):
    # The frontend has historically sent a few different field names /
    # extra fields; accept them all and ignore what we do not use.
    query: str | None = None
    message: str | None = None
    session_id: str | None = None
    jurisdiction: str | None = None
    jurisdiction_filter: str | None = None
    extract_metadata: bool | None = None
    top_k: int | None = None


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _citations_from_retrieved(retrieved: list) -> list:
    """Shape retrieved chunks into the {statute, section, title, page} form
    the frontend citation UI expects."""

    citations = []
    for item in retrieved:
        citations.append(
            {
                "statute": item.get("document") or "Source",
                "section": (
                    item.get("legal_reference")
                    or (f"p.{item.get('page')}" if item.get("page") else "")
                ),
                "title": item.get("snippet") or item.get("text", "")[:120],
                "page": item.get("page"),
                "chunk_id": item.get("chunk_id"),
                "reranker_score": item.get("reranker_score"),
            }
        )
    return citations


def _run_query(query: str, top_k: int | None) -> dict | None:
    """Shared guard + dispatch. Returns None when the backend is not ready."""

    rag = _STATE.get("rag")
    if rag is None:
        return None
    return rag.answer(query, top_k=top_k)


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------


@app.get("/health")
def health() -> dict:
    if _STATE.get("error"):
        status = "degraded"
    elif _STATE.get("rag") is None:
        status = "starting"
    else:
        status = "ok"

    return {
        "status": status,
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "detail": _STATE.get("error"),
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:

    query = (request.query or "").strip()

    if not query:
        return AskResponse(
            answer="Please provide a non-empty 'query'.",
            sources=[],
            retrieved=[],
            error="empty_query",
        )

    result = _run_query(query, request.top_k)
    if result is None:
        return AskResponse(
            answer=(
                "The backend is not ready. "
                + (_STATE.get("error") or "Models/services are still loading.")
            ),
            sources=[],
            retrieved=[],
            error="not_ready",
        )

    return AskResponse(
        answer=result["answer"],
        sources=result["sources"],
        retrieved=result["retrieved"],
        error=result.get("error"),
    )


@app.post("/api/chat/")
def api_chat(request: ChatRequest) -> dict:

    query = (request.query or request.message or "").strip()

    if not query:
        return {
            "answer": "Please provide a non-empty question.",
            "citations": [],
            "retrieved": [],
            "sources": [],
            "error": "empty_query",
        }

    result = _run_query(query, request.top_k)
    if result is None:
        return {
            "answer": (
                "The backend is not ready. "
                + (_STATE.get("error") or "Models/services are still loading.")
            ),
            "citations": [],
            "retrieved": [],
            "sources": [],
            "error": "not_ready",
        }

    return {
        "answer": result["answer"],
        "citations": _citations_from_retrieved(result["retrieved"]),
        "retrieved": result["retrieved"],
        "sources": result["sources"],
        "error": result.get("error"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
