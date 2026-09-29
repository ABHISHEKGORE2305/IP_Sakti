"""
Periodic web-corpus ingestion — fetches every entry in
src/web_sources.WEB_SOURCES, chunks/embeds/upserts only the ones whose
content actually changed since the last run, and writes the result to
data/processed/chunks_web.json (kept separate from the PDF pipeline's
chunks.json — this script never touches that file or DOCUMENTS).

Run manually or via an OS-level cron entry, e.g. weekly:

    PYTHONPATH=src python3 src/ingest_web.py

    # crontab -e:
    0 6 * * 1 cd /path/to/IP_Sakti && PYTHONPATH=src venv/bin/python3 src/ingest_web.py >> logs/ingest_web.log 2>&1

This is intentionally a standalone script, not a scheduler inside the
FastAPI process — see implementation_plan.md's "Live Web-Sourced Corpus"
section. After it finishes, the API process must be restarted for the
new/changed content to become searchable (AyurvedicHybridRetriever loads
chunks.json/chunks_web.json once, at startup — no hot-reload).
"""

import hashlib
import json
from datetime import date
from pathlib import Path

from chunker import create_chunks
from embedding_model import EmbeddingModel
from vector_store import QdrantVectorStore
from web_loader import WebFetchError, load_url
from web_sources import WEB_SOURCES
import config


PROCESSED_DIR = Path("data/processed")
WEB_CHUNKS_PATH = Path(config.WEB_CHUNKS_PATH)
MANIFEST_PATH = Path(config.WEB_SOURCES_MANIFEST_PATH)


def _content_hash(pages: list[dict]) -> str:
    combined = "\n".join(p["text"] for p in pages)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def _load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_json(path: Path, data) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def main() -> None:
    print("\n" + "=" * 80)
    print("WEB CORPUS INGESTION")
    print("=" * 80)

    manifest = _load_json(MANIFEST_PATH, {})
    web_chunks = _load_json(WEB_CHUNKS_PATH, [])

    vector_store = QdrantVectorStore(
        url=config.QDRANT_URL,
        collection_name=config.COLLECTION_NAME,
        vector_size=config.VECTOR_SIZE,
    )

    # Loaded lazily — skip paying the embedding-model load cost entirely
    # if every source turns out unchanged.
    embedding_model = None

    fetched_count = 0
    unchanged_count = 0
    failed_count = 0

    for source in WEB_SOURCES:
        source_id = source["source_id"]
        print("\n" + "-" * 60)
        print(f"Source: {source['document']} ({source_id})")

        try:
            pages = load_url(source)
        except WebFetchError as exc:
            print(f"FAILED: {exc}")
            failed_count += 1
            continue

        content_hash = _content_hash(pages)
        previous = manifest.get(source_id)

        if previous and previous.get("content_hash") == content_hash:
            print("Unchanged since last fetch — skipping re-embed.")
            unchanged_count += 1
            continue

        chunks = create_chunks(pages)
        if not chunks:
            print("WARNING: no chunks produced from this fetch — skipping.")
            failed_count += 1
            continue

        print(f"Chunks: {len(chunks)}")

        if embedding_model is None:
            embedding_model = EmbeddingModel()

        texts = [c["text"] for c in chunks]
        vectors = embedding_model.embed_documents(texts)

        fetched_at = date.today().isoformat()
        for chunk, vector in zip(chunks, vectors):
            chunk["vector"] = vector
            chunk["fetched_at"] = fetched_at

        # Replace this source's points/chunks wholesale — if the page now
        # chunks differently than last time, this avoids leaving orphaned
        # stale points/chunks behind under old chunk_ids.
        vector_store.delete_by_document_id(source_id)
        vector_store.add_chunks(chunks)

        web_chunks = [c for c in web_chunks if c.get("document_id") != source_id]
        web_chunks.extend(chunks)

        manifest[source_id] = {
            "content_hash": content_hash,
            "fetched_at": fetched_at,
            "chunk_ids": [c["chunk_id"] for c in chunks],
        }

        fetched_count += 1

    _save_json(WEB_CHUNKS_PATH, web_chunks)
    _save_json(MANIFEST_PATH, manifest)

    print("\n" + "=" * 80)
    print("WEB CORPUS INGESTION COMPLETE")
    print("=" * 80)
    print(f"Sources configured: {len(WEB_SOURCES)}")
    print(f"Fetched/updated: {fetched_count}")
    print(f"Unchanged: {unchanged_count}")
    print(f"Failed: {failed_count}")
    print(f"Total web chunks: {len(web_chunks)}")
    print(f"Saved to: {WEB_CHUNKS_PATH}")
    if fetched_count:
        print(
            "\nNOTE: restart the API process for the updated content to "
            "become searchable — chunks_web.json is only loaded at startup."
        )
    print("=" * 80)


if __name__ == "__main__":
    main()
