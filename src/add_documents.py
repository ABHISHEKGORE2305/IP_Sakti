"""
Add or re-ingest individual documents without rebuilding the whole corpus.

ingest.py rebuilds chunks.json and the Qdrant collection from every entry
in document_config.DOCUMENTS. That re-embeds ~3,000 chunks and reshuffles
every document's chunk boundaries whenever the chunker has changed since
the last full run. This script runs the same load -> chunk -> consolidate
-> embed steps for the named documents only, and replaces just their
chunks: in chunks.json (which BM25 and the exact-reference path read) and
in Qdrant (delete by document_id, then upsert).

Use it to add a newly registered document or to pick up a metadata change
(title, type, jurisdiction, page_range) on an existing one. Documents are
selected by document_id (the filename stem, unless the config sets one).

Run with:
    PYTHONPATH=src python src/add_documents.py --list
    PYTHONPATH=src python src/add_documents.py wto_trips_agreement_amended_2017 --dry-run
    PYTHONPATH=src python src/add_documents.py wto_trips_agreement_amended_2017 eu_directive_2004_24_ec_thmpd

This only touches the Qdrant at config.QDRANT_URL (local by default). Push
the result to a hosted collection with scripts/sync_qdrant.py.
"""

import argparse
import json
from pathlib import Path

import config
from chunker import consolidate_chunks, create_chunks
from document_config import DOCUMENTS
from document_loader import load_pdf

RAW_DIR = Path("data/raw")


def document_id(doc: dict) -> str:
    return doc.get("document_id") or Path(doc["filename"]).stem


def chunk_document(doc: dict) -> list[dict]:
    pages = load_pdf(str(RAW_DIR / doc["filename"]), metadata=doc)
    chunks = create_chunks(pages, chunk_size=1000, chunk_overlap=200)
    return consolidate_chunks(chunks)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("document_ids", nargs="*")
    parser.add_argument("--list", action="store_true", help="show configured documents and chunk counts")
    parser.add_argument("--dry-run", action="store_true", help="chunk and print, write nothing")
    parser.add_argument("--chunks", default=config.CHUNKS_PATH)
    args = parser.parse_args()

    chunks_path = Path(args.chunks)
    corpus = json.loads(chunks_path.read_text(encoding="utf-8"))

    if args.list or not args.document_ids:
        counts = {}
        for c in corpus:
            counts[c.get("document_id")] = counts.get(c.get("document_id"), 0) + 1
        for doc in DOCUMENTS:
            did = document_id(doc)
            exists = (RAW_DIR / doc["filename"]).exists()
            print(f"{counts.get(did, 0):>5}  {'   ' if exists else 'NO PDF'}  {did}")
        return

    by_id = {document_id(d): d for d in DOCUMENTS}
    unknown = [d for d in args.document_ids if d not in by_id]
    if unknown:
        raise SystemExit(f"Not in document_config.DOCUMENTS: {unknown} (see --list)")

    new_chunks = []
    for did in args.document_ids:
        chunks = chunk_document(by_id[did])
        labelled = sum(1 for c in chunks if c.get("legal_reference"))
        print(f"{did}: {len(chunks)} chunks, {labelled} with a provision label")
        for c in chunks[:: max(1, len(chunks) // 6)]:
            print(f"    p.{c['page']:<3} {str(c.get('legal_reference'))[:28]:<28} "
                  f"{' '.join(c['text'].split())[:90]}")
        new_chunks.extend(chunks)

    if args.dry_run:
        return

    from embedding_model import EmbeddingModel
    from vector_store import QdrantVectorStore

    vectors = EmbeddingModel().embed_documents([c["text"] for c in new_chunks])
    for chunk, vector in zip(new_chunks, vectors, strict=True):
        chunk["vector"] = vector

    replaced = set(args.document_ids)
    kept = [c for c in corpus if c.get("document_id") not in replaced]
    removed = len(corpus) - len(kept)

    store = QdrantVectorStore(
        url=config.QDRANT_URL,
        collection_name=config.COLLECTION_NAME,
        vector_size=config.VECTOR_SIZE,
    )
    for did in args.document_ids:
        store.delete_by_document_id(did)
    store.add_chunks(new_chunks)

    tmp = chunks_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(kept + new_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(chunks_path)
    print(f"\nchunks.json: removed {removed}, added {len(new_chunks)} -> {len(kept) + len(new_chunks)} total")


if __name__ == "__main__":
    main()
