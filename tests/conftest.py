"""
Shared pytest setup.

The suite runs from the repository root so the relative paths used across
src/ (data/processed/..., benchmark_results/...) resolve exactly as they do
in the app; pyproject.toml puts src/ on sys.path.

Markers (registered in pyproject.toml):
    integration  needs Qdrant, the embedding/reranker models or data/ files
    llm          calls a real LLM provider
Both are deselected by default: `pytest` runs only the fast, hermetic tests.
"""

import os
import threading
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
os.chdir(REPO_ROOT)


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """Point src/db.py at a throwaway SQLite file for one test."""

    import db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.db")
    # Connections are cached per thread; a fresh threading.local drops them.
    monkeypatch.setattr(db, "_local", threading.local())
    db.init_db()
    return db


@pytest.fixture
def api_client(isolated_db, tmp_path, monkeypatch):
    """A TestClient on the real app, without loading any models.

    The lifespan (which loads the embedding model, reranker and LLM) only
    runs when TestClient is used as a context manager, so it is not used as
    one here: STATE["rag"] stays None and model-backed routes answer
    "not_ready", which is all the HTTP-layer tests need.
    """

    from fastapi.testclient import TestClient

    import api
    from server.routers import admin
    from server.security import ALL_LIMITERS

    monkeypatch.setattr(admin, "RAW_DIR", tmp_path / "raw")
    for limiter in ALL_LIMITERS:
        limiter.reset()
    yield TestClient(api.app)
    for limiter in ALL_LIMITERS:
        limiter.reset()
