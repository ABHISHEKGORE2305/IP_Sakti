"""
LangGraph multi-agent orchestration graph.

    InputSanitizer -> SupervisorRouter -> {specialist agent}
        -> VerificationGuardrail -> OutputSynthesizer | FallbackHandler

See implementation_plan.md Phase 3.1 for the full state diagram.

Run interactively:
    PYTHONPATH=src python3 -c "from agents.graph import run; \
        import json; print(json.dumps(run('What is Section 3(p)?'), indent=2))"
"""

import time

from langgraph.graph import END, StateGraph

from agents.citation_agent import verify_citations
from agents.specialists import SPECIALISTS
from agents.state import AgentState
from agents.supervisor import route
from guardrails.confidence import ABSTENTION_MESSAGE, evaluate_confidence
from guardrails.injection_filter import detect_prompt_injection
from guardrails.pii_sanitizer import sanitize_pii


def _trace(node: str, summary: str) -> dict:
    """One entry for AgentState's `trace` list (see state.py) — every
    node's return dict includes {"trace": [_trace(...)]} so the
    Annotated[list, operator.add] reducer concatenates them into a real,
    inspectable step-by-step record (winning_features.md item 11)."""
    return {"node": node, "summary": summary, "timestamp": time.time()}


# ----------------------------------------------------------------------
# Nodes
# ----------------------------------------------------------------------

def input_sanitizer(state: AgentState) -> dict:

    query = (state.get("query") or "").strip()

    if not query:
        return {
            "sanitized_query": "", "blocked": True, "block_reason": "empty_query", "pii_redactions": [],
            "trace": [_trace("input_sanitizer", "blocked: empty query")],
        }

    # DPDP data minimization: redact PII before the query ever reaches
    # embedding/retrieval or the LLM prompt. sanitize_pii() returns the
    # original matched value too (useful for a caller that needs it
    # synchronously); we deliberately drop that here before it enters
    # AgentState, so `pii_redactions` - which may end up in an API
    # response or a log - carries only the PII *type* found, never the
    # raw value or the original query text.
    pii_result = sanitize_pii(query)
    query = pii_result["sanitized_text"]
    redaction_types = [{"type": r["type"]} for r in pii_result["redactions"]]

    injection_match = detect_prompt_injection(query)
    if injection_match:
        return {
            "sanitized_query": query,
            "blocked": True,
            "block_reason": "prompt_injection_pattern",
            "pii_redactions": redaction_types,
            "trace": [_trace("input_sanitizer", f"blocked: prompt-injection pattern matched ({injection_match!r})")],
        }

    return {
        "sanitized_query": query,
        "blocked": False,
        "block_reason": None,
        "pii_redactions": redaction_types,
        "trace": [_trace(
            "input_sanitizer",
            f"passed; {len(redaction_types)} PII redaction(s)" if redaction_types else "passed",
        )],
    }


