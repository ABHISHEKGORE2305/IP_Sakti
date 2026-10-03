import math
import os
import time

from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:  # noqa: BLE001 - some interpreters lack a caller frame
    pass


# Default and fallback models for Groq. llama-3.3-70b-versatile,
# llama-3.1-8b-instant, mixtral-8x7b-32768 and gemma2-9b-it have all been
# decommissioned/removed from the Groq catalog (confirmed via GET
# https://api.groq.com/openai/v1/models against this project's key) and
# were 404/400-ing on every request. openai/gpt-oss-120b (and its smaller
# sibling) are the current text-generation models Groq actually serves.
GROQ_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
]

# Fallback models for Gemini (if Gemini is used as fallback). gemini-1.5-flash
# and gemini-2.0-flash-exp are retired for keys created after their
# retirement (404 NOT_FOUND) - confirmed via client.models.list().
GEMINI_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
]


class LLMError(RuntimeError):
    """Raised when the LLM call cannot be completed."""


# Groq free-tier tokens-per-minute limit per model. A request is rejected with
# 413 when input tokens + max_tokens exceed it, so every call is sized to fit.
# Override a model with GROQ_TPM_LIMITS="model=limit,model=limit". Models not
# listed use GROQ_DEFAULT_TPM_LIMIT.
GROQ_DEFAULT_TPM_LIMIT = int(os.getenv("GROQ_DEFAULT_TPM_LIMIT", "6000"))
GROQ_TPM_LIMITS = {
    "openai/gpt-oss-120b": 8000,
    "openai/gpt-oss-20b": 8000,
    "qwen/qwen3.8-27b": 7000,
}
for _pair in filter(None, os.getenv("GROQ_TPM_LIMITS", "").split(",")):
    _name, _, _value = _pair.partition("=")
    if _value.strip().isdigit():
        GROQ_TPM_LIMITS[_name.strip()] = int(_value)


def _output_budget(model: str, prompt: str, requested: int | None) -> int:
    """Max output tokens that keeps input + output under the model's limit.
    Raises LLMError when even the minimum output cannot fit (caller then moves
    to the next model instead of sending a request that would 413)."""
    import config

    limit = GROQ_TPM_LIMITS.get(model, GROQ_DEFAULT_TPM_LIMIT)
    est_input = math.ceil(len(prompt) / config.LLM_CHARS_PER_TOKEN) + 50  # + system msg
    room = limit - est_input - config.LLM_TOKEN_MARGIN
    wanted = requested if requested is not None else config.LLM_MAX_OUTPUT_TOKENS
    minimum = min(wanted, config.LLM_MIN_OUTPUT_TOKENS)
    if room < minimum:
        raise LLMError(
            f"prompt (~{est_input} tokens) too large for {model} budget "
            f"(limit {limit}, need >= {minimum} output tokens)"
        )
    return min(wanted, room)


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
                # A hung, slow or rate-limited model should fall through to the
                # next one rather than stall the request: fail after GROQ_TIMEOUT
                # seconds (default 20) and never wait/retry inside the SDK. Each
                # Groq model has its own tokens-per-minute bucket, so moving to
                # the next model is faster than waiting for this one to refill.
                self.groq_client = Groq(
                    api_key=self.groq_api_key,
                    timeout=float(os.getenv("GROQ_TIMEOUT", "20")),
                    max_retries=0,
                )
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

    def _call_groq(self, model: str, prompt: str, max_tokens: int | None = None) -> str:
        out_tokens = _output_budget(model, prompt, max_tokens)
        # Long answers only: a word hint leaves room for reasoning tokens that
        # also count against the cap. Short calls (e.g. query expansion) skip it.
        words = int((out_tokens - 300) * 0.7) if out_tokens >= 1000 else 0
        extra = {}
        # gpt-oss models reason before answering; "low"/"medium"/"high" trades
        # answer depth for latency (reasoning tokens count toward the output
        # cap). Default "low"; set GROQ_REASONING_EFFORT="" for provider default.
        effort = os.getenv("GROQ_REASONING_EFFORT", "low")
        if effort and model.startswith("openai/gpt-oss"):
            extra["reasoning_effort"] = effort

        chat_completion = self.groq_client.chat.completions.create(
            **extra,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional Ayurvedic & Indian Patent law research AI."
                        + (
                            f" Keep the complete answer under {words} words and "
                            "finish every section within that limit."
                            if words
                            else ""
                        )
                    ),
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
            max_tokens=out_tokens,
        )
        choice = chat_completion.choices[0]
        usage = getattr(chat_completion, "usage", None)
        if usage:
            print(
                f"[llm:groq] {model} in={usage.prompt_tokens} "
                f"out={usage.completion_tokens} cap={out_tokens}",
                flush=True,
            )
        if getattr(choice, "finish_reason", None) == "length":
            print(f"[llm:groq] {model} hit the {out_tokens}-token output cap", flush=True)
        text = choice.message.content
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

    def generate(
        self, prompt: str, max_attempts: int = 3, max_tokens: int | None = None
    ) -> str:
        start = time.perf_counter()
        try:
            return self._generate(prompt, max_attempts, max_tokens)
        finally:
            print(
                f"[timing] llm.generate {time.perf_counter() - start:.2f}s "
                f"prompt_chars={len(prompt)}",
                flush=True,
            )

    def _generate(
        self, prompt: str, max_attempts: int = 3, max_tokens: int | None = None
    ) -> str:
        last_error = None

        if self.provider == "groq":
            for model in self._models:
                for attempt in range(1, max_attempts + 1):
                    try:
                        return self._call_groq(model, prompt, max_tokens)
                    except Exception as exc:  # noqa: BLE001
                        message = str(exc)
                        last_error = exc

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
