"""
LangGraph AgentState schema for the IP-Sakti multi-agent pipeline.

    InputSanitizer -> SupervisorRouter -> {ClassifierAgent, PatentAgent,
    TMGIAgent, ABSAgent, RegAgent, IntlAgent} -> VerificationGuardrail
    -> OutputSynthesizer | FallbackHandler

See implementation_plan.md Phase 3.1 for the full state diagram.
"""

from typing import Literal, TypedDict
from typing_extensions import NotRequired


AgentName = Literal[
    "classifier_agent",
    "patent_agent",
    "tm_gi_agent",
    "abs_agent",
    "reg_agent",
    "intl_agent",
]


class AgentState(TypedDict):

    # ---- input ----
    query: str
    jurisdiction: NotRequired[str]                       # "India" | "International"
    forced_agent: NotRequired[str]                         # explicit AgentName (e.g. the UI's issue picker)
    classification_inputs: NotRequired[dict]              # structured facts for classifier_agent
    target_market: NotRequired[str]                       # "US" | "EU" | "UK" for intl_agent
    market_inputs: NotRequired[dict]                      # structured facts for engines.intl_engine.advise_market
    gratk_inputs: NotRequired[dict]                        # structured facts for engines.intl_engine.gratk_disclosure_requirement
    tk_inputs: NotRequired[dict]                            # structured facts for engines.tk_engine.analyze_tk_patentability (patent_agent)
    ipr_inputs: NotRequired[dict]                           # {"regime": ...} for engines.ipr_router.advise_regime (tm_gi_agent)
    abs_inputs: NotRequired[dict]                           # structured facts for engines.abs_engine.analyze_abs_compliance (abs_agent)
    reg_inputs: NotRequired[dict]                           # structured facts for engines.reg_engine.analyze_regulatory_pathway (reg_agent)

    # ---- InputSanitizer ----
    sanitized_query: NotRequired[str]
    blocked: NotRequired[bool]
    block_reason: NotRequired[str | None]
    pii_redactions: NotRequired[list[dict]]    # DPDP audit trail: [{"type": "aadhaar", ...}], never the raw query

    # ---- SupervisorRouter ----
    selected_agents: NotRequired[list[str]]
    routing_reason: NotRequired[str]
    is_default: NotRequired[bool]

    # ---- specialist agent output ----
    agent: NotRequired[str]
    retrieved: NotRequired[list[dict]]
    draft_answer: NotRequired[str | None]
    engine_results: NotRequired[dict]
    note: NotRequired[str]
    error: NotRequired[str | None]

    # ---- VerificationGuardrail ----
    citation_report: NotRequired[dict | None]
    confidence_report: NotRequired[dict]

    # ---- terminal ----
    final_answer: NotRequired[str]
    sources: NotRequired[list[dict]]
