from qdrant_client import QdrantClient

from embedding_model import EmbeddingModel
import config


class AyurvedicRetriever:

    def __init__(
        self,
        qdrant_url: str = config.QDRANT_URL,
        collection_name: str = config.COLLECTION_NAME,
        api_key: str | None = config.QDRANT_API_KEY,
    ):

        self.client = QdrantClient(
            url=qdrant_url,
            api_key=api_key,
        )

        self.collection_name = (
            collection_name
        )

        self.embedding_model = (
            EmbeddingModel()
        )


    # --------------------------------
    # Semantic search
    # --------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):

        # --------------------------------
        # Convert query into embedding
        # --------------------------------

        query_vector = (
            self.embedding_model.embed_text(
                query
            )
        )


        # --------------------------------
        # Search Qdrant
        # --------------------------------

        results = self.client.query_points(

            collection_name=(
                self.collection_name
            ),

            query=query_vector,

            limit=top_k,

            with_payload=True,
        ).points


        # --------------------------------
        # Format results
        # --------------------------------

        formatted_results = []

        for result in results:

            payload = result.payload

            formatted_results.append({

                "score":
                    result.score,

                "chunk_id":
                    payload.get(
                        "chunk_id"
                    ),

                "text":
                    payload.get(
                        "text"
                    ),

                "source":
                    payload.get(
                        "source"
                    ),

                "page":
                    payload.get(
                        "page"
                    ),

                "document_id":
                    payload.get(
                        "document_id"
                    ),

                "document":
                    payload.get(
                        "document"
                    ),

                "document_type":
                    payload.get(
                        "document_type"
                    ),

                "jurisdiction":
                    payload.get(
                        "jurisdiction"
                    ),

                "section":
                    payload.get(
                        "section"
                    ),

                "rule":
                    payload.get(
                        "rule"
                    ),

                "legal_reference":
                    payload.get(
                        "legal_reference"
                    ),  

                "language":
                    payload.get(
                        "language"
                    ),

                "authority_weight":
                    payload.get(
                        "authority_weight"
                    ),
            })

        return formatted_results