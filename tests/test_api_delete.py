from api_support import client,headers

def test_admin_cannot_delete_another_tenant_document():
 c,s=client();d=s.documents("acme")[0];url=f"/api/documents/{d['id']}"
 assert c.delete(url,headers=headers()).status_code==403
 assert c.delete(url,headers=headers("beta",admin=True)).status_code==404
 assert c.delete(url,headers=headers(admin=True)).status_code==204
 assert c.delete(url,headers=headers(admin=True)).status_code==204
