export function messageFor(body) {
  if (!body || typeof body !== "object")
    return "The request could not be completed. Please try again.";
  if (Array.isArray(body.detail))
    return body.detail.map((x) => typeof x?.msg === "string" ? x.msg : "Invalid input").join("; ");
  return typeof body.detail === "string"
    ? body.detail
    : "The request could not be completed. Please try again.";
}
export async function apiRequest(path, access, init = {}) {
  if (!path.startsWith("/api/")) throw new Error("Invalid API destination");
  const headers = {
    ...(init.body && typeof init.body === "string"
      ? { "Content-Type": "application/json" }
      : {}),
    ...init.headers,
    Authorization: "Bearer " + access,
  };
  const response = await fetch(path, { ...init, headers, redirect: "error" });
  if (response.status === 204) return null;
  let body;
  try { body = await response.json(); }
  catch { throw new Error(`The service returned an unreadable response (${response.status}).`); }
  if (!response.ok) throw new Error(messageFor(body));
  return body;
}
