from scripts.vector_index import configure


class RecordingStore:
    def __init__(self):
        self.calls = []

    def upgrade_vector_extension(self):
        self.calls.append("upgrade")

    def configure_vector_index(self, strategy):
        self.calls.append(strategy)
        return strategy


def test_upgrade_is_explicit_and_precedes_index_creation():
    store = RecordingStore()
    assert configure(store, "hnsw") == "hnsw"
    assert store.calls == ["hnsw"]
    store.calls.clear()
    assert configure(store, "hnsw", upgrade=True) == "hnsw"
    assert store.calls == ["upgrade", "hnsw"]
