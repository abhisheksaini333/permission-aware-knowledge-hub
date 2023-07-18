from io import BytesIO
from pathlib import PurePath
from PyPDF2 import PdfReader
from .content import normalize


def extract(filename, payload, max_bytes=2000000, max_pages=100):
    if len(payload) > max_bytes:
        raise ValueError("Document exceeds upload limit")
    suffix = PurePath(filename).suffix.lower()
    if suffix in {".md", ".txt"}:
        return normalize(payload)
    if suffix != ".pdf":
        raise ValueError("Use Markdown, text, or PDF")
    try:
        pdf = PdfReader(BytesIO(payload), strict=True)
        if pdf.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported")
        if len(pdf.pages) > max_pages:
            raise ValueError("PDF exceeds page limit")
        text = "\f".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as exc:
        raise ValueError(
            "PDF could not be read; upload an unencrypted text PDF"
        ) from exc
    if not text.strip():
        raise ValueError("PDF has no extractable text; run OCR before uploading")
    if len(text.encode()) > max_bytes:
        raise ValueError("Extracted PDF text exceeds limit")
    return text
