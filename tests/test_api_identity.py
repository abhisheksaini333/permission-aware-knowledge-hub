from api_support import client,headers

def test_identity_requires_signed_bearer_and_health_does_not():
 c,s=client()
 assert c.get("/health").status_code==200
 assert c.get("/api/me").status_code==401
 assert c.get("/api/me",headers={"Authorization":"Bearer nope"}).status_code==401
 r=c.get("/api/me",headers=headers());assert r.status_code==200 and r.json()["tenant"]=="acme"
