import pytest
from knowledge.formats import extract

class Page:
    def extract_text(self): return "text\0"
class Reader:
    is_encrypted=False
    pages=[Page(),Page()]

def test_pdf_policy_errors_remain_specific(monkeypatch):
    monkeypatch.setattr("knowledge.formats.PdfReader", lambda *a, **k: Reader())
    with pytest.raises(ValueError, match="page limit"): extract("a.pdf", b"a", max_pages=1)
    with pytest.raises(ValueError, match="null bytes"): extract("a.pdf", b"a")
    Reader.is_encrypted=True
    try:
        with pytest.raises(ValueError, match="Encrypted"): extract("a.pdf", b"a")
    finally: Reader.is_encrypted=False
