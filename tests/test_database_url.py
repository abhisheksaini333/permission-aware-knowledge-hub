import pytest
from knowledge.database import open_store


def test_sqlite_url_and_invalid_scheme(tmp_path):
    s = open_store("sqlite:///" + str(tmp_path / "test.db"))
    assert s.documents("a") == []
    s.close()
    with pytest.raises(ValueError):
        open_store("https://not-a-database")
