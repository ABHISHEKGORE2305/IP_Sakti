from rag_pipeline import AyurvedicIPRAG


rag = AyurvedicIPRAG()


query = "What is Charaka Samhita?"


print("\n")
print("=" * 80)
print(f"QUESTION: {query}")
print("=" * 80)


result = rag.answer(
    query=query,
    top_k=5,
    candidate_k=10,
)


print("\n")
print("=" * 80)
print("ANSWER")
print("=" * 80)

print(result["answer"])


print("\n")
print("=" * 80)
print("SOURCES")
print("=" * 80)


for source in result["sources"]:

    print(
        f"\n[Source {source['source_number']}]"
    )

    print(
        f"Document: "
        f"{source['document']}"
    )

    print(
        f"Page: "
        f"{source['page']}"
    )

    print(
        f"Chunk: "
        f"{source['chunk_id']}"
    )


print("\n")
print("=" * 80)
print("RAG TEST COMPLETE")
print("=" * 80)