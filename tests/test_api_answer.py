from api_support import client, headers


class Broken:
    def generate(self, prompt):
        raise RuntimeError("private provider failure")


def test_unavailable_model_and_validation_are_clear():
    c, s = client()
    r = c.post("/api/ask", json={"question": "support"}, headers=headers())
    assert r.status_code == 200 and r.json()["abstained"]
    assert (
        c.post("/api/ask", json={"question": ""}, headers=headers()).status_code == 422
    )
    c, s = client(Broken())
    r = c.post("/api/ask", json={"question": "support"}, headers=headers())
    assert r.status_code == 503 and "private" not in r.text
