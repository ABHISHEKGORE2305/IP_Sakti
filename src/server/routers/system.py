"""Service health, the evaluation dashboard data, and official-portal references."""

import json
from pathlib import Path

from fastapi import APIRouter

import config
from references import REFERENCE_CATEGORIES
from server.state import STATE

SERVICE_NAME = "ayurvedic-ip-rag"
SERVICE_VERSION = "1.0"

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict:
    if STATE.get("error"):
        status = "degraded"
    elif STATE.get("rag") is None:
        status = "starting"
    else:
        status = "ok"

    return {
        "status": status,
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "detail": STATE.get("error"),
    }


@router.get("/api/eval-results")
def api_eval_results() -> dict:
    """
    Evaluation dashboard (winning_features.md item 19). Reads the JSON
    written by `PYTHONPATH=src python3 src/eval_benchmark.py --out-json
    data/processed/eval_results.json`. Clear "not yet run" state if that
    file doesn't exist, rather than a 404/500 the frontend has to
    special-case.
    """

    path = Path(config.EVAL_RESULTS_PATH)
    if not path.exists():
        return {"available": False}

    return {"available": True, **json.loads(path.read_text(encoding="utf-8"))}


@router.get("/api/references")
def api_references() -> dict:
    """Deep links to free official portals (IP India, WIPO, GI Registry,
    TKDL, AYUSH, FSSAI, NBA, ...). Paid/subscription databases are out of
    scope here — item 16 of left_to_do.md requires explicit per-use
    permission and access logging for those, which is a separate,
    deliberately-not-built feature."""

    return {"categories": REFERENCE_CATEGORIES}
