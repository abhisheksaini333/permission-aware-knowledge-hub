from knowledge.answers import supported
from knowledge.service import KnowledgeHub
from test_search import fixture
from knowledge.identity import Principal


class Generator:
    def generate(self, prompt):
        return "nine to five"


def test_supported_answer_and_missing_evidence():
    h = KnowledgeHub(fixture(), generator=Generator())
    p = Principal("u", "acme", frozenset(), frozenset({"reader"}))
    a = h.ask(p, "What are the support hours?")
    assert not a["abstained"] and a["answer"] == "nine to five" and a["citations"]
    assert h.ask(p, "What is the acquisition price?")["abstained"]


def test_hallucinated_fact_and_unknown_are_rejected():
    assert not supported("UNKNOWN", [dict(text="Support ends at five")])
    assert not supported("elephants live on Mars", [dict(text="Support ends at five")])
    assert supported("seven days", [dict(text="Retention is seven days")])
