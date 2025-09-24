import pytest
from knowledge.limits import RateLimiter

@pytest.mark.parametrize("args", [(True,60),(0,60),(1.5,60),(1,float("nan")),(1,float("inf")),(1,-1)])
def test_invalid_limit_configuration(args):
    with pytest.raises(ValueError): RateLimiter(*args)

def test_invalid_clock_does_not_consume_quota():
    limiter=RateLimiter(1, 10)
    with pytest.raises(ValueError): limiter.allow("u", float("nan"))
    assert limiter.allow("u", 0)
    assert limiter.allow("u", 10)
