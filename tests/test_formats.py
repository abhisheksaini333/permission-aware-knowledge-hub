from io import BytesIO
import pytest
from reportlab.pdfgen import canvas
from knowledge.formats import extract


def test_pdf_pages_preserve_order():
    b = BytesIO()
    c = canvas.Canvas(b)
    c.drawString(50, 750, "First page")
    c.showPage()
    c.drawString(50, 750, "Second page")
    c.save()
    text = extract("manual.pdf", b.getvalue())
    assert "First page" in text.split("\f")[0] and "Second page" in text.split("\f")[1]


def test_only_supported_files_with_size_limit():
    assert extract("x.md", b"# Hello") == "# Hello"
    with pytest.raises(ValueError):
        extract("x.exe", b"hello")
    with pytest.raises(ValueError):
        extract("x.md", b"hello", max_bytes=4)
    with pytest.raises(ValueError):
        extract("x.pdf", b"corrupt")
