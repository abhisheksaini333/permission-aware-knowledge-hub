from api_support import client, headers


def test_acl_change_revisions_document_and_immediately_hides_old_chunks():
    c, s = client()
    d = [d for d in s.documents("acme") if not d["groups"]][0]
    r = c.put(
        f"/api/documents/{d['id']}/access",
        json={"groups": ["finance"]},
        headers=headers(admin=True),
    )
    assert r.status_code == 200 and r.json()["revision"] == 2
    assert c.get("/api/search?q=support", headers=headers()).json()["hits"] == []
    assert (
        c.put(
            f"/api/documents/{d['id']}/access",
            json={"groups": []},
            headers=headers("beta", admin=True),
        ).status_code
        == 404
    )
