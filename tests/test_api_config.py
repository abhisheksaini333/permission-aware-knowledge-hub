from api_support import client

def test_public_configuration_contains_only_sign_in_coordinates():
 c,s=client();r=c.get("/api/config")
 assert r.status_code==200 and r.json()["client_id"]=="knowledge-ui"
 assert set(r.json())=={"issuer","client_id","dense_available","answers_available"}
