from hybrid_retriever import HybridRetriever
from reranker import MedicalIPReranker


class MedicalIPRAGRetriever:

    def __init__(self):

        # --------------------------------
        # Hybrid retrieval
        # --------------------------------

        self.hybrid_retriever = (
            HybridRetriever()
        )


        # --------------------------------
        # Cross-encoder reranker
        # --------------------------------

        self.reranker = (
            MedicalIPReranker()
        )


    # --------------------------------
    # Retrieve + rerank
    # --------------------------------

    def search(
        self,
        query: str,
        retrieval_k: int = 20,
        top_k: int = 5,
    ):

        # -------------------------------
        # Stage 1: Hybrid retrieval
        # -------------------------------

        candidates = (
            self.hybrid_retriever.search(
                query,
                top_k=retrieval_k,
            )
        )


        # -------------------------------
        # Stage 2: Reranking
        # -------------------------------

        results = self.reranker.rerank(

            query,

            candidates,

            top_k=top_k,
        )


        return results
if __name__ == "__main__":

    retriever = MedicalIPRAGRetriever()


    query = (
        "Can I patent an Ayurvedic formulation "
        "if its ingredients are already known?"
    )


    results = retriever.search(
        query,
        retrieval_k=20,
        top_k=5,
    )


    print(
        f"\nQuery:\n{query}\n"
    )


    for i, result in enumerate(
        results,
        start=1,
    ):

        print("=" * 80)

        print(
            f"FINAL RANK: {i}"
        )

        print(
            f"Reranker score: "
            f"{result['rerank_score']:.4f}"
        )

        print(
            f"RRF score: "
            f"{result.get('rrf_score', 0):.5f}"
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