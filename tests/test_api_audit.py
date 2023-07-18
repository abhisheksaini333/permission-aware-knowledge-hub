from api_support import client, headers


def test_administrative_events_omit_sensitive_payloads():
    c, s = client()
    c.put(
        "/api/memberships/reader",
        json={"groups": [], "roles": ["reader"]},
        headers=headers(admin=True),
    )
    assert c.get("/api/audit", headers=headers()).status_code == 403
    events = c.get("/api/audit", headers=headers(admin=True)).json()["events"]
    assert (
        events[0]["action"] == "membership.changed"
        and "token" not in str(events).lower()
    )
