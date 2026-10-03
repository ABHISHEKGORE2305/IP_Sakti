import os

from sentence_transformers import CrossEncoder

import config


MODEL_NAME = config.RERANKER_MODEL_NAME


class AyurvedicIPReranker:

    def __init__(self):
        print(f"Loading reranker model: {MODEL_NAME}")

        # bf16 is ~3.5x faster than fp32 on CPUs with bf16 support (AMX/
        # AVX512-bf16, e.g. AWS c7i): 12 passages took 16.3s in fp32 vs 4.7s
        # in bf16 on a 4-vCPU c7i, with a max score difference of ~0.004.
        # RERANKER_BF16=0 forces fp32 (e.g. on CPUs without bf16 support).
        self.model = None
        if os.getenv("RERANKER_BF16", "1") != "0":
            try:
                import torch

                self.model = CrossEncoder(
                    MODEL_NAME,
                    max_length=512,
                    model_kwargs={"torch_dtype": torch.bfloat16},
                )
                print("Reranker running in bf16")
            except Exception as exc:  # noqa: BLE001
                print(f"[reranker] bf16 unavailable ({exc}); using fp32")

        if self.model is None:
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