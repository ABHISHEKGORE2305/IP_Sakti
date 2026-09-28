"""
FastAPI server for the IP-Sakti Ayurvedic / Indian IP RAG backend.

Run:
    PYTHONPATH=src python -m uvicorn api:app --port 8000
    # or
    PYTHONPATH=src python src/api.py

Endpoints:
    GET  /health       -> {"status": "ok", ...}
    POST /ask          -> {"answer", "sources", "retrieved", "error"}
    POST /api/chat/    -> {"answer", "citations", "retrieved", "sources", "error"}
                          (compatibility shape consumed by the legacy frontend/ UI)
    POST /api/agent     -> runs the Sprint 3/4 multi-agent graph (agents.graph.run):
                          jurisdiction toggle, forced_agent (issue picker),
                          classification_inputs, target_market/market_inputs,
                          gratk_inputs, confidence/citation reports.
    POST /api/translate -> Gemini-based translation of an answer into one of
                          the Sprint 5 Indian languages, preserving bracketed
                          statutory citations in English. Bhashini API access
                          was not available, so this is a pragmatic substitute
                          using the same Gemini client already in use — swap
                          the implementation for the real Bhashini API when
                          credentials are available.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import graph as agent_graph
from agents import specialists as agent_specialists
from llm import LLMError
from prompt import TRANSLATION_PROMPT
from rag_pipeline import AyurvedicIPRAG
import config


SERVICE_NAME = "ayurvedic-ip-rag"
SERVICE_VERSION = "1.0"

_STATE: dict = {"rag": None, "error": None}

_LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "pa": "Punjabi",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models / clients once at startup.
    try:
        rag = AyurvedicIPRAG()
        _STATE["rag"] = rag

        # Reuse the already-loaded retriever/reranker/LLM for the agent
        # graph too, instead of it lazily loading a second copy on its
        # first request.
        agent_specialists.configure(
            retriever=rag.retriever,
            llm=rag.llm,
            context_builder=rag.context_builder,
        )
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
    allow_origins=config.CORS_ALLOW_ORIGINS,
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


class AgentRequest(BaseModel):
    query: str
    jurisdiction: str = "India"                 # "India" | "International"
    forced_agent: str | None = None             # e.g. "patent_agent" — the wizard's issue picker
    classification_inputs: dict | None = None    # engines.classifier.classify_product kwargs
    target_market: str | None = None             # "US" | "EU" | "UK"
    market_inputs: dict | None = None             # engines.intl_engine.advise_market kwargs
    gratk_inputs: dict | None = None                # engines.intl_engine.gratk_disclosure_requirement kwargs
    tk_inputs: dict | None = None                    # engines.tk_engine.analyze_tk_patentability kwargs
    ipr_inputs: dict | None = None                   # {"regime": ...} for engines.ipr_router.advise_regime
    abs_inputs: dict | None = None                    # engines.abs_engine.analyze_abs_compliance kwargs
    reg_inputs: dict | None = None                    # engines.reg_engine.analyze_regulatory_pathway kwargs


class AgentSource(BaseModel):
    document: str | None = None
    legal_reference: str | None = None
    page: int | None = None
    chunk_id: str | None = None
    snippet: str | None = None
    reranker_score: float | None = None
    authority_weight: float | None = None


class AgentResponse(BaseModel):
    final_answer: str
    sources: list[AgentSource]
    selected_agents: list[str]
    routing_reason: str | None = None
    confidence: dict | None = None
    citations: dict | None = None
    engine_results: dict | None = None
    pii_redactions: list[dict] | None = None   # [{"type": "aadhaar"}, ...] - types only, DPDP audit trail
    error: str | None = None


class TranslateRequest(BaseModel):
    text: str
    target_language: str    # ISO code, see _LANGUAGE_NAMES


class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str
    error: str | None = None


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


def _agent_sources(retrieved: list) -> list[dict]:
    """
    Shape the agent graph's `retrieved` chunks (full text/score/authority)
    into the richer AgentSource form the Sprint 5 citation inspector uses
    — the graph's own `sources` field (see agents.graph.output_synthesizer)
    intentionally strips this down for the plain answer payload.
    """

    sources = []
    for item in retrieved or []:
        sources.append({
            "document": item.get("document"),
            "legal_reference": item.get("legal_reference"),
            "page": item.get("page"),
            "chunk_id": item.get("chunk_id"),
            "snippet": " ".join((item.get("text") or "").split())[:280],
            "reranker_score": item.get("reranker_score"),
            "authority_weight": item.get("authority_weight"),
        })
    return sources


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


@app.post("/api/agent", response_model=AgentResponse)
def api_agent(request: AgentRequest) -> AgentResponse:
    """
    Run the Sprint 3/4 LangGraph multi-agent pipeline: input sanitation,
    supervisor routing (or forced_agent from the issue picker /
    classification_inputs / target_market), the specialist agent,
    citation verification, and confidence-gated abstention.
    """

    query = (request.query or "").strip()

    if not query and not request.classification_inputs and not request.target_market:
        return AgentResponse(
            final_answer="Please provide a non-empty question.",
            sources=[],
            selected_agents=[],
            error="empty_query",
        )

    if _STATE.get("rag") is None:
        return AgentResponse(
            final_answer=(
                "The backend is not ready. "
                + (_STATE.get("error") or "Models/services are still loading.")
            ),
            sources=[],
            selected_agents=[],
            error="not_ready",
        )

    extra: dict = {}
    if request.forced_agent:
        extra["forced_agent"] = request.forced_agent
    if request.classification_inputs:
        extra["classification_inputs"] = request.classification_inputs
    if request.target_market:
        extra["target_market"] = request.target_market
    if request.market_inputs:
        extra["market_inputs"] = request.market_inputs
    if request.gratk_inputs:
        extra["gratk_inputs"] = request.gratk_inputs
    if request.tk_inputs:
        extra["tk_inputs"] = request.tk_inputs
    if request.ipr_inputs:
        extra["ipr_inputs"] = request.ipr_inputs
    if request.abs_inputs:
        extra["abs_inputs"] = request.abs_inputs
    if request.reg_inputs:
        extra["reg_inputs"] = request.reg_inputs

    try:
        result = agent_graph.run(query, jurisdiction=request.jurisdiction or "India", **extra)
    except Exception as exc:  # noqa: BLE001
        return AgentResponse(
            final_answer="The agent pipeline failed to process this request.",
            sources=[],
            selected_agents=[],
            error=f"agent_pipeline_failed: {exc}",
        )

    return AgentResponse(
        final_answer=result.get("final_answer", ""),
        sources=_agent_sources(result.get("retrieved", [])),
        selected_agents=result.get("selected_agents", []),
        routing_reason=result.get("routing_reason"),
        confidence=result.get("confidence_report"),
        citations=result.get("citation_report"),
        engine_results=result.get("engine_results"),
        pii_redactions=result.get("pii_redactions"),
        error=result.get("error"),
    )


@app.post("/api/translate", response_model=TranslateResponse)
def api_translate(request: TranslateRequest) -> TranslateResponse:
    """
    Translate `text` into one of the Sprint 5 Indian languages, keeping
    bracketed statutory citations in English (see prompt.TRANSLATION_PROMPT).

    Implemented with the Gemini client already used for generation —
    Bhashini API credentials were not available, so this is a pragmatic
    substitute for the same layer, not the real Bhashini integration.
    """

    text = (request.text or "").strip()
    language_name = _LANGUAGE_NAMES.get(request.target_language)

    if not language_name:
        return TranslateResponse(
            translated_text=request.text,
            target_language=request.target_language,
            error="unsupported_language",
        )

    if language_name == "English" or not text:
        return TranslateResponse(translated_text=request.text, target_language=request.target_language)

    rag = _STATE.get("rag")
    if rag is None:
        return TranslateResponse(
            translated_text=request.text,
            target_language=request.target_language,
            error="not_ready",
        )

    prompt = TRANSLATION_PROMPT.format(language=language_name, text=text)

    try:
        translated = rag.llm.generate(prompt)
    except LLMError as exc:
        return TranslateResponse(
            translated_text=request.text,
            target_language=request.target_language,
            error=str(exc),
        )

    return TranslateResponse(translated_text=translated, target_language=request.target_language)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
