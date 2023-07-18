from knowledge.store import Store


def test_cache_expires_and_is_tenant_scoped():
    s = Store()
    s.cache_put("a", "key", {"answer": "hello"}, now=10, ttl=5)
    assert s.cache_get("a", "key", now=12)["answer"] == "hello"
    assert s.cache_get("b", "key", now=12) is None
    assert s.cache_get("a", "key", now=15) is None
