"""
Corpus admin panel (winning_features.md item 20).

Every route here needs a valid X-Admin-Key (server/security.py). The
rate limit runs before the key check so the key cannot be brute-forced.
"""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

import config
import db
from server.security import PDF_MAGIC, admin_rate_limit, require_admin, safe_upload_filename

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(admin_rate_limit), Depends(require_admin)],
)

RAW_DIR = Path("data/raw")
_READ_CHUNK = 1024 * 1024


def _chunk_counts(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    chunks = json.loads(p.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for c in chunks:
        doc_id = c.get("document_id")
        if doc_id:
            counts[doc_id] = counts.get(doc_id, 0) + 1
    return counts


@router.get("/corpus")
def api_admin_corpus() -> dict:
    """Lists every known document — the static PDF corpus
    (document_config.DOCUMENTS), the periodic web corpus
    (web_sources.WEB_SOURCES), and anything uploaded via
    POST /api/admin/corpus/upload — with chunk counts from the actual
    ingested chunks.json/chunks_web.json where available."""

    from document_config import DOCUMENTS
    from web_sources import WEB_SOURCES

    pdf_counts = _chunk_counts(config.CHUNKS_PATH)
    web_counts = _chunk_counts(config.WEB_CHUNKS_PATH)

    documents = []
    for d in DOCUMENTS:
        doc_id = d["filename"].rsplit(".", 1)[0]
        documents.append({
            "document_id": doc_id,
            "filename": d["filename"],
            "document": d.get("document"),
            "document_type": d.get("document_type"),
            "jurisdiction": d.get("jurisdiction"),
            "source": "pdf",
            "chunk_count": pdf_counts.get(doc_id, 0),
            "status": "indexed" if doc_id in pdf_counts else "not_ingested",
        })
    for s in WEB_SOURCES:
        documents.append({
            "document_id": s["source_id"],
            "filename": s["url"],
            "document": s.get("document"),
            "document_type": s.get("document_type"),
            "jurisdiction": s.get("jurisdiction"),
            "source": "web",
            "chunk_count": web_counts.get(s["source_id"], 0),
            "status": "indexed" if s["source_id"] in web_counts else "not_ingested",
        })
    for u in db.list_corpus_documents():
        documents.append({
            "document_id": u["document_id"],
            "filename": u["filename"],
            "document": u["filename"],
            "document_type": u.get("document_type"),
            "jurisdiction": u.get("jurisdiction"),
            "source": "uploaded",
            "chunk_count": pdf_counts.get(u["document_id"], 0),
            "status": u["status"],
        })

    return {"documents": documents}


async def _read_capped(file: UploadFile, limit: int) -> bytes:
    """Read at most `limit` bytes, failing as soon as the upload exceeds it
    (the client's Content-Length is not trusted)."""

    data = bytearray()
    while chunk := await file.read(_READ_CHUNK):
        data.extend(chunk)
        if len(data) > limit:
            raise HTTPException(status_code=413, detail=f"file_too_large: limit is {limit // (1024 * 1024)} MB")
    return bytes(data)


@router.post("/corpus/upload")
async def api_admin_corpus_upload(file: UploadFile = File(...)) -> dict:  # noqa: B008 - FastAPI idiom
    """
    Saves an uploaded PDF to data/raw/ and registers it as
    status="pending_reindex" — deliberately does NOT synchronously
    re-embed inside the request (the same reasoning as ingest_web.py
    being a standalone script rather than an in-process job: embedding
    is slow enough that a request handler is the wrong place for it).
    The admin panel shows the pending status and the operator runs
    `PYTHONPATH=src python3 src/ingest.py` (after adding the file to
    document_config.DOCUMENTS) to actually index it.

    The filename is reduced to a safe bare name, so a client cannot write
    outside data/raw/ ("../../src/x.pdf"), and an existing file is never
    overwritten — the statutes already in the corpus cannot be replaced
    through this route.
    """

    filename = safe_upload_filename(file.filename)
    if filename is None:
        raise HTTPException(status_code=400, detail="invalid_filename: expected a plain name ending in .pdf")

    contents = await _read_capped(file, config.MAX_UPLOAD_BYTES)
    if not contents.startswith(PDF_MAGIC):
        raise HTTPException(status_code=415, detail="not_a_pdf: file content is not a PDF")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / filename
    # safe_upload_filename already guarantees this; checked again so a future
    # change to it cannot silently reopen the traversal.
    if dest.resolve().parent != RAW_DIR.resolve():
        raise HTTPException(status_code=400, detail="invalid_filename")

    try:
        with dest.open("xb") as fh:    # "x": fail rather than overwrite
            fh.write(contents)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=f"already_exists: {filename} is already in the corpus") from exc

    document_id = dest.stem
    db.record_corpus_document(document_id, filename, document_type=None, jurisdiction=None, status="pending_reindex")

    return {
        "saved": True,
        "document_id": document_id,
        "status": "pending_reindex",
        "next_step": (
            f"Add {{'filename': '{filename}', 'document': ..., 'document_type': ..., "
            f"'jurisdiction': ...}} to document_config.DOCUMENTS, then run "
            "`PYTHONPATH=src python3 src/ingest.py` to index it."
        ),
    }
