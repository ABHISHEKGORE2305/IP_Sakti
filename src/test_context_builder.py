from final_retriever import AyurvedicIPRetriever
from context_builder import ContextBuilder


retriever = AyurvedicIPRetriever()

context_builder = ContextBuilder(
    max_context_chars=12000
)


query = "What is Charaka Samhita?"


print("\n")
print("=" * 80)
print(f"QUERY: {query}")
print("=" * 80)


print("\nRetrieving documents...")

results = retriever.search(
    query=query,
    top_k=5,
    candidate_k=10,
)


print(
    f"Retrieved {len(results)} results"
)


print("\nBuilding context...")

output = context_builder.build_context(
    results
)


context = output["context"]
sources = output["sources"]


print("\n")
print("=" * 80)
print("GENERATED CONTEXT")
print("=" * 80)

print(context)


print("\n")
print("=" * 80)
print("SOURCES")
print("=" * 80)


for source in sources:

    print(
        f"\n[{source['source_number']}] "
        f"{source['document']}"
    )

    print(
        f"Page: {source['page']}"
    )

    print(
        f"Chunk: {source['chunk_id']}"
    )

    print(
        f"Reranker Score: "
        f"{source['reranker_score']:.4f}"
    )


print("\n")
print("=" * 80)
print("CONTEXT BUILDER TEST COMPLETE")
print("=" * 80)