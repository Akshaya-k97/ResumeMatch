"""PDF text extraction (PyMuPDF). Nothing is written to disk."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

MIN_USEFUL_CHARS = 200  # below this, the PDF is probably scanned/image-only


@dataclass
class ExtractionResult:
    text: str
    pages: int
    warnings: list[str] = field(default_factory=list)


def extract_text_from_pdf(source: str | Path | bytes) -> ExtractionResult:
    """Extract text from a PDF given a file path or raw bytes (e.g. a Streamlit upload)."""
    import fitz  # PyMuPDF; imported here so the rest of the package works without it

    if isinstance(source, (bytes, bytearray)):
        doc = fitz.open(stream=bytes(source), filetype="pdf")
    else:
        doc = fitz.open(str(source))

    warnings: list[str] = []
    try:
        if doc.needs_pass:
            return ExtractionResult("", doc.page_count, ["PDF is password-protected."])
        # sort=True orders text blocks top-to-bottom, left-to-right, which helps with columns
        parts = [page.get_text("text", sort=True) for page in doc]
        pages = doc.page_count
    finally:
        doc.close()

    text = "\n".join(parts)
    if len(text.strip()) < MIN_USEFUL_CHARS:
        warnings.append(
            "Very little text was found. This PDF may be a scanned image; "
            "try exporting your resume as a text-based PDF."
        )
    return ExtractionResult(text=text, pages=pages, warnings=warnings)
