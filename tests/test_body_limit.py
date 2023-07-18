from api_support import client, headers


def test_declared_oversize_and_actual_chunked_body_are_rejected():
    c, s = client()
    r = c.post(
        "/api/documents",
        content=b"{}",
        headers={
            **headers(admin=True),
            "Content-Type": "application/json",
            "Content-Length": "3000000",
        },
    )
    assert r.status_code == 413
    r = c.post(
        "/api/documents",
        content=b"x" * 2100001,
        headers={**headers(admin=True), "Content-Type": "application/json"},
    )
    assert r.status_code == 413
