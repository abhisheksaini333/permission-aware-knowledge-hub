import pytest
from knowledge.api import DocumentRequest, MembershipRequest, FeedbackRequest

@pytest.mark.parametrize("field", ["source", "title"])
def test_nonblank_document_labels(field):
    body = dict(source="s", title="t", content="c", groups=[])
    body[field] = "  "
    with pytest.raises(ValueError): DocumentRequest(**body)

def test_exact_roles_ratings_and_groups():
    with pytest.raises(ValueError): MembershipRequest(groups=[], roles=["reader\n"])
    with pytest.raises(ValueError): MembershipRequest(groups=[" "], roles=["reader"])
    with pytest.raises(ValueError): FeedbackRequest(question="q", rating="helpful\n")
    assert MembershipRequest(groups=["team"], roles=["reader"]).roles == ["reader"]
