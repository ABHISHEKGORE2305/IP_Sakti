from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-m3"


class EmbeddingModel:

    def __init__(self):

        print(
            f"Loading embedding model: {MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        print("Embedding model loaded!")

    def embed_text(
        self,
        text: str
    ):

        vector = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return vector.tolist()

    def embed_documents(
        self,
        texts: list[str]
    ):

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return vectors.tolist()


if __name__ == "__main__":

    model = EmbeddingModel()

    text = (
        "Hypertension is persistent elevation "
        "of blood pressure."
    )

    vector = model.embed_text(text)

    print("\nEmbedding generated!")

    print(
        "Vector dimensions:",
        len(vector)
    )

    print(
        "First 10 values:",
        vector[:10]
    )