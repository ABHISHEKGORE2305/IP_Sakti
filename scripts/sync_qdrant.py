"""
Sync data/processed/chunks.json -> Qdrant Cloud without re-chunking or
re-embedding. chunks.json already stores a "vector" per chunk, so this upserts
those vectors as-is, then makes sure the payload indexes the retrievers filter
on exist.

Dry-run by default (read-only). Nothing is written without --apply.

    python scripts/sync_qdrant.py                    # report what would change
    python scripts/sync_qdrant.py --apply            # upsert chunks.json + indexes
    python scripts/sync_qdrant.py --apply --prune    # ...and delete orphans
    python scripts/sync_qdrant.py --verify 5         # re-embed 5 chunks locally
                                                     # and compare to stored vectors

A point ID is uuid5(chunk_id), but a chunk_id can map to different text after a
re-chunk, so "missing" IDs are not the whole story: --apply upserts EVERY chunk
(overwriting same-ID points), and --prune then removes points whose ID is not in
chunks.json, so the collection ends up equal to chunks.json. Without --prune
stale orphans stay and dense search can return old-chunking text.

Uses QDRANT_URL / QDRANT_API_KEY from the environment or ./.env.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from qdrant_client import QdrantClient  # noqa: E402
from qdrant_client.models import PayloadSchemaType  # noqa: E402

import config  # noqa: E402
from vector_store import QdrantVectorStore  # noqa: E402

# Fields the retrievers filter on (src/retriever.py). The cluster runs strict
# mode with unindexed_filtering_retrieve=False, so a filter on an unindexed
# field raises instead of falling back to a scan.
INDEXED_FIELDS = {
    "document_id": PayloadSchemaType.KEYWORD,
    "jurisdiction": PayloadSchemaType.KEYWORD,
}


def existing_point_ids(client: QdrantClient) -> dict[str, object]:
    """str(id) -> original id. Legacy points have INTEGER ids, which must be
    passed back to Qdrant as ints when deleting."""
    ids: dict[str, object] = {}
    offset = None
    while True:
        points, offset = client.scroll(
            config.COLLECTION_NAME,
            limit=1000,
            offset=offset,
            with_payload=False,
            with_vectors=False,
        )
        ids.update({str(p.id): p.id for p in points})
        if offset is None:
            return ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write to Qdrant")
    ap.add_argument("--prune", action="store_true",
                    help="with --apply: delete points not present in chunks.json")
    ap.add_argument("--verify", type=int, metavar="N", default=0,
                    help="re-embed N random chunks locally and compare "
                         "(loads bge-m3; read-only)")
    ap.add_argument("--chunks", default=str(ROOT / config.CHUNKS_PATH))
    args = ap.parse_args()

    if not config.QDRANT_API_KEY or "localhost" in config.QDRANT_URL:
        print(f"Refusing: QDRANT_URL={config.QDRANT_URL!r} / key missing. "
              "Set the Qdrant Cloud values in .env.")
        return 1

    chunks = json.loads(Path(args.chunks).read_text(encoding="utf-8"))
    bad = [c.get("chunk_id") for c in chunks
           if not c.get("vector") or len(c["vector"]) != config.VECTOR_SIZE]
    if bad:
        print(f"ABORT: {len(bad)} chunks lack a {config.VECTOR_SIZE}-dim vector "
              f"(e.g. {bad[:3]}). Re-embed those first.")
        return 1
    if len({c["chunk_id"] for c in chunks}) != len(chunks):
        print("ABORT: duplicate chunk_id values in chunks.json.")
        return 1

    client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY,
                          timeout=60)
    if not client.collection_exists(config.COLLECTION_NAME):
        print(f"Collection {config.COLLECTION_NAME!r} missing; --apply will "
              "create it and upload everything.")
        have = {}
    else:
        have = existing_point_ids(client)

    gen = QdrantVectorStore.generate_point_id
    wanted = {gen(c["chunk_id"]): c for c in chunks}
    missing = [c for pid, c in wanted.items() if pid not in have]
    orphans = {k: v for k, v in have.items() if k not in wanted}

    print(f"chunks.json: {len(chunks)}   qdrant: {len(have)}")
    print(f"IDs missing in Qdrant: {len(missing)}   "
          f"orphan IDs (pruned only with --prune): {len(orphans)}")
    by_doc = collections.Counter(c["document_id"] for c in missing)
    for doc, n in by_doc.most_common():
        print(f"  + {n:5d}  {doc}")

    mb = sum(len(json.dumps(c)) for c in missing) / 1e6
    print(f"approx upload size: {mb:.1f} MB")

    # A chunk_id can map to different text after a re-chunk, so also count
    # same-ID points whose stored text is stale.
    changed_text = 0
    sample_ids = [pid for pid in wanted if pid in have]
    for i in range(0, len(sample_ids), 500):
        got = client.retrieve(config.COLLECTION_NAME, ids=sample_ids[i:i + 500],
                              with_payload=["text"])
        changed_text += sum(
            1 for p in got if p.payload.get("text") != wanted[str(p.id)]["text"])
    print(f"same-ID points whose text differs from chunks.json: {changed_text}")

    if args.verify:
        import random

        import numpy as np
        from embedding_model import EmbeddingModel

        model = EmbeddingModel()
        picks = random.sample(chunks, min(args.verify, len(chunks)))
        vecs = np.array(model.embed_documents([c["text"] for c in picks]))
        sims = [float(v @ np.array(c["vector"])) for v, c in zip(vecs, picks)]
        print(f"verify: cosine(local re-embed, stored vector) min={min(sims):.4f} "
              f"mean={sum(sims) / len(sims):.4f}  (expect >0.99)")
        if min(sims) < 0.99:
            print("ABORT: stored vectors do not match the current model.")
            return 1

    if not args.apply:
        print("\nDry run only. Re-run with --apply (and --prune) to write.")
        return 0

    # Upsert everything: same-ID points may hold stale text.
    # QdrantVectorStore reuses the exact payload shape used by ingest.py.
    store = QdrantVectorStore(url=config.QDRANT_URL)
    store.add_chunks(chunks, batch_size=64)

    if args.prune and orphans:
        ids = list(orphans.values())
        for i in range(0, len(ids), 500):
            client.delete(config.COLLECTION_NAME,
                          points_selector=ids[i:i + 500])
        print(f"pruned {len(ids)} orphan points")

    schema = client.get_collection(config.COLLECTION_NAME).payload_schema or {}
    for field, ftype in INDEXED_FIELDS.items():
        if field in schema:
            print(f"index ok: {field}")
        else:
            client.create_payload_index(config.COLLECTION_NAME, field, ftype)
            print(f"index created: {field}")

    final = client.count(config.COLLECTION_NAME, exact=True).count
    expected = len(chunks) if args.prune else len(chunks) + len(orphans)
    print(f"\nQdrant now has {final} points (expected {expected}).")
    return 0 if final == expected else 2


if __name__ == "__main__":
    sys.exit(main())
