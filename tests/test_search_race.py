from knowledge.service import KnowledgeHub
from knowledge.identity import Principal
from knowledge.worker import IndexWorker
from test_search import fixture

class Revoker:
 def __init__(self,s):self.s=s
 def encode(self,texts):self.s.set_membership("acme","u",[],["reader"]);return [[1.,0.] for t in texts]

def test_permissions_changed_during_embedding_do_not_leak_search_text():
 s=fixture();p=Principal("u","acme",frozenset({"finance"}),frozenset({"reader"}))
 assert KnowledgeHub(s,Revoker(s)).search(p,"acquisition","fusion")==[]
