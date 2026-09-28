import json

from retriever import AyurvedicRetriever
from bm25_retriever import BM25Retriever
import config


DEFAULT_AUTHORITY_WEIGHT = config.DEFAULT_AUTHORITY_WEIGHT


class AyurvedicHybridRetriever:

    def __init__(
        self,
        chunks_path: str = config.CHUNKS_PATH,
        qdrant_url: str = config.QDRANT_URL,
        collection_name: str = config.COLLECTION_NAME,
    ):

        # --------------------------------
        # Load chunks for BM25
        # --------------------------------

        with open(
            chunks_path,
            "r",
            encoding="utf-8",
        ) as file:

            self.chunks = json.load(file)


        # --------------------------------
        # Initialize retrievers
        # --------------------------------

        self.dense_retriever = (
            AyurvedicRetriever(
                qdrant_url=qdrant_url,
                collection_name=collection_name,
            )
        )

        self.bm25_retriever = (
            BM25Retriever(
                self.chunks
            )
        )


    # --------------------------------
    # Reciprocal Rank Fusion
    # --------------------------------

    @staticmethod
    def reciprocal_rank_fusion(
        result_lists,
        k: int = config.RRF_K,
    ):
        """
        Authority-weighted RRF:

            Score(d) = sum_m [ 1 / (k + Rank_m(d)) ] * Authority(d)

        Authority(d) is the source document's authority_weight
        (statute=1.0 down to reference material=0.5), so a
        statute ranked #3 by both retrievers outranks an
        educational overview ranked #1 by both.
        """

        fused_scores = {}
        result_data = {}

        for results in result_lists:

            for rank, result in enumerate(
                results,
                start=1,
            ):

                chunk_id = result[
                    "chunk_id"
                ]

                authority = (
                    result.get("authority_weight")
                    or DEFAULT_AUTHORITY_WEIGHT
                )

                fused_scores[chunk_id] = (
                    fused_scores.get(
                        chunk_id,
                        0,
                    )
                    + (1 / (k + rank)) * authority
                )

                result_data[
                    chunk_id
                ] = result


        # --------------------------------
        # Sort by RRF score
        # --------------------------------

        ranked_chunk_ids = sorted(
            fused_scores,
            key=fused_scores.get,
            reverse=True,
        )


        # --------------------------------
        # Build final results
        # --------------------------------

        final_results = []

        for chunk_id in ranked_chunk_ids:

            result = result_data[
                chunk_id
            ].copy()

            result["rrf_score"] = (
                fused_scores[chunk_id]
            )

            final_results.append(
                result
            )


        return final_results


    # --------------------------------
    # Hybrid search
    # --------------------------------

    def search(
        self,
        query: str,
        top_k: int = config.TOP_K,
        candidate_k: int = config.CANDIDATE_K,
    ):

        # --------------------------------
        # Dense retrieval
        # --------------------------------

        dense_results = (
            self.dense_retriever.search(
                query,
                top_k=candidate_k,
            )
        )


        # --------------------------------
        # BM25 retrieval
        # --------------------------------

        bm25_results = (
            self.bm25_retriever.search(
                query,
                top_k=candidate_k,
            )
        )


        # --------------------------------
        # RRF fusion
        # --------------------------------

        fused_results = (
            self.reciprocal_rank_fusion(
                [
                    dense_results,
                    bm25_results,
                ]
            )
        )


        return fused_results[:top_k]