def supervisor_router(state: AgentState) -> dict:

    forced_agent = state.get("forced_agent")
    if forced_agent:
        # Explicit selection (e.g. the Sprint 5 wizard's Issue Picker
        # step) always wins — the user has told us which specialist
        # they want, so don't second-guess it with keyword/structured
        # routing below.
        if forced_agent not in SPECIALISTS:
            return {
                "selected_agents": [],
                "routing_reason": f"forced_agent '{forced_agent}' is not a known agent.",
                "error": f"unknown_agent: {forced_agent}",
                "trace": [_trace("supervisor_router", f"error: unknown forced_agent {forced_agent!r}")],
            }
        return {
            "selected_agents": [forced_agent],
            "routing_reason": f"forced_agent={forced_agent} — explicit selection.",
            "trace": [_trace("supervisor_router", f"routed to {forced_agent} (forced_agent)")],
        }

    # Structured-input fast path: when the caller supplies the
    # dedicated engine inputs for a specialist (e.g. from the Sprint 5
    # guided wizard's structured forms), route straight to it rather
    # than relying on keyword matching over free text that may not even
    # name the topic - every specialist accepts one of these (see
    # agents.specialists), so this list must stay in sync with that.
    for state_key, agent_name in (
        ("classification_inputs", "classifier_agent"),
        ("target_market", "intl_agent"),
        ("tk_inputs", "patent_agent"),
        ("ipr_inputs", "tm_gi_agent"),
        ("abs_inputs", "abs_agent"),
        ("reg_inputs", "reg_agent"),
    ):
        if state.get(state_key):
            return {
                "selected_agents": [agent_name],
                "routing_reason": f"{state_key} supplied — routed directly to {agent_name}.",
                "trace": [_trace("supervisor_router", f"routed to {agent_name} ({state_key} supplied)")],
            }

    result = route(state["sanitized_query"])

    # Jurisdiction toggle: when the caller has explicitly scoped this
    # query as International and no domain keyword matched free text,
    # prefer the International specialist over the India-specific
    # Patent Agent default.
    if result.get("is_default") and state.get("jurisdiction") == "International":
        return {
            "selected_agents": ["intl_agent"],
            "routing_reason": (
                "No domain keywords matched; jurisdiction=International, "
                "defaulted to intl_agent instead of patent_agent."
            ),
            "trace": [_trace("supervisor_router", "routed to intl_agent (jurisdiction=International default)")],
        }

    return {**result, "trace": [_trace("supervisor_router", f"routed to {result.get('selected_agents')}")]}


def _run_specialist(agent_name: str):
    def node(state: AgentState) -> dict:
        result = SPECIALISTS[agent_name](state)
        n_retrieved = len(result.get("retrieved") or [])
        summary = (
            f"ran {agent_name}; error={result['error']}" if result.get("error")
            else f"ran {agent_name}; {n_retrieved} chunk(s) retrieved" if "retrieved" in result
            else f"ran {agent_name}; deterministic engine output"
        )
        trace_entries = result.get("trace", []) + [_trace(agent_name, summary)]
        return {**result, "trace": trace_entries}
    return node


def verification_guardrail(state: AgentState) -> dict:

    answer = state.get("draft_answer")
    retrieved = state.get("retrieved", [])

    if state.get("engine_results") and not answer:
        # Deterministic rule-engine output (e.g. classifier_agent with
        # structured inputs) carries no generative hallucination risk,
        # so it bypasses the retrieval confidence gate entirely.
        return {
            "citation_report": None,
            "confidence_report": {
                "confidence": 1.0,
                "band": "high",
                "abstain": False,
                "abstention_message": None,
                "scores": None,
                "note": "deterministic engine output — not subject to retrieval confidence gating",
            },
            "trace": [_trace("verification_guardrail", "deterministic engine output — confidence gate bypassed")],
        }

    if not answer:
        confidence_report = evaluate_confidence(state["sanitized_query"], retrieved)
        return {
            "citation_report": None,
            "confidence_report": confidence_report,
            "trace": [_trace("verification_guardrail", f"no draft answer; confidence={confidence_report.get('band')}")],
        }

    citation_report = verify_citations(answer, retrieved)
    confidence_report = evaluate_confidence(state["sanitized_query"], retrieved, citation_report)

    return {
        "citation_report": citation_report,
        "confidence_report": confidence_report,
        "trace": [_trace(
            "verification_guardrail",
            f"{citation_report.get('verified_citations', 0)}/{citation_report.get('total_citations', 0)} "
            f"citations verified; confidence={confidence_report.get('band')}",
        )],
    }


