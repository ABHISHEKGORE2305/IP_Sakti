from document_loader import load_pdf
from chunker import create_chunks


PDF_PATH = (
    "data/raw/An_Overview_of_Ayurveda.pdf"
)


DOCUMENT_METADATA = {
    "document": "An Overview of Ayurveda",
    "document_type": "ayurvedic_reference",
    "jurisdiction": "India",
    "language": "en",
}


print("\n==============================")
print("TESTING DOCUMENT LOADER")
print("==============================")

pages = load_pdf(
    PDF_PATH,
    metadata=DOCUMENT_METADATA,
)

print(
    f"Pages loaded: {len(pages)}"
)


print("\nFirst page metadata:")

print(
    "Document:",
    pages[0].get("document")
)

print(
    "Document Type:",
    pages[0].get("document_type")
)

print(
    "Jurisdiction:",
    pages[0].get("jurisdiction")
)

print(
    "Language:",
    pages[0].get("language")
)


print("\n==============================")
print("TESTING CHUNKER")
print("==============================")

chunks = create_chunks(
    pages,
    chunk_size=1000,
    chunk_overlap=200,
)

print(
    f"Chunks created: {len(chunks)}"
)


print("\nFirst chunk:")

first_chunk = chunks[0]

print(
    "Chunk ID:",
    first_chunk["chunk_id"]
)

print(
    "Page:",
    first_chunk["page"]
)

print(
    "Document:",
    first_chunk["document"]
)

print(
    "Document Type:",
    first_chunk["document_type"]
)

print(
    "Jurisdiction:",
    first_chunk["jurisdiction"]
)

print(
    "Language:",
    first_chunk["language"]
)

print(
    "\nText preview:"
)

print(
    first_chunk["text"][:500]
)


print("\n==============================")
print("TESTING CHUNK IDS")
print("==============================")

for chunk in chunks[:5]:

    print(
        chunk["chunk_id"]
    )


print("\n==============================")
print("TEST COMPLETE")
print("==============================")