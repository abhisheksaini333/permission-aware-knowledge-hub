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
        if not {"reader", "admin"}.intersection(p.roles):
            return []
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

    def vector_version(self):
        return self.db.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()[0]

    def upgrade_vector_extension(self):
        """Explicit maintenance operation; install the upgrade image and back up first."""
        with self.transaction():
            version = self.vector_version()
            if version == "0.5.0":
                return version
            if version != "0.4.0":
                raise ValueError("Only the verified pgvector 0.4.0 to 0.5.0 upgrade is supported")
            self.db.execute("ALTER EXTENSION vector UPDATE TO '0.5.0'")
            return self.vector_version()

    def configure_vector_index(self, strategy):
        if strategy not in {"exact", "ivfflat", "hnsw"}:
            raise ValueError("Use exact, ivfflat or hnsw")
        with self.transaction():
            if strategy == "hnsw" and tuple(int(part) for part in self.vector_version().split(".")) < (0, 5, 0):
                raise ValueError("HNSW requires pgvector 0.5.0 or later; upgrade explicitly first")
            self.db.execute("DROP INDEX IF EXISTS knowledge_vector_ivfflat")
            self.db.execute("DROP INDEX IF EXISTS knowledge_vector_hnsw")
            if strategy == "ivfflat":
                self.db.execute("CREATE INDEX knowledge_vector_ivfflat ON vectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10)")
            elif strategy == "hnsw":
                self.db.execute("CREATE INDEX knowledge_vector_hnsw ON vectors USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)")
            self.db.execute("ANALYZE vectors")
        return strategy
