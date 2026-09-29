"""
Specialist domain agent nodes.

Each specialist retrieves grounded context via the Sprint 1 hybrid
retriever and drafts an answer via the Gemini LLM, using the shared
zero-hallucination system prompt (src/prompt.py). Every specialist also
accepts an optional structured-inputs field matching its Sprint 2/4
deterministic engine's signature (tk_inputs, ipr_inputs, abs_inputs,
reg_inputs, market_inputs for classifier_agent/intl_agent respectively)
— when supplied, the engine runs directly instead of generating text,
which is deterministic and carries no hallucination risk, so it
bypasses the confidence/citation gate entirely (see
agents.graph.verification_guardrail). Falls back to RAG generation
whenever no structured input is given, so free-text queries still work.

Retrieval/LLM clients are process-wide singletons — each specialist
would otherwise reload the embedding + reranker models on every call.
"""

from final_retriever import AyurvedicIPRetriever
from context_builder import ContextBuilder
from llm import GeminiLLM, LLMError
from prompt import SYSTEM_PROMPT, persona_guidance_text


_retriever = None
_context_builder = None
_llm = None


def configure(retriever=None, llm=None, context_builder=None) -> None:
    """
    Inject already-constructed singletons instead of lazily building new
    ones. api.py's lifespan already loads an AyurvedicIPRetriever +
    GeminiLLM for the plain RAG pipeline (rag_pipeline.AyurvedicIPRAG) —
    without this, the first agent-graph request would load a second,
    independent copy of the embedding + reranker models (real memory
    and startup cost), so it reuses those instead.
    """

    global _retriever, _llm, _context_builder

    if retriever is not None:
        _retriever = retriever
    if llm is not None:
        _llm = llm
    if context_builder is not None:
        _context_builder = context_builder


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = AyurvedicIPRetriever()
    return _retriever


def _get_context_builder():
    global _context_builder
    if _context_builder is None:
        _context_builder = ContextBuilder()
    return _context_builder


def _get_llm():
    global _llm
    if _llm is None:
        _llm = GeminiLLM()
    return _llm


def _retrieve_and_draft(
    query: str,
    top_k: int = 6,
    candidate_k: int = 20,
    jurisdiction_filter: str | None = None,
    persona: str | None = None,
) -> dict:
    """Shared retrieval + grounded-generation path used by every RAG specialist.

    jurisdiction_filter enforces the India/International separation at
    the actual Qdrant/BM25 query (retriever.jurisdiction_query_filter,
    bm25_retriever._jurisdiction_matches) — not just via which specialist
    got picked, per winning_features.md item 2's "architectural"
    requirement."""

    try:
        results = _get_retriever().search(
            query=query, top_k=top_k, candidate_k=candidate_k, jurisdiction_filter=jurisdiction_filter,
        )
    except Exception as exc:  # noqa: BLE001
        # Mirrors rag_pipeline.AyurvedicIPRAG.answer()'s guard around the
        # same call (e.g. Qdrant unreachable) - every specialist funnels
        # through this helper for its RAG fallback path, so without this
        # a retrieval outage would crash the whole graph run instead of
        # surfacing a clean error.
        return {"retrieved": [], "draft_answer": None, "error": f"retrieval_failed: {exc}"}

    if not results:
        return {"retrieved": [], "draft_answer": None}

    context_data = _get_context_builder().build_context(results)
    prompt = SYSTEM_PROMPT.format(
        context=context_data["context"], query=query, persona_guidance=persona_guidance_text(persona),
        history_block="",
    )

    try:
        answer = _get_llm().generate(prompt)
    except LLMError as exc:
        return {"retrieved": results, "draft_answer": None, "error": str(exc)}

    return {"retrieved": results, "draft_answer": answer}


