from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)


class QdrantVectorStore:

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "medical_documents",
        vector_size: int = 1024,
    ):

        self.collection_name = collection_name
        self.vector_size = vector_size

        self.client = QdrantClient(
            url=url
        )

        self._create_collection_if_needed()


    # --------------------------------
    # Create collection
    # --------------------------------

    def _create_collection_if_needed(self):

        if not self.client.collection_exists(
            self.collection_name
        ):

            self.client.create_collection(

                collection_name=self.collection_name,

                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

            print(
                f"Created collection: "
                f"{self.collection_name}"
            )

        else:

            print(
                f"Collection already exists: "
                f"{self.collection_name}"
            )


    # --------------------------------
    # Insert chunks
    # --------------------------------

    def add_chunks(
        self,
        chunks: list[dict],
        batch_size: int = 64,
    ):

        points = []

        for chunk in chunks:

            point = PointStruct(

                id=chunk["chunk_id"],

                vector=chunk["vector"],

                payload={
                    "text": chunk["text"],

                    "source": chunk["source"],

                    "page": chunk["page"],

                    "document_id": chunk[
                        "document_id"
                    ],
                },
            )

            points.append(point)


        # --------------------------------
        # Upload in batches
        # --------------------------------

        for start in range(
            0,
            len(points),
            batch_size
        ):

            batch = points[
                start:start + batch_size
            ]

            self.client.upsert(

                collection_name=self.collection_name,

                points=batch,
            )

            print(
                f"Uploaded "
                f"{len(batch)} vectors"
            )


        print(
            f"\nSuccessfully uploaded "
            f"{len(points)} chunks"
        )