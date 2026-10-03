import threading
import time

from hybrid_retriever import AyurvedicHybridRetriever
from reranker import AyurvedicIPReranker
from legal_reference import extract_legal_references, match_reference
from bm25_retriever import _jurisdiction_matches
import config


# Score bonuses added on top of the cross-encoder score when the query
# names an explicit provision. Only applied in that case.
EXACT_REFERENCE_BONUS = config.EXACT_REFERENCE_BONUS
SAME_SECTION_BONUS = config.SAME_SECTION_BONUS
STATUTORY_SOURCE_BONUS = config.STATUTORY_SOURCE_BONUS

# Ceiling on chunks force-injected into the reranker pool by the
# exact-reference path — see _inject_exact_matches.
MAX_INJECTED_PER_SEARCH = 12


class AyurvedicIPRetriever:

    def __init__(
        self,
        chunks_path: str = config.CHUNKS_PATH,
        qdrant_url: str = config.QDRANT_URL,
        collection_name: str = config.COLLECTION_NAME,
    ):

        print("\nInitializing hybrid retriever...")

        self.hybrid_retriever = AyurvedicHybridRetriever(
            chunks_path=chunks_path,
            qdrant_url=qdrant_url,
            collection_name=collection_name,
        )

        print("\nInitializing cross-encoder reranker...")

        self.reranker = AyurvedicIPReranker()

        # FastAPI runs the sync /api/chat/ endpoint in a worker threadpool, and
        # the chat UI deliberately lets a user send a second question before the
        # first reply lands — so concurrent calls into these shared torch models
        # are normal, not an edge case. They are not thread-safe, and the work is
        # CPU-bound anyway: running four at once oversubscribed every core and
        # wedged the server so badly that even /health stopped responding.
        # Serialising costs nothing in throughput on a single CPU box and keeps
        # the process responsive. The LLM call is left outside this lock, so
        # generation for several chats still overlaps.
        self._inference_lock = threading.Lock()

        print("\nFinal retriever ready!")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _candidate_from_chunk(self, chunk: dict) -> dict:
        """Shape a raw stored chunk like a retriever result."""

        candidate = {
            key: value
            for key, value in chunk.items()
            if key != "vector"
        }
        candidate.setdefault("score", 0.0)
        candidate["rrf_score"] = 0.0
        candidate["exact_reference_match"] = True
        return candidate

    def _inject_exact_matches(self, references, candidates, jurisdiction_filter=None, document_id_filter=None):
        """
        Make sure the chunks that literally are the requested
        provision are in the pool the reranker sees - otherwise a
        bad dense/BM25 round can drop them before we ever score them.

        jurisdiction_filter/document_id_filter are enforced here too -
        this bypasses the normal hybrid search, so without this check an
        India-scoped (or law-version-scoped) query could still have a
        non-matching chunk injected via an exact statutory-reference
        match, defeating the retrieval-time separation in
        retriever.combined_query_filter/bm25_retriever._jurisdiction_matches.
        """

        present = {c.get("chunk_id") for c in candidates}

        injected = 0

        for chunk in self.hybrid_retriever.chunks:

            # A provision label is not unique across a 4,600-chunk corpus (a
            # long section spans several chunks, and "Rule 2" recurs across
            # instruments), and every injected chunk also receives the +2.0
            # exact-reference bonus. Uncapped, one reference could fill the
            # entire top-k with chunks the ranking never actually chose.
            if injected >= MAX_INJECTED_PER_SEARCH:
                break

            if chunk.get("chunk_id") in present:
                continue

            if not _jurisdiction_matches(chunk.get("jurisdiction"), jurisdiction_filter):
                continue

            if document_id_filter and chunk.get("document_id") != document_id_filter:
                continue

            if any(
                match_reference(ref, chunk) == "exact"
                for ref in references
            ):
                candidates.append(self._candidate_from_chunk(chunk))
                injected += 1

        return candidates

    def _apply_legal_boost(self, references, results):

        for result in results:

            relation = None
            for ref in references:
                current = match_reference(ref, result)
                if current == "exact":
                    relation = "exact"
                    break
                if current == "section":
                    relation = "section"

            bonus = 0.0
            if relation == "exact":
                bonus += EXACT_REFERENCE_BONUS
            elif relation == "section":
                bonus += SAME_SECTION_BONUS

            if bonus and result.get("document_type") in ("statute", "rules"):
                bonus += STATUTORY_SOURCE_BONUS

            result["legal_boost"] = bonus
            result["reranker_score"] = (
                result.get("reranker_score", 0.0) + bonus
            )

        results.sort(
            key=lambda r: r.get("reranker_score", 0.0),
            reverse=True,
        )
        return results

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = config.TOP_K,
        candidate_k: int = config.CANDIDATE_K,
        jurisdiction_filter: str | None = None,
        document_id_filter: str | None = None,
        reference_query: str | None = None,
    ):
        """
        reference_query: the text to mine for explicit statutory references,
        when it differs from the text used for semantic matching. Callers that
        expand a query for retrieval (see query_expansion.py) must pass the
        user's ORIGINAL wording here: an expansion names provisions
        speculatively, and the exact-reference path below injects every chunk
        carrying that label and adds a +2.5 score override — so letting a
        guess drive it lets the expansion overrule the actual ranking.
        """

        references = extract_legal_references(
            reference_query if reference_query is not None else query
        )

        with self._inference_lock:

            # --------------------------------
            # STEP 1: Hybrid retrieval
            # --------------------------------

            _t0 = time.perf_counter()
            candidates = self.hybrid_retriever.search(
                query=query,
                top_k=candidate_k,
                candidate_k=candidate_k,
                jurisdiction_filter=jurisdiction_filter,
                document_id_filter=document_id_filter,
            )

            # --------------------------------
            # No explicit legal reference -> unchanged behaviour
            # --------------------------------

            _t1 = time.perf_counter()

            if not references:
                reranked = self.reranker.rerank(
                    query=query,
                    results=candidates,
                    top_k=top_k,
                )
                print(
                    f"[timing] retrieval hybrid={_t1 - _t0:.2f}s "
                    f"rerank={time.perf_counter() - _t1:.2f}s "
                    f"candidates={len(candidates)}",
                    flush=True,
                )
                return reranked

            # --------------------------------
            # Explicit legal reference -> targeted handling
            # --------------------------------

            candidates = self._inject_exact_matches(
                references, candidates, jurisdiction_filter, document_id_filter
            )

            reranked = self.reranker.rerank(
                query=query,
                results=candidates,
                top_k=len(candidates),
            )
            print(
                f"[timing] retrieval hybrid={_t1 - _t0:.2f}s "
                f"rerank={time.perf_counter() - _t1:.2f}s "
                f"candidates={len(candidates)} (exact-reference path)",
                flush=True,
            )

        reranked = self._apply_legal_boost(references, reranked)

        return reranked[:top_k]
