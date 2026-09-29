"""
Bhashini (Govt of India's free ASR/MT/TTS API — bhashini.gov.in) client.

winning_features.md item 13 asks for real Bhashini integration rather
than the Gemini-based translation substitute currently in prompt.py/
api.py. Same env-var-gated pattern as llm.py's GEMINI_API_KEY and
escalation.py's SMTP config: build it now, wire real credentials in
later — is_configured() gates every call, and every caller falls back
to the existing Gemini/Web-Speech-API path when this returns False.

    BHASHINI_USER_ID
    BHASHINI_API_KEY              (ULCA "inference API key" a.k.a. udyat key)
    BHASHINI_PIPELINE_ID           (optional — default public pipeline id)

IMPORTANT — API shape not live-verified: Bhashini's public contract is
the ULCA (Universal Language Contribution API) two-step "pipeline"
pattern:
    1. POST getModelsPipeline (discovery) -> returns a pipelineInferenceAPIEndPoint
       {callbackUrl, inferenceApiKey} plus the model/service ids for each task.
    2. POST that callbackUrl with task-specific input -> the actual
       translation/ASR/TTS output.
This module is written against that documented shape (meity-auth.ulcacontrib.org
+ dhruva inference endpoints), but has never been exercised against a real
key in this environment. # VERIFY the exact request/response field names
against https://bhashini.gitbook.io/bhashini-apis (or whatever the
current official docs are) once real credentials are available, the same
way web_sources.py's URLs were flagged unverified until live-checked.
"""

import os

import requests
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:  # noqa: BLE001
    pass


PIPELINE_DISCOVERY_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
REQUEST_TIMEOUT = 20

# ULCA task-type ids — # VERIFY these match current Bhashini pipeline
# task-type naming (translation/asr/tts have been renamed before).
TASK_TRANSLATION = "translation"
TASK_ASR = "asr"
TASK_TTS = "tts"


class BhashiniError(RuntimeError):
    """Raised when a Bhashini call cannot be completed (missing config,
    network failure, or an unexpected response shape)."""


def is_configured() -> bool:
    return bool(os.getenv("BHASHINI_USER_ID") and os.getenv("BHASHINI_API_KEY"))


