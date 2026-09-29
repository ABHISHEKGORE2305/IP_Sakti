from rank_bm25 import BM25Okapi


def _jurisdiction_matches(chunk_jurisdiction: str | None, jurisdiction_filter: str | None) -> bool:
    """Same semantics as retriever.jurisdiction_query_filter, applied
    client-side — Qdrant's Filter has no BM25 equivalent, so hybrid_
    retriever needs this to keep both retrieval paths' jurisdiction
    separation consistent."""

    if jurisdiction_filter == "India":
        return chunk_jurisdiction == "India"
    if jurisdiction_filter == "International":
        return chunk_jurisdiction != "India"
    return True


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
        jurisdiction_filter: str | None = None,
        document_id_filter: str | None = None,
    ):

        tokenized_query = self.tokenize(
            query
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        all_ranked = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )

        if jurisdiction_filter:
            all_ranked = [
                i for i in all_ranked
                if _jurisdiction_matches(self.chunks[i].get("jurisdiction"), jurisdiction_filter)
            ]

        if document_id_filter:
            all_ranked = [i for i in all_ranked if self.chunks[i].get("document_id") == document_id_filter]

        ranked_indices = all_ranked[:top_k]


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

                "authority_weight":
                    chunk.get(
                        "authority_weight"
                    ),
            })


        return results