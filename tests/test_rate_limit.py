from knowledge.limits import RateLimiter


def test_rate_window_isolated_by_subject_and_recovers():
    limit = RateLimiter(2, 10)
    assert limit.allow(("a", "u"), 0) and limit.allow(("a", "u"), 1)
    assert not limit.allow(("a", "u"), 2)
    assert limit.allow(("b", "u"), 2)
    assert limit.allow(("a", "u"), 11)
