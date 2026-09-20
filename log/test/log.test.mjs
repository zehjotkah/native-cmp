// SPDX-License-Identifier: AGPL-3.0-or-later
// End-to-end test of the consent log against a local Worker with a local D1 database.
//   cd log && npm install && npm test
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";

const PORT = Number(process.env.PORT || 8799);
const BASE = `http://127.0.0.1:${PORT}`;
const TOKEN = "test-token-1234567890";
const ORIGIN = "https://example.com";

let failures = 0;
const check = (name, ok, detail = "") => {
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? "  (" + detail + ")" : ""}`);
  if (!ok) failures++;
};

const entry = (extra = {}) => ({
  id: "c7f3aa11-0000-4000-8000-000000000001",
  time: new Date().toISOString(),
  type: "accept",
  consents: { "consent-manager": true, youtube: true, vimeo: false },
  config: "1a2b3c",
  language: "en",
  engine: "1.3.0",
  ...extra,
});

const post = (body, origin = ORIGIN) =>
  fetch(BASE, { method: "POST", headers: { "content-type": "text/plain", origin }, body: typeof body === "string" ? body : JSON.stringify(body) });

const worker = spawn(
  "npx",
  // a fresh database per run, so counts are predictable
  ["--yes", "wrangler@4", "dev", "--port", String(PORT), "--local", "--persist-to", mkdtempSync(join(tmpdir(), "consent-log-test-")), "--var", `RETENTION_DAYS:1095`, "--var", `ALLOWED_ORIGINS:${ORIGIN}`, "--var", `EXPORT_TOKEN:${TOKEN}`],
  { cwd: new URL("..", import.meta.url).pathname, stdio: ["ignore", "pipe", "pipe"], env: { ...process.env, CLOUDFLARE_API_TOKEN: "", WRANGLER_SEND_METRICS: "false" } }
);
worker.stdout.on("data", (chunk) => process.env.VERBOSE && process.stdout.write(chunk));
worker.stderr.on("data", (chunk) => process.env.VERBOSE && process.stderr.write(chunk));

try {
  let up = false;
  for (let i = 0; i < 90 && !up; i++) {
    up = await fetch(`${BASE}/status`).then((r) => r.ok).catch(() => false);
    if (!up) await sleep(1000);
  }
  if (!up) throw new Error("worker did not start; run with VERBOSE=1 to see why");

  const accepted = await post(entry());
  check("stores a valid entry", accepted.status === 202, String(accepted.status));

  check("rejects another origin", (await post(entry(), "https://evil.example")).status === 403);
  check("rejects invalid JSON", (await post("not json")).status === 400);
  check("rejects an entry without a consent ID", (await post(entry({ id: "" }))).status === 400);
  check("rejects an oversized body", (await post(entry({ config: "x".repeat(5000) }))).status === 413);

  await post(entry({ id: "c7f3aa11-0000-4000-8000-000000000002", type: "decline", consents: { "consent-manager": true, youtube: false } }));
  await post(entry({ type: "reset" }));

  const info = await (await fetch(`${BASE}/status`)).json();
  check("status reports the entries", info.entries === 3, `entries=${info.entries}`);
  check("status reports the retention", info.retentionDays === 1095);

  check("export needs a token", (await fetch(`${BASE}/export.csv`)).status === 401);
  check("export rejects a wrong token", (await fetch(`${BASE}/export.csv?token=nope`)).status === 401);

  const csv = await (await fetch(`${BASE}/export.csv?token=${TOKEN}`)).text();
  const lines = csv.trim().split("\n");
  check("export returns every entry as CSV", lines.length === 4 && lines[0].startsWith("consent_id,decided_at,received_at,type"), `lines=${lines.length}`);
  check("export contains the choices and no IP column", csv.includes('""youtube"":true') && !/\bip\b/i.test(lines[0]));

  const single = await (await fetch(`${BASE}/export.csv?token=${TOKEN}&id=c7f3aa11-0000-4000-8000-000000000002`)).text();
  check("export filters by consent ID", single.trim().split("\n").length === 2);

  const home = await (await fetch(BASE)).text();
  check("info page shows the count and the custom domain hint", home.includes("Consent log") && home.includes("consentlog.yourdomain.com"));

  const preflight = await fetch(BASE, { method: "OPTIONS", headers: { origin: ORIGIN } });
  check("answers preflight requests", preflight.status === 204 && preflight.headers.get("access-control-allow-origin") === ORIGIN);
} catch (error) {
  console.error(error);
  failures++;
} finally {
  worker.kill("SIGTERM");
}

console.log(`\n${failures === 0 ? "all checks passed" : failures + " check(s) failed"}`);
process.exit(failures === 0 ? 0 : 1);
