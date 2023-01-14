from knowledge.store import Store
from knowledge.chunks import chunk_text

def test_deleted_documents_cannot_be_resurrected_by_retry():
 s=Store();d=s.ingest("a","x","X","secret",[]);s.index(d["id"],1,chunk_text("secret"))
 assert s.delete(d["id"],"a")
 assert s.chunks("a")==[] and not s.index(d["id"],1,chunk_text("secret"))
 assert s.document(d["id"])["deleted"]
 assert not s.delete(d["id"],"b")
 assert s.ingest("a","x","X","new",[])["revision"]==3
