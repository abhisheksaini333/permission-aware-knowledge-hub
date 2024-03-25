import pytest
from knowledge.settings import Settings
from knowledge.chunks import chunk_text

@pytest.mark.parametrize("bad", [True, 3.5, 0, -1])
def test_invalid_positive_limits(bad):
    for field in ("chunk_size", "max_document_bytes", "max_query_chars"):
        with pytest.raises(ValueError): Settings(**{field: bad})
    with pytest.raises(ValueError): chunk_text("abc", size=bad, overlap=0)

@pytest.mark.parametrize("bad", [True, 0.5, -1])
def test_invalid_overlap(bad):
    with pytest.raises(ValueError): chunk_text("abc", size=3, overlap=bad)
    with pytest.raises(ValueError): Settings(chunk_overlap=bad)
