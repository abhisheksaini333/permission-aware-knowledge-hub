from knowledge.store import Store
from knowledge.backup import backup_sqlite, restore_sqlite
import pytest


def test_restore_preserves_revisions_and_memberships(tmp_path):
    path = tmp_path / "live.db"
    s = Store(str(path))
    d = s.ingest("a", "x", "X", "hello", [])
    s.set_membership("a", "u", [], ["reader"])
    archive = tmp_path / "backup.db"
    backup_sqlite(s, archive)
    s.close()
    target = tmp_path / "restored.db"
    restore_sqlite(archive, target)
    r = Store(str(target))
    assert r.document(d["id"])["content"] == "hello"
    r.close()
    with pytest.raises(ValueError):
        restore_sqlite(archive, target)
