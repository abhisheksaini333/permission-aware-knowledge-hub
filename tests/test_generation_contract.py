import pytest
from knowledge.models import generation_limits


def test_generation_budget_cannot_expand_without_bound():
    assert generation_limits(32) == dict(
        max_new_tokens=32, do_sample=False, num_beams=1
    )
    for n in [0, 129, -1]:
        with pytest.raises(ValueError):
            generation_limits(n)
