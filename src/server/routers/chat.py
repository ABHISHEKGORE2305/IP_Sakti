"""Plain RAG question answering: /ask and the chat tab's /api/chat/."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from server.security import llm_rate_limit
from server.state import citations_from_retrieved, get_rag, normalize_jurisdiction, not_ready_message

router = APIRouter(tags=["chat"], dependencies=[Depends(llm_rate_limit)])


class AskRequest(BaseModel):
    query: str
    top_k: int | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list
    retrieved: list
    error: str | None = None


class ChatMessage(BaseModel):
    role: str    # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    # The frontend has historically sent a few different field names /
    # extra fields; accept them all and ignore what we do not use.
    query: str | None = None
    message: str | None = None
    session_id: str | None = None
    jurisdiction: str | None = None
    jurisdiction_filter: str | None = None
    extract_metadata: bool | None = None
    top_k: int | None = None
    # Prior turns of the chat tab's conversation (oldest first), used only
    # as follow-up context for the prompt — see prompt.history_block_text.
    history: list[ChatMessage] | None = None


def _run_query(
    query: str,
    top_k: int | None,
    history: list | None = None,
    jurisdiction: str | None = None,
) -> dict | None:
    """Shared guard + dispatch. Returns None when the backend is not ready."""

    rag = get_rag()
    if rag is None:
        return None
    history_dicts = [h.model_dump() for h in history] if history else None
    return rag.answer(
        query,
        top_k=top_k,
        history=history_dicts,
        jurisdiction_filter=normalize_jurisdiction(jurisdiction),
    )


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:

    query = (request.query or "").strip()

    if not query:
        return AskResponse(
            answer="Please provide a non-empty 'query'.",
            sources=[],
            retrieved=[],
            error="empty_query",
        )

    result = _run_query(query, request.top_k)
    if result is None:
        return AskResponse(answer=not_ready_message(), sources=[], retrieved=[], error="not_ready")

    return AskResponse(
        answer=result["answer"],
        sources=result["sources"],
        retrieved=result["retrieved"],
        error=result.get("error"),
    )


@router.post("/api/chat/")
def api_chat(request: ChatRequest) -> dict:

    query = (request.query or request.message or "").strip()

    if not query:
        return {
            "answer": "Please provide a non-empty question.",
            "citations": [],
            "retrieved": [],
            "sources": [],
            "error": "empty_query",
        }

    result = _run_query(
        query,
        request.top_k,
        history=request.history,
        jurisdiction=request.jurisdiction or request.jurisdiction_filter,
    )
    if result is None:
        return {
            "answer": not_ready_message(),
            "citations": [],
            "retrieved": [],
            "sources": [],
            "error": "not_ready",
        }

    return {
        "answer": result["answer"],
        "citations": citations_from_retrieved(result["retrieved"]),
        "retrieved": result["retrieved"],
        "sources": result["sources"],
        "error": result.get("error"),
    }
