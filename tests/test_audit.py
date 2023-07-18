from knowledge.store import Store


def test_audit_records_are_tenant_scoped_and_ordered():
    s = Store()
    s.audit("a", "user", "document.deleted", {"document_id": "d"})
    s.audit("b", "other", "membership.changed", {"subject": "x"})
    events = s.audit_events("a")
    assert len(events) == 1 and events[0]["action"] == "document.deleted"
    assert events[0]["details"] == {"document_id": "d"}
