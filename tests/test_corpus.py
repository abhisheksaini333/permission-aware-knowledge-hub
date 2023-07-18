import json
from pathlib import Path


def test_owned_corpus_has_three_tenants_distinct_roles_and_labels():
    d = json.loads(Path("fixtures/corpus.json").read_text())
    assert {x["tenant"] for x in d["documents"]} == {"acme", "beta", "cobalt"}
    assert {q["role"] for q in d["questions"]} == {"reader", "admin"}
    for q in d["questions"]:
        if q["source"]:
            assert any(
                x["source"] == q["source"] and x["tenant"] == q["tenant"]
                for x in d["documents"]
            )
    assert any(q["answer"] is None for q in d["questions"])
