from api_support import client, headers


def test_security_headers_and_request_limits():
    c, s = client()
    r = c.get("/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    h = headers()
    responses = [c.get("/api/me", headers=h) for i in range(121)]
    assert (
        responses[-1].status_code == 429
        and responses[-1].headers["retry-after"] == "60"
    )
