import sqlite3
from knowledge.backup import restore_sqlite

def test_restore_uri_special_filename(tmp_path):
    source=tmp_path/"archive?#.db"
    with sqlite3.connect(source) as db: db.execute("CREATE TABLE records(value TEXT)")
    target=tmp_path/"restored.db"
    restore_sqlite(source,target)
    with sqlite3.connect(target) as db: assert db.execute("SELECT count(*) FROM records").fetchone()[0] == 0
    assert target.stat().st_mode & 0o777 == 0o600

def test_special_source_cannot_bypass_integrity_check(tmp_path):
    import pytest
    source=tmp_path/'invalid?#.db'
    source.write_bytes(b'not a SQLite database')
    target=tmp_path/'restored.db'
    with pytest.raises((ValueError, sqlite3.DatabaseError)):
        restore_sqlite(source, target)
    assert not target.exists()
