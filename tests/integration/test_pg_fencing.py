import os
from knowledge.postgres import PostgresStore


def test_separate_connections_cannot_publish_stale_worker_results(pgstore):
    s = pgstore
    schema = s.db.execute("SELECT current_schema()").fetchone()[0]
    other = PostgresStore(os.environ["KNOWLEDGE_TEST_DATABASE"], schema=schema)
    try:
        d = s.ingest("a", "lease.md", "Lease", "current", [])
        old = s.claim("old", now=0, lease_seconds=1)
        new = other.claim("new", now=2)
        vector = [1.0] + [0.0] * 383
        fresh = [dict(text="fresh", page=1, start=0, end=5, vector=vector)]
        stale = [dict(text="stale", page=1, start=0, end=5, vector=vector)]
        assert other.index(d["id"], 1, fresh, job=new, now=3)
        assert not s.index(d["id"], 1, stale, job=old, now=3)
        assert not s.finish(old, now=3)
        assert s.chunks("a")[0]["text"] == "fresh"
        assert s.db.execute("SELECT count(*) FROM vectors").fetchone()[0] == 1
    finally:
        other.close()
