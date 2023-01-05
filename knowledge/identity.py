from dataclasses import dataclass

@dataclass(frozen=True)
class Principal:
 subject: str
 tenant: str
 groups: frozenset[str]
 roles: frozenset[str]
 @property
 def is_admin(self):return "admin" in self.roles

def allowed(principal,tenant,groups):
 return principal.tenant == tenant and (not groups or bool(principal.groups.intersection(groups)))
