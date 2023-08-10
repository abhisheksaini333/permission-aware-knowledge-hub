import pytest
from knowledge.identity import Principal

def test_index_strategy_can_be_enabled_and_reverted(pgstore):
 s=pgstore
 assert s.configure_vector_index("ivfflat")=="ivfflat"
 assert s.db.execute("SELECT count(*) FROM pg_indexes WHERE schemaname=current_schema() AND indexname='knowledge_vector_ivfflat'").fetchone()[0]==1
 assert s.configure_vector_index("exact")=="exact"
 assert s.db.execute("SELECT count(*) FROM pg_indexes WHERE schemaname=current_schema() AND indexname='knowledge_vector_ivfflat'").fetchone()[0]==0
 with pytest.raises(ValueError):s.configure_vector_index("unsafe sql")

def test_database_adapter_denies_application_role_revocation_directly(pgstore):
 s=pgstore;p=Principal("u","a",frozenset(),frozenset())
 assert s.vector_search(p,[1.]+[0.]*383)==[]
