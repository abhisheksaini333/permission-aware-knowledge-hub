from api_support import client,headers

def test_reader_listing_hides_restricted_and_cross_tenant_documents():
 c,s=client();r=c.get("/api/documents",headers=headers())
 assert r.status_code==200 and len(r.json()["documents"])==1
 assert "content" not in r.json()["documents"][0]
 assert len(c.get("/api/documents",headers=headers(admin=True)).json()["documents"])==2
