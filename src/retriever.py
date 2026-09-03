from qdrant_client import QdrantClient

from embedding_model import EmbeddingModel


class MedicalRetriever:

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "medical_documents",
    ):

        # --------------------------------
        # Connect to Qdrant
        # --------------------------------

        self.client = QdrantClient(
            url=qdrant_url
        )

        self.collection_name = (
            collection_name
        )


        # --------------------------------
        # Load embedding model
        # --------------------------------

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

        # Convert question to embedding

        query_vector = (
            self.embedding_model.embed_text(
                query
            )
        )


        # Search Qdrant

        results = self.client.query_points(

            collection_name=self.collection_name,

            query=query_vector,

            limit=top_k,

            with_payload=True,

        ).points


        # Format results

        formatted_results = []


        for result in results:

            formatted_results.append({

                "score": result.score,

                "text": result.payload[
                    "text"
                ],

                "source": result.payload[
                    "source"
                ],

                "page": result.payload[
                    "page"
                ],

                "document_id": result.payload[
                    "document_id"
                ],

            })


        return formatted_results


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    retriever = MedicalRetriever()


    question = (
        "history of ayurveda"
    )


    results = retriever.search(
        question,
        top_k=5,
    )


    print(
        f"\nQuestion: {question}"
    )


    print(
        f"\nRetrieved "
        f"{len(results)} chunks\n"
    )


    for i, result in enumerate(
        results,
        start=1
    ):

        print("=" * 80)

        print(
            f"Result #{i}"
        )

        print(
            f"Score: "
            f"{result['score']:.4f}"
        )

        print(
            f"Source: "
            f"{result['source']}"
        )

        print(
            f"Page: "
            f"{result['page']}"
        )

        print("\nText:")

        print(
            result["text"]
        )

        print()