"""
Multi-Factor Confidence Scoring & Safe Abstention Guardrail.

    Confidence = 0.40 * S_rerank + 0.30 * S_retrieval_density
               + 0.20 * S_authority + 0.10 * S_query_term_coverage

    Score >= 0.75         -> High confidence
    0.50 <= Score < 0.75  -> Medium confidence
    Score < 0.50          -> Low confidence / safe abstention

A citation-verification report (see agents.citation_agent) can further
downgrade the band: any unverified ("hallucinated") citation caps the
band at Medium, and citation precision below 0.5 forces abstention
regardless of the retrieval-side score — in keeping with the
platform's zero-phantom-citation target.
"""

import math
import re

import config


ABSTENTION_MESSAGE = (
    "I could not locate sufficiently authoritative statutory provisions "
    "or official guidelines to answer this specific query with certainty. "
    "In accordance with legal safety guidelines, I will not generate an "
    "unsubstantiated legal interpretation. Please consult an accredited "
    "IP professional or refer to the primary portals listed below."
)

HIGH_THRESHOLD = config.HIGH_THRESHOLD
MEDIUM_THRESHOLD = config.MEDIUM_THRESHOLD

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "of", "in", "on", "for", "to", "and", "or", "but", "with", "as",
    "by", "at", "from", "this", "that", "these", "those", "it", "its",
    "can", "does", "do", "what", "which", "who", "how", "i", "we",
    "you", "my", "our",
}


# bge-reranker-v2-m3 (see reranker.py) does not center its raw scores
# on 0 the way a plain sigmoid assumes: empirically, a genuinely
# relevant query/passage pair scores strongly positive (+0.5 to +3+),
# while a genuinely irrelevant one clusters just ABOVE zero
# (~0.0001-0.0004), not negative. An unshifted sigmoid(x) maps that
# near-zero "no signal" case to ~0.5 ("medium confidence"), which is
# exactly backwards - it was letting the pipeline treat out-of-corpus
# queries (e.g. "what's a good pizza recipe?") as medium-confidence
# instead of triggering abstention. Shifting the sigmoid's midpoint to
# RERANK_THRESHOLD and steepening it (RERANK_STEEPNESS) recalibrates
# "near zero" to read as low confidence while still saturating to ~1
# for the strongly-positive relevant case - verified against
# src/eval_benchmark.py category 10 (safe abstention) after the fix.
RERANK_THRESHOLD = config.RERANK_THRESHOLD
RERANK_STEEPNESS = config.RERANK_STEEPNESS


def _sigmoid(x: float, midpoint: float = RERANK_THRESHOLD, steepness: float = RERANK_STEEPNESS) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-steepness * (x - midpoint)))
    except OverflowError:
        return 0.0 if x < midpoint else 1.0


def _rerank_score(results: list[dict]) -> float:
    if not results:
        return 0.0
    return _sigmoid(results[0].get("reranker_score", 0.0))


def _retrieval_density(results: list[dict]) -> float:
    if not results:
        return 0.0
    scores = [_sigmoid(r.get("reranker_score", 0.0)) for r in results]
    return sum(scores) / len(scores)


def _authority(results: list[dict]) -> float:
    if not results:
        return 0.0
    weights = [r.get("authority_weight") or config.DEFAULT_AUTHORITY_WEIGHT for r in results]
    return sum(weights) / len(weights)


def _significant_terms(query: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", (query or "").lower())
    return {w for w in words if len(w) >= 4 and w not in _STOPWORDS}


def _query_term_coverage(query: str, results: list[dict]) -> float:
    terms = _significant_terms(query)
    if not terms:
        return 1.0

    corpus = " ".join(r.get("text", "") or "" for r in results).lower()
    covered = sum(1 for term in terms if term in corpus)

    return covered / len(terms)


def score_retrieval_confidence(query: str, results: list[dict]) -> dict:
    """Compute the four sub-scores and the weighted retrieval confidence."""

    s_rerank = _rerank_score(results)
    s_density = _retrieval_density(results)
    s_authority = _authority(results)
    s_coverage = _query_term_coverage(query, results)

    confidence = (
        0.40 * s_rerank
        + 0.30 * s_density
        + 0.20 * s_authority
        + 0.10 * s_coverage
    )

    return {
        "s_rerank": s_rerank,
        "s_retrieval_density": s_density,
        "s_authority": s_authority,
        "s_query_term_coverage": s_coverage,
        "confidence": confidence,
    }


def _band(confidence: float) -> str:
    if confidence >= HIGH_THRESHOLD:
        return "high"
    if confidence >= MEDIUM_THRESHOLD:
        return "medium"
    return "low"


def evaluate_confidence(
    query: str,
    results: list[dict],
    citation_report: dict | None = None,
) -> dict:
    """
    Full confidence + abstention gate.

    Args:
        query: the user's question.
        results: the retrieved/reranked chunks used to answer it.
        citation_report: optional output of
            agents.citation_agent.verify_citations(answer, results) —
            when given, an unverified citation caps the band at
            "medium", and citation precision below 0.5 forces abstention.

    Returns:
        confidence (float), band ("high"|"medium"|"low"), abstain (bool),
        abstention_message (str | None), and the underlying sub-scores.
    """

    scores = score_retrieval_confidence(query, results)
    confidence = scores["confidence"]
    band = _band(confidence)

    if citation_report is not None:
        precision = citation_report.get("citation_precision", 1.0)

        if precision < 0.5:
            band = "low"
        elif citation_report.get("has_unverified_citations") and band == "high":
            band = "medium"

    abstain = band == "low"

    return {
        "confidence": confidence,
        "band": band,
        "abstain": abstain,
        "abstention_message": ABSTENTION_MESSAGE if abstain else None,
        "scores": scores,
    }
