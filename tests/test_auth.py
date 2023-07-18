import time, jwt, pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from knowledge.auth import decode_token, AuthError

KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def token(**changes):
    c = dict(
        sub="reader",
        tenant="acme",
        groups=["staff"],
        realm_access={"roles": ["reader"]},
        iat=int(time.time()),
        exp=int(time.time()) + 60,
        iss="https://issuer",
        aud="api",
    )
    c.update(changes)
    return jwt.encode(c, KEY, algorithm="RS256")


def test_signed_principal_and_wrong_audience():
    p = decode_token(token(), KEY.public_key(), "https://issuer", "api")
    assert p.tenant == "acme" and "staff" in p.groups
    with pytest.raises(AuthError):
        decode_token(token(aud="other"), KEY.public_key(), "https://issuer", "api")


def test_expired_missing_tenant_and_unsigned_tokens_rejected():
    for t in [
        token(exp=1),
        token(tenant=["acme", "beta"]),
        jwt.encode({"sub": "x"}, key=None, algorithm="none"),
    ]:
        with pytest.raises(AuthError):
            decode_token(t, KEY.public_key(), "https://issuer", "api")
