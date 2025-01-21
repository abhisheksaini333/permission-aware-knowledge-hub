import math
import pytest
from knowledge.retrieval import cosine

@pytest.mark.parametrize("scale", [1e200, 1e-200])
def test_stable_cosine(scale):
    assert cosine([scale, scale], [scale, scale]) == pytest.approx(1)
    assert cosine([scale, scale], [-scale, -scale]) == pytest.approx(-1)
    assert cosine([0, 0], [scale, scale]) == 0

@pytest.mark.parametrize("bad", [True, "x", None, float("nan")])
def test_bad_embedding_element(bad):
    with pytest.raises(ValueError): cosine([bad], [1])
