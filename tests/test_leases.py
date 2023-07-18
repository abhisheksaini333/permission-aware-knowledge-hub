from knowledge.store import Store


def test_worker_lease_prevents_duplicate_claim_and_expires():
    s = Store()
    s.ingest("a", "x", "X", "hello", [])
    a = s.claim("w1", now=100, lease_seconds=10)
    assert a["attempts"] == 1 and s.claim("w2", now=105) is None
    b = s.claim("w2", now=111)
    assert b["owner"] == "w2" and b["attempts"] == 2
