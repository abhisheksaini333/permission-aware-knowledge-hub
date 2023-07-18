from knowledge.store import Store
from knowledge.chunks import chunk_text


def test_index_is_revision_bound_and_replaces_old_chunks():
    s = Store()
    d = s.ingest("a", "x", "X", "first", [])
    assert s.index(d["id"], 1, chunk_text("first"))
    assert s.chunks("a")[0]["text"] == "first"
    s.ingest("a", "x", "X", "second", [])
    assert not s.index(d["id"], 1, chunk_text("first"))
    assert s.index(d["id"], 2, chunk_text("second"))
    assert len(s.chunks("a")) == 1 and s.chunks("a")[0]["revision"] == 2
