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
    POST /api/escalate -> Emails a case brief to the configured IP
                          facilitator inbox (see escalation.py). Returns
                          error="not_configured" until SMTP_HOST/SMTP_USER/
                          SMTP_PASSWORD/ESCALATION_EMAIL_TO are set in .env.
    GET  /api/references -> Deep links to free official portals (IP India,
                          WIPO, GI Registry, TKDL, AYUSH, FSSAI, NBA, ...).
    POST /api/knowledge-graph -> Multi-hop relational graph (engines/
                          knowledge_graph.py) built from classification/
                          tk/abs inputs, e.g. Product -> Ingredient ->
                          Biological Resource -> TK -> IP Type -> Jurisdiction.
"""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import graph as agent_graph
from agents import specialists as agent_specialists
from llm import LLMError
from prompt import TRANSLATION_PROMPT
from rag_pipeline import AyurvedicIPRAG
from escalation import EscalationError, is_configured as escalation_is_configured, send_case_brief
from references import REFERENCE_CATEGORIES
from freshness import freshness_note, web_freshness_note
from engines.knowledge_graph import build_graph
from engines.ipr_router import plan_ip_route
import bhashini_client
from law_versions import get_law_families, find_version
import db
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


class ChatMessage(BaseModel):
    role: str    # "user" | "assistant"
    content: str


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
    # Prior turns of the chat tab's conversation (oldest first), used only
    # as follow-up context for the prompt — see prompt.history_block_text.
    history: list[ChatMessage] | None = None


class AgentRequest(BaseModel):
    query: str
    jurisdiction: str = "India"                 # "India" | "International" | "Both"
    persona: str | None = None                  # "practitioner" | "researcher" | "startup_msme" | "cultivator"
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
    freshness_note: str | None = None


class AgentResponse(BaseModel):
    final_answer: str
    sources: list[AgentSource]
    selected_agents: list[str]
    routing_reason: str | None = None
    confidence: dict | None = None
    citations: dict | None = None
    engine_results: dict | None = None
    pii_redactions: list[dict] | None = None   # [{"type": "aadhaar"}, ...] - types only, DPDP audit trail
    trace: list[dict] | None = None            # winning_features.md item 11 — real per-node agent step trace
    error: str | None = None
    # jurisdiction="Both" (winning_features.md item 2): populated INSTEAD of
    # the top-level fields above, which stay at their defaults in that case
    # — the two answers are never merged into one.
    india: "AgentResponse | None" = None
    international: "AgentResponse | None" = None


class TranslateRequest(BaseModel):
    text: str
    target_language: str    # ISO code, see _LANGUAGE_NAMES


class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str
    provider: str | None = None   # "bhashini" | "gemini" — which backend actually served this
    error: str | None = None


class EscalateRequest(BaseModel):
    case_brief_markdown: str    # pre-built brief, e.g. lib/caseBrief.js's buildCaseBriefMarkdown()
    query: str | None = None
    reply_to: str | None = None  # user's email, set as Reply-To so the facilitator can respond directly


class EscalateResponse(BaseModel):
    sent: bool
    error: str | None = None


class IPRoutePlanRequest(BaseModel):
    ip_regimes: dict          # the `ip_regimes` field from a classify_product()/classifier_agent result
    tk_risk: str | None = None            # overall_risk from analyze_tk_patentability(), if run
    is_region_linked: bool = False


class LawVersionQueryRequest(BaseModel):
    query: str
    document_id: str


class KnowledgeGraphRequest(BaseModel):
    jurisdiction: str = "India"
    ingredient: str | None = None
    biological_resource: str | None = None
    classification_inputs: dict | None = None   # engines.classifier.classify_product kwargs
    tk_inputs: dict | None = None                # engines.tk_engine.analyze_tk_patentability kwargs
    abs_inputs: dict | None = None               # engines.abs_engine.analyze_abs_compliance kwargs


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _session_id(request: Request) -> str:
    """No-login session identity (src/db.py) — the frontend generates a
    UUID once, stores it in localStorage, and sends it as X-Session-Id.
    A caller without the header (e.g. a raw curl/test) still gets a
    fresh per-request id rather than a crash, it just won't accumulate
    audit-log history across requests."""

    return request.headers.get("X-Session-Id") or str(uuid.uuid4())


def _audit_log_best_effort(request: Request, event_type: str, payload: dict) -> None:
    """A DB hiccup must never break the actual API response — this is
    best-effort observability, not a transactional requirement."""

    try:
        db.log_event(_session_id(request), event_type, payload)
    except Exception as exc:  # noqa: BLE001
        print(f"[api] audit log write failed (non-fatal): {exc}")


def _resolve_freshness_note(item: dict) -> str | None:
    """
    fetched_at is only ever set on web-sourced chunks (src/web_loader.py,
    src/ingest_web.py) — use the days-since-fetch check for those,
    otherwise fall back to the title-year check used for PDFs.
    """

    fetched_at = item.get("fetched_at")
    if fetched_at:
        return web_freshness_note(fetched_at)
    return freshness_note(item.get("document_id"))


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
                "freshness_note": _resolve_freshness_note(item),
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
            "freshness_note": _resolve_freshness_note(item),
        })
    return sources


def _normalize_jurisdiction(value: str | None) -> str | None:
    """Map a UI/caller jurisdiction label onto the two filter values the
    retrievers understand ("India"/"International"), or None for no filter.

    Anything explicitly dual-scoped, unrecognized or absent returns None:
    an unknown label must widen the search rather than silently narrow it to
    the wrong regime.
    """

    if not value:
        return None

    text = value.strip().lower()
    if not text:
        return None

    if "both" in text or "dual" in text:
        return None
    # "India (National & International Multi-Step)" is a dual-scope question
    # despite leading with India, so check for a co-mention first.
    india = "india" in text
    international = any(
        term in text
        for term in ("international", "global", "wipo", "pct", "foreign", "export")
    )
    if india and international:
        return None
    if india:
        return "India"
    if international:
        return "International"
    return None


def _run_query(
    query: str,
    top_k: int | None,
    history: list | None = None,
    jurisdiction: str | None = None,
) -> dict | None:
    """Shared guard + dispatch. Returns None when the backend is not ready."""

    rag = _STATE.get("rag")
    if rag is None:
        return None
    history_dicts = [h.model_dump() for h in history] if history else None
    return rag.answer(
        query,
        top_k=top_k,
        history=history_dicts,
        jurisdiction_filter=_normalize_jurisdiction(jurisdiction),
    )


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------


@app.get("/health")
async def health() -> dict:
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

    result = _run_query(
        query,
        request.top_k,
        history=request.history,
        jurisdiction=request.jurisdiction or request.jurisdiction_filter,
    )
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


def _agent_response_from_state(result: dict) -> AgentResponse:
    return AgentResponse(
        final_answer=result.get("final_answer", ""),
        sources=_agent_sources(result.get("retrieved", [])),
        selected_agents=result.get("selected_agents", []),
        routing_reason=result.get("routing_reason"),
        confidence=result.get("confidence_report"),
        citations=result.get("citation_report"),
        engine_results=result.get("engine_results"),
        pii_redactions=result.get("pii_redactions"),
        trace=result.get("trace"),
        error=result.get("error"),
    )


@app.post("/api/agent", response_model=AgentResponse)
def api_agent(request: AgentRequest, http_request: Request) -> AgentResponse:
    """
    Run the Sprint 3/4 LangGraph multi-agent pipeline: input sanitation,
    supervisor routing (or forced_agent from the issue picker /
    classification_inputs / target_market), the specialist agent,
    citation verification, and confidence-gated abstention.

    jurisdiction="Both" (winning_features.md item 2) runs it twice and
    returns india/international as separate sub-responses instead of the
    top-level fields.
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
    if request.persona:
        extra["persona"] = request.persona
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

    if result.get("both"):
        response = AgentResponse(
            final_answer="",
            sources=[],
            selected_agents=[],
            india=_agent_response_from_state(result["india"]),
            international=_agent_response_from_state(result["international"]),
        )
    else:
        response = _agent_response_from_state(result)

    _audit_log_best_effort(http_request, "agent_query", {
        "query": query[:200],
        "jurisdiction": request.jurisdiction,
        "selected_agents": response.selected_agents or (
            (response.india.selected_agents if response.india else [])
            + (response.international.selected_agents if response.international else [])
        ),
    })

    return response


