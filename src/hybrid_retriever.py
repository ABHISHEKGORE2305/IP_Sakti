import json

from retriever import MedicalRetriever
from bm25_retriever import BM25Retriever


class HybridRetriever:

    def __init__(self):

        # --------------------------------
        # Dense retriever
        # --------------------------------

        self.dense_retriever = (
            MedicalRetriever()
        )


        # --------------------------------
        # Load chunks
        # --------------------------------

        with open(
            "data/processed/chunks.json",
            "r",
            encoding="utf-8",
        ) as file:

            chunks = json.load(file)


        # --------------------------------
        # BM25 retriever
        # --------------------------------

        self.bm25_retriever = (
            BM25Retriever(chunks)
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
                start=1
            ):

                key = (
                    result["document_id"],
                    result["page"],
                    result["text"],
                )


                fused_scores[key] = (
                    fused_scores.get(key, 0)
                    + 1 / (k + rank)
                )


                result_data[key] = result


        ranked_keys = sorted(
            fused_scores,
            key=fused_scores.get,
            reverse=True,
        )


        final_results = []


        for key in ranked_keys:

            result = result_data[key].copy()

            result["rrf_score"] = (
                fused_scores[key]
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
    ):

        dense_results = (
            self.dense_retriever.search(
                query,
                top_k=20,
            )
        )


        bm25_results = (
            self.bm25_retriever.search(
                query,
                top_k=20,
            )
        )


        fused_results = (
            self.reciprocal_rank_fusion(
                [
                    dense_results,
                    bm25_results,
                ]
            )
        )


        return fused_results[:top_k]


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    retriever = HybridRetriever()


    query = (
        "tell me about origin of ayurveda"
    )
 

    results = retriever.search(
        query,
        top_k=5,
    )


    print(
        f"\nQuery: {query}\n"
    )


    for i, result in enumerate(
        results,
        start=1
    ):

        print("=" * 80)

        print(
            f"Result #{i}"
        )

        print(
            f"RRF Score: "
            f"{result['rrf_score']:.5f}"
        )

        print(
            f"Source: "
            f"{result['source']}"
        )

        print(
            f"Page: "
            f"{result['page']}"
        )

        print("\nText:")

        print(
            result["text"]
        )

        print()