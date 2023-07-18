import pytest
from knowledge.auth import decode_token, AuthError
from test_auth import token, KEY


def test_malformed_role_claims_are_denied_instead_of_server_errors():
    for roles in [[], "admin", None]:
        with pytest.raises(AuthError):
            decode_token(
                token(realm_access=roles), KEY.public_key(), "https://issuer", "api"
            )