@app.post("/api/translate", response_model=TranslateResponse)
def api_translate(request: TranslateRequest) -> TranslateResponse:
    """
    Translate `text` into one of the Sprint 5 Indian languages, keeping
    bracketed statutory citations in English (see prompt.TRANSLATION_PROMPT).

    Tries Bhashini first (winning_features.md item 13) when configured —
    the real free Indian-language MT API. Falls back to the Gemini-based
    substitute on missing config or any Bhashini failure, so this never
    breaks even before real credentials are added (see
    bhashini_client.py's module docstring for the "build now, wire later"
    pattern, same as escalation.py's SMTP config).

    NOTE: bhashini_client.py preserves statutory citations in English
    less reliably than the Gemini path's explicit TRANSLATION_PROMPT
    instruction (a generic MT API has no citation-preservation concept)
    — worth a manual spot-check once real Bhashini credentials land.
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

    if bhashini_client.is_configured():
        try:
            translated = bhashini_client.translate(text, source_lang="en", target_lang=request.target_language)
            return TranslateResponse(
                translated_text=translated, target_language=request.target_language, provider="bhashini",
            )
        except bhashini_client.BhashiniError as exc:
            print(f"[api] Bhashini translation failed, falling back to Gemini: {exc}")

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

    return TranslateResponse(translated_text=translated, target_language=request.target_language, provider="gemini")


@app.get("/api/bhashini/status")
def api_bhashini_status() -> dict:
    return {"configured": bhashini_client.is_configured()}


class TTSRequest(BaseModel):
    text: str
    lang: str    # ISO code, see _LANGUAGE_NAMES


@app.post("/api/tts")
def api_tts(request: TTSRequest) -> dict:
    """
    Bhashini text-to-speech (winning_features.md item 13's voice-first
    mode). Only available when Bhashini is configured — the frontend's
    existing browser Web Speech API TTS ("Listen" button in
    StepAction.jsx) remains the fallback/default; this is additive, not
    a replacement, since Web Speech works with zero backend config.
    """

    if not bhashini_client.is_configured():
        return {"available": False, "audio_base64": None, "error": "not_configured"}

    import base64

    try:
        audio_bytes = bhashini_client.text_to_speech(request.text, request.lang)
        return {"available": True, "audio_base64": base64.b64encode(audio_bytes).decode("ascii"), "error": None}
    except bhashini_client.BhashiniError as exc:
        return {"available": True, "audio_base64": None, "error": str(exc)}


@app.post("/api/stt")
async def api_stt(audio: UploadFile = File(...), lang: str = "hi") -> dict:
    """Bhashini speech-to-text — same additive relationship to the
    frontend's existing Web Speech API STT as /api/tts above."""

    if not bhashini_client.is_configured():
        return {"available": False, "text": None, "error": "not_configured"}

    try:
        audio_bytes = await audio.read()
        text = bhashini_client.speech_to_text(audio_bytes, lang)
        return {"available": True, "text": text, "error": None}
    except bhashini_client.BhashiniError as exc:
        return {"available": True, "text": None, "error": str(exc)}


