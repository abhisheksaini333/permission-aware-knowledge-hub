import math
import os
import uuid
import pytest
from knowledge.chunks import chunk_text
from knowledge.identity import Principal


@pytest.fixture
def upgrade_store():
    url = os.getenv("KNOWLEDGE_HNSW_TEST_DATABASE")
    if not url:
        pytest.skip("Set KNOWLEDGE_HNSW_TEST_DATABASE to a pgvector 0.5 image")
    import psycopg2
    from psycopg2 import sql
    from knowledge.postgres import PostgresStore
    database = "upgrade_" + uuid.uuid4().hex
    connection = psycopg2.connect(url)
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
    options = psycopg2.extensions.parse_dsn(url)
    options["dbname"] = database
    target = psycopg2.extensions.make_dsn(**options)
    prepared = psycopg2.connect(target)
    prepared.autocommit = True
    with prepared.cursor() as cursor:
        cursor.execute("CREATE EXTENSION vector WITH SCHEMA public VERSION '0.4.0'")
    prepared.close()
    store = PostgresStore(target)
    try:
        yield store
    finally:
        store.close()
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database)))
        connection.close()


def test_upgrade_preserves_data_and_hnsw_respects_authorization(upgrade_store):
    store = upgrade_store
    for i in range(120):
        tenant = ("a", "b", "c")[i % 3]
        groups = ["secret"] if i % 2 else []
        document = store.ingest(tenant, str(i), "Document", "evidence " + str(i), groups)
        chunks = chunk_text(document["content"])
        angle = i / 120.0
        chunks[0]["vector"] = [math.cos(angle), math.sin(angle)] + [0.0] * 382
        store.index(document["id"], 1, chunks)
    principal = Principal("reader", "a", frozenset(), frozenset({"reader"}))
    vector = [math.cos(.27), math.sin(.27)] + [0.0] * 382
    exact = store.vector_search(principal, vector, 10)
    assert store.vector_version() == "0.4.0"
    assert store.upgrade_vector_extension() == "0.5.0"
    assert store.upgrade_vector_extension() == "0.5.0"
    assert store.configure_vector_index("hnsw") == "hnsw"
    store.db.execute("SET hnsw.ef_search=200")
    actual = store.vector_search(principal, vector, 10)
    assert [hit[0]["id"] for hit in actual] == [hit[0]["id"] for hit in exact]
    assert len(actual) == 10 and all(hit[0]["tenant"] == "a" for hit in actual)
    assert all(not store.document(hit[0]["document_id"])["groups"] for hit in actual)
    store.db.execute("SET enable_seqscan=off")
    plan = store.db.execute("EXPLAIN SELECT id FROM vectors ORDER BY embedding <=> ?::vector LIMIT 5", (str(vector),)).fetchall()
    assert "knowledge_vector_hnsw" in " ".join(row[0] for row in plan)
    assert store.configure_vector_index("exact") == "exact"
    assert store.db.execute("SELECT count(*) FROM pg_indexes WHERE indexname='knowledge_vector_hnsw'").fetchone()[0] == 0


def test_hnsw_rejects_old_extension_before_changing_index(pgstore):
    store = pgstore
    store.configure_vector_index("ivfflat")
    with pytest.raises(ValueError, match="0.5.0"):
        store.configure_vector_index("hnsw")
    assert store.db.execute("SELECT count(*) FROM pg_indexes WHERE schemaname=current_schema() AND indexname='knowledge_vector_ivfflat'").fetchone()[0] == 1
