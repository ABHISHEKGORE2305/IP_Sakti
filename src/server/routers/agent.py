"""The multi-agent graph (/api/agent) and the engine-only planners built on the same inputs."""

import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from agents import graph as agent_graph
from engines.ipr_router import plan_ip_route
from engines.knowledge_graph import build_graph
from server.security import llm_rate_limit
from server.state import audit_log_best_effort, get_rag, not_ready_message, resolve_freshness_note

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agent"])


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


class IPRoutePlanRequest(BaseModel):
    ip_regimes: dict          # the `ip_regimes` field from a classify_product()/classifier_agent result
    tk_risk: str | None = None            # overall_risk from analyze_tk_patentability(), if run
    is_region_linked: bool = False


class KnowledgeGraphRequest(BaseModel):
    jurisdiction: str = "India"
    ingredient: str | None = None
    biological_resource: str | None = None
    classification_inputs: dict | None = None   # engines.classifier.classify_product kwargs
    tk_inputs: dict | None = None                # engines.tk_engine.analyze_tk_patentability kwargs
    abs_inputs: dict | None = None               # engines.abs_engine.analyze_abs_compliance kwargs


# AgentRequest fields forwarded to agents.graph.run only when set.
_OPTIONAL_GRAPH_INPUTS = (
    "persona", "forced_agent", "classification_inputs", "target_market", "market_inputs",
    "gratk_inputs", "tk_inputs", "ipr_inputs", "abs_inputs", "reg_inputs",
)


def _agent_sources(retrieved: list) -> list[AgentSource]:
    """
    Shape the agent graph's `retrieved` chunks (full text/score/authority)
    into the richer AgentSource form the Sprint 5 citation inspector uses
    — the graph's own `sources` field (see agents.graph.output_synthesizer)
    intentionally strips this down for the plain answer payload.
    """

    return [
        AgentSource(
            document=item.get("document"),
            legal_reference=item.get("legal_reference"),
            page=item.get("page"),
            chunk_id=item.get("chunk_id"),
            snippet=" ".join((item.get("text") or "").split())[:280],
            reranker_score=item.get("reranker_score"),
            authority_weight=item.get("authority_weight"),
            freshness_note=resolve_freshness_note(item),
        )
        for item in retrieved or []
    ]


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


@router.post("/api/agent", response_model=AgentResponse, dependencies=[Depends(llm_rate_limit)])
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

    if get_rag() is None:
        return AgentResponse(final_answer=not_ready_message(), sources=[], selected_agents=[], error="not_ready")

    extra = {name: getattr(request, name) for name in _OPTIONAL_GRAPH_INPUTS if getattr(request, name)}

    try:
        result = agent_graph.run(query, jurisdiction=request.jurisdiction or "India", **extra)
    except Exception as exc:
        logger.exception("agent pipeline failed")
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

    audit_log_best_effort(http_request, "agent_query", {
        "query": query[:200],
        "jurisdiction": request.jurisdiction,
        "selected_agents": response.selected_agents or (
            (response.india.selected_agents if response.india else [])
            + (response.international.selected_agents if response.international else [])
        ),
    })

    return response


@router.post("/api/ip-route-plan")
def api_ip_route_plan(request: IPRoutePlanRequest) -> dict:
    """
    IP Route Planner (winning_features.md item 6) — a per-regime strategy
    list built from engines.ipr_router.plan_ip_route(): composing the
    classification's own `ip_regimes` blurbs with a Section 3(p) risk and
    GI region-linkage, not new legal facts. Rendered as a flow/decision
    tree in the frontend, not a paragraph.
    """

    return {"plan": plan_ip_route(request.ip_regimes, request.tk_risk, request.is_region_linked)}


@router.post("/api/knowledge-graph")
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
