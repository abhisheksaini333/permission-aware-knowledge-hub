from knowledge.answers import supporting_hits
from knowledge.service import KnowledgeHub
from knowledge.identity import Principal
from test_search import fixture


def test_irrelevant_retrieved_passages_are_not_labeled_supporting_sources():
    hits = [
        dict(text="Retention is seven days"),
        dict(text="Support hours are nine to five"),
    ]
    assert supporting_hits("seven days", hits) == [hits[0]]
    assert supporting_hits("seven five", hits) == []
