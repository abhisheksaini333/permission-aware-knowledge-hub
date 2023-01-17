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
  CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,tenant TEXT NOT NULL,body TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS chunks(id TEXT PRIMARY KEY,document_id TEXT NOT NULL,tenant TEXT NOT NULL,body TEXT NOT NULL);
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
   job=dict(id=f"{key}:{revision}",document_id=key,tenant=tenant,revision=revision,status="pending",attempts=0,available_at=0,lease_until=0,owner=None,error=None)
   self.db.execute("INSERT INTO jobs VALUES(?,?,?)",(job["id"],tenant,json.dumps(job)))
   self.db.execute("INSERT INTO revisions VALUES(?,?,?)",(key,revision,json.dumps(doc)))
  return doc

 def documents(self,tenant):
  with self.lock:
   return [json.loads(r[0]) for r in self.db.execute("SELECT body FROM documents WHERE tenant=? ORDER BY id",(tenant,)).fetchall()]

 def index(self,key,revision,chunks):
  with self.transaction():
   doc=self.document(key)
   if not doc or doc["deleted"] or doc["revision"]!=revision:return False
   self.db.execute("DELETE FROM chunks WHERE document_id=?",(key,))
   for i,chunk in enumerate(chunks):
    c=dict(chunk,id=f"{key}:{revision}:{i}",document_id=key,revision=revision,tenant=doc["tenant"])
    self.db.execute("INSERT INTO chunks VALUES(?,?,?,?)",(c["id"],key,doc["tenant"],json.dumps(c)))
   doc["status"]="ready";self._save(doc)
  return True
 def chunks(self,tenant):
  with self.lock:
   chunks=[json.loads(r[0]) for r in self.db.execute("SELECT body FROM chunks WHERE tenant=? ORDER BY id",(tenant,))]
   return [c for c in chunks if (d:=self.document(c["document_id"])) and not d["deleted"] and d["revision"]==c["revision"] and d["status"]=="ready"]

 def delete(self,key,tenant):
  with self.transaction():
   doc=self.document(key)
   if not doc or doc["tenant"]!=tenant:return False
   if doc["deleted"]:return True
   doc.update(deleted=True,status="deleted",content="",revision=doc["revision"]+1)
   self._save(doc);self.db.execute("DELETE FROM chunks WHERE document_id=?",(key,))
  return True

 def jobs(self,tenant):
  with self.lock:return [json.loads(r[0]) for r in self.db.execute("SELECT body FROM jobs WHERE tenant=? ORDER BY id",(tenant,))]
 def _save_job(self,job):self.db.execute("UPDATE jobs SET body=? WHERE id=?",(json.dumps(job),job["id"]))

 def claim(self,owner,now=None,lease_seconds=60):
  now=time.time() if now is None else now
  with self.transaction():
   for row in self.db.execute("SELECT body FROM jobs ORDER BY id").fetchall():
    j=json.loads(row[0])
    if (j["status"]=="pending" and j["available_at"]<=now) or (j["status"]=="running" and j["lease_until"]<=now):
     j.update(status="running",owner=owner,attempts=j["attempts"]+1,lease_until=now+lease_seconds)
     self._save_job(j);return j
  return None
