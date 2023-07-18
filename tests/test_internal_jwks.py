from knowledge.auth import OIDCVerifier


def test_jwks_transport_override_does_not_change_verified_issuer():
    v = OIDCVerifier(
        "http://localhost:8183/realms/knowledge",
        "api",
        jwks_url="http://keycloak:8080/realms/knowledge/protocol/openid-connect/certs",
    )
    assert v.issuer == "http://localhost:8183/realms/knowledge"
    assert v.jwks.uri.startswith("http://keycloak:8080/")
