from api_support import client,headers

def test_index_health_is_admin_only_and_excludes_other_tenants():
 c,s=client();assert c.get("/api/index-health",headers=headers()).status_code==403
 r=c.get("/api/index-health",headers=headers(admin=True)).json()
 assert r["documents"]==2 and r["ready"]==2 and r["failed_jobs"]==0
