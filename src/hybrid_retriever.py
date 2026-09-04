import json

from retriever import AyurvedicRetriever
from bm25_retriever import BM25Retriever


class AyurvedicHybridRetriever:

    def __init__(
        self,
        chunks_path: str = (
            "data/processed/chunks.json"
        ),
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "medical_documents",
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
        k: int = 60,
    ):

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

                fused_scores[chunk_id] = (
                    fused_scores.get(
                        chunk_id,
                        0,
                    )
                    + 1 / (k + rank)
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
        top_k: int = 5,
        candidate_k: int = 20,
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