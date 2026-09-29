"""
Web fetcher for src/web_sources.py entries — mirrors document_loader.py's
load_pdf() output contract exactly (list[dict] of "page" records) so it
slots into chunker.create_chunks() unchanged.

Only fetches from the curated WEB_SOURCES registry — this is not a
general-purpose crawler. Honors robots.txt, sends an honest User-Agent,
and treats any single-source failure as non-fatal (raises a specific
exception the caller can catch and skip).
"""

import tempfile
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from document_loader import clean_text, load_pdf
from chunker import split_into_paragraphs

USER_AGENT = "IP-Sakti-CorpusUpdater/1.0 (+https://github.com/; contact: repo maintainer)"
REQUEST_TIMEOUT = 20

# Target size (characters) for each synthetic "page" handed to
# chunker.create_chunks() — chunker flushes a chunk at end-of-page, so
# without this a whole fetched page would collapse into one oversized
# chunk (no legal Section/Clause markers to split it, unlike the PDF
# statutes). Grouping paragraphs into ~1400-char pages keeps chunk
# granularity comparable to the PDF pipeline's page-sized chunks.
_SYNTHETIC_PAGE_CHARS = 1400


class WebFetchError(RuntimeError):
    """Raised when a single source can't be fetched — callers should
    catch this per-source and continue the batch, not abort it."""


def _robots_allowed(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except Exception:
        # robots.txt missing/unreachable — don't block on that alone.
        return True
    return parser.can_fetch(USER_AGENT, url)


def _fetch(url: str) -> requests.Response:
    if not _robots_allowed(url):
        raise WebFetchError(f"robots.txt disallows fetching {url}")

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise WebFetchError(f"Failed to fetch {url}: {exc}") from exc

    return response


def _extract_html_text(html: str, content_selector: str, url: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    region = soup.select_one(content_selector)
    if region is None:
        raise WebFetchError(
            f"content_selector {content_selector!r} matched nothing on {url} "
            "— the page structure may have changed; update web_sources.py."
        )

    for tag in region.select("script, style, nav, footer, noscript"):
        tag.decompose()

    return clean_text(region.get_text(separator="\n"))


def _split_into_synthetic_pages(text: str, max_chars: int = _SYNTHETIC_PAGE_CHARS) -> list[str]:
    paragraphs = split_into_paragraphs(text)
    if not paragraphs:
        return [text] if text else []

    pages = []
    current = []
    current_len = 0

    for para in paragraphs:
        if current and current_len + len(para) > max_chars:
            pages.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para)

    if current:
        pages.append("\n\n".join(current))

    return pages


def load_url(source: dict) -> list[dict]:
    """
    Fetch one src/web_sources.WEB_SOURCES entry and return page records
    in document_loader.load_pdf()'s exact shape:

        {"text": ..., "page": N, "source": url, "document_id": source_id,
         **metadata}

    `source` is one WEB_SOURCES dict — must contain source_id, url,
    fetch_method, and (for fetch_method="html") content_selector.
    Metadata fields (document, document_type, jurisdiction, language,
    authority_weight) are carried onto every page record, same as
    document_loader.load_pdf's `metadata` argument.
    """

    source_id = source["source_id"]
    url = source["url"]
    fetch_method = source["fetch_method"]

    metadata = {
        k: v
        for k, v in source.items()
        if k not in ("source_id", "url", "fetch_method", "content_selector")
    }
    metadata["document_id"] = source_id

    if fetch_method == "pdf_link":
        response = _fetch(url)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        try:
            pages = load_pdf(tmp_path, metadata=metadata)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        # load_pdf stamps document_id from the temp file's stem — restore
        # the real source_id (metadata is applied AFTER document_id in
        # load_pdf, so this actually already wins; kept explicit here in
        # case that ordering ever changes).
        for page in pages:
            page["document_id"] = source_id
            page["source"] = url
        return pages

    if fetch_method != "html":
        raise WebFetchError(f"Unknown fetch_method {fetch_method!r} for source {source_id!r}")

    if not source.get("content_selector"):
        raise WebFetchError(f"content_selector is required for fetch_method='html' (source {source_id!r})")

    response = _fetch(url)
    text = _extract_html_text(response.text, source["content_selector"], url)

    if not text:
        raise WebFetchError(f"No text extracted from {url} with selector {source['content_selector']!r}")

    synthetic_pages = _split_into_synthetic_pages(text)

    pages = []
    for i, page_text in enumerate(synthetic_pages, start=1):
        page_data = {
            "text": page_text,
            "page": i,
            "source": url,
            "document_id": source_id,
        }
        page_data.update(metadata)
        pages.append(page_data)

    return pages
