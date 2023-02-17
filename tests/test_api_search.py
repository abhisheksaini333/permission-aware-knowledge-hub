from api_support import client,headers

def test_search_controls_and_cross_tenant_isolation():
 c,s=client();r=c.get("/api/search",params={"q":"support"},headers=headers())
 assert r.status_code==200 and len(r.json()["hits"])==1
 assert r.json()["hits"][0]["tenant"]=="acme"
 assert c.get("/api/search",params={"q":"acquisition"},headers=headers()).json()["hits"]==[]
 assert c.get("/api/search",params={"q":"x","mode":"bad"},headers=headers()).status_code==422
