from knowledge.answers import build_prompt, citations


def test_prompt_includes_question_and_cited_evidence_with_budget():
    hits = [
        dict(
            id="a",
            document_id="d",
            revision=2,
            page=3,
            start=10,
            end=30,
            text="Policy allows seven days",
            title="Policy",
            source="policy.md",
        )
    ]
    prompt, used = build_prompt("How long?", hits, budget=1000)
    assert "How long?" in prompt and "[1] Policy allows seven days" in prompt
    assert (
        citations(used)[0]["url"]
        == "/api/documents/d/revisions/2?page=3&start=10&end=30"
    )
    import pytest
    with pytest.raises(ValueError, match="budget"):
        build_prompt("Q", hits, budget=10)
