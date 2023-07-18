from knowledge.retrieval import rerank


def test_reranking_uses_coverage_without_inventing_new_candidates():
    a = dict(id="a", text="backup noise noise")
    b = dict(id="b", text="backup retention is seven days")
    out = rerank("backup retention", [(a, 10), (b, 1)])
    assert out[0][0]["id"] == "b" and len(out) == 2
