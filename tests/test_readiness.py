from api_support import client


def test_readiness_checks_storage_without_disclosing_connection_details():
    c, s = client()
    assert c.get("/ready").status_code == 200
    s.close()
    r = c.get("/ready")
    assert r.status_code == 503 and "sqlite" not in r.text.lower()