def _discover_pipeline(task_type: str, source_lang: str, target_lang: str | None = None) -> dict:
    """
    Step 1 of the ULCA pattern — ask Bhashini which model/service to use
    for this task+language pair, and get back the actual inference
    endpoint + its own API key. # VERIFY payload shape.
    """

    user_id = os.getenv("BHASHINI_USER_ID")
    api_key = os.getenv("BHASHINI_API_KEY")
    pipeline_id = os.getenv("BHASHINI_PIPELINE_ID", "64392f96daac500b55c543cd")  # VERIFY — public default pipeline id

    task_config: dict = {"taskType": task_type}
    if task_type == TASK_TRANSLATION:
        task_config["config"] = {"language": {"sourceLanguage": source_lang, "targetLanguage": target_lang}}
    else:
        task_config["config"] = {"language": {"sourceLanguage": source_lang}}

    try:
        response = requests.post(
            PIPELINE_DISCOVERY_URL,
            headers={
                "userID": user_id,
                "ulcaApiKey": api_key,
                "Content-Type": "application/json",
            },
            json={"pipelineTasks": [task_config], "pipelineRequestConfig": {"pipelineId": pipeline_id}},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise BhashiniError(f"Bhashini pipeline discovery failed: {exc}") from exc


def translate(text: str, source_lang: str, target_lang: str) -> str:
    """Translate `text` from source_lang to target_lang (ISO-639 codes,
    e.g. 'en', 'hi', 'mr') via Bhashini's NMT pipeline."""

    if not is_configured():
        raise BhashiniError("Bhashini is not configured (BHASHINI_USER_ID/BHASHINI_API_KEY unset).")

    pipeline = _discover_pipeline(TASK_TRANSLATION, source_lang, target_lang)

    try:
        endpoint = pipeline["pipelineInferenceAPIEndPoint"]
        callback_url = endpoint["callbackUrl"]
        inference_key = endpoint["inferenceApiKey"]["value"]
        service_id = pipeline["pipelineResponseConfig"][0]["config"][0]["serviceId"]
    except (KeyError, IndexError) as exc:
        raise BhashiniError(f"Unexpected Bhashini pipeline-discovery response shape: {exc}") from exc

    try:
        response = requests.post(
            callback_url,
            headers={inference_key.split(":", 1)[0] if ":" in inference_key else "Authorization": inference_key},
            json={
                "pipelineTasks": [{
                    "taskType": TASK_TRANSLATION,
                    "config": {
                        "language": {"sourceLanguage": source_lang, "targetLanguage": target_lang},
                        "serviceId": service_id,
                    },
                }],
                "inputData": {"input": [{"source": text}]},
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data["pipelineResponse"][0]["output"][0]["target"]
    except (requests.RequestException, KeyError, IndexError) as exc:
        raise BhashiniError(f"Bhashini translation inference failed: {exc}") from exc


def text_to_speech(text: str, lang: str) -> bytes:
    """Synthesize `text` (in `lang`) to audio via Bhashini's TTS pipeline.
    Returns raw audio bytes (base64-decoded from the API's response —
    # VERIFY the exact encoding field name/format)."""

    if not is_configured():
        raise BhashiniError("Bhashini is not configured (BHASHINI_USER_ID/BHASHINI_API_KEY unset).")

    import base64

    pipeline = _discover_pipeline(TASK_TTS, lang)

    try:
        endpoint = pipeline["pipelineInferenceAPIEndPoint"]
        callback_url = endpoint["callbackUrl"]
        inference_key = endpoint["inferenceApiKey"]["value"]
        service_id = pipeline["pipelineResponseConfig"][0]["config"][0]["serviceId"]
    except (KeyError, IndexError) as exc:
        raise BhashiniError(f"Unexpected Bhashini pipeline-discovery response shape: {exc}") from exc

    try:
        response = requests.post(
            callback_url,
            headers={"Authorization": inference_key},
            json={
                "pipelineTasks": [{
                    "taskType": TASK_TTS,
                    "config": {"language": {"sourceLanguage": lang}, "serviceId": service_id},
                }],
                "inputData": {"input": [{"source": text}]},
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        audio_b64 = data["pipelineResponse"][0]["audio"][0]["audioContent"]
        return base64.b64decode(audio_b64)
    except (requests.RequestException, KeyError, IndexError) as exc:
        raise BhashiniError(f"Bhashini TTS inference failed: {exc}") from exc


def speech_to_text(audio_bytes: bytes, lang: str) -> str:
    """Transcribe `audio_bytes` (in `lang`) via Bhashini's ASR pipeline."""

    if not is_configured():
        raise BhashiniError("Bhashini is not configured (BHASHINI_USER_ID/BHASHINI_API_KEY unset).")

    import base64

    pipeline = _discover_pipeline(TASK_ASR, lang)

    try:
        endpoint = pipeline["pipelineInferenceAPIEndPoint"]
        callback_url = endpoint["callbackUrl"]
        inference_key = endpoint["inferenceApiKey"]["value"]
        service_id = pipeline["pipelineResponseConfig"][0]["config"][0]["serviceId"]
    except (KeyError, IndexError) as exc:
        raise BhashiniError(f"Unexpected Bhashini pipeline-discovery response shape: {exc}") from exc

    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

    try:
        response = requests.post(
            callback_url,
            headers={"Authorization": inference_key},
            json={
                "pipelineTasks": [{
                    "taskType": TASK_ASR,
                    "config": {"language": {"sourceLanguage": lang}, "serviceId": service_id},
                }],
                "inputData": {"audio": [{"audioContent": audio_b64}]},
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data["pipelineResponse"][0]["output"][0]["source"]
    except (requests.RequestException, KeyError, IndexError) as exc:
        raise BhashiniError(f"Bhashini ASR inference failed: {exc}") from exc
