from hybrid_retriever import AyurvedicHybridRetriever
from reranker import AyurvedicIPReranker


print("Initializing hybrid retriever...")

hybrid_retriever = AyurvedicHybridRetriever()

print("\nInitializing reranker...")

reranker = AyurvedicIPReranker()


queries = [
    "What is Ayurveda?",
    "What are the origins of Ayurveda?",
    "What is Charaka Samhita?",
    "What is the Vedic period?",
]


for query in queries:

    print("\n")
    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    print("\nRetrieving hybrid candidates...")

    candidates = hybrid_retriever.search(
        query,
        top_k=10,
        candidate_k=10,
    )

    print(
        f"Retrieved {len(candidates)} candidates"
    )

    print("\nReranking candidates...")

    results = reranker.rerank(
        query,
        candidates,
        top_k=5,
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print("\n")
        print(f"RESULT {rank}")

        print(
            f"Reranker Score: "
            f"{result['reranker_score']:.4f}"
        )

        print(
            f"RRF Score: "
            f"{result['rrf_score']:.6f}"
        )

        print(
            f"Chunk ID: "
            f"{result['chunk_id']}"
        )

        print(
            f"Page: "
            f"{result['page']}"
        )

        print(
            f"Document: "
            f"{result['document']}"
        )

        print("\nText:")

        print(
            result["text"][:600]
        )


print("\n")
print("=" * 80)
print("RERANKER TEST COMPLETE")
print("=" * 80)