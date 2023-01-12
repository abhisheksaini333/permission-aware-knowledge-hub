from knowledge.store import Store

def test_documents_are_listed_by_tenant():
 s=Store();s.ingest("a","x","X","one",[]);s.ingest("b","x","X","two",[])
 assert len(s.documents("a"))==1
 assert s.documents("a")[0]["content"]=="one"
 assert s.documents("none")==[]
