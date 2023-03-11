from knowledge.identity import Principal
from knowledge.chunks import chunk_text

def test_sql_vector_search_filters_forbidden_neighbors(pgstore):
 s=pgstore;v=[1.]+[0.]*383
 for tenant,groups in [("a",[]),("a",["secret"]),("b",[])]:
  d=s.ingest(tenant,str(groups),"Doc","hello",groups);c=chunk_text("hello");c[0]["vector"]=v;s.index(d["id"],1,c)
 p=Principal("u","a",frozenset(),frozenset({"reader"}))
 hits=s.vector_search(p,v,10)
 assert len(hits)==1 and hits[0][0]["tenant"]=="a"
 assert len(s.vector_search(Principal("u","a",frozenset({"secret"}),frozenset({"reader"})),v,10))==2
