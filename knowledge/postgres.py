import threading
import psycopg2
from psycopg2 import sql
from .store import Store


class Connection:
    def __init__(self, url, schema):
        self.raw = psycopg2.connect(url, connect_timeout=5)
        self.raw.autocommit = True
        with self.raw.cursor() as c:
            c.execute(
                sql.SQL("SET search_path TO {},public").format(sql.Identifier(schema))
            )

    def execute(self, query, args=()):
        cursor = self.raw.cursor()
        if query == "BEGIN IMMEDIATE":
            cursor.execute("BEGIN")
            cursor.execute("SELECT pg_advisory_xact_lock(39838083)")
            return cursor
        cursor.execute(query.replace("?", "%s"), args)
        return cursor

    def executescript(self, script):
        for statement in script.split(";"):
            if statement.strip():
                self.execute(statement)

    def close(self):
        self.raw.close()


class PostgresStore(Store):
    def __init__(self, url, schema="public"):
        self.db = Connection(url, schema)
        self.lock = threading.RLock()
        self._schema()
        self.db.execute("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS vectors(id TEXT PRIMARY KEY,document_id TEXT NOT NULL,tenant TEXT NOT NULL,revision INTEGER NOT NULL,embedding vector(384) NOT NULL)"
        )

    def _remove_vectors(self, key):
        self.db.execute("DELETE FROM vectors WHERE document_id=?", (key,))

    def _index_vectors(self, doc, chunks):
        for i, c in enumerate(chunks):
            if "vector" in c:
                self.db.execute(
                    "INSERT INTO vectors VALUES(?,?,?,?,?::vector)",
                    (
                        f"{doc['id']}:{doc['revision']}:{i}",
                        doc["id"],
                        doc["tenant"],
                        doc["revision"],
                        str(c["vector"]),
                    ),
                )

    def vector_search(self, principal, vector, limit=20):
        import json
        from .retrieval import cosine

        cosine(vector, vector)
        if len(vector) != 384:
            raise ValueError("Expected a 384-dimensional MiniLM vector")
        p = self.resolve(principal)
        query = """SELECT c.body,1-(v.embedding <=> ?::vector) AS score
  FROM vectors v JOIN chunks c ON c.id=v.id JOIN documents d ON d.id=v.document_id
  WHERE v.tenant=? AND NOT (d.body::jsonb->>'deleted')::boolean
  AND v.revision=(d.body::jsonb->>'revision')::integer AND d.body::jsonb->>'status'='ready'
  AND (jsonb_array_length(d.body::jsonb->'groups')=0 OR EXISTS (
   SELECT 1 FROM jsonb_array_elements_text(d.body::jsonb->'groups') g WHERE g=ANY(?::text[])))
  ORDER BY v.embedding <=> ?::vector,v.id LIMIT ?"""
        with self.lock:
            rows = self.db.execute(
                query, (str(vector), p.tenant, list(p.groups), str(vector), limit)
            ).fetchall()
            return [(json.loads(body), float(score)) for body, score in rows]
