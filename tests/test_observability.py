"""Structured logging and per-stage timing (src/observability.py)."""

import json
import logging
import threading

from observability import JsonFormatter, request_context, request_id_var, stage


def _record(msg="hello", **extra):
    record = logging.LogRecord("t", logging.INFO, __file__, 1, msg, None, None)
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_emits_one_object_with_extras():
    line = JsonFormatter().format(_record(request_id="r1", stage="rerank", duration_ms=12.5))
    payload = json.loads(line)
    assert payload["msg"] == "hello"
    assert payload["request_id"] == "r1"
    assert payload["stage"] == "rerank" and payload["duration_ms"] == 12.5
    assert "\n" not in line


def test_json_formatter_includes_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        import sys
        record = logging.LogRecord("t", logging.ERROR, __file__, 1, "failed", None, sys.exc_info())
    assert "ValueError: boom" in json.loads(JsonFormatter().format(record))["exc"]


def test_stages_accumulate_into_the_request_totals():
    with request_context("req-1") as timings:
        assert request_id_var.get() == "req-1"
        with stage("llm_generate"):
            pass
        with stage("llm_generate"):
            pass
        with stage("rerank"):
            pass
    assert set(timings) == {"llm_generate", "rerank"}
    assert request_id_var.get() is None


def test_stage_is_recorded_even_when_the_body_raises():
    with request_context("req-2") as timings:
        try:
            with stage("retrieval"):
                raise RuntimeError("qdrant down")
        except RuntimeError:
            pass
    assert "retrieval" in timings


def test_stage_outside_a_request_does_not_fail():
    with stage("offline_job"):
        pass


def test_worker_thread_with_copied_context_reports_back():
    # FastAPI runs sync endpoints in a thread with a copy of the request
    # context; stages timed there must still reach the request's totals.
    import contextvars

    with request_context("req-3") as timings:
        ctx = contextvars.copy_context()

        def work():
            with stage("hybrid_retrieval"):
                pass

        t = threading.Thread(target=ctx.run, args=(work,))
        t.start()
        t.join()
    assert "hybrid_retrieval" in timings
