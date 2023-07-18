from knowledge.store import Store
from knowledge.worker import IndexWorker
import time


def test_stale_worker_cannot_publish_after_reclaim():
    s = Store()
    d = s.ingest("a", "x", "X", "hello", [])
    old = s.claim("old", now=100, lease_seconds=1)
    new = s.claim("new", now=102)
    chunk = [dict(text="stale", page=1, start=0, end=5)]
    assert not s.index(d["id"], 1, chunk, job=old, now=103)
    assert not s.index(d["id"], 1, chunk, now=103)
    assert s.index(
        d["id"], 1, [dict(text="fresh", page=1, start=0, end=5)], job=new, now=103
    )
    assert s.chunks("a")[0]["text"] == "fresh"


def test_expired_owner_cannot_publish_or_complete_even_before_reclaim():
    s = Store()
    d = s.ingest("a", "x", "X", "hello", [])
    job = s.claim("old", now=0, lease_seconds=1)
    assert not s.index(d["id"], 1, [], job=job, now=2)
    assert not s.finish(job, now=2)


def test_worker_passes_lease_to_publication_after_encoder_reclaims():
    s = Store()
    s.ingest("a", "x", "X", "hello", [])

    class Encoder:
        def encode(self, texts):
            s.claim("replacement", now=time.time() + 61)
            return [[1.0] + [0.0] * 383 for t in texts]

    IndexWorker(s, Encoder()).once()
    assert s.chunks("a") == []
    assert s.jobs("a")[0]["owner"] == "replacement"
