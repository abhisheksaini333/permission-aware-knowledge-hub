from knowledge.store import Store
from knowledge.worker import IndexWorker

class Invalid:
 def encode(self,texts):return [[float("nan")]+[0.]*383 for t in texts]

def test_nonfinite_embeddings_leave_document_unpublished():
 s=Store();s.ingest("a","x","X","hello",[]);IndexWorker(s,Invalid()).once()
 assert s.chunks("a")==[] and s.jobs("a")[0]["error"]=="ValueError"
