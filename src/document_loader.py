from pathlib import Path
import pymupdf
import re


def clean_text(text: str) -> str:

    # Replace multiple spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def load_pdf(
    pdf_path: str,
    metadata: dict | None = None,
):

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = pymupdf.open(pdf_path)

    pages = []

    # Optional (first_page, last_page) 1-based inclusive window, for a PDF
    # that bundles two distinct instruments — the Drugs and Cosmetics volume
    # carries the Act on pp.1-38 and the Rules from p.39, and they must be
    # ingested as separate documents so numbered provisions are labelled
    # "Section N" vs "Rule N" correctly rather than all as sections.
    page_range = (metadata or {}).get("page_range")

    for page_number, page in enumerate(document):

        if page_range and not (page_range[0] <= page_number + 1 <= page_range[1]):
            continue

        raw_text = page.get_text()

        text = clean_text(raw_text)

        if not text:
            continue

        # Basic page metadata
        page_data = {
            "text": text,
            "page": page_number + 1,
            "source": pdf_path.name,
            "document_id": pdf_path.stem,
        }

        # Add document-level metadata
        if metadata:
            page_data.update(metadata)

        pages.append(page_data)

    document.close()

    return pages


if __name__ == "__main__":

    metadata = {
        "document": "An Overview of Ayurveda",
        "document_type": "reference",
        "jurisdiction": "India",
        "language": "en",
    }

    pages = load_pdf(
        "data/raw/An_Overview_of_Ayurveda.pdf",
        metadata=metadata,
    )

    print(f"Loaded {len(pages)} pages")

    for page in pages[:2]:

        print("\n--------------------")

        print("Page:", page["page"])
        print("Source:", page["source"])
        print("Document:", page.get("document"))
        print("Document Type:", page.get("document_type"))
        print("Jurisdiction:", page.get("jurisdiction"))
        print("Language:", page.get("language"))

        print("\nText:")
        print(page["text"][:1000])
