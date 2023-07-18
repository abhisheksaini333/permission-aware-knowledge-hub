import pytest
from knowledge.identity import Principal, allowed


def test_same_tenant_group_intersection_only():
    p = Principal("reader", "acme", frozenset({"engineering"}), frozenset({"reader"}))
    assert allowed(p, "acme", ["engineering"])
    assert not allowed(p, "beta", ["engineering"])
    assert not allowed(p, "acme", ["finance"])
    assert allowed(p, "acme", [])


def test_administrator_does_not_bypass_document_groups():
    p = Principal("admin", "acme", frozenset(), frozenset({"admin"}))
    assert p.is_admin
    assert not allowed(p, "acme", ["finance"])
