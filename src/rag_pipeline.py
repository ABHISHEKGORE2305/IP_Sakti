"""
End-to-end RAG pipeline:

    query -> hybrid retrieval -> cross-encoder rerank -> context builder
          -> Gemini -> grounded answer + citations

Interactive demo:
    PYTHONPATH=src python src/rag_pipeline.py
"""

from final_retriever import AyurvedicIPRetriever
from context_builder import ContextBuilder
from llm import GeminiLLM, LLMError
from prompt import SYSTEM_PROMPT, history_block_text
from query_expansion import QueryExpander
import config


INSUFFICIENT_CONTEXT_MESSAGE = (
    "The available sources do not contain enough information to answer "
    "this question."
)


class AyurvedicIPRAG:

    def __init__(
        self,
        top_k: int = config.TOP_K,
        candidate_k: int = config.CANDIDATE_K,
        max_context_chars: int = config.MAX_CONTEXT_CHARS,
    ):

        print("\nInitializing RAG system...")

        self.top_k = top_k
        self.candidate_k = candidate_k

        self.retriever = AyurvedicIPRetriever()
        self.context_builder = ContextBuilder(
            max_context_chars=max_context_chars
        )
        self.llm = GeminiLLM()
        self.query_expander = QueryExpander(llm=self.llm)

        print("\nRAG system ready!\n")

    # ------------------------------------------------------------------

    def answer(
        self,
        query: str,
        top_k: int | None = None,
        candidate_k: int | None = None,
        jurisdiction_filter: str | None = None,
        document_id_filter: str | None = None,
        history: list[dict] | None = None,
    ) -> dict:

        query = (query or "").strip()

        if not query:
            return {
                "query": query,
                "answer": "Please enter a question.",
                "sources": [],
                "retrieved": [],
                "error": "empty_query",
            }

        top_k = top_k or self.top_k
        candidate_k = candidate_k or self.candidate_k

        # ---------------- retrieval ----------------
        # Retrieve on the statutory-vocabulary expansion, generate from the
        # user's own wording — see query_expansion.py.
        retrieval_query = self.query_expander.expand(query)

        try:
            results = self.retriever.search(
                query=retrieval_query,
                top_k=top_k,
                candidate_k=candidate_k,
                jurisdiction_filter=jurisdiction_filter,
                document_id_filter=document_id_filter,
                reference_query=query,
            )
        except Exception as exc:  # noqa: BLE001
            return {
                "query": query,
                "answer": (
                    "Retrieval is unavailable right now. Please check that "
                    "Qdrant is running on http://localhost:6333."
                ),
                "sources": [],
                "retrieved": [],
                "error": f"retrieval_failed: {exc}",
            }

        if not results:
            return {
                "query": query,
                "answer": INSUFFICIENT_CONTEXT_MESSAGE,
                "sources": [],
                "retrieved": [],
                "error": "no_results",
            }

        # ---------------- context ----------------
        context_data = self.context_builder.build_context(results)
        context = context_data["context"]
        sources = context_data["sources"]

        retrieved = [
            {
                "rank": index,
                "document": r.get("document"),
                "legal_reference": (
                    r.get("legal_reference")
                    or (
                        f"Section {r['section']}"
                        if r.get("section")
                        else r.get("rule")
                    )
                ),
                "page": r.get("page"),
                "chunk_id": r.get("chunk_id"),
                "reranker_score": r.get("reranker_score"),
                "snippet": " ".join((r.get("text") or "").split())[:240],
            }
            for index, r in enumerate(results, start=1)
        ]

        # ---------------- generation ----------------
        prompt = SYSTEM_PROMPT.format(
            context=context,
            query=query,
            persona_guidance="",
            history_block=history_block_text(history),
        )

        try:
            answer_text = self.llm.generate(prompt)
        except LLMError as exc:
            return {
                "query": query,
                "answer": (
                    "The language model could not be reached, so no "
                    "generated answer is available. The retrieved sources "
                    "below are still relevant."
                ),
                "sources": sources,
                "retrieved": retrieved,
                "error": f"llm_failed: {exc}",
            }

        return {
            "query": query,
            "answer": answer_text,
            "sources": sources,
            "retrieved": retrieved,
        }


# ----------------------------------------------------------------------
# Interactive demo
# ----------------------------------------------------------------------


def _print_answer(response: dict) -> None:

    print("\n" + "-" * 80)
    print("RETRIEVED (query -> legal sources)")
    print("-" * 80)

    if not response["retrieved"]:
        print("  (nothing retrieved)")
    for item in response["retrieved"]:
        score = item.get("reranker_score")
        score_text = f"{score:+.3f}" if score is not None else "n/a"
        print(
            f"  {item['rank']:>2}. [{score_text}] {item['document']} "
            f"| {item['legal_reference'] or '-'} | p.{item['page']}"
        )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(response["answer"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)
    if not response["sources"]:
        print("  (none)")
    for source in response["sources"]:
        line = f"  {source['source_number']}. {source.get('document')}"
        ref = source.get("legal_reference") or source.get("rule")
        if ref:
            line += f"\n     {ref}"
        if source.get("page") is not None:
            line += f"\n     Page {source.get('page')}"
        print(line)

    if response.get("error"):
        print(f"\n[note: {response['error']}]")
    print()


def main() -> None:

    rag = AyurvedicIPRAG()

    print("Ask a question about Indian patent law / Ayurvedic inventions.")
    print("Press Enter on an empty line (or Ctrl-C) to quit.\n")

    while True:
        try:
            query = input("Ask: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query:
            break

        response = rag.answer(query)
        _print_answer(response)


if __name__ == "__main__":
    main()
