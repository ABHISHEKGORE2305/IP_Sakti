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


def load_pdf(pdf_path: str):

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):

        raw_text = page.get_text()

        text = clean_text(raw_text)

        if not text:
            continue

        pages.append({
            "text": text,
            "page": page_number + 1,
            "source": pdf_path.name,
            "document_id": pdf_path.stem,
        })

    document.close()

    return pages

if __name__ == "__main__":

    pages = load_pdf(
        "data/raw/An_Overview_of_Ayurveda.pdf"
    )

    print(f"Loaded {len(pages)} pages")

    for page in pages[:2]:

        print("\n--------------------")

        print("Page:", page["page"])

        print("Source:", page["source"])

        print("Text:")
        print(page["text"][:1000])
