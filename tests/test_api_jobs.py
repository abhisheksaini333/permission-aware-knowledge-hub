from api_support import client,headers

def test_only_admin_can_view_own_indexing_jobs():
 c,s=client()
 assert c.get("/api/jobs",headers=headers()).status_code==403
 jobs=c.get("/api/jobs",headers=headers(admin=True)).json()["jobs"]
 assert len(jobs)==2 and all(j["tenant"]=="acme" for j in jobs)
