from knowledge.store import Store
from knowledge.cli import seed


def test_seed_is_incremental_and_counts_actual_revisions():
    s = Store()
    items = [dict(tenant="a", source="x.md", title="X", content="hello", groups=[])]
    assert seed(s, items) == 1
    assert seed(s, items) == 0
    assert len(s.jobs("a")) == 1