def patent_agent(state: dict) -> dict:
    """
    Novelty, inventive step, TK exclusions (3(p)), admixtures (3(e)).

    When `state["tk_inputs"]` is supplied (documented_in_classical_text,
    is_combination_of_known_herbs, has_synergistic_data, etc.), runs
    engines.tk_engine.analyze_tk_patentability directly — a
    deterministic Section 3(p)/3(e)/3(d)/2(1)(j) risk analysis, not a
    generative claim. Falls back to RAG for free-text questions.
    """

    inputs = state.get("tk_inputs")

    if inputs:
        from engines.tk_engine import analyze_tk_patentability

        try:
            analysis = analyze_tk_patentability(**inputs)
        except TypeError as exc:
            return {"agent": "patent_agent", "draft_answer": None, "retrieved": [], "error": str(exc)}

        return {
            "agent": "patent_agent",
            "engine_results": {"tk_patentability": analysis},
            "draft_answer": None,
            "retrieved": [],
        }

    result = _retrieve_and_draft(
        state["sanitized_query"], jurisdiction_filter=state.get("jurisdiction"), persona=state.get("persona"),
    )
    result["agent"] = "patent_agent"
    return result


def tm_gi_agent(state: dict) -> dict:
    """
    Trademark distinctiveness, NICE classes, GI/Design/Trade-Secret/
    Copyright/PPV&FR registration.

    When `state["ipr_inputs"]` is supplied ({"regime": "trademark"|
    "geographical_indication"|"industrial_design"|"trade_secret"|
    "copyright"|"ppv_fr", ...regime-specific kwargs}), runs
    engines.ipr_router.advise_regime directly. Falls back to RAG for
    free-text questions — no Trade Marks Act/GI Act/Designs Act corpus
    has been ingested, so that fallback is best-effort against the
    current India-patent-focused corpus.
    """

    inputs = state.get("ipr_inputs")

    if inputs:
        from engines.ipr_router import advise_regime

        regime = inputs.get("regime")
        kwargs = {k: v for k, v in inputs.items() if k != "regime"}

        try:
            guidance = advise_regime(regime, **kwargs)
        except (ValueError, TypeError) as exc:
            return {"agent": "tm_gi_agent", "draft_answer": None, "retrieved": [], "error": str(exc)}

        return {
            "agent": "tm_gi_agent",
            "engine_results": {"ipr_guidance": guidance},
            "draft_answer": None,
            "retrieved": [],
        }

    result = _retrieve_and_draft(
        state["sanitized_query"], jurisdiction_filter=state.get("jurisdiction"), persona=state.get("persona"),
    )
    result["agent"] = "tm_gi_agent"
    result["note"] = (
        "No Trade Marks Act/GI Act/Designs Act corpus has been ingested — this "
        "answer is grounded only in the current India-patent-focused corpus and "
        "is likely incomplete. Supply ipr_inputs={'regime': ...} for deterministic "
        "regime-specific guidance instead."
    )
    return result


def abs_agent(state: dict) -> dict:
    """
    Biological material sourcing, NBA/SBB jurisdiction, Form I-IV.

    When `state["abs_inputs"]` is supplied (entity_type, activity_type,
    etc.), runs engines.abs_engine.analyze_abs_compliance directly — a
    deterministic entity/approval-form determination, not a generative
    claim. Falls back to RAG for free-text questions.
    """

    inputs = state.get("abs_inputs")

    if inputs:
        from engines.abs_engine import analyze_abs_compliance

        try:
            compliance = analyze_abs_compliance(**inputs)
        except (ValueError, TypeError) as exc:
            # ValueError: an invalid entity_type/activity_type string (the
            # engine converts these to EntityType/ActivityType enums
            # internally); TypeError: a missing/unknown kwarg.
            return {"agent": "abs_agent", "draft_answer": None, "retrieved": [], "error": str(exc)}

        return {
            "agent": "abs_agent",
            "engine_results": {"abs_compliance": compliance},
            "draft_answer": None,
            "retrieved": [],
        }

    result = _retrieve_and_draft(
        state["sanitized_query"], jurisdiction_filter=state.get("jurisdiction"), persona=state.get("persona"),
    )
    result["agent"] = "abs_agent"
    return result


def reg_agent(state: dict) -> dict:
    """
    AYUSH licensing, FSSAI Ayurveda-Aahar, CDSCO phytopharmaceuticals.

    When `state["reg_inputs"]` is supplied (product_category, optionally
    makes_disease_cure_claim), runs
    engines.reg_engine.analyze_regulatory_pathway directly — a
    deterministic AYUSH/FSSAI/CDSCO cross-walk plus DMR(OA) advertising
    check, not a generative claim. Falls back to RAG for free-text
    questions.
    """

    inputs = state.get("reg_inputs")

    if inputs:
        from engines.reg_engine import analyze_regulatory_pathway

        try:
            pathway = analyze_regulatory_pathway(**inputs)
        except TypeError as exc:
            return {"agent": "reg_agent", "draft_answer": None, "retrieved": [], "error": str(exc)}

        return {
            "agent": "reg_agent",
            "engine_results": {"regulatory_pathway": pathway},
            "draft_answer": None,
            "retrieved": [],
        }

    result = _retrieve_and_draft(
        state["sanitized_query"], jurisdiction_filter=state.get("jurisdiction"), persona=state.get("persona"),
    )
    result["agent"] = "reg_agent"
    return result


