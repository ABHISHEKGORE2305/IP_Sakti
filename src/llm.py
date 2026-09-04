import os
import time

from dotenv import load_dotenv
from google import genai


try:
    load_dotenv()
except Exception:  # noqa: BLE001 - some interpreters lack a caller frame
    pass


# Gemini's free tier meters requests *per model per day* (currently 20/day).
# When one model's daily bucket is exhausted you get 429 RESOURCE_EXHAUSTED;
# switching to another flash model gives a fresh bucket. `gemini-flash-latest`
# tracks the current production flash model. Override with GEMINI_MODEL, e.g.
#   GEMINI_MODEL=gemini-3.5-flash
# Note: `gemini-2.5-flash` returns 404 for keys created after its retirement.
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Fallback models tried, in order, when the primary hits a per-day quota wall.
FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
]


class LLMError(RuntimeError):
    """Raised when the LLM call cannot be completed."""


def _is_daily_quota(message: str) -> bool:
    m = message.lower()
    return "resource_exhausted" in m or "perday" in m or "per day" in m or "free_tier" in m


def _is_transient(message: str) -> bool:
    return any(t in message for t in ("503", "UNAVAILABLE", "500", "INTERNAL"))


class GeminiLLM:

    def __init__(self, model: str | None = None):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise LLMError(
                "GEMINI_API_KEY not found. Add it to medical-rag/.env"
            )

        self.model = model or DEFAULT_MODEL

        # Primary first, then any distinct fallbacks.
        self._models = [self.model] + [
            m for m in FALLBACK_MODELS if m != self.model
        ]

        self.client = genai.Client(api_key=api_key)

        print(f"Gemini LLM initialized: {self.model}")

    def _call(self, model: str, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
        )
        text = getattr(response, "text", None)
        if not text:
            raise LLMError("Gemini returned an empty response.")
        return text.strip()

    def generate(self, prompt: str, max_attempts: int = 3) -> str:

        last_error = None

        for model in self._models:

            for attempt in range(1, max_attempts + 1):
                try:
                    return self._call(model, prompt)
                except LLMError:
                    raise
                except Exception as exc:  # noqa: BLE001
                    message = str(exc)
                    last_error = exc

                    # Per-day quota or retired model: retrying is pointless.
                    if ("429" in message and _is_daily_quota(message)) or "404" in message:
                        print(f"[llm] {model} unusable ({message[:80]}); trying next model")
                        break

                    # Per-minute rate limit / transient server error: back off
                    # and retry this model a couple of times.
                    if attempt < max_attempts:
                        time.sleep(2 * attempt)
                        continue

                    # Still failing after retries -> fall through to next model.
                    print(f"[llm] {model} failing ({message[:80]}); trying next model")

        raise LLMError(
            "All Gemini models are unavailable or rate-limited "
            f"(last error: {last_error}). The free tier allows ~20 requests/day "
            "per model; wait for the daily reset, set GEMINI_MODEL to another "
            "model, or enable billing on the Google AI Studio project."
        )
