from api_support import client,headers

def test_reindex_endpoint_honors_admin_and_tenant():
 c,s=client();d=s.documents("acme")[0];url=f"/api/documents/{d['id']}/reindex"
 assert c.post(url,headers=headers()).status_code==403
 assert c.post(url,headers=headers("beta",admin=True)).status_code==404
 assert c.post(url,headers=headers(admin=True)).status_code==202
 assert s.document(d["id"])["status"]=="pending"
