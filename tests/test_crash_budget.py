from knowledge.store import Store

def test_expired_claims_eventually_fail_without_unbounded_retries():
 s=Store();s.ingest("a","x","X","hello",[])
 for now in [0,2,4]:assert s.claim("worker",now=now,lease_seconds=1)
 assert s.claim("worker",now=6,lease_seconds=1) is None
 assert s.jobs("a")[0]["status"]=="failed"
