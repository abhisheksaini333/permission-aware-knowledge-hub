import sqlite3,shutil
from pathlib import Path

def backup_sqlite(store,target):
 if not isinstance(store.db,sqlite3.Connection):raise ValueError("Use pg_dump for PostgreSQL")
 target=Path(target)
 if target.exists():raise ValueError("Backup destination already exists")
 target.parent.mkdir(parents=True,exist_ok=True)
 with store.lock,sqlite3.connect(str(target)) as destination:store.db.backup(destination)
 target.chmod(0o600)

def restore_sqlite(source,target):
 source=Path(source);target=Path(target)
 if target.exists():raise ValueError("Restore destination must be empty")
 with sqlite3.connect(f"file:{source.resolve()}?mode=ro",uri=True) as db:
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise ValueError("Backup integrity failed")
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);target.chmod(0o600)
