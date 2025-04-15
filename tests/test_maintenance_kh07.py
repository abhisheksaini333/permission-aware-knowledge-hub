import pytest
from knowledge.models import generation_limits

@pytest.mark.parametrize("bad", [True, 1.5, "3", 0, 129])
def test_strict_generation_budget(bad):
    with pytest.raises(ValueError): generation_limits(bad)

def test_generation_boundaries():
    assert generation_limits(1)["max_new_tokens"] == 1
    assert generation_limits(128)["max_new_tokens"] == 128
