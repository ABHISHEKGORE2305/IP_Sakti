"""
Retrieval stack against the real corpus and models: BM25 over chunks.json,
the bge-m3 embedder, the bge-reranker cross-encoder, hybrid dense+BM25
retrieval with RRF, and the final reranked retriever.

These replace the old print-and-eyeball scripts (src/test_bm25.py,
test_hybrid.py, test_reranker.py, ...) with assertions on statutory
questions whose correct source is known.

Requirements, each skipped with a reason when missing:
    data/processed/chunks.json      BM25 and context tests
    model weights (HF cache/net)    embedding and reranker tests
    Qdrant at QDRANT_URL            hybrid and final retriever tests

Run: pytest -m integration tests/integration/test_retrieval_stack.py
"""

import json
import os

import pytest
import requests

import config

pytestmark = pytest.mark.integration

# (query, document_id expected among the top results)
KNOWN_ANSWERS = [
    ("What inventions are not patentable under Section 3 of the Patents Act?", "patents_act_1970"),
    ("traditional knowledge aggregation or duplication of known properties", "patents_act_1970"),
    ("approval of the National Biodiversity Authority before applying for a patent", "26_Biological_Diversity_Act_2002_IndiaCode"),
]


@pytest.fixture(scope="module")
def chunks():
    if not os.path.exists(config.CHUNKS_PATH):
        pytest.skip(f"{config.CHUNKS_PATH} not present (build it with src/ingest.py)")
    with open(config.CHUNKS_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def qdrant():
    try:
        requests.get(f"{config.QDRANT_URL}/collections", timeout=2).raise_for_status()
    except requests.RequestException as exc:
        pytest.skip(f"Qdrant not reachable at {config.QDRANT_URL}: {exc}")


@pytest.fixture(scope="module")
def embedder():
    from embedding_model import EmbeddingModel

    return EmbeddingModel()


@pytest.fixture(scope="module")
def reranker():
    from reranker import AyurvedicIPReranker

    return AyurvedicIPReranker()


@pytest.fixture(scope="module")
def final_retriever(qdrant, chunks):
    from final_retriever import AyurvedicIPRetriever

    return AyurvedicIPRetriever()


def _doc_ids(results):
    return [r.get("document_id") or (r.get("chunk_id") or "").rsplit("_", 1)[0] for r in results]


# ----------------------------------------------------------------------
# No Qdrant needed
# ----------------------------------------------------------------------


def test_corpus_chunks_carry_citation_metadata(chunks):
    assert len(chunks) > 1000
    sample = chunks[0]
    for key in ("chunk_id", "document", "document_id", "page", "jurisdiction", "text"):
        assert key in sample, key
    assert all(c["jurisdiction"] for c in chunks)


def test_bm25_finds_the_traditional_knowledge_clause(chunks):
    from bm25_retriever import BM25Retriever

    results = BM25Retriever(chunks).search("Section 3(p) traditional knowledge known properties", top_k=5)
    assert "patents_act_1970" in _doc_ids(results)


def test_bm25_jurisdiction_filter_is_strict(chunks):
    from bm25_retriever import BM25Retriever

    results = BM25Retriever(chunks).search("patent", top_k=20, jurisdiction_filter="India")
    assert results and all(r["jurisdiction"] == "India" for r in results)


def test_embeddings_rank_paraphrase_above_unrelated_text(embedder):
    a, b, c = embedder.embed_documents([
        "An invention that is traditional knowledge is not patentable.",
        "Traditional knowledge cannot be granted a patent.",
        "Bananas contain potassium.",
    ])
    assert len(a) == config.VECTOR_SIZE

    def dot(x, y):
        return sum(p * q for p, q in zip(x, y, strict=True))

    assert dot(a, b) > dot(a, c) + 0.1


def test_reranker_puts_the_relevant_passage_first(reranker):
    passages = [
        {"chunk_id": "irrelevant", "text": "The Trade Marks Registry shall maintain an index of marks."},
        {"chunk_id": "relevant", "text": (
            "(p) an invention which, in effect, is traditional knowledge or which is an "
            "aggregation or duplication of known properties of traditionally known component or components."
        )},
    ]
    ranked = reranker.rerank("Is traditional knowledge patentable?", passages, top_k=2)
    assert ranked[0]["chunk_id"] == "relevant"
    assert ranked[0]["reranker_score"] > ranked[1]["reranker_score"]


def test_context_builder_numbers_sources_and_respects_budget(chunks):
    from context_builder import ContextBuilder

    output = ContextBuilder(max_context_chars=3000).build_context(chunks[:50])
    assert 0 < len(output["context"]) <= 3000
    assert [s["source_number"] for s in output["sources"]] == list(range(1, len(output["sources"]) + 1))
    assert output["context"].startswith("SOURCE 1\n")


# ----------------------------------------------------------------------
# Qdrant-backed
# ----------------------------------------------------------------------


@pytest.mark.parametrize("query, document_id", KNOWN_ANSWERS)
def test_final_retriever_returns_the_governing_instrument(final_retriever, query, document_id):
    results = final_retriever.search(query=query, top_k=5)
    assert document_id in _doc_ids(results), [(r.get("document"), r.get("legal_reference")) for r in results]
    scores = [r["reranker_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_explicit_section_reference_is_ranked_first(final_retriever):
    results = final_retriever.search(query="What does Section 3(p) of the Patents Act say?", top_k=5)
    # Provisions are labelled at section level, so clause (p) lives in a
    # "Section 3" chunk; the right one is the chunk that contains its text.
    top = results[0]
    assert (top.get("document_id"), top["legal_reference"]) == ("patents_act_1970", "Section 3")
    assert "traditional knowledge" in top["text"].lower()


def test_india_scope_is_a_hard_filter(final_retriever):
    results = final_retriever.search(query="patentability of herbal formulations", top_k=10, jurisdiction_filter="India")
    assert results and all(r.get("jurisdiction") == "India" for r in results)
