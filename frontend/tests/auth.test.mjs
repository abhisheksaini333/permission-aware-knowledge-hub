import test from "node:test";
import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import {
  createPkce,
  authorizationUrl,
  validateCallback,
  logoutUrl,
} from "../src/auth.mjs";
if (!globalThis.crypto) globalThis.crypto = webcrypto;
test("PKCE uses unique verifier/state and S256 authorization", async () => {
  const a = await createPkce(),
    b = await createPkce();
  assert.notEqual(a.verifier, b.verifier);
  assert.equal(a.challenge.length, 43);
  const u = new URL(
    authorizationUrl(
      { issuer: "https://id/realms/k", client_id: "ui" },
      a,
      "http://localhost:5183/"
    )
  );
  assert.equal(u.searchParams.get("code_challenge_method"), "S256");
  assert.equal(u.searchParams.get("state"), a.state);
});
test("callback rejects mismatched or expired state", () => {
  assert.throws(() =>
    validateCallback({ state: "a", expires: 100 }, { state: "b", code: "x" }, 1)
  );
  assert.throws(() =>
    validateCallback({ state: "a", expires: 0 }, { state: "a", code: "x" }, 1)
  );
  assert.equal(
    validateCallback(
      { state: "a", expires: 100 },
      { state: "a", code: "x" },
      1
    ),
    "x"
  );
});

test("logout binds the end-session request to the signed identity token", () => {
  const u = new URL(
    logoutUrl(
      { issuer: "https://id/realms/k" },
      "signed-id-token",
      "http://localhost:5183/"
    )
  );
  assert.equal(u.pathname, "/realms/k/protocol/openid-connect/logout");
  assert.equal(u.searchParams.get("id_token_hint"), "signed-id-token");
  assert.equal(
    u.searchParams.get("post_logout_redirect_uri"),
    "http://localhost:5183/"
  );
});
