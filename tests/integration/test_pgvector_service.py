from knowledge.identity import Principal
from knowledge.service import KnowledgeHub
from knowledge.worker import IndexWorker

class Encoder:
 def encode(self,texts):return [[1.]+[0.]*383 for t in texts]

def test_service_dense_retrieval_uses_persisted_vectors(pgstore):
 s=pgstore;s.ingest("a","x","X","support hours",[]);IndexWorker(s,Encoder()).once()
 p=Principal("u","a",frozenset(),frozenset({"reader"}))
 out=KnowledgeHub(s,Encoder()).search(p,"support","dense")
 assert len(out)==1 and out[0]["score"]>.99
