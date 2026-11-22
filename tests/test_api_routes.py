"""
HTTP contract tests for the routers, with no models loaded: input
validation, the "not ready" path, and the request-id / Server-Timing
headers added by the logging middleware.
"""

import json
import logging

import pytest

import server.state as state
from server.state import normalize_jurisdiction


def test_health_reports_starting_before_models_load(api_client):
    body = api_client.get("/health").json()
    assert body["status"] == "starting"
    assert body["service"] == "ayurvedic-ip-rag"


def test_health_reports_degraded_with_reason(api_client, monkeypatch):
    monkeypatch.setitem(state.STATE, "error", "Qdrant unreachable")
    body = api_client.get("/health").json()
    assert body == {**body, "status": "degraded", "detail": "Qdrant unreachable"}


@pytest.mark.parametrize("path, payload, error", [
    ("/ask", {"query": "   "}, "empty_query"),
    ("/api/chat/", {"message": ""}, "empty_query"),
    ("/ask", {"query": "What is Section 3(p)?"}, "not_ready"),
    ("/api/chat/", {"query": "What is Section 3(p)?"}, "not_ready"),
    ("/api/agent", {"query": ""}, "empty_query"),
    ("/api/agent", {"query": "Is turmeric paste patentable?"}, "not_ready"),
])
def test_query_routes_validate_and_report_not_ready(api_client, path, payload, error):
    response = api_client.post(path, json=payload)
    assert response.status_code == 200
    assert response.json()["error"] == error


def test_engine_routes_work_without_models(api_client):
    plan = api_client.post("/api/ip-route-plan", json={"ip_regimes": {"patent": "n", "trademark": "n"}, "tk_risk": "barred"})
    assert {p["regime"]: p["outlook"] for p in plan.json()["plan"]}["patent"] == "barred"

    graph = api_client.post("/api/knowledge-graph", json={"jurisdiction": "India"})
    assert {n["kind"] for n in graph.json()["nodes"]} == {"Product", "Jurisdiction"}


def test_translate_rejects_unsupported_language(api_client):
    body = api_client.post("/api/translate", json={"text": "hello", "target_language": "xx"}).json()
    assert body["error"] == "unsupported_language"


def test_privacy_routes_are_session_scoped(api_client):
    alice, bob = {"X-Session-Id": "alice"}, {"X-Session-Id": "bob"}
    api_client.post("/api/consent", json={"consent_type": "premium_db", "granted": True}, headers=alice)

    assert api_client.get("/api/consent", headers=alice).json()["consent"]
    assert not api_client.get("/api/consent", headers=bob).json()["consent"]

    api_client.post("/api/privacy/delete", headers=bob)
    assert api_client.get("/api/consent", headers=alice).json()["consent"]


# ----------------------------------------------------------------------
# Request ids, timing headers, access log
# ----------------------------------------------------------------------


def test_every_response_carries_a_request_id_and_server_timing(api_client):
    response = api_client.get("/health")
    assert len(response.headers["X-Request-Id"]) == 32
    assert response.headers["Server-Timing"].startswith("total;dur=")


def test_client_request_id_is_echoed_when_safe(api_client):
    assert api_client.get("/health", headers={"X-Request-Id": "trace-abc.123"}).headers["X-Request-Id"] == "trace-abc.123"


@pytest.mark.parametrize("unsafe", ["has space", "x" * 65, 'inject"}\n{"level":"ERROR'])
def test_unsafe_client_request_id_is_replaced(api_client, unsafe):
    assert api_client.get("/health", headers={"X-Request-Id": unsafe}).headers["X-Request-Id"] != unsafe


def test_access_log_line_is_structured(api_client, caplog):
    with caplog.at_level(logging.INFO, logger="access"):
        response = api_client.post("/ask", json={"query": "x"}, headers={"X-Request-Id": "req-42"})

    record = next(r for r in caplog.records if r.name == "access")
    assert record.request_id == "req-42"
    assert (record.method, record.path, record.status) == ("POST", "/ask", response.status_code)
    assert record.duration_ms >= 0
    # The record must serialise as one JSON object.
    from observability import JsonFormatter
    line = json.loads(JsonFormatter().format(record))
    assert line["request_id"] == "req-42" and line["path"] == "/ask"


# ----------------------------------------------------------------------
# Jurisdiction normalisation (shared by /ask and /api/chat/)
# ----------------------------------------------------------------------


@pytest.mark.parametrize("label, expected", [
    ("India", "India"),
    ("International", "International"),
    ("Global / WIPO", "International"),
    ("Both", None),
    ("India (National & International Multi-Step)", None),
    ("Atlantis", None),
    ("", None),
    (None, None),
])
def test_normalize_jurisdiction(label, expected):
    assert normalize_jurisdiction(label) == expected
