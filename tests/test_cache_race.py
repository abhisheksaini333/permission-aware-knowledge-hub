from knowledge.service import KnowledgeHub
from knowledge.identity import Principal
from test_search import fixture

class G:
 def generate(self,prompt):return "forty million"

def test_cache_read_racing_with_revocation_does_not_return_sensitive_answer():
 s=fixture();h=KnowledgeHub(s,generator=G());p=Principal("u","acme",frozenset({"finance"}),frozenset({"reader"}));h.ask(p,"acquisition")
 original=s.cache_get
 def read(*a,**kw):
  result=original(*a,**kw);s.set_membership("acme","u",[],["reader"]);return result
 s.cache_get=read
 result=h.ask(p,"acquisition")
 assert result["abstained"] and result["citations"]==[]
