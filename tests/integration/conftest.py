import os, uuid, pytest


@pytest.fixture
def pgstore():
    url = os.getenv("KNOWLEDGE_TEST_DATABASE")
    if not url:
        pytest.skip("Set KNOWLEDGE_TEST_DATABASE for actual PostgreSQL checks")
    import psycopg2
    from psycopg2 import sql
    from knowledge.postgres import PostgresStore

    schema = "test_" + uuid.uuid4().hex
    connection = psycopg2.connect(url)
    connection.autocommit = True
    with connection.cursor() as cur:
        cur.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    store = PostgresStore(url, schema=schema)
    try:
        yield store
    finally:
        store.close()
        with connection.cursor() as cur:
            cur.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )
        connection.close()
