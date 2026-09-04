from hybrid_retriever import AyurvedicHybridRetriever
from reranker import AyurvedicIPReranker


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

    def search(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 20,
    ):

        # --------------------------------
        # STEP 1: Hybrid retrieval
        # --------------------------------

        candidates = self.hybrid_retriever.search(
            query=query,
            top_k=candidate_k,
            candidate_k=candidate_k,
        )

        # --------------------------------
        # STEP 2: Cross-encoder reranking
        # --------------------------------

        reranked_results = self.reranker.rerank(
            query=query,
            results=candidates,
            top_k=top_k,
        )

        return reranked_results