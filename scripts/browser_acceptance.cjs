/* Real Keycloak/browser/API acceptance. Requires the documented running demo. */
const { chromium } = require("../frontend/node_modules/@playwright/test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const base = process.env.KNOWLEDGE_WEB_URL || "http://localhost:5183";
const api = process.env.KNOWLEDGE_API_URL || "http://localhost:8083";
const password = process.env.KNOWLEDGE_DEMO_PASSWORD;
const output = process.env.KNOWLEDGE_EVIDENCE_DIR || "artifacts/browser";
if (!password) throw new Error("Set KNOWLEDGE_DEMO_PASSWORD");
fs.mkdirSync(output, { recursive: true });
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROME_BIN
      ? { executablePath: process.env.CHROME_BIN }
      : {}),
  });
  const report = { identities: [], checks: [], browserErrors: [] };
  const contexts = [];
  async function login(username) {
    const context = await browser.newContext({
      viewport: { width: 1360, height: 1000 },
    });
    contexts.push(context);
    const page = await context.newPage();
    let token = "";
    page.on("pageerror", (error) => report.browserErrors.push(error.message));
    page.on("response", async (response) => {
      if (
        response.url().endsWith("/protocol/openid-connect/token") &&
        response.status() === 200
      )
        token = (await response.json()).access_token;
    });
    await page.goto(base);
    await page
      .locator('button:has-text("Sign in with company account")')
      .click();
    await page.locator("#username").fill(username);
    await page.locator("#password").fill(password);
    await page.locator("#kc-login").click();
    await page.locator(".session").waitFor({ timeout: 60000 });
    assert(token, "Actual OIDC access token received");
    async function call(endpoint, method = "GET", body) {
      const response = await context.request.fetch(api + endpoint, {
        method,
        headers: { Authorization: "Bearer " + token },
        ...(body === undefined ? {} : { data: body }),
      });
      return {
        status: response.status(),
        body: response.status() === 204 ? null : await response.json(),
      };
    }
    const identity = await call("/api/me");
    assert.equal(identity.status, 200);
    report.identities.push({
      username,
      tenant: identity.body.tenant,
      roles: identity.body.roles,
    });
    return { page, context, call, identity: identity.body, token };
  }
  let admin, reader, document;
  try {
    admin = await login("acme-admin");
    reader = await login("acme-reader");
    assert.equal(
      await reader.page.locator("text=Manage company knowledge").count(),
      0
    );
    for (const tenant of ["beta", "cobalt"]) {
      for (const role of ["reader", "admin"]) {
        const actor = await login(tenant + "-" + role);
        assert.equal(actor.identity.tenant, tenant);
        assert(actor.identity.roles.includes(role));
        await actor.context.close();
      }
    }
    report.checks.push(
      "Six real PKCE identities across three tenants and two roles"
    );
    const finance = (await admin.call("/api/documents")).body.documents.find(
      (d) => d.source === "finance.md"
    );
    assert.equal(
      (await reader.call(`/api/documents/${finance.id}/revisions/1`)).status,
      404
    );
    const wrongToken = admin.token.split(".");
    wrongToken[1] = Buffer.from(
      JSON.stringify({ sub: "attacker", tenant: "beta" })
    ).toString("base64url");
    const tampered = await admin.context.request.get(api + "/api/me", {
      headers: { Authorization: "Bearer " + wrongToken.join(".") },
    });
    assert.equal(tampered.status(), 401);
    report.checks.push(
      "Restricted revision denied and tampered signed token rejected"
    );
    const q = { question: "What is the acquisition budget?", mode: "fusion" };
    assert.equal(
      (await reader.call("/api/ask", "POST", q)).body.abstained,
      true
    );
    await admin.call("/api/memberships/" + reader.identity.subject, "PUT", {
      groups: ["staff", "finance"],
      roles: ["reader"],
    });
    const granted = (await reader.call("/api/ask", "POST", q)).body;
    assert.equal(granted.abstained, false);
    assert(granted.citations.some((c) => c.document_id === finance.id));
    assert.equal((await reader.call("/api/ask", "POST", q)).body.cached, true);
    await admin.call("/api/memberships/" + reader.identity.subject, "PUT", {
      groups: ["staff"],
      roles: ["reader"],
    });
    const revoked = (await reader.call("/api/ask", "POST", q)).body;
    assert.equal(revoked.abstained, true);
    assert.equal(revoked.citations.length, 0);
    await admin.call("/api/memberships/" + reader.identity.subject, "PUT", {
      groups: [],
      roles: [],
    });
    assert.equal((await reader.call("/api/search?q=support")).status, 403);
    await admin.call("/api/memberships/" + reader.identity.subject, "PUT", {
      groups: ["staff"],
      roles: ["reader"],
    });
    report.checks.push(
      "Same signed token: grant, cached answer, group revocation, whole-account revocation"
    );
    async function upload(content) {
      await admin.page
        .locator('input[name="file"]')
        .setInputFiles({
          name: "lifecycle-laboratory.md",
          mimeType: "text/markdown",
          buffer: Buffer.from(content),
        });
      await admin.page
        .locator('input[name="title"]')
        .fill("Lifecycle laboratory");
      await admin.page.locator('input[name="groups"]').first().fill("staff");
      await admin.page.locator('button:has-text("Upload document")').click();
      const deadline = Date.now() + 30000;
      while (Date.now() < deadline) {
        const docs = (await admin.call("/api/documents")).body.documents;
        const found = docs.find((d) => d.source === "lifecycle-laboratory.md");
        if (
          found &&
          found.status === "ready" &&
          (!document || found.revision > document.revision)
        ) {
          document = found;
          return;
        }
        await sleep(200);
      }
      throw new Error("Document did not reach ready state");
    }
    await upload(
      "The laboratory recovery window is eleven days. The laboratory owner is the recovery team."
    );
    await reader.page
      .locator("#question")
      .fill("What is the laboratory recovery window?");
    await reader.page.locator("#action").selectOption("ask");
    await reader.page.locator('button:has-text("Ask knowledge")').click();
    await reader.page.locator(".answer-card").waitFor();
    assert.match(
      await reader.page.locator(".answer-card").innerText(),
      /eleven days/
    );
    await reader.page
      .locator('.source-link:has-text("Lifecycle laboratory")')
      .click();
    await reader.page.locator("[role=dialog]").waitFor();
    assert.match(
      await reader.page.locator("[role=dialog]").innerText(),
      /eleven days/
    );
    await reader.page.keyboard.press("Escape");
    await reader.page.locator("[role=dialog]").waitFor({ state: "hidden" });
    await reader.page.locator('button:has-text("Helpful")').click();
    await reader.page.locator("text=Your feedback is recorded.").waitFor();
    await reader.page.screenshot({
      path: path.join(output, "answer-desktop.png"),
      fullPage: true,
    });
    report.checks.push(
      "Browser file upload, actual model answer, source reader, Escape focus handling, feedback"
    );
    const oldRevision = document.revision;
    const question = {
      question: "What is the laboratory recovery window?",
      mode: "lexical",
    };
    assert.equal(
      (await reader.call("/api/ask", "POST", question)).body.cached,
      true
    );
    await upload(
      "The laboratory recovery window is thirteen days. The laboratory owner is the recovery team."
    );
    const updated = (await reader.call("/api/ask", "POST", question)).body;
    assert.match(updated.answer, /thirteen days/);
    assert(
      updated.citations.some(
        (c) => c.document_id === document.id && c.revision > oldRevision
      )
    );
    await admin.page.locator('button:has-text("Refresh status")').click();
    admin.page.once("dialog", (dialog) => dialog.accept());
    await admin.page
      .locator('tr:has-text("Lifecycle laboratory") button:has-text("Delete")')
      .click();
    const deadline = Date.now() + 10000;
    while (
      Date.now() < deadline &&
      (
        await reader.call(
          `/api/documents/${document.id}/revisions/${document.revision}`
        )
      ).status !== 404
    )
      await sleep(100);
    assert.equal(
      (
        await reader.call(
          `/api/documents/${document.id}/revisions/${document.revision}`
        )
      ).status,
      404
    );
    const deleted = (await reader.call("/api/ask", "POST", question)).body;
    assert(!deleted.citations.some((c) => c.document_id === document.id));
    assert(!deleted.answer.includes("thirteen days"));
    report.checks.push(
      "Updated source replaces cached answer and citation revision; deletion denies old source and answer"
    );
    await reader.page.setViewportSize({ width: 390, height: 844 });
    await reader.page.locator('button:has-text("Ask knowledge")').click();
    await reader.page.waitForTimeout(500);
    const overflow = await reader.page.evaluate(
      () => document.documentElement.scrollWidth > innerWidth
    );
    assert.equal(overflow, false);
    await reader.page.screenshot({
      path: path.join(output, "answer-mobile.png"),
      fullPage: true,
    });
    report.checks.push("Mobile layout has no horizontal overflow");
    assert.deepEqual(report.browserErrors, []);
    report.status = "passed";
    fs.writeFileSync(
      path.join(output, "report.json"),
      JSON.stringify(report, null, 2)
    );
    console.log(JSON.stringify(report, null, 2));
  } finally {
    if (admin && reader)
      await admin
        .call("/api/memberships/" + reader.identity.subject, "PUT", {
          groups: ["staff"],
          roles: ["reader"],
        })
        .catch(() => {});
    for (const context of contexts) await context.close().catch(() => {});
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
