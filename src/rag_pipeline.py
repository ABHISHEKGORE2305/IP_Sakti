from final_retriever import AyurvedicIPRetriever
from context_builder import ContextBuilder
from llm import GeminiLLM
from prompt import SYSTEM_PROMPT


class AyurvedicIPRAG:

    def __init__(self):

        print("\nInitializing RAG system...")

        self.retriever = AyurvedicIPRetriever()

        self.context_builder = ContextBuilder(
            max_context_chars=12000
        )

        self.llm = GeminiLLM()

        print("\nRAG system ready!")

    def answer(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 10,
    ):

        # -----------------------------
        # STEP 1: Retrieve
        # -----------------------------

        results = self.retriever.search(
            query=query,
            top_k=top_k,
            candidate_k=candidate_k,
        )

        # -----------------------------
        # STEP 2: Build context
        # -----------------------------

        context_data = (
            self.context_builder.build_context(
                results
            )
        )

        context = context_data["context"]
        sources = context_data["sources"]

        # -----------------------------
        # STEP 3: Build prompt
        # -----------------------------

        prompt = SYSTEM_PROMPT.format(
            context=context,
            query=query,
        )

        # -----------------------------
        # STEP 4: Generate answer
        # -----------------------------

        answer = self.llm.generate(
            prompt
        )

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
        }