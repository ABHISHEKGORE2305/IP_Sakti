"""
Prompt-injection detection — deterministic phrase/pattern matching, not an
LLM judge. Consistent with the rest of this pipeline's guardrail
philosophy: agents/supervisor.py's routing is deliberately keyword-based
rather than an LLM call so it stays "auditable and free" (see its own
module comment) — this filter follows the same reasoning: a regex list is
inspectable, testable, and costs nothing per request, where an LLM-judge
would add latency, cost, and its own hallucination surface to a safety
gate.

This is necessarily incomplete — determined adversarial phrasing can
evade any fixed pattern list — but it raises the bar past the previous
4-phrase check and catches the common jailbreak/exfiltration templates.
"""

import re

# Each pattern is matched case-insensitively against the (already
# PII-redacted) query text. Grouped by what they're trying to do, purely
# for readability — detect_prompt_injection() doesn't care which group
# matched, only that one did.
_PATTERNS = [
    # Instruction override
    r"\bignore (all )?(the )?(previous|prior|above) instructions?\b",
    r"\bdisregard (the )?(system prompt|your instructions)\b",
    r"\bforget (everything|all) (you (were|have been) told|above)\b",
    r"\boverride (your|the) (instructions|system prompt|rules)\b",
    r"\bnew instructions?:\s",

    # Role-play / jailbreak framing
    r"\byou are now\b.{0,40}\b(dan|jailbroken|unrestricted|unfiltered)\b",
    r"\bpretend (that )?you (have no|don't have any) (restrictions|rules|guardrails)\b",
    r"\bact as (an?|the) (unrestricted|unfiltered|uncensored)\b",
    r"\bdeveloper mode\b",
    r"\bno (ethical|moral|legal) (restrictions|guidelines|guardrails)\b",

    # System-prompt exfiltration
    r"\brepeat (your|the) (system prompt|instructions) (verbatim|exactly)?\b",
    r"\bwhat (are|were) your (original )?instructions\b",
    r"\bprint (your|the) (system prompt|configuration)\b",

    # Fake delimiter / role injection (trying to smuggle a new "system"
    # turn inside user text)
    r"```\s*system\b",
    r"\[system\]",
    r"<\|?system\|?>",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PATTERNS]


def detect_prompt_injection(text: str) -> str | None:
    """
    Returns the matched pattern (for logging/audit) if `text` looks like a
    prompt-injection attempt, else None. Callers should block/flag the
    request rather than passing it to the LLM.
    """

    if not text:
        return None

    for pattern in _COMPILED:
        match = pattern.search(text)
        if match:
            return match.group(0)

    return None
