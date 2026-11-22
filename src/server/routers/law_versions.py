"""Law Version Timeline: known versions per law family, and version-scoped questions."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from law_versions import find_version, get_law_families
from server.security import llm_rate_limit
from server.state import citations_from_retrieved, get_rag

router = APIRouter(tags=["law-versions"])


class LawVersionQueryRequest(BaseModel):
    query: str
    document_id: str


@router.get("/api/law-versions")
def api_law_versions() -> dict:
    """
    Law Version Timeline (winning_features.md item 9) — known versions
    per law family, from law_versions.py. Not a text diff (see that
    module's docstring for why); use POST /api/law-version-query to ask
    the same question scoped to one specific version.
    """

    return {"families": get_law_families()}


@router.post("/api/law-version-query", dependencies=[Depends(llm_rate_limit)])
def api_law_version_query(request: LawVersionQueryRequest) -> dict:
    """
    Runs `query` with retrieval scoped to exactly `document_id` (via
    rag_pipeline.AyurvedicIPRAG.answer's document_id_filter ->
    retriever.combined_query_filter) — retrieval-enforced, not just a
    prompt instruction to "answer as if under law X". Call this once per
    version in a family and compare the answers side by side.
    """

    version = find_version(request.document_id)
    if version is None:
        return {"answer": "", "sources": [], "error": "unknown_document_id"}

    rag = get_rag()
    if rag is None:
        return {"answer": "", "sources": [], "error": "not_ready"}

    result = rag.answer(request.query, document_id_filter=request.document_id)
    return {
        "answer": result.get("answer", ""),
        "sources": citations_from_retrieved(result.get("retrieved", [])),
        "version": version,
        "error": result.get("error"),
    }
