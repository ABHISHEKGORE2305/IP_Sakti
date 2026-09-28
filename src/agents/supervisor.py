"""
Supervisor Agent — intent analysis & sub-agent selection.

Deterministic keyword-based router (no LLM call). Kept rule-based so
routing is auditable, free, and instant — the specialist agents are
where LLM calls (and their cost/latency) actually happen.
"""

import re


_ROUTES = [
    ("abs_agent", re.compile(
        r"\bbiological (diversity|resource)s?\b|\bnbA\b|\baccess and benefit sharing\b|"
        r"\babs\b|\bbenefit[- ]sharing\b|\bform (i|ii|iii|iv)\b|"
        r"\bstate biodiversity board\b|\bsbb\b",
        re.IGNORECASE,
    )),
    ("reg_agent", re.compile(
        r"\bfssai\b|\bcdsco\b|\bayush\b|\blicen[cs]e\b|\bmanufactur|"
        r"\bayurveda[- ]aahar\b|\bdrugs and cosmetics\b|\bclinical trial\b|"
        r"\badvertisement\b|\bmagic remed",
        re.IGNORECASE,
    )),
    ("tm_gi_agent", re.compile(
        r"\btrademark\b|\bbrand name\b|\bgeographical indication\b|\bgi\b|\bnice class",
        re.IGNORECASE,
    )),
    ("intl_agent", re.compile(
        r"\bwipo\b|\bpct\b|\bmadrid\b|\bhague system\b|\bus fda\b|\beu thmpd\b|"
        r"\bthmpd\b|\bexport market\b|\binternational\b|\bnagoya\b|\bgratk\b|"
        r"\bmhra\b|\bdshea\b|\bbotanical drug\b|\balice[/ ]mayo\b|\buspto\b|"
        r"\btrips\b|\b35 u\.?s\.?c\.?\s*10?1\b",
        re.IGNORECASE,
    )),
    ("classifier_agent", re.compile(
        r"\bclassif|\bwhat (type|category) of product\b|\bis this a drug or\b",
        re.IGNORECASE,
    )),
    ("patent_agent", re.compile(
        r"\bpatent\b|\bsection 3\b|\btraditional knowledge\b|\btkdl\b|"
        r"\binventive step\b|\bnovelty\b|\bsynergis|\badmixture\b|\bprior art\b",
        re.IGNORECASE,
    )),
]

DEFAULT_AGENT = "patent_agent"


def route(query: str) -> dict:
    """
    Decide which specialist agent(s) should handle `query`.

    Every matching route is returned (a query can span domains, e.g.
    "can I patent this and what licence do I need"); the first match
    is what the graph actually dispatches to (see agents.graph), the
    rest are reported for transparency/future multi-agent fan-out. If
    nothing matches, falls back to the Patent Agent — patentability /
    Section 3(p) analysis is this platform's primary use case.
    """

    matched = [name for name, pattern in _ROUTES if pattern.search(query or "")]

    if not matched:
        return {
            "selected_agents": [DEFAULT_AGENT],
            "routing_reason": "No domain keywords matched; defaulted to patent_agent.",
            "is_default": True,
        }

    return {
        "selected_agents": matched,
        "routing_reason": f"Matched domain keyword(s) for: {', '.join(matched)}.",
        "is_default": False,
    }
