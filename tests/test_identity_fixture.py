import pytest
from knowledge.demo_identity import realm

def test_demo_has_three_tenants_reader_admin_and_pkce_only_client():
 r=realm("a-strong-demo-password")
 assert {u["attributes"]["tenant"][0] for u in r["users"]}=={"acme","beta","cobalt"}
 assert len(r["users"])==6
 client=r["clients"][0]
 assert client["publicClient"] and not client["directAccessGrantsEnabled"]
 assert client["attributes"]["pkce.code.challenge.method"]=="S256"
 assert all({"reader","admin"}.intersection(u["realmRoles"]) for u in r["users"])
 with pytest.raises(ValueError):realm("short")
