import pytest
from knowledge.api import DocumentRequest, AccessRequest

def test_acl_typos_fail_closed():
    with pytest.raises(ValueError): DocumentRequest(source="s", title="t", content="c", group=["private"])
    with pytest.raises(ValueError): AccessRequest(groups=[], group=["private"])
    assert DocumentRequest(source="s", title="t", content="c", groups=["private"]).groups == ["private"]
