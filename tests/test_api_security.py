"""
Security tests for the HTTP layer: admin authentication, the corpus upload's
filename/size/content checks, and per-client rate limiting.

The upload route used to take the client's filename verbatim and write it
under data/raw/ with no authentication, so "../../src/x.pdf" wrote outside
the corpus directory and any existing statute PDF could be overwritten.
"""

import pytest

import config
from server.security import RateLimiter, llm_rate_limit, safe_upload_filename

ADMIN_KEY = "test-admin-key"
PDF_BYTES = b"%PDF-1.7\n%test document\n"


@pytest.fixture
def admin_enabled(monkeypatch):
    monkeypatch.setattr(config, "ADMIN_API_KEY", ADMIN_KEY)


def _upload(client, filename, content=PDF_BYTES, key=ADMIN_KEY):
    headers = {"X-Admin-Key": key} if key is not None else {}
    return client.post(
        "/api/admin/corpus/upload",
        files={"file": (filename, content, "application/pdf")},
        headers=headers,
    )


# ----------------------------------------------------------------------
# Authentication
# ----------------------------------------------------------------------


def test_admin_routes_fail_closed_without_configured_key(api_client, monkeypatch):
    monkeypatch.setattr(config, "ADMIN_API_KEY", None)
    assert api_client.get("/api/admin/corpus").status_code == 503
    assert _upload(api_client, "doc.pdf").status_code == 503


@pytest.mark.usefixtures("admin_enabled")
@pytest.mark.parametrize("key", [None, "", "wrong-key", ADMIN_KEY + "x"])
def test_admin_routes_reject_missing_or_wrong_key(api_client, key):
    headers = {"X-Admin-Key": key} if key is not None else {}
    assert api_client.get("/api/admin/corpus", headers=headers).status_code == 401
    assert _upload(api_client, "doc.pdf", key=key).status_code == 401


@pytest.mark.usefixtures("admin_enabled")
def test_admin_corpus_listing_with_valid_key(api_client):
    response = api_client.get("/api/admin/corpus", headers={"X-Admin-Key": ADMIN_KEY})
    assert response.status_code == 200
    assert isinstance(response.json()["documents"], list)


# ----------------------------------------------------------------------
# Upload validation
# ----------------------------------------------------------------------


@pytest.mark.usefixtures("admin_enabled")
def test_valid_upload_is_saved_inside_raw_dir(api_client, tmp_path):
    response = _upload(api_client, "New Guidance 2026.pdf")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "pending_reindex"
    assert (tmp_path / "raw" / "New Guidance 2026.pdf").read_bytes() == PDF_BYTES


@pytest.mark.usefixtures("admin_enabled")
@pytest.mark.parametrize("filename", [
    "../../src/evil.pdf",
    "..\\..\\src\\evil.pdf",
    "/etc/cron.d/evil.pdf",
])
def test_path_traversal_is_neutralised(api_client, tmp_path, filename):
    response = _upload(api_client, filename)
    # Either rejected outright or reduced to a bare name inside raw/ —
    # never written anywhere else.
    assert response.status_code in (200, 400)
    written = [p for p in tmp_path.rglob("*.pdf")]
    assert all(p.parent == tmp_path / "raw" for p in written), written


@pytest.mark.usefixtures("admin_enabled")
@pytest.mark.parametrize("filename", ["notes.txt", "evil.pdf.exe", ".hidden.pdf", "a\x00b.pdf", "x" * 200 + ".pdf"])
def test_bad_filenames_are_rejected(api_client, filename):
    assert _upload(api_client, filename).status_code == 400


@pytest.mark.usefixtures("admin_enabled")
def test_non_pdf_content_is_rejected(api_client):
    assert _upload(api_client, "fake.pdf", content=b"MZ\x90\x00 not a pdf").status_code == 415


@pytest.mark.usefixtures("admin_enabled")
def test_oversized_upload_is_rejected(api_client, monkeypatch, tmp_path):
    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 1024)
    response = _upload(api_client, "big.pdf", content=PDF_BYTES + b"0" * 2048)
    assert response.status_code == 413
    assert not (tmp_path / "raw" / "big.pdf").exists()


@pytest.mark.usefixtures("admin_enabled")
def test_existing_corpus_file_is_never_overwritten(api_client, tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "patents_act_1970.pdf").write_bytes(b"%PDF- original statute")

    response = _upload(api_client, "patents_act_1970.pdf", content=b"%PDF- replacement")

    assert response.status_code == 409
    assert (raw / "patents_act_1970.pdf").read_bytes() == b"%PDF- original statute"


@pytest.mark.parametrize("raw, expected", [
    ("report.pdf", "report.pdf"),
    ("dir/sub/report.PDF", "report.PDF"),
    ("..\\..\\report.pdf", "report.pdf"),
    ("../../../etc/passwd", None),
    ("", None),
    (None, None),
    ("..pdf", None),
])
def test_safe_upload_filename(raw, expected):
    assert safe_upload_filename(raw) == expected


# ----------------------------------------------------------------------
# Rate limiting
# ----------------------------------------------------------------------


def test_llm_routes_are_rate_limited_per_client(api_client, monkeypatch):
    monkeypatch.setattr(llm_rate_limit, "limit", 3)
    statuses = [api_client.post("/ask", json={"query": "What is Section 3(p)?"}).status_code for _ in range(4)]
    assert statuses == [200, 200, 200, 429]

    blocked = api_client.post("/api/chat/", json={"query": "x"})
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) >= 1


def test_rate_limit_failures_happen_before_admin_key_check(api_client, monkeypatch, admin_enabled):
    from server.security import admin_rate_limit

    monkeypatch.setattr(admin_rate_limit, "limit", 2)
    statuses = [api_client.get("/api/admin/corpus", headers={"X-Admin-Key": "guess"}).status_code for _ in range(3)]
    # Key guessing is throttled like any other admin request.
    assert statuses == [401, 401, 429]


def test_rate_limiter_window_expires(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr("server.security.time.monotonic", lambda: clock[0])

    class _Req:
        class client:
            host = "203.0.113.7"

    limiter = RateLimiter("t", limit=2, window_s=60)
    limiter(_Req)
    limiter(_Req)
    with pytest.raises(Exception) as exc:
        limiter(_Req)
    assert exc.value.status_code == 429

    clock[0] += 61
    limiter(_Req)   # window has rolled over


def test_zero_limit_disables_rate_limiting():
    class _Req:
        class client:
            host = "203.0.113.8"

    limiter = RateLimiter("off", limit=0, window_s=60)
    for _ in range(100):
        limiter(_Req)
