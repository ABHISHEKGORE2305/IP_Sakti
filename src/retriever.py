from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from embedding_model import EmbeddingModel
import config


def jurisdiction_query_filter(jurisdiction_filter: str | None) -> "Filter | None":
    """
    Build the Qdrant payload filter enforcing jurisdiction separation at
    RETRIEVAL time (winning_features.md item 2) — not just via which
    specialist agent gets picked, and not just a prompt instruction. This
    is what makes the doc's "architectural" separation claim actually
    true: an India-scoped query cannot retrieve International-jurisdiction
    chunks (or vice versa), regardless of what the LLM does with them.

    "India" -> only chunks whose payload jurisdiction == "India".
    "International" -> everything EXCEPT jurisdiction == "India" (covers
        "International", "United States", "European Union", "United
        Kingdom", ... in one filter — the corpus has several distinct
        non-India jurisdiction values, not just one).
    None / "Both" / anything else -> no filter (unchanged behavior).
    """

    if jurisdiction_filter == "India":
        return Filter(must=[FieldCondition(key="jurisdiction", match=MatchValue(value="India"))])
    if jurisdiction_filter == "International":
        return Filter(must_not=[FieldCondition(key="jurisdiction", match=MatchValue(value="India"))])
    return None


def combined_query_filter(jurisdiction_filter: str | None, document_id_filter: str | None) -> "Filter | None":
    """
    Adds an optional exact document_id restriction on top of
    jurisdiction_query_filter — used by the Law Version Timeline
    (winning_features.md item 9) to scope a query to exactly one known
    version of a law (e.g. "patent_rules_2003" vs
    "3_Patents_Amendment_Rules_2024_16-03-2024"), so the demo moment of
    "ask under the old law vs the current law" is retrieval-enforced, not
    just prompt-suggested — same reasoning as jurisdiction_query_filter.
    """

    conditions = []
    jurisdiction_part = jurisdiction_query_filter(jurisdiction_filter)
    if jurisdiction_part is not None:
        conditions.append(jurisdiction_part)
    if document_id_filter:
        conditions.append(Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=document_id_filter))]))

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return Filter(must=conditions)


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
        jurisdiction_filter: str | None = None,
        document_id_filter: str | None = None,
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

            query_filter=combined_query_filter(jurisdiction_filter, document_id_filter),

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