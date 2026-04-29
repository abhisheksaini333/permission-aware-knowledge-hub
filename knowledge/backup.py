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
    db = sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Backup integrity failed")
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise ValueError("Restore destination must be empty") from exc
        os.close(descriptor)
        try:
            destination = sqlite3.connect(str(target))
            try:
                db.backup(destination)
            finally:
                destination.close()
        except BaseException:
            target.unlink(missing_ok=True)
            raise
    finally:
        db.close()
