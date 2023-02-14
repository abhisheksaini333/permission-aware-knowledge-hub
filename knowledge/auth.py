import jwt
from .identity import Principal

class AuthError(ValueError):pass

def decode_token(token,key,issuer,audience):
 try:
  c=jwt.decode(token,key,algorithms=["RS256"],issuer=issuer,audience=audience,options={"require":["exp","iat","sub","iss","aud","tenant"]})
  tenant=c["tenant"];subject=c["sub"];groups=c.get("groups",[]);roles=c.get("realm_access",{}).get("roles",[])
  if not isinstance(tenant,str) or not tenant or len(tenant)>80 or not isinstance(subject,str) or not subject:raise ValueError("Invalid identity")
  if not isinstance(groups,list) or not all(isinstance(x,str) for x in groups):raise ValueError("Invalid groups")
  if not isinstance(roles,list) or not {"reader","admin"}.intersection(roles):raise ValueError("Missing application role")
  return Principal(subject,tenant,frozenset(groups),frozenset(roles))
 except (jwt.PyJWTError,ValueError,TypeError,KeyError) as exc:raise AuthError("Invalid or expired access token") from exc
