import pytest
from knowledge.retrieval import dense, cosine


def test_dense_ranking_and_invalid_vectors():
    c = [dict(id="a", vector=[1, 0]), dict(id="b", vector=[0, 1])]
    assert dense([0.9, 0.1], c)[0][0]["id"] == "a"
    assert cosine([0, 0], [1, 2]) == 0
    with pytest.raises(ValueError):
        cosine([1], [1, 2])
    with pytest.raises(ValueError):
        cosine([float("nan")], [1])
