import pytest
from knowledge.auth import OIDCVerifier,AuthError

def test_jwks_url_is_derived_from_trusted_issuer():
 v=OIDCVerifier("https://identity.example/realms/knowledge","api")
 assert v.jwks.uri=="https://identity.example/realms/knowledge/protocol/openid-connect/certs"
 with pytest.raises(AuthError):v.verify("not-a-jwt")
