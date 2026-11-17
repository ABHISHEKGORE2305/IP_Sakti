"""
Tests for jurisdiction-aware candidate pooling and ranking in
final_retriever.AyurvedicIPRetriever (no models, Qdrant or LLM: the
hybrid retriever and reranker are stubs).

International scope used to be a hard "exclude India" filter, which left
~150 searchable chunks and dropped the India-labelled sources that describe
international mechanisms (TKDL factsheet for "how does the USPTO use TKDL",
Patents Act PCT provisions). It is now a pooled search with a score penalty
on India sources; India scope is still a hard filter.

Run directly:      python src/tests/test_jurisdiction_ranking.py
Run with pytest:   pytest src/tests/test_jurisdiction_ranking.py
"""

import os
import sys

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import final_retriever  # noqa: E402
from final_retriever import AyurvedicIPRetriever  # noqa: E402


def _chunk(cid, jurisdiction, text="", score=0.5):
    return {"chunk_id": cid, "jurisdiction": jurisdiction, "text": text, "score": score}


class _StubHybrid:
    """Returns India + international chunks unless a filter narrows them,
    mirroring bm25_retriever._jurisdiction_matches."""

    def __init__(self, chunks):
        self.chunks = chunks
        self.calls = []

    def search(self, query, top_k, candidate_k, jurisdiction_filter=None, document_id_filter=None):
        self.calls.append(jurisdiction_filter)
        if jurisdiction_filter == "India":
            return [dict(c) for c in self.chunks if c["jurisdiction"] == "India"]
        if jurisdiction_filter == "International":
            return [dict(c) for c in self.chunks if c["jurisdiction"] != "India"]
        return [dict(c) for c in self.chunks]


class _StubReranker:
    """Scores each chunk by a fixed table keyed on chunk_id."""

    def __init__(self, scores):
        self.scores = scores

    def rerank(self, query, results, top_k=5):
        out = [dict(r, reranker_score=self.scores[r["chunk_id"]]) for r in results]
        out.sort(key=lambda r: r["reranker_score"], reverse=True)
        return out[:top_k]


def _retriever(chunks, scores):
    import threading

    r = AyurvedicIPRetriever.__new__(AyurvedicIPRetriever)
    r.hybrid_retriever = _StubHybrid(chunks)
    r.reranker = _StubReranker(scores)
    r._inference_lock = threading.Lock()
    return r


CHUNKS = [
    _chunk("tkdl", "India", "TKDL access agreements with USPTO and EPO"),
    _chunk("patents_s3", "India", "3. What are not inventions"),
    _chunk("gratk", "International", "GRATK Article 3 disclosure"),
    _chunk("fda", "United States", "Botanical drug guidance"),
]


def test_international_pools_india_sources_once():
    r = _retriever(CHUNKS, {})
    pooled = r._hybrid_candidates("q", 12, "International", None)
    ids = [c["chunk_id"] for c in pooled]
    assert r.hybrid_retriever.calls == ["International", None]
    assert sorted(ids) == sorted(c["chunk_id"] for c in CHUNKS)
    assert len(ids) == len(set(ids)), "pooled candidates must be de-duplicated"
    # International-filtered hits come first, so a candidate cap keeps them.
    assert ids[:2] == ["gratk", "fda"]


def test_india_scope_is_still_a_single_hard_filtered_search():
    r = _retriever(CHUNKS, {})
    pooled = r._hybrid_candidates("q", 12, "India", None)
    assert r.hybrid_retriever.calls == ["India"]
    assert {c["jurisdiction"] for c in pooled} == {"India"}


def test_penalty_ranks_india_below_comparable_international_source():
    p = final_retriever.OFF_JURISDICTION_PENALTY
    r = _retriever(CHUNKS, {"tkdl": 0.60, "patents_s3": 0.05,
                            "gratk": 0.60 - p / 2, "fda": 0.01})
    results = r.search("q", top_k=4, jurisdiction_filter="International",
                       reference_query="how does the USPTO use TKDL")
    ids = [c["chunk_id"] for c in results]
    assert ids.index("gratk") < ids.index("tkdl")
    tkdl = next(c for c in results if c["chunk_id"] == "tkdl")
    assert abs(tkdl["reranker_score"] - (0.60 - p)) < 1e-9
    assert tkdl["jurisdiction_penalty"] == p


def test_strongly_relevant_india_source_still_reaches_top_k():
    """The point of the change: the TKDL factsheet answers a USPTO/TKDL
    question even under International scope."""

    r = _retriever(CHUNKS, {"tkdl": 0.95, "patents_s3": 0.02, "gratk": 0.10, "fda": 0.01})
    results = r.search("q", top_k=2, jurisdiction_filter="International",
                       reference_query="how does the USPTO use TKDL")
    assert [c["chunk_id"] for c in results][0] == "tkdl"


def test_no_penalty_outside_international_scope():
    r = _retriever(CHUNKS, {"tkdl": 0.9, "patents_s3": 0.8, "gratk": 0.7, "fda": 0.6})
    for scope in (None, "India"):
        results = r.search("q", top_k=4, jurisdiction_filter=scope, reference_query="q")
        assert all("jurisdiction_penalty" not in c for c in results), scope
        scores = [c["reranker_score"] for c in results]
        assert scores == sorted(scores, reverse=True)


# ------------------------------------------------------------------


def _run_standalone():
    tests = [
        (name, obj)
        for name, obj in sorted(globals().items())
        if name.startswith("test_") and callable(obj)
    ]

    passed = 0
    failed = 0

    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {name}\n      {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"ERROR {name}\n      {type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"ok    {name}")

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_standalone())
