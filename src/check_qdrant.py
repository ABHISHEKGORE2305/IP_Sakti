from qdrant_client import QdrantClient

import config

QDRANT_URL = config.QDRANT_URL
COLLECTION_NAME = config.COLLECTION_NAME


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
        (point.payload or {}).get("chunk_id")
    )

    print(
        "Document:",
        (point.payload or {}).get("document")
    )

    print(
        "Document Type:",
        (point.payload or {}).get("document_type")
    )

    print(
        "Jurisdiction:",
        (point.payload or {}).get("jurisdiction")
    )

    print(
        "Page:",
        (point.payload or {}).get("page")
    )

    print(
        "Language:",
        (point.payload or {}).get("language")
    )

    print(
        "Section:",
        (point.payload or {}).get("section")
    )

    text = (point.payload or {}).get(
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