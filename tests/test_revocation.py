from knowledge.store import Store
from knowledge.identity import Principal

def test_server_revocation_overrides_stale_token_groups():
 s=Store();p=Principal("u","a",frozenset({"finance"}),frozenset({"reader"}))
 assert s.resolve(p)==p
 s.set_membership("a","u",[],["reader"])
 assert s.resolve(p).groups==frozenset()
 assert s.resolve(Principal("u","b",frozenset({"finance"}),frozenset())).groups==frozenset({"finance"})