@app.post("/api/escalate", response_model=EscalateResponse)
def api_escalate(request: EscalateRequest) -> EscalateResponse:
    """Email the case brief to the configured IP facilitator inbox."""

    brief = (request.case_brief_markdown or "").strip()
    if not brief:
        return EscalateResponse(sent=False, error="empty_case_brief")

    subject_query = (request.query or "").strip()
    subject = f"IP-Sakti case escalation — {subject_query[:80]}" if subject_query else "IP-Sakti case escalation"

    try:
        send_case_brief(subject=subject, body_markdown=brief, reply_to=request.reply_to)
    except EscalationError as exc:
        return EscalateResponse(sent=False, error=str(exc))

    return EscalateResponse(sent=True)


@app.get("/api/escalate/status")
def api_escalate_status() -> dict:
    return {"configured": escalation_is_configured()}


@app.get("/api/law-versions")
def api_law_versions() -> dict:
    """
    Law Version Timeline (winning_features.md item 9) — known versions
    per law family, from law_versions.py. Not a text diff (see that
    module's docstring for why); use POST /api/law-version-query to ask
    the same question scoped to one specific version.
    """

    return {"families": get_law_families()}


@app.post("/api/law-version-query")
def api_law_version_query(request: LawVersionQueryRequest) -> dict:
    """
    Runs `query` with retrieval scoped to exactly `document_id` (via
    rag_pipeline.AyurvedicIPRAG.answer's document_id_filter ->
    retriever.combined_query_filter) — retrieval-enforced, not just a
    prompt instruction to "answer as if under law X". Call this once per
    version in a family and compare the answers side by side.
    """

    version = find_version(request.document_id)
    if version is None:
        return {"answer": "", "sources": [], "error": "unknown_document_id"}

    rag = _STATE.get("rag")
    if rag is None:
        return {"answer": "", "sources": [], "error": "not_ready"}

    result = rag.answer(request.query, document_id_filter=request.document_id)
    return {
        "answer": result.get("answer", ""),
        "sources": _citations_from_retrieved(result.get("retrieved", [])),
        "version": version,
        "error": result.get("error"),
    }


