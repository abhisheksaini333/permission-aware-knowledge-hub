import os
import sqlite3
import pytest
from knowledge.store import Store
from knowledge.backup import backup_sqlite

def test_backup_private_before_connect(tmp_path, monkeypatch):
    store=Store(str(tmp_path/"live.db")); target=tmp_path/"backup.db"
    connect=sqlite3.connect
    def checked(path, *a, **k):
        assert target.exists()
        assert target.stat().st_mode & 0o777 == 0o600
        return connect(path, *a, **k)
    monkeypatch.setattr(sqlite3, "connect", checked)
    try: backup_sqlite(store, target)
    finally: store.close()

def test_failed_backup_removes_partial(tmp_path, monkeypatch):
    store=Store(str(tmp_path/"live.db")); target=tmp_path/"backup.db"
    def fail(*a, **k): raise RuntimeError("unavailable")
    monkeypatch.setattr(sqlite3, "connect", fail)
    try:
        with pytest.raises(RuntimeError): backup_sqlite(store,target)
        assert not target.exists()
    finally: store.close()
