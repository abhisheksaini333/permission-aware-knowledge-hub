from knowledge.store import Store


def test_revisions_persist_across_restart(tmp_path):
    path = str(tmp_path / "hub.db")
    s = Store(path)
    a = s.ingest("acme", "handbook.md", "Handbook", "first", ["staff"])
    b = s.ingest("acme", "handbook.md", "Handbook", "second", ["staff"])
    assert a["id"] == b["id"] and b["revision"] == 2
    s.close()
    again = Store(path)
    assert again.document(a["id"])["content"] == "second"
    assert again.revision(a["id"], 1)["content"] == "first"
