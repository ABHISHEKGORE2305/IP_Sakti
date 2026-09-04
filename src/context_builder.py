class ContextBuilder:

    def __init__(
        self,
        max_context_chars: int = 12000,
    ):
        self.max_context_chars = max_context_chars

    def build_context(
        self,
        results: list[dict],
    ):

        context_parts = []
        sources = []

        current_length = 0

        for index, result in enumerate(
            results,
            start=1,
        ):

            text = result["text"]

            source_block = (
                f"SOURCE {index}\n"
                f"Document: {result.get('document')}\n"
                f"Page: {result.get('page')}\n"
                f"Chunk ID: {result.get('chunk_id')}\n"
                f"\n"
                f"{text}\n"
            )

            if (
                current_length
                + len(source_block)
                > self.max_context_chars
            ):
                break

            context_parts.append(source_block)

            sources.append({
                "source_number": index,
                "chunk_id": result.get("chunk_id"),
                "document": result.get("document"),
                "document_id": result.get("document_id"),
                "source": result.get("source"),
                "page": result.get("page"),
                "section": result.get("section"),
                "reranker_score": result.get(
                    "reranker_score"
                ),
            })

            current_length += len(source_block)

        context = "\n\n".join(
            context_parts
        )

        return {
            "context": context,
            "sources": sources,
        }