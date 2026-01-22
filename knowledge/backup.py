import sqlite3, shutil, os
from pathlib import Path


def backup_sqlite(store, target):
    if not isinstance(store.db, sqlite3.Connection):
        raise ValueError("Use pg_dump for PostgreSQL")
    target = Path(target)
    if target.exists():
        raise ValueError("Backup destination already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError("Backup destination already exists") from exc
    os.close(descriptor)
    try:
        with store.lock:
            destination = sqlite3.connect(str(target))
            try:
                store.db.backup(destination)
            finally:
                destination.close()
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def restore_sqlite(source, target):
    source = Path(source)
    target = Path(target)
    if target.exists():
        raise ValueError("Restore destination must be empty")
    with sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True) as db:
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Backup integrity failed")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    target.chmod(0o600)
