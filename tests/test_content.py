import pytest
from knowledge.content import normalize, content_digest, document_key


def test_line_endings_and_bom_normalized():
    assert normalize(b"\xef\xbb\xbfOne\r\nTwo\rThree") == "One\nTwo\nThree"
    assert content_digest("One") == content_digest("One")
    assert document_key("a", "x") != document_key("b", "x")


def test_invalid_text_and_control_bytes_rejected():
    with pytest.raises(ValueError):
        normalize(b"\xff")
    with pytest.raises(ValueError):
        normalize(b"a\x00b")
