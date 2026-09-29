"""
Minimal, no-login persistence layer — foundation for the audit log,
consent/privacy dashboard, and corpus admin panel (winning_features.md
items 15/16/17/20). stdlib sqlite3 only, no new dependency.

Callers identify themselves with a client-generated `session_id` (a UUID
the frontend stores in localStorage and sends as an `X-Session-Id`
header — see api.py's `_session_id` dependency). There is no login/auth;
this is a demo-grade session-scoped store, not a production multi-tenant
database. DPDP-relevant: every read is session-scoped, never global, and
`delete_session_data` gives a real "delete my data" primitive.
"""

import json
import sqlite3
import threading
import time
from pathlib import Path

import config

DB_PATH = Path(config.DB_PATH)

_local = threading.local()


def _connect() -> sqlite3.Connection:
    if not hasattr(_local, "conn"):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        _local.conn = conn
    return _local.conn


def init_db() -> None:
    conn = _connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp REAL NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_audit_log_session ON audit_log(session_id);

        CREATE TABLE IF NOT EXISTS consent (
            session_id TEXT NOT NULL,
            consent_type TEXT NOT NULL,
            granted INTEGER NOT NULL,
            timestamp REAL NOT NULL,
            PRIMARY KEY (session_id, consent_type)
        );

        CREATE TABLE IF NOT EXISTS corpus_documents (
            document_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            document_type TEXT,
            jurisdiction TEXT,
            status TEXT NOT NULL,
            uploaded_at REAL NOT NULL
        );
        """
    )
    conn.commit()


# ------------------------------------------------------------------
# Audit log
# ------------------------------------------------------------------

def log_event(session_id: str, event_type: str, payload: dict) -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO audit_log (session_id, timestamp, event_type, payload_json) VALUES (?, ?, ?, ?)",
        (session_id, time.time(), event_type, json.dumps(payload, ensure_ascii=False, default=str)),
    )
    conn.commit()


def get_audit_log(session_id: str, limit: int = 200) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT timestamp, event_type, payload_json FROM audit_log "
        "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit),
    ).fetchall()
    return [
        {"timestamp": r["timestamp"], "event_type": r["event_type"], "payload": json.loads(r["payload_json"])}
        for r in rows
    ]


# ------------------------------------------------------------------
# Consent
# ------------------------------------------------------------------

def set_consent(session_id: str, consent_type: str, granted: bool) -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO consent (session_id, consent_type, granted, timestamp) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(session_id, consent_type) DO UPDATE SET granted = excluded.granted, timestamp = excluded.timestamp",
        (session_id, consent_type, int(granted), time.time()),
    )
    conn.commit()
    log_event(session_id, "consent_change", {"consent_type": consent_type, "granted": granted})


def get_consent(session_id: str) -> dict[str, bool]:
    conn = _connect()
    rows = conn.execute(
        "SELECT consent_type, granted FROM consent WHERE session_id = ?",
        (session_id,),
    ).fetchall()
    return {r["consent_type"]: bool(r["granted"]) for r in rows}


# ------------------------------------------------------------------
# Privacy — "delete my data"
# ------------------------------------------------------------------

def delete_session_data(session_id: str) -> dict:
    conn = _connect()
    audit_deleted = conn.execute("DELETE FROM audit_log WHERE session_id = ?", (session_id,)).rowcount
    consent_deleted = conn.execute("DELETE FROM consent WHERE session_id = ?", (session_id,)).rowcount
    conn.commit()
    return {"audit_log_rows_deleted": audit_deleted, "consent_rows_deleted": consent_deleted}


def privacy_summary(session_id: str) -> dict:
    conn = _connect()
    audit_count = conn.execute(
        "SELECT COUNT(*) AS n FROM audit_log WHERE session_id = ?", (session_id,)
    ).fetchone()["n"]
    consent_rows = get_consent(session_id)
    return {"audit_log_entries": audit_count, "consent": consent_rows}


# ------------------------------------------------------------------
# Corpus admin (winning_features.md item 20)
# ------------------------------------------------------------------

def record_corpus_document(document_id: str, filename: str, document_type: str | None, jurisdiction: str | None, status: str = "pending_reindex") -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO corpus_documents (document_id, filename, document_type, jurisdiction, status, uploaded_at) "
        "VALUES (?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(document_id) DO UPDATE SET status = excluded.status, uploaded_at = excluded.uploaded_at",
        (document_id, filename, document_type, jurisdiction, status, time.time()),
    )
    conn.commit()


def list_corpus_documents() -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT document_id, filename, document_type, jurisdiction, status, uploaded_at "
        "FROM corpus_documents ORDER BY uploaded_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def mark_document_status(document_id: str, status: str) -> None:
    conn = _connect()
    conn.execute("UPDATE corpus_documents SET status = ? WHERE document_id = ?", (status, document_id))
    conn.commit()


init_db()
