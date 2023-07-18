from pathlib import Path
from fastapi.testclient import TestClient
from knowledge.runtime import mount_frontend
from api_support import client


def test_frontend_mount_keeps_api_routes_and_renders_html(tmp_path):
    (tmp_path / "index.html").write_text("<h1>Knowledge Hub</h1>")
    c, s = client()
    mount_frontend(c.app, tmp_path)
    assert c.get("/").status_code == 200 and "Knowledge Hub" in c.get("/").text
    assert c.get("/health").json()["status"] == "ok"
