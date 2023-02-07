from knowledge.store import Store
from knowledge.worker import IndexWorker
from knowledge.identity import Principal
from knowledge.service import KnowledgeHub

def fixture():
 s=Store()
 for tenant in ["acme","beta","cobalt"]:
  s.ingest(tenant,"public.md","Public","Support hours are nine to five",[])
  s.ingest(tenant,"finance.md","Finance","Acquisition price is forty million",["finance"])
 while IndexWorker(s).once():pass
 return s

def test_three_tenants_and_two_roles_never_bypass_group_checks():
 s=fixture();hub=KnowledgeHub(s)
 for tenant in ["acme","beta","cobalt"]:
  for role in ["reader","admin"]:
   p=Principal("u",tenant,frozenset(),frozenset({role}))
   assert hub.search(p,"acquisition")==[]
   hits=hub.search(p,"support");assert len(hits)==1 and hits[0]["tenant"]==tenant

def test_revoked_membership_affects_existing_principal():
 s=fixture();hub=KnowledgeHub(s);p=Principal("u","acme",frozenset({"finance"}),frozenset({"reader"}))
 assert hub.search(p,"acquisition")
 s.set_membership("acme","u",[],["reader"])
 assert hub.search(p,"acquisition")==[]
