from document_loader import load_pdf
from chunker import create_chunks
from embedding_model import EmbeddingModel
from vector_store import QdrantVectorStore
import json


# --------------------------------
# Configuration
# --------------------------------

PDF_PATH = (
    "data/raw/An_Overview_of_Ayurveda.pdf"

)


# --------------------------------
# Step 1: Load PDF
# --------------------------------

print("\n[1/4] Loading PDF...")

pages = load_pdf(
    PDF_PATH
)

print(
    f"Loaded {len(pages)} pages"
)


# --------------------------------
# Step 2: Create chunks
# --------------------------------

print("\n[2/4] Creating chunks...")

chunks = create_chunks(
    pages,

    chunk_size=1000,

    chunk_overlap=200,
)

print(
    f"Created {len(chunks)} chunks"
)


# --------------------------------
# Step 3: Generate embeddings
# --------------------------------

print("\n[3/4] Generating embeddings...")

embedding_model = EmbeddingModel()


texts = [
    chunk["text"]
    for chunk in chunks
]


vectors = embedding_model.embed_documents(
    texts
)


# Attach vectors to chunks

for chunk, vector in zip(
    chunks,
    vectors
):

    chunk["vector"] = vector


print(
    "Embeddings generated"
)

# --------------------------------
# Save chunks for BM25
# --------------------------------
bm25_chunks = []

for chunk in chunks:

    bm25_chunks.append({

        "chunk_id":
            chunk["chunk_id"],

        "text":
            chunk["text"],

        "source":
            chunk["source"],

        "page":
            chunk["page"],

        "document_id":
            chunk["document_id"],
    })

with open(
    "data/processed/chunks.json",
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        chunks,
        file,
        ensure_ascii=False,
        indent=2,
    )


print(
    "Saved chunks to "
    "data/processed/chunks.json"
)

# --------------------------------
# Step 4: Upload to Qdrant
# --------------------------------

print("\n[4/4] Uploading to Qdrant...")

vector_store = QdrantVectorStore(
    url="http://localhost:6333",

    collection_name="medical_documents",

    vector_size=1024,
)


vector_store.add_chunks(
    chunks
)


print("\nINGESTION COMPLETE!")