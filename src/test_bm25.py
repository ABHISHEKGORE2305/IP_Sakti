import json

from bm25_retriever import BM25Retriever


# --------------------------------
# Load chunks
# --------------------------------

print(
    "\nLoading chunks..."
)

with open(
    "data/processed/chunks.json",
    "r",
    encoding="utf-8",
) as file:

    chunks = json.load(file)


print(
    f"Loaded {len(chunks)} chunks"
)


# --------------------------------
# Create BM25 retriever
# --------------------------------

retriever = BM25Retriever(
    chunks
)


print(
    "BM25 index created"
)


# --------------------------------
# Test queries
# --------------------------------

queries = [

    "Charaka Samhita",

    "Sushruta Samhita",

    "Vedic period",

    "Ayurvedic system of medicine",

]


# --------------------------------
# Run searches
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
            f"BM25 Score: "
            f"{result['score']:.4f}"
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
            "\nText:"
        )

        print(
            result["text"][:700]
        )


print("\n")
print("=" * 80)
print("BM25 TEST COMPLETE")
print("=" * 80)