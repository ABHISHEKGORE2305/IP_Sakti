import os
import time

from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:  # noqa: BLE001 - some interpreters lack a caller frame
    pass


GROQ_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_FALLBACK_MODELS = [
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
]

# Fallback models for Gemini
GEMINI_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_FALLBACK_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


class LLMError(RuntimeError):
    """Raised when the LLM call cannot be completed."""


def _is_rate_limit(message: str) -> bool:
    m = message.lower()
    return "429" in m or "rate limit" in m or "resource_exhausted" in m or "quota" in m


class GroqLLM:
    """Unified LLM client defaulting to Groq for ultra-fast, free inference,

    with fallback support.
    """

    def __init__(self, model: str | None = None):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not self.groq_api_key and not self.gemini_api_key:
            raise LLMError(
                "Neither GROQ_API_KEY nor GEMINI_API_KEY was found. "
                "Please add GROQ_API_KEY=gsk_... to your .env file."
            )

        self.provider = "groq" if self.groq_api_key else "gemini"

        if self.provider == "groq":
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
            except ImportError:
                raise LLMError("groq package not installed. Run: pip install groq")

            self.model = model or GROQ_DEFAULT_MODEL
            self._models = [self.model] + [
                m for m in GROQ_FALLBACK_MODELS if m != self.model
            ]
            print(f"Groq LLM initialized: {self.model}")

        else:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            except ImportError:
                raise LLMError("google-genai package not installed.")

            self.model = model or GEMINI_DEFAULT_MODEL
            self._models = [self.model] + [
                m for m in GEMINI_FALLBACK_MODELS if m != self.model
            ]
            print(f"Gemini LLM initialized (fallback): {self.model}")

    def _call_groq(self, model: str, prompt: str) -> str:
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional Ayurvedic & Indian Patent law research AI.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model=model,
            temperature=0.2,
            # The five-section answer format with a framework table and a
            # checklist runs long; without an explicit ceiling the provider
            # default truncated answers mid-sentence.
            max_tokens=4096,
        )
        text = chat_completion.choices[0].message.content
        if not text:
            raise LLMError("Groq returned an empty response.")
        return text.strip()

    def _call_gemini(self, model: str, prompt: str) -> str:
        response = self.gemini_client.models.generate_content(
            model=model,
            contents=prompt,
        )
        text = getattr(response, "text", None)
        if not text:
            raise LLMError("Gemini returned an empty response.")
        return text.strip()

    def generate(self, prompt: str, max_attempts: int = 3) -> str:
        last_error = None

        if self.provider == "groq":
            for model in self._models:
                for attempt in range(1, max_attempts + 1):
                    try:
                        return self._call_groq(model, prompt)
                    except Exception as exc:  # noqa: BLE001
                        message = str(exc)
                        last_error = exc

                        if _is_rate_limit(message) and attempt < max_attempts:
                            time.sleep(1.5 * attempt)
                            continue

                        print(f"[llm:groq] {model} issue ({message[:80]}); trying next model...")
                        break

            # If all Groq models failed and Gemini key is available, attempt
            # Gemini fallback - try every fallback model, not just the first,
            # since a single retired model name shouldn't abandon the fallback.
            if self.gemini_api_key:
                try:
                    from google import genai
                    client = genai.Client(api_key=self.gemini_api_key)
                except Exception as exc:  # noqa: BLE001
                    print(f"[llm:gemini fallback unavailable]: {exc}")
                else:
                    for gemini_model in GEMINI_FALLBACK_MODELS:
                        try:
                            print(f"[llm] Falling back to Gemini ({gemini_model})...")
                            resp = client.models.generate_content(
                                model=gemini_model,
                                contents=prompt,
                            )
                            text = getattr(resp, "text", None)
                            if text:
                                return text.strip()
                        except Exception as exc:  # noqa: BLE001
                            last_error = exc
                            print(f"[llm:gemini fallback] {gemini_model} failed: {str(exc)[:80]}")

        else:
            # Provider is Gemini
            for model in self._models:
                for attempt in range(1, max_attempts + 1):
                    try:
                        return self._call_gemini(model, prompt)
                    except Exception as exc:  # noqa: BLE001
                        message = str(exc)
                        last_error = exc

                        if attempt < max_attempts:
                            time.sleep(2 * attempt)
                            continue

                        print(f"[llm:gemini] {model} failing ({message[:80]}); trying next model")
                        break

        raise LLMError(
            f"All LLM models are unavailable or rate-limited. (Last error: {last_error})"
        )


# Backward compatibility aliases
GeminiLLM = GroqLLM
LLM = GroqLLM
