"""
PRIORITY 1 - quick, human-readable retrieval sanity check.

Runs the demo questions through the existing hybrid + reranker
pipeline (AyurvedicIPRetriever) and prints, per query, the top
retrieved chunks with their document / legal reference / page /
reranker score. No test framework, no assertions - just eyeballing.

Run:
    PYTHONPATH=src python src/eval_retrieval.py
"""

import sys

from final_retriever import AyurvedicIPRetriever


QUERIES = [
    "What is Section 3(p) of the Patents Act?",
    "Can traditional knowledge be patented in India?",
    "Can I patent my new Ayurvedic formulation in India?",
    "Can an Ayurvedic formulation made from known ingredients be patented?",
    "What makes an invention novel under Indian patent law?",
    "What is inventive step?",
    "Can I patent a new process for preparing an Ayurvedic medicine?",
    "What inventions are not patentable in India?",
    "What are the requirements for filing a patent in India?",
    "Does prior art affect my Ayurvedic formulation?",
]


def run(queries, top_k: int = 8, candidate_k: int = 20):

    retriever = AyurvedicIPRetriever()

    for query in queries:

        print("\n" + "=" * 100)
        print(f"QUERY: {query}")
        print("=" * 100)

        results = retriever.search(
            query=query,
            top_k=top_k,
            candidate_k=candidate_k,
        )

        if not results:
            print("  (no results)")
            continue

        for rank, result in enumerate(results, start=1):

            ref = (
                result.get("legal_reference")
                or (
                    f"Section {result['section']}"
                    if result.get("section")
                    else result.get("rule")
                )
                or "-"
            )

            score = result.get("reranker_score")
            score_text = f"{score:+.3f}" if score is not None else "n/a"

            print(
                f"  {rank:>2}. [{score_text}] "
                f"{result.get('document')}  "
                f"| ref={ref}  "
                f"| p.{result.get('page')}  "
                f"| {result.get('chunk_id')}"
            )
            snippet = " ".join(result.get("text", "").split())[:140]
            print(f"       {snippet}")


if __name__ == "__main__":

    selected = QUERIES
    if len(sys.argv) > 1:
        selected = [" ".join(sys.argv[1:])]

    run(selected)
