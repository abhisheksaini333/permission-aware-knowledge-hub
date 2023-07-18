from api_support import client, headers


def test_only_admin_ingests_and_upload_is_tenant_bound():
    c, s = client()
    body = dict(
        source="guide.md",
        title="Guide",
        content="Database backups last seven days",
        groups=["staff"],
    )
    assert c.post("/api/documents", json=body, headers=headers()).status_code == 403
    r = c.post("/api/documents", json=body, headers=headers(admin=True))
    assert r.status_code == 201
    assert r.json()["tenant"] == "acme" and r.json()["status"] == "pending"
    assert (
        c.post(
            "/api/documents", json={**body, "content": ""}, headers=headers(admin=True)
        ).status_code
        == 422
    )
