from knowledge.worker import IndexWorker

def test_postgres_revisions_jobs_and_tombstones(pgstore):
 s=pgstore;d=s.ingest("a","x","X","first",[])
 assert s.document(d["id"])["revision"]==1
 assert IndexWorker(s).once()
 assert s.chunks("a")[0]["text"]=="first"
 assert s.delete(d["id"],"a") and s.chunks("a")==[]

def test_postgres_lease_fencing(pgstore):
 s=pgstore;s.ingest("a","x","X","hello",[])
 old=s.claim("old",now=0,lease_seconds=1);new=s.claim("new",now=2)
 assert not s.finish(old,now=2) and s.finish(new,now=3)
