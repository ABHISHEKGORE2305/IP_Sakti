"""
End-to-end answer generation with a real LLM: retrieval, generation and
citation verification together. Spends tokens, so it is marked `llm` and
`integration` and skips without an API key or Qdrant.

Answer *quality* across the 400-question benchmark is measured by
src/eval_answers.py; this only checks the pipeline produces a grounded,
cited answer at all.

Run: pytest -m "integration and llm" tests/integration/test_rag_answer.py
"""

import os

import pytest
import requests

import config

pytestmark = [pytest.mark.integration, pytest.mark.llm]


@pytest.fixture(scope="module")
def rag():
    if not (os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")):
        pytest.skip("GROQ_API_KEY / GEMINI_API_KEY not set")
    try:
        requests.get(f"{config.QDRANT_URL}/collections", timeout=2).raise_for_status()
    except requests.RequestException as exc:
        pytest.skip(f"Qdrant not reachable at {config.QDRANT_URL}: {exc}")

    from rag_pipeline import AyurvedicIPRAG

    return AyurvedicIPRAG()


def test_answer_cites_only_retrieved_sources(rag):
    from agents.citation_agent import verify_citations

    result = rag.answer("Can traditional knowledge be patented in India?", jurisdiction_filter="India")

    assert result.get("error") is None, result.get("error")
    assert result["sources"]
    report = verify_citations(result["answer"], result["retrieved"])
    assert report["total_citations"] > 0
    assert report["citation_precision"] >= 0.5
