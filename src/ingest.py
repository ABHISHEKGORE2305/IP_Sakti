from pathlib import Path
import json

from document_loader import load_pdf
from chunker import create_chunks, consolidate_chunks
from embedding_model import EmbeddingModel
from vector_store import QdrantVectorStore
from document_config import DOCUMENTS
import config


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

COLLECTION_NAME = config.COLLECTION_NAME


print("\n" + "=" * 80)
print("MULTI-DOCUMENT RAG INGESTION")
print("=" * 80)


# --------------------------------------------------
# 1. Load all documents
# --------------------------------------------------

all_chunks = []

print("\n[1/4] Loading documents...")

for document_config in DOCUMENTS:

    pdf_path = RAW_DIR / document_config["filename"]

    print("\n" + "-" * 60)
    print(f"Document: {document_config['document']}")
    print(f"File: {pdf_path}")

    if not pdf_path.exists():
        print(f"WARNING: File not found: {pdf_path}")
        continue

    pages = load_pdf(
        str(pdf_path),
        metadata=document_config,
    )

    print(f"Pages loaded: {len(pages)}")


    # --------------------------------------------------
    # 2. Create chunks
    # --------------------------------------------------

    chunks = create_chunks(
        pages,
        chunk_size=1000,
        chunk_overlap=200,
    )

    consolidated = consolidate_chunks(chunks)

    print(
        f"Chunks created: {len(chunks)} -> "
        f"{len(consolidated)} after section consolidation"
    )

    all_chunks.extend(consolidated)


print("\n" + "=" * 80)
print(f"TOTAL CHUNKS: {len(all_chunks)}")
print("=" * 80)


# --------------------------------------------------
# 3. Generate embeddings
# --------------------------------------------------

print("\n[2/4] Generating embeddings...")

embedding_model = EmbeddingModel()

texts = [
    chunk["text"]
    for chunk in all_chunks
]

vectors = embedding_model.embed_documents(
    texts
)

for chunk, vector in zip(
    all_chunks,
    vectors,
):
    chunk["vector"] = vector

print("Embeddings generated successfully!")


# --------------------------------------------------
# 4. Save processed chunks
# --------------------------------------------------

print("\n[3/4] Saving processed chunks...")

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

chunks_path = (
    PROCESSED_DIR / "chunks.json"
)

with open(
    chunks_path,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        all_chunks,
        file,
        ensure_ascii=False,
        indent=2,
    )

print(f"Saved to: {chunks_path}")


# --------------------------------------------------
# 5. Upload to Qdrant
# --------------------------------------------------

print("\n[4/4] Uploading to Qdrant...")

vector_store = QdrantVectorStore(
    url=config.QDRANT_URL,
    collection_name=COLLECTION_NAME,
    vector_size=config.VECTOR_SIZE,
)

vector_store.add_chunks(
    all_chunks
)


print("\n" + "=" * 80)
print("MULTI-DOCUMENT INGESTION COMPLETE!")
print("=" * 80)

print(f"Documents configured: {len(DOCUMENTS)}")
print(f"Chunks indexed: {len(all_chunks)}")
print(f"Qdrant collection: {COLLECTION_NAME}")
print("=" * 80)