def intl_agent(state: dict) -> dict:
    """
    International IP & export market access.

    When `state["target_market"]` ("US"/"EU"/"UK") is supplied, runs the
    deterministic engines.intl_engine pathway determination — these are
    statutory threshold checks (years of use, claim-type restrictions),
    not generative claims, so no LLM/citation risk. `gratk_inputs`
    layers on the genetic-resource/TK disclosure check regardless of
    market. Falls back to RAG when no target_market is given — the
    international treaty/export corpus (WIPO GRATK, US FDA, EU THMPD)
    hasn't been ingested yet (blocked on source PDFs), so that fallback
    answer is grounded only in the current India-focused corpus.
    """

    target_market = state.get("target_market")
    gratk_inputs = state.get("gratk_inputs")

    if target_market:
        from engines.intl_engine import advise_market, gratk_disclosure_requirement

        try:
            pathway = advise_market(target_market, **(state.get("market_inputs") or {}))
        except (ValueError, TypeError) as exc:
            return {
                "agent": "intl_agent",
                "draft_answer": None,
                "retrieved": [],
                "error": str(exc),
            }

        engine_results = {"market_pathway": pathway}

        if gratk_inputs is not None:
            engine_results["gratk_disclosure"] = gratk_disclosure_requirement(**gratk_inputs)

        return {
            "agent": "intl_agent",
            "engine_results": engine_results,
            "draft_answer": None,
            "retrieved": [],
        }

    result = _retrieve_and_draft(
        state["sanitized_query"], jurisdiction_filter=state.get("jurisdiction"), persona=state.get("persona"),
    )
    result["agent"] = "intl_agent"
    result["note"] = (
        "No target_market supplied, and the international treaty/export corpus "
        "(WIPO GRATK, US FDA Botanical Guidance, EU THMPD) has not been ingested "
        "yet — this answer is grounded only in the current India-focused corpus "
        "and is likely incomplete. Supply target_market='US'|'EU'|'UK' (plus "
        "market_inputs) for a deterministic pathway determination instead."
    )
    return result


def classifier_agent(state: dict) -> dict:
    """
    Statutory product classification.

    Requires structured facts (in_first_schedule, formulation_modified,
    intended_use) that a real deployment collects via the guided wizard
    (Sprint 5). When `state["classification_inputs"]` isn't supplied,
    falls back to a grounded RAG answer explaining what's needed.
    """

    inputs = state.get("classification_inputs")

    if inputs:
        from engines.classifier import ClassificationError, classify_product

        try:
            classification = classify_product(**inputs)
            return {
                "agent": "classifier_agent",
                "engine_results": {"classifier": classification},
                "draft_answer": None,
                "retrieved": [],
            }
        except (ClassificationError, ValueError, TypeError) as exc:
            # ValueError: an invalid intended_use string (classify_product
            # converts it to the IntendedUse enum internally).
            return {
                "agent": "classifier_agent",
                "draft_answer": None,
                "retrieved": [],
                "error": str(exc),
            }

    result = _retrieve_and_draft(
        state["sanitized_query"], jurisdiction_filter=state.get("jurisdiction"), persona=state.get("persona"),
    )
    result["agent"] = "classifier_agent"
    result["note"] = (
        "No structured classification inputs supplied — this answer is "
        "grounded RAG only. Supply in_first_schedule/formulation_modified/"
        "intended_use for a deterministic statutory classification."
    )
    return result


SPECIALISTS = {
    "patent_agent": patent_agent,
    "tm_gi_agent": tm_gi_agent,
    "abs_agent": abs_agent,
    "reg_agent": reg_agent,
    "intl_agent": intl_agent,
    "classifier_agent": classifier_agent,
}
