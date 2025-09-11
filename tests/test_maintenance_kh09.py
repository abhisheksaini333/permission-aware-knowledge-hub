import pytest
from knowledge.evaluation import percentile, average

@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1, True])
def test_invalid_duration_observations(bad):
    with pytest.raises(ValueError): percentile([1, bad], .5)

@pytest.mark.parametrize("bad", [-.1, 1.1, True, float("nan")])
def test_invalid_percentiles(bad):
    with pytest.raises(ValueError): percentile([1, 2], bad)

def test_average_refuses_corruption():
    with pytest.raises(ValueError): average([{"score":float("nan")}], "score")
    assert average([{"score":None}], "score") is None
    assert percentile([1,2,3], 1) == 3
