from typing import List, Dict


def split_into_paragraphs(text: str) -> List[str]:
    """
    Split extracted text into paragraphs.
    """

    paragraphs = text.split("\n\n")

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def create_chunks(
    pages: List[Dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Dict]:

    chunks = []

    for page in pages:

        paragraphs = split_into_paragraphs(
            page["text"]
        )

        current_paragraphs = []
        current_length = 0

        for paragraph in paragraphs:

            paragraph_length = len(paragraph)

            # Add paragraph to current chunk
            if (
                current_length
                + paragraph_length
                + 2
                <= chunk_size
            ):

                current_paragraphs.append(paragraph)

                current_length += (
                    paragraph_length + 2
                )

                continue

            # Save current chunk
            if current_paragraphs:

                chunk_text = "\n\n".join(
                    current_paragraphs
                )

                chunks.append({
                    "chunk_id": len(chunks),
                    "text": chunk_text,
                    "page": page["page"],
                    "source": page["source"],
                    "document_id": page["document_id"],
                })

            # ----------------------------------
            # Create overlap
            # ----------------------------------

            overlap_paragraphs = []
            overlap_length = 0

            for previous in reversed(current_paragraphs):

                if (
                    overlap_length
                    + len(previous)
                    <= chunk_overlap
                ):

                    overlap_paragraphs.insert(
                        0,
                        previous
                    )

                    overlap_length += (
                        len(previous) + 2
                    )

                else:
                    break

            current_paragraphs = (
                overlap_paragraphs
                + [paragraph]
            )

            current_length = sum(
                len(p) + 2
                for p in current_paragraphs
            )

        # Save final chunk
        if current_paragraphs:

            chunk_text = "\n\n".join(
                current_paragraphs
            )

            chunks.append({
                "chunk_id": len(chunks),
                "text": chunk_text,
                "page": page["page"],
                "source": page["source"],
                "document_id": page["document_id"],
            })

    return chunks

if __name__ == "__main__":

    from document_loader import load_pdf

    pages = load_pdf(
        "data/raw/hypertension_guideline.pdf"
    )

    chunks = create_chunks(
        pages,
        chunk_size=1000,
        chunk_overlap=200,
    )

    print(
        f"\nCreated {len(chunks)} chunks"
    )

    for chunk in chunks[:5]:

        print("\n")
        print("=" * 70)

        print(
            f"Chunk ID: {chunk['chunk_id']}"
        )

        print(
            f"Page: {chunk['page']}"
        )

        print(
            f"Characters: {len(chunk['text'])}"
        )

        print("=" * 70)

        print(chunk["text"])