import sqlite3,json,threading,time
from contextlib import contextmanager
from pathlib import Path
from .content import document_key,content_digest

class Store:
 def __init__(self,path=":memory:"):
  if path!=":memory:":Path(path).parent.mkdir(parents=True,exist_ok=True)
  self.db=sqlite3.connect(path,check_same_thread=False,isolation_level=None)
  self.db.row_factory=sqlite3.Row;self.lock=threading.RLock()
  self.db.execute("PRAGMA foreign_keys=ON")
  self.db.execute("PRAGMA journal_mode=WAL")
  self.db.executescript("""
  CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY,tenant TEXT NOT NULL,body TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS revisions(document_id TEXT,revision INTEGER,body TEXT NOT NULL,PRIMARY KEY(document_id,revision));
  """)
 @contextmanager
 def transaction(self):
  with self.lock:
   self.db.execute("BEGIN IMMEDIATE")
   try:yield;self.db.execute("COMMIT")
   except BaseException:self.db.execute("ROLLBACK");raise
 def close(self):self.db.close()
 def document(self,key):
  with self.lock:
   row=self.db.execute("SELECT body FROM documents WHERE id=?",(key,)).fetchone()
   return json.loads(row[0]) if row else None
 def revision(self,key,revision):
  with self.lock:
   row=self.db.execute("SELECT body FROM revisions WHERE document_id=? AND revision=?",(key,revision)).fetchone()
   return json.loads(row[0]) if row else None
 def _save(self,doc):
  self.db.execute("INSERT INTO documents(id,tenant,body) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body",(doc["id"],doc["tenant"],json.dumps(doc)))
 def ingest(self,tenant,source,title,content,groups):
  key=document_key(tenant,source)
  with self.transaction():
   old=self.document(key)
   if old and not old["deleted"] and all(old[k]==v for k,v in dict(title=title,content=content,groups=sorted(set(groups))).items()):return old
   revision=old["revision"]+1 if old else 1
   doc=dict(id=key,tenant=tenant,source=source,title=title,content=content,groups=sorted(set(groups)),revision=revision,digest=content_digest(content),deleted=False,status="pending")
   self._save(doc)
   self.db.execute("INSERT INTO revisions VALUES(?,?,?)",(key,revision,json.dumps(doc)))
  return doc
