from knowledge.store import Store


def test_same_content_metadata_does_not_create_revision():
    s = Store()
    a = s.ingest("a", "x", "X", "hello", ["g"])
    b = s.ingest("a", "x", "X", "hello", ["g", "g"])
    assert a == b and b["revision"] == 1
    c = s.ingest("a", "x", "New title", "hello", ["g"])
    assert c["revision"] == 2
