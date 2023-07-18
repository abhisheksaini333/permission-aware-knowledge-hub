from knowledge.retrieval import lexical, tokens


def test_bm25_ranks_relevant_passage_and_excludes_no_overlap():
    chunks = [
        dict(id="a", text="Database backup retention is seven days"),
        dict(id="b", text="Vacation requests go to HR"),
    ]
    out = lexical("backup retention", chunks)
    assert out[0][0]["id"] == "a" and len(out) == 1
    assert tokens("Backup, RETENTION!") == ["backup", "retention"]
    assert lexical("zebra", chunks) == []
