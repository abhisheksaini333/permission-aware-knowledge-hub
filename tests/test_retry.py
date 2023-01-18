from knowledge.store import Store

def test_failed_jobs_back_off_and_stop_at_attempt_budget():
 s=Store();s.ingest("a","x","X","hello",[])
 a=s.claim("w",now=0)
 assert s.finish(a,"temporary",now=0,max_attempts=2)
 assert s.claim("w",now=1) is None
 a=s.claim("w",now=3);assert s.finish(a,"still down",now=3,max_attempts=2)
 assert s.jobs("a")[0]["status"]=="failed"
 assert s.claim("w",now=1000) is None

def test_recovered_lease_rejects_previous_owner():
 s=Store();s.ingest("a","x","X","hello",[])
 old=s.claim("old",now=0,lease_seconds=1);new=s.claim("new",now=2)
 assert not s.finish(old)
 assert s.finish(new)
