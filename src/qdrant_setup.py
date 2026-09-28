from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

import config


QDRANT_URL = config.QDRANT_URL

COLLECTION_NAME = config.COLLECTION_NAME

VECTOR_SIZE = config.VECTOR_SIZE


# --------------------------------
# Connect to Qdrant
# --------------------------------

client = QdrantClient(
    url=QDRANT_URL
)

print("Connected to Qdrant")


# --------------------------------
# Create collection if it doesn't exist
# --------------------------------

if not client.collection_exists(COLLECTION_NAME):

    print(
        f"Creating collection: {COLLECTION_NAME}"
    )

    client.create_collection(
        collection_name=COLLECTION_NAME,

        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print("Collection created successfully!")

else:

    print(
        f"Collection already exists: "
        f"{COLLECTION_NAME}"
    )


# --------------------------------
# Get collection information
# --------------------------------

collection_info = client.get_collection(
    COLLECTION_NAME
)


print("\nCollection Information:")
print(
    "Collection:",
    COLLECTION_NAME
)

print(
    "Vector size:",
    VECTOR_SIZE
)

print(
    "Distance:",
    "COSINE"
)

print(
    "Points stored:",
    collection_info.points_count
)


# --------------------------------
# List all collections
# --------------------------------

collections = client.get_collections()

print("\nAvailable collections:")

for collection in collections.collections:

    print(
        "-",
        collection.name
    )