const base64url = (bytes) =>
  btoa(String.fromCharCode(...bytes))
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replaceAll("=", "");
export async function createPkce() {
  const verifier = base64url(crypto.getRandomValues(new Uint8Array(32)));
  const state = base64url(crypto.getRandomValues(new Uint8Array(24)));
  const hash = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(verifier)
  );
  return {
    verifier,
    state,
    challenge: base64url(new Uint8Array(hash)),
    expires: Date.now() + 300000,
  };
}
export function authorizationUrl(config, flow, redirect) {
  const url = new URL(config.issuer + "/protocol/openid-connect/auth");
  url.search = new URLSearchParams({
    client_id: config.client_id,
    response_type: "code",
    scope: "openid profile",
    redirect_uri: redirect,
    state: flow.state,
    code_challenge: flow.challenge,
    code_challenge_method: "S256",
  }).toString();
  return url.toString();
}
export function validateCallback(flow, params, now = Date.now()) {
  if (
    !flow ||
    flow.expires < now ||
    !params.state ||
    flow.state !== params.state ||
    !params.code
  )
    throw new Error("Sign-in could not be verified. Please start again.");
  return params.code;
}
export async function exchangeCode(config, flow, code, redirect) {
  const response = await fetch(
    config.issuer + "/protocol/openid-connect/token",
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        client_id: config.client_id,
        redirect_uri: redirect,
        code,
        code_verifier: flow.verifier,
      }),
    }
  );
  if (!response.ok) throw new Error("Sign-in expired. Please try again.");
  return response.json();
}

export function logoutUrl(config,idToken,redirect){const url=new URL(config.issuer+"/protocol/openid-connect/logout");url.search=new URLSearchParams({id_token_hint:idToken,post_logout_redirect_uri:redirect}).toString();return url.toString();}
