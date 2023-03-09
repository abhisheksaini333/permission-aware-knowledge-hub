import threading
import psycopg2
from psycopg2 import sql
from .store import Store

class Connection:
 def __init__(self,url,schema):
  self.raw=psycopg2.connect(url,connect_timeout=5);self.raw.autocommit=True
  with self.raw.cursor() as c:c.execute(sql.SQL("SET search_path TO {},public").format(sql.Identifier(schema)))
 def execute(self,query,args=()):
  cursor=self.raw.cursor()
  if query=="BEGIN IMMEDIATE":
   cursor.execute("BEGIN");cursor.execute("SELECT pg_advisory_xact_lock(39838083)");return cursor
  cursor.execute(query.replace("?","%s"),args);return cursor
 def executescript(self,script):
  for statement in script.split(";"):
   if statement.strip():self.execute(statement)
 def close(self):self.raw.close()

class PostgresStore(Store):
 def __init__(self,url,schema="public"):
  self.db=Connection(url,schema);self.lock=threading.RLock();self._schema()
