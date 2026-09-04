from retriever import AyurvedicRetriever


retriever = AyurvedicRetriever()


queries = [
    "What is Ayurveda?",
    "What are the origins of Ayurveda?",
    "What are the basic principles of Ayurveda?",
]


for query in queries:

    print("\n")
    print("=" * 80)

    print(
        f"QUERY: {query}"
    )

    print("=" * 80)


    results = retriever.search(
        query,
        top_k=3,
    )


    for rank, result in enumerate(
        results,
        start=1
    ):

        print("\n")
        print(
            f"RESULT {rank}"
        )

        print(
            f"Score: "
            f"{result['score']:.4f}"
        )

        print(
            f"Chunk ID: "
            f"{result['chunk_id']}"
        )

        print(
            f"Document: "
            f"{result['document']}"
        )

        print(
            f"Page: "
            f"{result['page']}"
        )

        print(
            f"Section: "
            f"{result['section']}"
        )

        print(
            "\nText:"
        )

        print(
            result["text"][:700]
        )