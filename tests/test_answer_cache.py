from knowledge.identity import Principal
from knowledge.service import KnowledgeHub
from test_search import fixture

class G:
 def __init__(self):self.calls=0
 def generate(self,prompt):self.calls+=1;return "forty million"

def test_revocation_cannot_reuse_cached_finance_answer():
 s=fixture();g=G();h=KnowledgeHub(s,generator=g);p=Principal("u","acme",frozenset({"finance"}),frozenset({"reader"}))
 assert not h.ask(p,"acquisition price")["cached"]
 assert h.ask(p,"acquisition price")["cached"] and g.calls==1
 s.set_membership("acme","u",[],["reader"])
 a=h.ask(p,"acquisition price");assert a["abstained"] and not a["cached"] and not a["citations"]

def test_deletion_invalidates_cache_even_when_old_token_still_valid():
 s=fixture();g=G();h=KnowledgeHub(s,generator=g);p=Principal("u","acme",frozenset({"finance"}),frozenset({"reader"}))
 a=h.ask(p,"acquisition price");s.delete(a["citations"][0]["document_id"],"acme")
 assert h.ask(p,"acquisition price")["abstained"]
