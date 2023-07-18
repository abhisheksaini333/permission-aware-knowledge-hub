import jwt
from .identity import Principal


class AuthError(ValueError):
    pass


def decode_token(token, key, issuer, audience):
    try:
        c = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=issuer,
            audience=audience,
            options={"require": ["exp", "iat", "sub", "iss", "aud", "tenant"]},
        )
        tenant = c["tenant"]
        subject = c["sub"]
        groups = c.get("groups", [])
        realm_access = c.get("realm_access", {})
        if not isinstance(realm_access, dict):
            raise ValueError("Invalid roles")
        roles = realm_access.get("roles", [])
        if (
            not isinstance(tenant, str)
            or not tenant
            or len(tenant) > 80
            or not isinstance(subject, str)
            or not subject
        ):
            raise ValueError("Invalid identity")
        if not isinstance(groups, list) or not all(isinstance(x, str) for x in groups):
            raise ValueError("Invalid groups")
        if not isinstance(roles, list) or not {"reader", "admin"}.intersection(roles):
            raise ValueError("Missing application role")
        return Principal(subject, tenant, frozenset(groups), frozenset(roles))
    except (jwt.PyJWTError, ValueError, TypeError, KeyError) as exc:
        raise AuthError("Invalid or expired access token") from exc


class OIDCVerifier:
    def __init__(self, issuer, audience, jwks_url=None):
        self.issuer = issuer.rstrip("/")
        self.audience = audience
        self.jwks = jwt.PyJWKClient(
            jwks_url or self.issuer + "/protocol/openid-connect/certs", cache_keys=True
        )

    def verify(self, token):
        try:
            key = self.jwks.get_signing_key_from_jwt(token).key
        except Exception as exc:
            raise AuthError("Unable to verify access token") from exc
        return decode_token(token, key, self.issuer, self.audience)
