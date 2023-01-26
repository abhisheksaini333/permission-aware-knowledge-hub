from knowledge.store import Store
from knowledge.worker import IndexWorker

class MissingEncoder:
 def encode(self,texts):return []

def test_short_embedding_batch_does_not_publish_partial_index():
 s=Store();s.ingest("a","x","X","secret",[])
 IndexWorker(s,MissingEncoder()).once()
 assert s.chunks("a")==[]
 assert s.jobs("a")[0]["status"]=="pending"
 assert s.jobs("a")[0]["error"]=="ValueError"
