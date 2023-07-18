from knowledge.store import Store
from knowledge.worker import IndexWorker


def test_reindex_resets_job_but_preserves_document_revision():
    s = Store()
    d = s.ingest("a", "x", "X", "hello", [])
    IndexWorker(s).once()
    assert s.reindex(d["id"], "a")
    assert (
        s.document(d["id"])["revision"] == 1
        and s.document(d["id"])["status"] == "pending"
    )
    assert s.chunks("a") == []
    assert IndexWorker(s).once() and s.chunks("a")
    s.delete(d["id"], "a")
    assert not s.reindex(d["id"], "a")
    assert not s.reindex(d["id"], "b")
