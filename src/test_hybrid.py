from hybrid_retriever import (
    AyurvedicHybridRetriever
)


# --------------------------------
# Initialize
# --------------------------------

retriever = AyurvedicHybridRetriever()


# --------------------------------
# Test queries
# --------------------------------

queries = [

    "What is Ayurveda?",

    "What are the origins of Ayurveda?",

    "Charaka Samhita",

    "Sushruta Samhita",

    "Vedic period",

]


# --------------------------------
# Run hybrid search
# --------------------------------

for query in queries:

    print("\n")
    print("=" * 80)

    print(
        f"QUERY: {query}"
    )

    print("=" * 80)


    results = retriever.search(
        query,
        top_k=5,
        candidate_k=10,
    )


    for rank, result in enumerate(
        results,
        start=1,
    ):

        print("\n")

        print(
            f"RESULT {rank}"
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

        print(
            "\nText:"
        )

        print(
            result["text"][:600]
        )


print("\n")
print("=" * 80)
print("HYBRID RETRIEVAL TEST COMPLETE")
print("=" * 80)