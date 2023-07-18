from api_support import client, headers


def test_citation_lookup_hides_forbidden_and_deleted_revisions():
    c, s = client()
    d = [d for d in s.documents("acme") if d["groups"]][0]
    url = f"/api/documents/{d['id']}/revisions/1"
    assert c.get(url, headers=headers()).status_code == 404
    assert c.get(url, headers=headers(groups=["finance"])).status_code == 200
    assert c.get(url, headers=headers("beta", groups=["finance"])).status_code == 404
    s.delete(d["id"], "acme")
    assert c.get(url, headers=headers(groups=["finance"])).status_code == 404
