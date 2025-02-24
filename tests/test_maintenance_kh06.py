import pytest
from knowledge.retrieval import fuse

@pytest.mark.parametrize("bad", [-1, True, float("nan"), float("inf"), "60"])
def test_invalid_fusion_constant(bad):
    with pytest.raises(ValueError): fuse([({"id": "a"}, 1)], k=bad)

def test_zero_fusion_constant():
    assert fuse([({"id":"a"},1)], k=0)[0][1] == 1