@app.post("/api/ip-route-plan")
def api_ip_route_plan(request: IPRoutePlanRequest) -> dict:
    """
    IP Route Planner (winning_features.md item 6) — a per-regime strategy
    list built from engines.ipr_router.plan_ip_route(): composing the
    classification's own `ip_regimes` blurbs with a Section 3(p) risk and
    GI region-linkage, not new legal facts. Rendered as a flow/decision
    tree in the frontend, not a paragraph.
    """

    return {"plan": plan_ip_route(request.ip_regimes, request.tk_risk, request.is_region_linked)}


@app.post("/api/knowledge-graph")
def api_knowledge_graph(request: KnowledgeGraphRequest) -> dict:
    """
    Multi-hop relational graph (left_to_do.md item 11): Product ->
    Ingredient -> Biological Resource -> TK -> Regulation -> IP Type ->
    Authority -> Jurisdiction, built from whichever structured inputs
    are supplied — see engines/knowledge_graph.py for why this is
    derived from the already-verified deterministic engines rather than
    a fabricated ingredient/regulation dataset.
    """

    return build_graph(
        jurisdiction=request.jurisdiction,
        ingredient=request.ingredient,
        biological_resource=request.biological_resource,
        classification_inputs=request.classification_inputs,
        tk_inputs=request.tk_inputs,
        abs_inputs=request.abs_inputs,
    )


@app.get("/api/eval-results")
def api_eval_results() -> dict:
    """
    Evaluation dashboard (winning_features.md item 19). Reads the JSON
    written by `PYTHONPATH=src python3 src/eval_benchmark.py --out-json
    data/processed/eval_results.json`. Clear "not yet run" state if that
    file doesn't exist, rather than a 404/500 the frontend has to
    special-case.
    """

    from pathlib import Path
    import json as _json

    path = Path(config.EVAL_RESULTS_PATH)
    if not path.exists():
        return {"available": False}

    return {"available": True, **_json.loads(path.read_text(encoding="utf-8"))}


@app.get("/api/references")
def api_references() -> dict:
    """Deep links to free official portals (IP India, WIPO, GI Registry,
    TKDL, AYUSH, FSSAI, NBA, ...). Paid/subscription databases are out of
    scope here — item 16 of left_to_do.md requires explicit per-use
    permission and access logging for those, which is a separate,
    deliberately-not-built feature."""

    return {"categories": REFERENCE_CATEGORIES}


# ----------------------------------------------------------------------
# Consent, audit log, privacy (winning_features.md items 15/16/17) — all
# session-scoped via src/db.py, never global. This is a demo-grade,
# no-login store (see db.py's module docstring), not a production
# multi-tenant privacy system.
# ----------------------------------------------------------------------


class ConsentRequest(BaseModel):
    consent_type: str    # e.g. "paid_source_premium_patent_db"
    granted: bool


@app.post("/api/consent")
def api_set_consent(request: ConsentRequest, http_request: Request) -> dict:
    session_id = _session_id(http_request)
    db.set_consent(session_id, request.consent_type, request.granted)
    return {"session_id": session_id, "consent": db.get_consent(session_id)}


@app.get("/api/consent")
def api_get_consent(http_request: Request) -> dict:
    session_id = _session_id(http_request)
    return {"session_id": session_id, "consent": db.get_consent(session_id)}


@app.get("/api/audit-log")
def api_audit_log(http_request: Request, limit: int = 200) -> dict:
    session_id = _session_id(http_request)
    return {"session_id": session_id, "entries": db.get_audit_log(session_id, limit=limit)}


@app.get("/api/privacy/summary")
def api_privacy_summary(http_request: Request) -> dict:
    session_id = _session_id(http_request)
    return {"session_id": session_id, **db.privacy_summary(session_id)}


