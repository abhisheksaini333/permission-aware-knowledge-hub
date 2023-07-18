from api_support import client, headers


def test_file_upload_format_and_reader_restrictions():
    c, s = client()
    r = c.post(
        "/api/upload",
        files={"file": ("guide.md", b"# Company guide", "text/markdown")},
        data={"groups": "staff,engineering"},
        headers=headers(admin=True),
    )
    assert r.status_code == 201 and r.json()["groups"] == ["engineering", "staff"]
    assert (
        c.post(
            "/api/upload",
            files={"file": ("bad.exe", b"binary")},
            headers=headers(admin=True),
        ).status_code
        == 422
    )
    assert (
        c.post(
            "/api/upload", files={"file": ("guide.md", b"hello")}, headers=headers()
        ).status_code
        == 403
    )
