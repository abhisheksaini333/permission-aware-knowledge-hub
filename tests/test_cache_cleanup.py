from knowledge.store import Store


def test_cache_cleanup_keeps_current_answers_only():
    s = Store()
    s.cache_put("a", "old", {}, now=0, ttl=5)
    s.cache_put("a", "new", {}, now=10, ttl=5)
    assert s.prune_cache(now=10) == 1
    assert s.cache_get("a", "new", now=11) == {}
