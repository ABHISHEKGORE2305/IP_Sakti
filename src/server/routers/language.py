"""Translation and Bhashini speech (TTS/STT)."""

import base64
import logging

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

import bhashini_client
from llm import LLMError
from prompt import TRANSLATION_PROMPT
from server.security import llm_rate_limit
from server.state import get_rag

logger = logging.getLogger(__name__)

router = APIRouter(tags=["language"])

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "pa": "Punjabi",
}


class TranslateRequest(BaseModel):
    text: str
    target_language: str    # ISO code, see LANGUAGE_NAMES


class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str
    provider: str | None = None   # "bhashini" | "gemini" — which backend actually served this
    error: str | None = None


class TTSRequest(BaseModel):
    text: str
    lang: str    # ISO code, see LANGUAGE_NAMES


@router.post("/api/translate", response_model=TranslateResponse, dependencies=[Depends(llm_rate_limit)])
def api_translate(request: TranslateRequest) -> TranslateResponse:
    """
    Translate `text` into one of the Sprint 5 Indian languages, keeping
    bracketed statutory citations in English (see prompt.TRANSLATION_PROMPT).

    Tries Bhashini first (winning_features.md item 13) when configured —
    the real free Indian-language MT API. Falls back to the Gemini-based
    substitute on missing config or any Bhashini failure, so this never
    breaks even before real credentials are added (see
    bhashini_client.py's module docstring for the "build now, wire later"
    pattern, same as escalation.py's SMTP config).

    NOTE: bhashini_client.py preserves statutory citations in English
    less reliably than the Gemini path's explicit TRANSLATION_PROMPT
    instruction (a generic MT API has no citation-preservation concept)
    — worth a manual spot-check once real Bhashini credentials land.
    """

    text = (request.text or "").strip()
    language_name = LANGUAGE_NAMES.get(request.target_language)

    if not language_name:
        return TranslateResponse(
            translated_text=request.text,
            target_language=request.target_language,
            error="unsupported_language",
        )

    if language_name == "English" or not text:
        return TranslateResponse(translated_text=request.text, target_language=request.target_language)

    if bhashini_client.is_configured():
        try:
            translated = bhashini_client.translate(text, source_lang="en", target_lang=request.target_language)
            return TranslateResponse(
                translated_text=translated, target_language=request.target_language, provider="bhashini",
            )
        except bhashini_client.BhashiniError as exc:
            logger.warning("Bhashini translation failed, falling back to Gemini: %s", exc)

    rag = get_rag()
    if rag is None:
        return TranslateResponse(
            translated_text=request.text,
            target_language=request.target_language,
            error="not_ready",
        )

    prompt = TRANSLATION_PROMPT.format(language=language_name, text=text)

    try:
        translated = rag.llm.generate(prompt)
    except LLMError as exc:
        return TranslateResponse(
            translated_text=request.text,
            target_language=request.target_language,
            error=str(exc),
        )

    return TranslateResponse(translated_text=translated, target_language=request.target_language, provider="gemini")


@router.get("/api/bhashini/status")
def api_bhashini_status() -> dict:
    return {"configured": bhashini_client.is_configured()}


@router.post("/api/tts", dependencies=[Depends(llm_rate_limit)])
def api_tts(request: TTSRequest) -> dict:
    """
    Bhashini text-to-speech (winning_features.md item 13's voice-first
    mode). Only available when Bhashini is configured — the frontend's
    existing browser Web Speech API TTS ("Listen" button in
    StepAction.jsx) remains the fallback/default; this is additive, not
    a replacement, since Web Speech works with zero backend config.
    """

    if not bhashini_client.is_configured():
        return {"available": False, "audio_base64": None, "error": "not_configured"}

    try:
        audio_bytes = bhashini_client.text_to_speech(request.text, request.lang)
        return {"available": True, "audio_base64": base64.b64encode(audio_bytes).decode("ascii"), "error": None}
    except bhashini_client.BhashiniError as exc:
        return {"available": True, "audio_base64": None, "error": str(exc)}


@router.post("/api/stt", dependencies=[Depends(llm_rate_limit)])
async def api_stt(audio: UploadFile = File(...), lang: str = "hi") -> dict:  # noqa: B008 - FastAPI idiom
    """Bhashini speech-to-text — same additive relationship to the
    frontend's existing Web Speech API STT as /api/tts above."""

    if not bhashini_client.is_configured():
        return {"available": False, "text": None, "error": "not_configured"}

    try:
        audio_bytes = await audio.read()
        text = bhashini_client.speech_to_text(audio_bytes, lang)
        return {"available": True, "text": text, "error": None}
    except bhashini_client.BhashiniError as exc:
        return {"available": True, "text": None, "error": str(exc)}
