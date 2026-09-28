import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

import config


class QdrantVectorStore:

    def __init__(
        self,
        url: str = config.QDRANT_URL,
        collection_name: str = config.COLLECTION_NAME,
        vector_size: int = config.VECTOR_SIZE,
        api_key: str | None = config.QDRANT_API_KEY,
    ):

        self.collection_name = collection_name
        self.vector_size = vector_size

        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=60.0,
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
    # Generate deterministic Qdrant ID
    # --------------------------------

    @staticmethod
    def generate_point_id(chunk_id: str) -> str:

        return str(
            uuid.uuid5(
                uuid.NAMESPACE_DNS,
                chunk_id,
            )
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

            point_id = self.generate_point_id(
                chunk["chunk_id"]
            )

            point = PointStruct(

                # Qdrant requires UUID or integer
                id=point_id,

                # 1024-dimensional embedding
                vector=chunk["vector"],

                # Chunk metadata
                payload={

                    "chunk_id":
                        chunk["chunk_id"],

                    "text":
                        chunk["text"],

                    "source":
                        chunk["source"],

                    "page":
                        chunk["page"],

                    "document_id":
                        chunk["document_id"],

                    "document":
                        chunk.get("document"),

                    "document_type":
                        chunk.get("document_type"),

                    "jurisdiction":
                        chunk.get("jurisdiction"),

                    "section":
                        chunk.get("section"),

                    "rule":
                        chunk.get("rule"),

                    "legal_reference":
                        chunk.get("legal_reference"),

                    "language":
                        chunk.get("language"),

                    "authority_weight":
                        chunk.get("authority_weight"),
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