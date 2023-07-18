from api_support import client, headers


def test_feedback_records_subject_from_token_only():
    c, s = client()
    body = dict(question="support hours", rating="helpful", comment="Useful")
    r = c.post("/api/feedback", json=body, headers=headers())
    assert r.status_code == 201
    record = s.feedback_records("acme")[0]
    assert record["subject"] == "reader" and record["question_hash"] != "support hours"
    assert (
        c.post(
            "/api/feedback", json={**body, "rating": "bad"}, headers=headers()
        ).status_code
        == 422
    )
