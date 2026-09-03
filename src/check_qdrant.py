from qdrant_client import QdrantClient


client = QdrantClient(
    url="http://localhost:6333"
)


COLLECTION_NAME = "medical_documents"


# --------------------------------
# Collection information
# --------------------------------

info = client.get_collection(
    COLLECTION_NAME
)


print("\nCollection information:")

print(
    "Vectors:",
    info.points_count
)


# --------------------------------
# Retrieve stored points
# --------------------------------

results = client.scroll(
    collection_name=COLLECTION_NAME,

    limit=3,

    with_payload=True,

    with_vectors=False,
)


points = results[0]


print("\nStored documents:\n")


for point in points:

    print("=" * 70)

    print("ID:", point.id)

    print(
        "Source:",
        point.payload["source"]
    )

    print(
        "Page:",
        point.payload["page"]
    )

    print(
        "Document:",
        point.payload["document_id"]
    )

    print("\nText:")

    print(
        point.payload["text"][:500]
    )