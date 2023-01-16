from knowledge.store import Store

def test_each_revision_enqueues_one_persisted_job(tmp_path):
 path=str(tmp_path/"db");s=Store(path)
 d=s.ingest("a","x","X","hello",[]);s.ingest("a","x","X","hello",[])
 assert len(s.jobs("a"))==1
 s.close();s=Store(path)
 assert s.jobs("a")[0]["revision"]==1
