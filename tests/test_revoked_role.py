from api_support import client,headers

def test_removing_all_roles_disables_old_token_access():
 c,s=client();s.set_membership("acme","reader",[],[])
 assert c.get("/api/me",headers=headers()).status_code==403
 assert c.get("/api/search?q=support",headers=headers()).status_code==403
