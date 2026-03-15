"""Tests for the text extraction service."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from my_note.services.extractor import ExtractionError, extract_text


# ── Raw text ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_raw_text():
    result = await extract_text(raw_text="Hello, world!", source_type="text")
    assert result == "Hello, world!"


@pytest.mark.asyncio
async def test_raw_text_empty_raises():
    with pytest.raises(ExtractionError):
        await extract_text(raw_text="   ", source_type="text")


# ── Text / Markdown files ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_markdown_file(tmp_path: Path):
    md = tmp_path / "note.md"
    md.write_text("# Heading\n\nSome content.", encoding="utf-8")
    result = await extract_text(file_path=str(md), source_type="markdown")
    assert "# Heading" in result
    assert "Some content." in result


@pytest.mark.asyncio
async def test_txt_file(tmp_path: Path):
    txt = tmp_path / "note.txt"
    txt.write_text("Plain text content.", encoding="utf-8")
    result = await extract_text(file_path=str(txt), source_type="text")
    assert result == "Plain text content."


# ── Code files ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_python_file(tmp_path: Path):
    py = tmp_path / "script.py"
    py.write_text("print('hi')\n", encoding="utf-8")
    result = await extract_text(file_path=str(py), source_type="code")
    assert result.startswith("# Language: Python")
    assert "print('hi')" in result


@pytest.mark.asyncio
async def test_typescript_file(tmp_path: Path):
    ts = tmp_path / "app.ts"
    ts.write_text("const x: number = 1;\n", encoding="utf-8")
    result = await extract_text(file_path=str(ts), source_type="code")
    assert result.startswith("# Language: TypeScript")


@pytest.mark.asyncio
async def test_json_file(tmp_path: Path):
    f = tmp_path / "data.json"
    f.write_text('{"key": "value"}', encoding="utf-8")
    result = await extract_text(file_path=str(f), source_type="code")
    assert "# Language: JSON" in result


# ── PDF extraction ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pdf_extraction(tmp_path: Path):
    fake_pdf = tmp_path / "doc.pdf"
    fake_pdf.touch()

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page one content."

    mock_pdf_ctx = MagicMock()
    mock_pdf_ctx.pages = [mock_page]
    mock_pdf_ctx.__enter__ = MagicMock(return_value=mock_pdf_ctx)
    mock_pdf_ctx.__exit__ = MagicMock(return_value=False)

    with patch.dict("sys.modules", {"pdfplumber": MagicMock()}) as _:
        import sys

        sys.modules["pdfplumber"].open.return_value = mock_pdf_ctx
        result = await extract_text(file_path=str(fake_pdf), source_type="pdf")

    assert "Page one content." in result


@pytest.mark.asyncio
async def test_pdf_multi_page(tmp_path: Path):
    fake_pdf = tmp_path / "doc.pdf"
    fake_pdf.touch()

    pages = []
    for text in ["First page.", "Second page."]:
        p = MagicMock()
        p.extract_text.return_value = text
        pages.append(p)

    mock_pdf_ctx = MagicMock()
    mock_pdf_ctx.pages = pages
    mock_pdf_ctx.__enter__ = MagicMock(return_value=mock_pdf_ctx)
    mock_pdf_ctx.__exit__ = MagicMock(return_value=False)

    with patch.dict("sys.modules", {"pdfplumber": MagicMock()}):
        import sys

        sys.modules["pdfplumber"].open.return_value = mock_pdf_ctx
        result = await extract_text(file_path=str(fake_pdf), source_type="pdf")

    assert "First page." in result
    assert "Second page." in result
    assert "--- Page Break ---" in result


@pytest.mark.asyncio
async def test_pdf_ocr_fallback(tmp_path: Path):
    """OCR fallback triggers when pdfplumber returns empty text."""
    fake_pdf = tmp_path / "scanned.pdf"
    fake_pdf.touch()

    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""

    mock_pdf_ctx = MagicMock()
    mock_pdf_ctx.pages = [mock_page]
    mock_pdf_ctx.__enter__ = MagicMock(return_value=mock_pdf_ctx)
    mock_pdf_ctx.__exit__ = MagicMock(return_value=False)

    mock_img = MagicMock()

    mock_pdfplumber = MagicMock()
    mock_pdfplumber.open.return_value = mock_pdf_ctx

    mock_pdf2image = MagicMock()
    mock_pdf2image.convert_from_path.return_value = [mock_img]

    mock_tesseract = MagicMock()
    mock_tesseract.image_to_string.return_value = "OCR extracted text"

    with patch.dict(
        "sys.modules",
        {
            "pdfplumber": mock_pdfplumber,
            "pdf2image": mock_pdf2image,
            "pytesseract": mock_tesseract,
        },
    ):
        result = await extract_text(
            file_path=str(fake_pdf), source_type="pdf"
        )

    assert "OCR extracted text" in result


# ── DOCX extraction ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_docx_extraction(tmp_path: Path):
    fake_docx = tmp_path / "doc.docx"
    fake_docx.touch()

    mock_para1 = MagicMock()
    mock_para1.text = "First paragraph."
    mock_para2 = MagicMock()
    mock_para2.text = "Second paragraph."

    mock_doc = MagicMock()
    mock_doc.paragraphs = [mock_para1, mock_para2]

    mock_docx_module = MagicMock()
    mock_docx_module.Document.return_value = mock_doc

    with patch.dict("sys.modules", {"docx": mock_docx_module}):
        result = await extract_text(
            file_path=str(fake_docx), source_type="docx"
        )

    assert "First paragraph." in result
    assert "Second paragraph." in result


# ── URL extraction ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_url_extraction():
    mock_traf = MagicMock()
    mock_traf.fetch_url.return_value = "<html>content</html>"
    mock_traf.extract.return_value = "Extracted article text."

    with patch.dict("sys.modules", {"trafilatura": mock_traf}):
        result = await extract_text(
            url="https://example.com/article", source_type="url"
        )

    assert result == "Extracted article text."


@pytest.mark.asyncio
async def test_url_fetch_failure():
    mock_traf = MagicMock()
    mock_traf.fetch_url.return_value = None

    with patch.dict("sys.modules", {"trafilatura": mock_traf}):
        with pytest.raises(ExtractionError, match="Failed to fetch URL"):
            await extract_text(
                url="https://example.com/bad", source_type="url"
            )


@pytest.mark.asyncio
async def test_url_extract_failure():
    mock_traf = MagicMock()
    mock_traf.fetch_url.return_value = "<html></html>"
    mock_traf.extract.return_value = None

    with patch.dict("sys.modules", {"trafilatura": mock_traf}):
        with pytest.raises(ExtractionError, match="Failed to extract content"):
            await extract_text(
                url="https://example.com/empty", source_type="url"
            )


# ── Error handling ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_unsupported_file_type(tmp_path: Path):
    f = tmp_path / "image.bmp"
    f.touch()
    with pytest.raises(ExtractionError, match="Unsupported file type"):
        await extract_text(file_path=str(f), source_type="unknown")


@pytest.mark.asyncio
async def test_no_input_raises():
    with pytest.raises(ExtractionError, match="No input provided"):
        await extract_text(source_type="none")


@pytest.mark.asyncio
async def test_extraction_error_has_source_type():
    with pytest.raises(ExtractionError) as exc_info:
        await extract_text(raw_text="", source_type="text")
    assert exc_info.value.source_type == "text"
