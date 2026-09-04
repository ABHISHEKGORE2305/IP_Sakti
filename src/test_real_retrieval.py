from final_retriever import AyurvedicIPRetriever


retriever = AyurvedicIPRetriever()


queries = [
    "Can I patent my new Ayurvedic formulation in India?",
    "Can traditional knowledge be patented?",
    "What inventions are not patentable in India?",
    "What is Section 3(p) of the Patents Act?",
    "What is novelty in patent law?",
    "What is inventive step?",
    "Can an Ayurvedic formulation made from known ingredients be patented?",
    "Can a new process for preparing an Ayurvedic medicine be patented?",
]


for query in queries:

    print("\n")
    print("=" * 80)
    print("QUERY:")
    print(query)
    print("=" * 80)

    results = retriever.search(
        query=query,
        top_k=5,
        candidate_k=20,
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print("\n" + "-" * 70)

        print(f"RANK: {rank}")

        print(
            f"Document: "
            f"{result.get('document')}"
        )

        print(
            f"Type: "
            f"{result.get('document_type')}"
        )

        print(
            f"Page: "
            f"{result.get('page')}"
        )

        print(
            f"Chunk: "
            f"{result.get('chunk_id')}"
        )

        print(
            f"Reranker score: "
            f"{result.get('reranker_score')}"
        )

        print("\nText:")

        print(
            result["text"][:500]
        )