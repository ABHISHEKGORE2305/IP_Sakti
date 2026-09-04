from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(
        self,
        chunks: list[dict],
    ):

        self.chunks = chunks

        # --------------------------------
        # Tokenize documents
        # --------------------------------

        self.tokenized_documents = [
            self.tokenize(
                chunk["text"]
            )
            for chunk in chunks
        ]

        # --------------------------------
        # Create BM25 index
        # --------------------------------

        self.bm25 = BM25Okapi(
            self.tokenized_documents
        )


    # --------------------------------
    # Tokenization
    # --------------------------------

    @staticmethod
    def tokenize(
        text: str
    ):

        return text.lower().split()


    # --------------------------------
    # Search
    # --------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):

        tokenized_query = self.tokenize(
            query
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )[:top_k]


        results = []

        for index in ranked_indices:

            chunk = self.chunks[index]

            results.append({

                "score":
                    float(scores[index]),

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
                    chunk.get(
                        "document"
                    ),

                "document_type":
                    chunk.get(
                        "document_type"
                    ),

                "jurisdiction":
                    chunk.get(
                        "jurisdiction"
                    ),

                "section":
                    chunk.get(
                        "section"
                    ),

                "rule":
                    chunk.get(
                        "rule"
                    ),

                "legal_reference":
                    chunk.get(
                        "legal_reference"
                    ),  

                "language":
                    chunk.get(
                        "language"
                    ),
            })


        return results