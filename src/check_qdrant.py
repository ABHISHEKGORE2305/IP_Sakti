from qdrant_client import QdrantClient


QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "medical_documents"


client = QdrantClient(
    url=QDRANT_URL
)


# --------------------------------
# Collection information
# --------------------------------

print("\n==============================")
print("QDRANT COLLECTION")
print("==============================")

info = client.get_collection(
    COLLECTION_NAME
)

print(
    f"Collection: {COLLECTION_NAME}"
)

print(
    f"Points stored: {info.points_count}"
)


# --------------------------------
# Retrieve sample points
# --------------------------------

print("\n==============================")
print("SAMPLE POINTS")
print("==============================")


points = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=3,
    with_payload=True,
    with_vectors=False,
)[0]


for point in points:

    print("\n------------------------------")

    print(
        "Qdrant ID:",
        point.id
    )

    print(
        "Chunk ID:",
        point.payload.get("chunk_id")
    )

    print(
        "Document:",
        point.payload.get("document")
    )

    print(
        "Document Type:",
        point.payload.get("document_type")
    )

    print(
        "Jurisdiction:",
        point.payload.get("jurisdiction")
    )

    print(
        "Page:",
        point.payload.get("page")
    )

    print(
        "Language:",
        point.payload.get("language")
    )

    print(
        "Section:",
        point.payload.get("section")
    )

    text = point.payload.get(
        "text",
        ""
    )

    print(
        "Text:",
        text[:300],
        "..."
    )


print("\n==============================")
print("VERIFICATION COMPLETE")
print("==============================")