def _format_engine_results(engine_results: dict) -> str:

    if "classifier" in engine_results:
        c = engine_results["classifier"]
        return "\n".join([
            f"Statutory Classification: {c['label']}",
            f"Statutory Basis: {c['statutory_basis']}",
            f"Primary Regulator: {c['primary_regulator']}",
            "Licensing Route: " + "; ".join(c["licensing_route"]),
            f"Clinical Evidence: {c['clinical_evidence']}",
            f"ABS/Biodiversity Triggers: {c['abs_biodiversity_triggers']}",
        ])

    if "market_pathway" in engine_results:
        p = engine_results["market_pathway"]
        lines = [f"Market: {p.get('market')}"]
        if p.get("route"):
            lines.append(f"Route: {p['route']}")
        lines.append(f"Governing Framework: {p.get('governing_framework')}")
        if p.get("requirements"):
            lines.append("Requirements: " + "; ".join(p["requirements"]))
        if p.get("requirement"):
            lines.append(f"Requirement: {p['requirement']}")
        if "eligible" in p:
            lines.append(f"Eligible on facts given: {p['eligible']}")
        lines.append(f"Finding: {p.get('finding')}")
        if p.get("recommendation"):
            lines.append(f"Recommendation: {p['recommendation']}")

        gratk = engine_results.get("gratk_disclosure")
        if gratk:
            lines.append("")
            lines.append(f"GRATK Disclosure Obligation Applicable: {gratk['applicable']}")
            lines.append(f"Finding: {gratk['finding']}")
            if gratk.get("recommendation"):
                lines.append(f"Recommendation: {gratk['recommendation']}")

        return "\n".join(lines)

    if "tk_patentability" in engine_results:
        analysis = engine_results["tk_patentability"]
        lines = [f"Overall Risk: {analysis['overall_risk']}", ""]
        for finding in analysis["findings"]:
            lines.append(f"{finding['section']} — {finding['risk']}")
            lines.append(f"  Finding: {finding['finding']}")
            if finding.get("recommendation"):
                lines.append(f"  Recommendation: {finding['recommendation']}")
            lines.append("")
        tkdl = analysis.get("tkdl_mitigation")
        if tkdl:
            lines.append(f"{tkdl['topic']}: {tkdl['finding']}")
            if tkdl.get("recommendation"):
                lines.append(f"Recommendation: {tkdl['recommendation']}")
        misappropriation = analysis.get("misappropriation_risk")
        if misappropriation:
            lines.append("")
            lines.append(f"{misappropriation['topic']} ({misappropriation['level']}): {misappropriation['finding']}")
        return "\n".join(lines)

    if "abs_compliance" in engine_results:
        c = engine_results["abs_compliance"]
        lines = [
            f"Entity Classification ({c['entity_classification']['governing_section']}): "
            f"{c['entity_classification']['finding']}",
            "",
            "Compliance Checklist:",
        ]
        lines.extend(f"- {step}" for step in c["compliance_checklist"])
        return "\n".join(lines)

    if "regulatory_pathway" in engine_results:
        p = engine_results["regulatory_pathway"]
        crosswalk = p["crosswalk"]
        lines = [f"Regulatory Cross-Walk: {crosswalk['finding']}"]
        for r in crosswalk.get("regulators", []):
            lines.append(f"- {r['name']} ({r['governing_law']})")
        ad = p.get("advertising_compliance")
        if ad:
            lines.append("")
            lines.append(f"Advertising Compliance ({ad['risk']}): {ad['finding']}")
            if ad.get("recommendation"):
                lines.append(f"Recommendation: {ad['recommendation']}")
        return "\n".join(lines)

    if "ipr_guidance" in engine_results:
        g = engine_results["ipr_guidance"]

        def _render(value, indent=0):
            pad = "  " * indent
            rendered = []
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, (dict, list)):
                        rendered.append(f"{pad}{k}:")
                        rendered.extend(_render(v, indent + 1))
                    else:
                        rendered.append(f"{pad}{k}: {v}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, (dict, list)):
                        rendered.extend(_render(item, indent))
                    else:
                        rendered.append(f"{pad}- {item}")
            else:
                rendered.append(f"{pad}{value}")
            return rendered

        return "\n".join(_render(g))

    return str(engine_results)


def output_synthesizer(state: AgentState) -> dict:

    sources = [
        {
            "document": r.get("document"),
            "legal_reference": r.get("legal_reference"),
            "page": r.get("page"),
            "chunk_id": r.get("chunk_id"),
        }
        for r in state.get("retrieved", [])
    ]

    final_answer = state.get("draft_answer")

    if not final_answer and state.get("engine_results"):
        final_answer = _format_engine_results(state["engine_results"])

    return {
        "final_answer": final_answer or "",
        "sources": sources,
        "trace": [_trace("output_synthesizer", f"{len(sources)} source(s) in final answer")],
    }


def fallback_handler(state: AgentState) -> dict:

    if state.get("blocked"):
        reason = state.get("block_reason")
        message = (
            "Please enter a question."
            if reason == "empty_query"
            else (
                "This query could not be processed as a legal information "
                "request. Please rephrase your question."
            )
        )
        return {"final_answer": message, "sources": [], "trace": [_trace("fallback_handler", f"blocked: {reason}")]}

    if state.get("error") and not state.get("confidence_report"):
        # Routing failed before any specialist ran (e.g. an unknown
        # forced_agent from a malformed UI request).
        return {
            "final_answer": f"Request could not be routed: {state['error']}",
            "sources": [],
            "trace": [_trace("fallback_handler", f"routing error: {state['error']}")],
        }

    confidence_report = state.get("confidence_report") or {}
    message = confidence_report.get("abstention_message") or ABSTENTION_MESSAGE

    return {
        "final_answer": message,
        "sources": [],
        "trace": [_trace("fallback_handler", f"abstained; confidence={confidence_report.get('band')}")],
    }


# ----------------------------------------------------------------------
# Routing
# ----------------------------------------------------------------------

def _route_after_sanitizer(state: AgentState) -> str:
    return "fallback" if state.get("blocked") else "supervisor"


def _route_after_supervisor(state: AgentState) -> str:
    # A query can match several domains (see agents.supervisor); the
    # graph dispatches to the first match and reports the rest via
    # `routing_reason` for transparency / future multi-agent fan-out.
    selected = state.get("selected_agents") or []
    if not selected:
        # e.g. an unknown forced_agent — nothing to dispatch to.
        return "fallback"
    return selected[0]


def _route_after_guardrail(state: AgentState) -> str:
    return "fallback" if state.get("confidence_report", {}).get("abstain") else "synthesizer"


# ----------------------------------------------------------------------
# Graph assembly
# ----------------------------------------------------------------------

def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("input_sanitizer", input_sanitizer)
    graph.add_node("supervisor_router", supervisor_router)
    for name in SPECIALISTS:
        graph.add_node(name, _run_specialist(name))
    graph.add_node("verification_guardrail", verification_guardrail)
    graph.add_node("output_synthesizer", output_synthesizer)
    graph.add_node("fallback_handler", fallback_handler)

    graph.set_entry_point("input_sanitizer")

    graph.add_conditional_edges(
        "input_sanitizer",
        _route_after_sanitizer,
        {"fallback": "fallback_handler", "supervisor": "supervisor_router"},
    )

    graph.add_conditional_edges(
        "supervisor_router",
        _route_after_supervisor,
        {**{name: name for name in SPECIALISTS}, "fallback": "fallback_handler"},
    )

    for name in SPECIALISTS:
        graph.add_edge(name, "verification_guardrail")

    graph.add_conditional_edges(
        "verification_guardrail",
        _route_after_guardrail,
        {"fallback": "fallback_handler", "synthesizer": "output_synthesizer"},
    )

    graph.add_edge("output_synthesizer", END)
    graph.add_edge("fallback_handler", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run(query: str, jurisdiction: str = "India", **extra) -> dict:
    """
    Execute the full multi-agent pipeline for `query` and return the final
    state. jurisdiction="Both" (winning_features.md item 2) runs the graph
    twice — once forced to "India", once to "International" — and returns
    {"india": <state>, "international": <state>} instead of a single flat
    state, so the two answers are never merged into one paragraph; callers
    (api.py) render them as separate panels.
    """

    if jurisdiction == "Both":
        india_state: AgentState = {"query": query, "jurisdiction": "India", **extra}
        intl_state: AgentState = {"query": query, "jurisdiction": "International", **extra}
        return {
            "both": True,
            "india": get_graph().invoke(india_state),
            "international": get_graph().invoke(intl_state),
        }

    initial_state: AgentState = {"query": query, "jurisdiction": jurisdiction, **extra}

    return get_graph().invoke(initial_state)