@app.post("/api/privacy/delete")
def api_privacy_delete(http_request: Request) -> dict:
    """DPDP "delete my data" — wipes every row for this session_id.
    Session-scoped by construction (db.delete_session_data takes only a
    session_id, never a global wipe), so one user can never delete
    another's data even accidentally."""

    session_id = _session_id(http_request)
    return {"session_id": session_id, **db.delete_session_data(session_id)}


# ----------------------------------------------------------------------
# Corpus admin panel (winning_features.md item 20)
# ----------------------------------------------------------------------


@app.get("/api/admin/corpus")
def api_admin_corpus() -> dict:
    """Lists every known document — the static PDF corpus
    (document_config.DOCUMENTS), the periodic web corpus
    (web_sources.WEB_SOURCES), and anything uploaded via
    POST /api/admin/corpus/upload — with chunk counts from the actual
    ingested chunks.json/chunks_web.json where available."""

    from pathlib import Path
    import json as _json
    from document_config import DOCUMENTS
    from web_sources import WEB_SOURCES

    def _chunk_counts(path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {}
        chunks = _json.loads(p.read_text(encoding="utf-8"))
        counts: dict[str, int] = {}
        for c in chunks:
            doc_id = c.get("document_id")
            if doc_id:
                counts[doc_id] = counts.get(doc_id, 0) + 1
        return counts

    pdf_counts = _chunk_counts(config.CHUNKS_PATH)
    web_counts = _chunk_counts(config.WEB_CHUNKS_PATH)

    documents = []
    for d in DOCUMENTS:
        doc_id = d["filename"].rsplit(".", 1)[0]
        documents.append({
            "document_id": doc_id,
            "filename": d["filename"],
            "document": d.get("document"),
            "document_type": d.get("document_type"),
            "jurisdiction": d.get("jurisdiction"),
            "source": "pdf",
            "chunk_count": pdf_counts.get(doc_id, 0),
            "status": "indexed" if doc_id in pdf_counts else "not_ingested",
        })
    for s in WEB_SOURCES:
        documents.append({
            "document_id": s["source_id"],
            "filename": s["url"],
            "document": s.get("document"),
            "document_type": s.get("document_type"),
            "jurisdiction": s.get("jurisdiction"),
            "source": "web",
            "chunk_count": web_counts.get(s["source_id"], 0),
            "status": "indexed" if s["source_id"] in web_counts else "not_ingested",
        })
    for u in db.list_corpus_documents():
        documents.append({
            "document_id": u["document_id"],
            "filename": u["filename"],
            "document": u["filename"],
            "document_type": u.get("document_type"),
            "jurisdiction": u.get("jurisdiction"),
            "source": "uploaded",
            "chunk_count": pdf_counts.get(u["document_id"], 0),
            "status": u["status"],
        })

    return {"documents": documents}


@app.post("/api/admin/corpus/upload")
async def api_admin_corpus_upload(file: UploadFile = File(...)) -> dict:
    """
    Saves an uploaded PDF to data/raw/ and registers it as
    status="pending_reindex" — deliberately does NOT synchronously
    re-embed inside the request (the same reasoning as ingest_web.py
    being a standalone script rather than an in-process job: embedding
    is slow enough that a request handler is the wrong place for it).
    The admin panel shows the pending status and the operator runs
    `PYTHONPATH=src python3 src/ingest.py` (after adding the file to
    document_config.DOCUMENTS) to actually index it.
    """

    from pathlib import Path

    if file is None or not file.filename:
        return {"saved": False, "error": "no_file"}
    if not file.filename.lower().endswith(".pdf"):
        return {"saved": False, "error": "only_pdf_supported"}

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / file.filename

    contents = await file.read()
    dest.write_bytes(contents)

    document_id = dest.stem
    db.record_corpus_document(document_id, file.filename, document_type=None, jurisdiction=None, status="pending_reindex")

    return {
        "saved": True,
        "document_id": document_id,
        "status": "pending_reindex",
        "next_step": (
            f"Add {{'filename': '{file.filename}', 'document': ..., 'document_type': ..., "
            f"'jurisdiction': ...}} to document_config.DOCUMENTS, then run "
            "`PYTHONPATH=src python3 src/ingest.py` to index it."
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
