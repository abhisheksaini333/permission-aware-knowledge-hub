from knowledge.store import Store
from knowledge.worker import IndexWorker

def test_worker_indexes_pages_and_records_completion():
 s=Store();d=s.ingest("a","x.pdf","X","first\fsecond",[])
 assert IndexWorker(s).once()
 chunks=s.chunks("a")
 assert [(c["page"],c["document_start"],c["text"]) for c in chunks]==[(1,0,"first"),(2,6,"second")]
 assert s.jobs("a")[0]["status"]=="succeeded"
 assert not IndexWorker(s).once()
