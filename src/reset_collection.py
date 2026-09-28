from qdrant_client import QdrantClient

import config


QDRANT_URL = config.QDRANT_URL
COLLECTION_NAME = config.COLLECTION_NAME


client = QdrantClient(
    url=QDRANT_URL
)


print(
    f"Checking collection: {COLLECTION_NAME}"
)


if client.collection_exists(
    COLLECTION_NAME
):

    print(
        f"Deleting collection: {COLLECTION_NAME}"
    )

    client.delete_collection(
        collection_name=COLLECTION_NAME
    )

    print(
        "Collection deleted successfully"
    )

else:

    print(
        "Collection does not exist"
    )


print("\nReset complete!")