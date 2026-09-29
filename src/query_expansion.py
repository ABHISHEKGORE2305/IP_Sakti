"""
Retrieval-time query expansion.

Users ask practical questions ("Can I patent my Chyawanprash extract?");
statutes are written in a different register ("an invention which, in effect,
is traditional knowledge or which is an aggregation or duplication of known
properties..."). Measured against bge-reranker-v2-m3, that register gap alone
drops the score of the *correct* provision from ~0.99 (statute-worded query)
to ~0.0005 (user-worded query) — so the right section loses to verbose
guidance prose and never reaches the LLM.

Expanding the query with the statutory vocabulary it implies closes that gap.
The expansion is used for retrieval and reranking ONLY; the user's original
wording is what gets answered, and the generation prompt never sees this text.
"""

from llm import GroqLLM, LLMError

EXPANSION_PROMPT = """\
Rewrite this user question as a retrieval query for a corpus of Indian IP and
AYUSH regulatory law (Patents Act 1970, Patents Rules, Drugs & Cosmetics Act
1940/Rules 1945, Biological Diversity Act & Rules, Trade Marks Act, PPV&FR
Act, FSSAI regulations, TKDL and WIPO/treaty material).

Output the original question followed by the statutory vocabulary and concepts
a lawyer would search for to answer it — provision names, the legal tests
involved, and the terms of art the statute itself uses. Name specific sections
or rules only when you are confident they are the governing ones.

Do not answer the question. Output at most 90 words, as plain prose with no
headings, no markdown and no preamble.

User question: {query}

Retrieval query:"""

MAX_QUERY_CHARS = 4000


class QueryExpander:
    """Expands a query into statutory vocabulary, falling back to the raw
    query whenever expansion is unavailable — retrieval must never break
    because the expansion model is down or rate-limited."""

    def __init__(self, llm: GroqLLM | None = None):
        self._llm = llm
        self._cache: dict[str, str] = {}

    def _get_llm(self) -> GroqLLM | None:
        if self._llm is None:
            try:
                self._llm = GroqLLM()
            except LLMError:
                return None
        return self._llm

    def expand(self, query: str) -> str:
        query = (query or "").strip()
        if not query:
            return query

        if query in self._cache:
            return self._cache[query]

        llm = self._get_llm()
        if llm is None:
            return query

        try:
            expansion = llm.generate(
                EXPANSION_PROMPT.format(query=query), max_attempts=1
            ).strip()
        except (LLMError, Exception):  # noqa: BLE001 - never fail retrieval
            return query

        # A model that ignored the instruction and answered at length is worse
        # than no expansion at all: it would steer retrieval toward its own
        # (ungrounded) answer rather than the user's question.
        if not expansion or len(expansion) > MAX_QUERY_CHARS:
            return query

        expanded = f"{query}\n{expansion}"
        self._cache[query] = expanded
        return expanded
