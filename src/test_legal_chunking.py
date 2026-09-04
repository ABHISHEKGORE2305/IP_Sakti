from document_loader import load_pdf
from chunker import create_chunks


PDF_PATH = (
    "data/raw/patents_act_1970.pdf"
)

METADATA = {
    "document": "The Patents Act, 1970",
    "document_type": "statute",
    "jurisdiction": "India",
    "language": "en",
}


pages = load_pdf(
    PDF_PATH,
    metadata=METADATA,
)

chunks = create_chunks(
    pages,
    chunk_size=1000,
    chunk_overlap=200,
)


print(
    f"\nPages: {len(pages)}"
)

print(
    f"Chunks: {len(chunks)}"
)


print("\n" + "=" * 80)
print("LEGAL REFERENCES FOUND")
print("=" * 80)


count = 0

for chunk in chunks:

    if (
        chunk.get("legal_reference")
        or chunk.get("section")
        or chunk.get("rule")
    ):

        count += 1

        print("\nChunk:", chunk["chunk_id"])

        print(
            "Page:",
            chunk["page"]
        )

        print(
            "Legal reference:",
            chunk.get(
                "legal_reference"
            )
        )

        print(
            "Section:",
            chunk.get("section")
        )

        print(
            "Rule:",
            chunk.get("rule")
        )

        print(
            "Text:",
            chunk["text"][:300]
        )


print("\n" + "=" * 80)

print(
    f"Chunks containing legal metadata: "
    f"{count}"
)

print("=" * 80)