import test from "node:test";
import assert from "node:assert/strict";
import {apiRequest,messageFor} from "../src/http.mjs";
test("malformed error envelopes retain a readable fallback", async () => {
  assert.match(messageFor(null), /could not/);
  assert.equal(messageFor({detail:[null,{msg:"bad"}]}),"Invalid input; bad");
  const original=global.fetch;
  global.fetch=async()=>new Response("<html>gateway</html>",{status:502});
  try { await assert.rejects(apiRequest("/api/me","token"), /502/); }
  finally {global.fetch=original;}
});
