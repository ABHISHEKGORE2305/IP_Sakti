from document_loader import load_pdf
from chunker import create_chunks
from embedding_model import EmbeddingModel
from vector_store import QdrantVectorStore


# --------------------------------
# Configuration
# --------------------------------

PDF_PATH = (
    "data/raw/An_Overview_of_Ayurveda.pdf"
)

COLLECTION_NAME = "medical_documents"


DOCUMENT_METADATA = {
    "document": "An Overview of Ayurveda",
    "document_type": "ayurvedic_reference",
    "jurisdiction": "India",
    "language": "en",
}


# --------------------------------
# Step 1: Load PDF
# --------------------------------

print("\n==============================")
print("STEP 1: LOADING PDF")
print("==============================")

pages = load_pdf(
    PDF_PATH,
    metadata=DOCUMENT_METADATA,
)

print(
    f"Pages loaded: {len(pages)}"
)


# --------------------------------
# Step 2: Create chunks
# --------------------------------

print("\n==============================")
print("STEP 2: CREATING CHUNKS")
print("==============================")

chunks = create_chunks(
    pages,
    chunk_size=1000,
    chunk_overlap=200,
)

print(
    f"Chunks created: {len(chunks)}"
)


# --------------------------------
# Step 3: Load embedding model
# --------------------------------

print("\n==============================")
print("STEP 3: LOADING EMBEDDING MODEL")
print("==============================")

embedding_model = EmbeddingModel()

print(
    "Embedding model loaded successfully"
)


# --------------------------------
# Step 4: Generate test embedding
# --------------------------------

print("\n==============================")
print("STEP 4: TESTING EMBEDDING")
print("==============================")

test_text = chunks[0]["text"]

test_vector = embedding_model.embed_text(
    test_text
)

print(
    f"Vector dimension: {len(test_vector)}"
)

print(
    f"First 5 values: {test_vector[:5]}"
)


# --------------------------------
# Verify vector dimension
# --------------------------------

if len(test_vector) != 1024:

    raise ValueError(
        f"Expected 1024 dimensions, "
        f"got {len(test_vector)}"
    )

print(
    "✓ Vector dimension is correct: 1024"
)


# --------------------------------
# Step 5: Connect to Qdrant
# --------------------------------

print("\n==============================")
print("STEP 5: TESTING QDRANT")
print("==============================")

vector_store = QdrantVectorStore(
    url="http://localhost:6333",
    collection_name=COLLECTION_NAME,
    vector_size=1024,
)

print(
    "✓ Connected to Qdrant"
)


# --------------------------------
# Step 6: Create test point
# --------------------------------

print("\n==============================")
print("STEP 6: TESTING QDRANT INSERT")
print("==============================")


test_chunk = chunks[0].copy()

test_chunk["vector"] = test_vector


# --------------------------------
# Use a temporary test chunk ID
# --------------------------------

test_chunk["chunk_id"] = (
    "TEST_An_Overview_of_Ayurveda_000001"
)


# Generate the exact UUID that
# QdrantVectorStore will use
test_point_id = (
    vector_store.generate_point_id(
        test_chunk["chunk_id"]
    )
)


print(
    f"Test chunk ID: "
    f"{test_chunk['chunk_id']}"
)

print(
    f"Qdrant point ID: "
    f"{test_point_id}"
)


# --------------------------------
# Upload test point
# --------------------------------

vector_store.add_chunks(
    [test_chunk]
)


print(
    "✓ Test vector uploaded successfully"
)


# --------------------------------
# Step 7: Verify point exists
# --------------------------------

print("\n==============================")
print("STEP 7: VERIFYING QDRANT DATA")
print("==============================")


results = vector_store.client.retrieve(
    collection_name=COLLECTION_NAME,
    ids=[test_point_id],
    with_payload=True,
)


if not results:

    raise ValueError(
        "Test point was not found in Qdrant"
    )


point = results[0]


print(
    "✓ Test point found"
)


# --------------------------------
# Verify vector exists
# --------------------------------

if point.vector is not None:

    print(
        "✓ Vector exists in Qdrant"
    )

else:

    raise ValueError(
        "Vector was not found in Qdrant"
    )


# --------------------------------
# Display stored payload
# --------------------------------

print("\nStored payload:")

for key, value in point.payload.items():

    if key == "text":

        print(
            f"{key}: "
            f"{value[:200]}..."
        )

    else:

        print(
            f"{key}: {value}"
        )


# --------------------------------
# Final checks
# --------------------------------

print("\n==============================")
print("FINAL CHECKS")
print("==============================")


required_fields = [
    "chunk_id",
    "text",
    "source",
    "page",
    "document_id",
    "document",
    "document_type",
    "jurisdiction",
    "section",
    "language",
]


for field in required_fields:

    if field not in point.payload:

        raise ValueError(
            f"Missing payload field: {field}"
        )

    print(
        f"✓ {field}"
    )


# --------------------------------
# Verify metadata values
# --------------------------------

if point.payload["document"] != (
    "An Overview of Ayurveda"
):

    raise ValueError(
        "Document metadata is incorrect"
    )

print(
    "✓ Document metadata is correct"
)


if point.payload["document_type"] != (
    "ayurvedic_reference"
):

    raise ValueError(
        "Document type metadata is incorrect"
    )

print(
    "✓ Document type metadata is correct"
)


if point.payload["jurisdiction"] != "India":

    raise ValueError(
        "Jurisdiction metadata is incorrect"
    )

print(
    "✓ Jurisdiction metadata is correct"
)


if point.payload["language"] != "en":

    raise ValueError(
        "Language metadata is incorrect"
    )

print(
    "✓ Language metadata is correct"
)


# --------------------------------
# Success
# --------------------------------

print("\n==============================")
print("ALL TESTS PASSED ✓")
print("==============================")