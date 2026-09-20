#!/usr/bin/env node
// SPDX-License-Identifier: AGPL-3.0-or-later
//
// One command to put the consent log into your own Cloudflare account:
//
//   npm install && npm run setup
//
// It creates the database, writes its id into wrangler.json, generates an
// export token, stores it as a secret and deploys the Worker.
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { randomBytes } from "node:crypto";

const CONFIG = new URL("./wrangler.json", import.meta.url).pathname;
const CHECK = process.argv.includes("--check"); // rehearse without creating or deploying anything
const step = (text) => console.log(`\n• ${text}`);

function wrangler(args, options = {}) {
  return execFileSync("npx", ["--yes", "wrangler@4", ...args], { encoding: "utf8", stdio: options.stdio ?? ["ignore", "pipe", "inherit"], input: options.input });
}

function readConfig() {
  return JSON.parse(readFileSync(CONFIG, "utf8"));
}

step("Checking that you are signed in to Cloudflare");
try {
  const who = wrangler(["whoami"]);
  const email = who.match(/associated with the email ([^.\s]+@[^.\s]+)/);
  console.log(`  signed in${email ? " as " + email[1] : ""}`);
} catch (error) {
  console.error("  Not signed in. Run: npx wrangler login");
  process.exit(1);
}

const config = readConfig();
const databaseName = config.d1_databases[0].database_name;

step(`Looking for the database "${databaseName}"`);
let databaseId = "";
try {
  const list = JSON.parse(wrangler(["d1", "list", "--json"]));
  databaseId = (list.find((database) => database.name === databaseName) || {}).uuid || "";
} catch (error) {
  // an empty account prints no JSON
}
if (databaseId) {
  console.log(`  reusing ${databaseId}`);
} else if (CHECK) {
  console.log("  not found; --check stops here, a real run would create it");
  process.exit(0);
} else {
  step(`Creating the database "${databaseName}"`);
  const created = wrangler(["d1", "create", databaseName]);
  databaseId = (created.match(/"database_id":\s*"([^"]+)"/) || created.match(/([0-9a-f-]{36})/) || [])[1] || "";
  if (!databaseId) {
    console.error("  Could not read the new database id. Run: npx wrangler d1 create " + databaseName);
    process.exit(1);
  }
  console.log(`  created ${databaseId}`);
}

if (CHECK) {
  console.log("\n--check: would write the database id, set the export token and deploy. Nothing changed.");
  process.exit(0);
}

if (config.d1_databases[0].database_id !== databaseId) {
  config.d1_databases[0].database_id = databaseId;
  writeFileSync(CONFIG, JSON.stringify(config, null, 2) + "\n");
  step("Wrote the database id into wrangler.json");
}

step("Setting the export token");
let token = "";
try {
  const secrets = JSON.parse(wrangler(["secret", "list", "--config", CONFIG]));
  if (secrets.some((secret) => secret.name === "EXPORT_TOKEN")) console.log("  EXPORT_TOKEN already set, keeping it");
  else token = randomBytes(24).toString("base64url");
} catch (error) {
  token = randomBytes(24).toString("base64url"); // no Worker yet, so no secrets yet
}

step("Deploying");
const output = wrangler(["deploy", "--config", CONFIG], { stdio: ["ignore", "pipe", "inherit"] });
const url = (output.match(/https:\/\/[^\s]+\.workers\.dev/) || [])[0] || "";
console.log(output.split("\n").filter((line) => line.includes("http")).join("\n"));

if (token) {
  wrangler(["secret", "put", "EXPORT_TOKEN", "--config", CONFIG], { input: token, stdio: ["pipe", "pipe", "inherit"] });
}

console.log(`
Done. Your consent log is live${url ? " at " + url : ""}.
${token ? `\nYour export token (store it in your password manager, it is shown only now):\n  ${token}\n` : ""}
Next:
1. Add a custom domain such as consentlog.yourdomain.com in the Cloudflare dashboard
   (Workers & Pages -> native-cmp-consent-log -> Settings -> Domains & Routes), so the log
   is not a third-party domain for your visitors.
2. Set ALLOWED_ORIGINS to your site in wrangler.json, then run: npm run deploy
3. In Webstudio, Project Settings -> Custom Code:
     window.cmpConfig = { consentLog: "https://consentlog.yourdomain.com" };
4. Add the log to your privacy policy: https://nativecmp.com/docs#proof-of-consent
`);
