from knowledge.store import Store
from knowledge.worker import IndexWorker
from knowledge.identity import Principal
from knowledge.service import KnowledgeHub


class Revoker:
    def __init__(self, s):
        self.s = s

    def generate(self, prompt):
        self.s.set_membership("a", "u", [], [])
        return "seven days"


def test_role_revoked_during_generation_blocks_public_document_answer():
    s = Store()
    s.ingest("a", "x", "X", "Backup retention is seven days", [])
    IndexWorker(s).once()
    p = Principal("u", "a", frozenset(), frozenset({"reader"}))
    hub = KnowledgeHub(s, generator=Revoker(s))
    a = hub.ask(p, "backup retention")
    assert a["abstained"] and not a["citations"]
    assert hub.search(p, "backup") == []
