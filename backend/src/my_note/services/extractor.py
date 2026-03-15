"""Text extraction service — first step of the ingestion pipeline.

Converts all supported formats to plain UTF-8 text before any LLM call.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Extension → language label mapping for code files
_CODE_EXTENSIONS: dict[str, str] = {
    ".py": "Python",
    ".sql": "SQL",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JSX",
    ".tsx": "TSX",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".rb": "Ruby",
    ".sh": "Shell",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".json": "JSON",
    ".xml": "XML",
    ".html": "HTML",
    ".css": "CSS",
}

_TEXT_EXTENSIONS: set[str] = {".txt", ".md", ".markdown", ".rst"}


class ExtractionError(Exception):
    """Raised when text extraction fails."""

    def __init__(self, message: str, source_type: str) -> None:
        self.source_type = source_type
        super().__init__(message)


def _ensure_non_empty(text: str, source_type: str, context: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ExtractionError(
            f"Extraction yielded empty text from {context}", source_type
        )
    return cleaned


def _extract_pdf(file_path: str) -> str:
    """Extract text from a PDF, falling back to OCR if needed."""
    import pdfplumber

    pages: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)

    combined = "\n\n--- Page Break ---\n\n".join(pages).strip()

    if len(combined.replace("--- Page Break ---", "").strip()) < 10:
        logger.warning(
            "pdfplumber returned near-empty text for %s — attempting OCR fallback",
            file_path,
        )
        combined = _extract_pdf_ocr(file_path)

    return combined


def _extract_pdf_ocr(file_path: str) -> str:
    """OCR fallback for scanned PDFs."""
    import pdf2image
    import pytesseract

    images = pdf2image.convert_from_path(file_path)
    pages: list[str] = []
    for img in images:
        text = pytesseract.image_to_string(img)
        pages.append(text)

    return "\n\n--- Page Break ---\n\n".join(pages).strip()


def _extract_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    from docx import Document

    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_url(url: str) -> str:
    """Fetch and extract main content from a URL."""
    import trafilatura

    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise ExtractionError(
            f"Failed to fetch URL: {url}", source_type="url"
        )

    text = trafilatura.extract(downloaded)
    if text is None:
        raise ExtractionError(
            f"Failed to extract content from URL: {url}", source_type="url"
        )
    return text


def _read_file(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")


async def extract_text(
    file_path: str | None = None,
    url: str | None = None,
    raw_text: str | None = None,
    source_type: str = "",
) -> str:
    """Extract plain UTF-8 text from a supported source.

    Exactly one of *file_path*, *url*, or *raw_text* should be provided.

    Returns clean UTF-8 text ready for downstream processing.
    Raises ``ExtractionError`` on any failure.
    """
    try:
        if raw_text is not None:
            return _ensure_non_empty(raw_text, source_type, "raw text input")

        if url is not None:
            text = _extract_url(url)
            return _ensure_non_empty(text, source_type, url)

        if file_path is None:
            raise ExtractionError(
                "No input provided — supply file_path, url, or raw_text",
                source_type,
            )

        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            text = _extract_pdf(file_path)
            return _ensure_non_empty(text, source_type, file_path)

        if ext == ".docx":
            text = _extract_docx(file_path)
            return _ensure_non_empty(text, source_type, file_path)

        if ext in _CODE_EXTENSIONS:
            content = _read_file(file_path)
            lang = _CODE_EXTENSIONS[ext]
            text = f"# Language: {lang}\n{content}"
            return _ensure_non_empty(text, source_type, file_path)

        if ext in _TEXT_EXTENSIONS:
            text = _read_file(file_path)
            return _ensure_non_empty(text, source_type, file_path)

        raise ExtractionError(
            f"Unsupported file type: {ext}", source_type
        )

    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(
            f"Extraction failed: {exc}", source_type
        ) from exc
