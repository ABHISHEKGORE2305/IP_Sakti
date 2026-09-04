from hybrid_retriever import AyurvedicHybridRetriever
from reranker import AyurvedicIPReranker
from legal_reference import extract_legal_references, match_reference


# Score bonuses added on top of the cross-encoder score when the query
# names an explicit provision. Only applied in that case.
EXACT_REFERENCE_BONUS = 2.0
SAME_SECTION_BONUS = 0.6
STATUTORY_SOURCE_BONUS = 0.5


class AyurvedicIPRetriever:

    def __init__(
        self,
        chunks_path: str = "data/processed/chunks.json",
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "medical_documents",
    ):

        print("\nInitializing hybrid retriever...")

        self.hybrid_retriever = AyurvedicHybridRetriever(
            chunks_path=chunks_path,
            qdrant_url=qdrant_url,
            collection_name=collection_name,
        )

        print("\nInitializing cross-encoder reranker...")

        self.reranker = AyurvedicIPReranker()

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

    def _inject_exact_matches(self, references, candidates):
        """
        Make sure the chunks that literally are the requested
        provision are in the pool the reranker sees - otherwise a
        bad dense/BM25 round can drop them before we ever score them.
        """

        present = {c.get("chunk_id") for c in candidates}

        for chunk in self.hybrid_retriever.chunks:

            if chunk.get("chunk_id") in present:
                continue

            if any(
                match_reference(ref, chunk) == "exact"
                for ref in references
            ):
                candidates.append(self._candidate_from_chunk(chunk))

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
        top_k: int = 5,
        candidate_k: int = 20,
    ):

        references = extract_legal_references(query)

        # --------------------------------
        # STEP 1: Hybrid retrieval
        # --------------------------------

        candidates = self.hybrid_retriever.search(
            query=query,
            top_k=candidate_k,
            candidate_k=candidate_k,
        )

        # --------------------------------
        # No explicit legal reference -> unchanged behaviour
        # --------------------------------

        if not references:
            return self.reranker.rerank(
                query=query,
                results=candidates,
                top_k=top_k,
            )

        # --------------------------------
        # Explicit legal reference -> targeted handling
        # --------------------------------

        candidates = self._inject_exact_matches(references, candidates)

        reranked = self.reranker.rerank(
            query=query,
            results=candidates,
            top_k=len(candidates),
        )

        reranked = self._apply_legal_boost(references, reranked)

        return reranked[:top_k]
