from api_support import client,headers

def test_membership_revocation_takes_effect_with_old_signed_token():
 c,s=client();h=headers(groups=["finance"])
 assert c.get("/api/search?q=acquisition",headers=h).json()["hits"]
 body=dict(groups=[],roles=["reader"])
 assert c.put("/api/memberships/reader",json=body,headers=h).status_code==403
 assert c.put("/api/memberships/reader",json=body,headers=headers(admin=True)).status_code==200
 assert c.get("/api/search?q=acquisition",headers=h).json()["hits"]==[]
