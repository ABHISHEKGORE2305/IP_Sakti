from document_loader import load_pdf
from chunker import create_chunks
from embedding_model import EmbeddingModel


PDF_PATH = "/Users/aspa/Desktop/abhishek/sih_26_manual/medical-rag/data/raw/An_Overview_of_Ayurveda.pdf"


# -------------------------------
# 1. Load PDF
# -------------------------------

pages = load_pdf(PDF_PATH)

print(
    f"Loaded {len(pages)} pages"
)


# -------------------------------
# 2. Create chunks
# -------------------------------

chunks = create_chunks(
    pages,
    chunk_size=1000,
    chunk_overlap=200,
)

print(
    f"Created {len(chunks)} chunks"
)


# -------------------------------
# 3. Load embedding model
# -------------------------------

embedding_model = EmbeddingModel()


# -------------------------------
# 4. Extract chunk text
# -------------------------------

texts = [
    chunk["text"]
    for chunk in chunks
]


# -------------------------------
# 5. Generate embeddings
# -------------------------------

vectors = embedding_model.embed_documents(
    texts
)


# -------------------------------
# 6. Attach vectors to chunks
# -------------------------------

for chunk, vector in zip(
    chunks,
    vectors
):

    chunk["vector"] = vector


# -------------------------------
# 7. Display result
# -------------------------------

print("\nFirst chunk:")

print(
    chunks[0]["text"][:500]
)

print(
    "\nVector dimensions:",
    len(chunks[0]["vector"])
)

print(
    "\nFirst 10 vector values:"
)

print(
    chunks[0]["vector"][:10]
)