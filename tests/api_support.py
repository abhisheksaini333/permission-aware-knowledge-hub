from fastapi.testclient import TestClient
from knowledge.api import create_app
from knowledge.service import KnowledgeHub
from test_auth import KEY,token
from knowledge.auth import decode_token
from test_search import fixture

class SignedVerifier:
 def verify(self,value):return decode_token(value,KEY.public_key(),"https://issuer","api")
def client(generator=None):
 s=fixture();app=create_app(KnowledgeHub(s,generator=generator),SignedVerifier())
 return TestClient(app),s

def headers(tenant="acme",admin=False,groups=None):
 return {"Authorization":"Bearer "+token(tenant=tenant,groups=groups or [],realm_access={"roles":["admin" if admin else "reader"]})}
