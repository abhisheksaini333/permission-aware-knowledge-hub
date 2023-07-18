export function messageFor(body) {
  if (Array.isArray(body.detail))
    return body.detail.map((x) => x.msg || "Invalid input").join("; ");
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
  const body = await response.json();
  if (!response.ok) throw new Error(messageFor(body));
  return body;
}
