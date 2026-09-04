from sentence_transformers import CrossEncoder


MODEL_NAME = "BAAI/bge-reranker-v2-m3"


class AyurvedicIPReranker:

    def __init__(self):
        print(f"Loading reranker model: {MODEL_NAME}")

        self.model = CrossEncoder(
            MODEL_NAME,
            max_length=512,
        )

        print("Reranker model loaded!")

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: int = 5,
    ):
        if not results:
            return []

        pairs = [
            [query, result["text"]]
            for result in results
        ]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        reranked_results = []

        for result, score in zip(results, scores):

            reranked_result = result.copy()

            reranked_result["reranker_score"] = float(score)

            reranked_results.append(
                reranked_result
            )

        reranked_results.sort(
            key=lambda x: x["reranker_score"],
            reverse=True,
        )

        return reranked_results[:top_k]