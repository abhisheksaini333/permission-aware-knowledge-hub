from knowledge.chunks import chunk_text


def test_vectors_follow_revision_replacement_and_deletion(pgstore):
    s = pgstore
    d = s.ingest("a", "x", "X", "hello", [])
    c = chunk_text("hello")
    c[0]["vector"] = [1.0] + [0.0] * 383
    assert s.index(d["id"], 1, c)
    assert s.db.execute("SELECT count(*) FROM vectors").fetchone()[0] == 1
    s.delete(d["id"], "a")
    assert s.db.execute("SELECT count(*) FROM vectors").fetchone()[0] == 0
