import pytest
from knowledge.settings import Settings


def test_defaults_are_local_and_limits_positive():
    s = Settings()
    assert s.max_document_bytes == 2000000
    assert s.chunk_size > s.chunk_overlap


def test_invalid_chunk_limits_rejected():
    with pytest.raises(ValueError):
        Settings(chunk_size=10, chunk_overlap=20)
