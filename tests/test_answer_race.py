from knowledge.identity import Principal
from knowledge.service import KnowledgeHub
from test_search import fixture


class RevokingGenerator:
    def __init__(self, store):
        self.store = store

    def generate(self, prompt):
        self.store.set_membership("acme", "u", [], ["reader"])
        return "forty million"


def test_revocation_during_generation_discards_answer():
    s = fixture()
    p = Principal("u", "acme", frozenset({"finance"}), frozenset({"reader"}))
    answer = KnowledgeHub(s, generator=RevokingGenerator(s)).ask(
        p, "What is the acquisition price?"
    )
    assert answer["abstained"] and answer["citations"] == []
