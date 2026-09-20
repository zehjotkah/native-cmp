// SPDX-License-Identifier: AGPL-3.0-or-later
//
// Native CMP consent log: a Cloudflare Worker that stores consent decisions in
// your own D1 database, so you can show what a visitor agreed to and when.
//
// It never stores IP addresses. Each entry is linked to the random consent ID
// that Native CMP keeps in the visitor's cmp_consent cookie.

const MAX_BODY = 4096;
const MAX_SERVICES = 100;
const CLEANUP_EVERY_MS = 6 * 60 * 60 * 1000;

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS entries (
     row_id INTEGER PRIMARY KEY AUTOINCREMENT,
     consent_id TEXT NOT NULL,
     decided_at TEXT NOT NULL,
     received_at TEXT NOT NULL,
     type TEXT NOT NULL,
     consents TEXT NOT NULL,
     config TEXT,
     language TEXT,
     engine TEXT,
     origin TEXT
   )`,
  `CREATE INDEX IF NOT EXISTS entries_consent_id ON entries (consent_id)`,
  `CREATE INDEX IF NOT EXISTS entries_received_at ON entries (received_at)`,
  `CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)`,
];

let ready = null;

async function setup(db) {
  if (!ready) ready = db.batch(SCHEMA.map((statement) => db.prepare(statement)));
  try {
    await ready;
  } catch (error) {
    ready = null;
    throw error;
  }
}

const text = (body, status = 200, headers = {}) => new Response(body, { status, headers: { "content-type": "text/plain; charset=utf-8", ...headers } });

function corsHeaders(origin) {
  return {
    "access-control-allow-origin": origin || "*",
    "access-control-allow-methods": "POST, OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
  };
}

function allowedOrigins(env) {
  return String(env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((value) => value.trim().replace(/\/$/, ""))
    .filter(Boolean);
}

function originAllowed(env, origin) {
  const allowed = allowedOrigins(env);
  if (!allowed.length) return true; // not configured: accept any site, the origin is stored with each entry
  return allowed.includes(String(origin || "").replace(/\/$/, ""));
}

function clean(value, max) {
  return typeof value === "string" ? value.slice(0, max) : "";
}

// Accepts only what the engine sends, so a stray request cannot fill the database.
function parseEntry(raw) {
  let data;
  try {
    data = JSON.parse(raw);
  } catch (error) {
    return null;
  }
  if (!data || typeof data !== "object") return null;
  const id = clean(data.id, 64);
  if (!id) return null;
  const consents = {};
  if (data.consents && typeof data.consents === "object") {
    for (const name of Object.keys(data.consents).slice(0, MAX_SERVICES)) {
      consents[clean(name, 64)] = !!data.consents[name];
    }
  }
  const decided = clean(data.time, 32);
  return {
    consent_id: id,
    decided_at: /^\d{4}-\d{2}-\d{2}T/.test(decided) ? decided : new Date().toISOString(),
    type: clean(data.type, 32) || "save",
    consents: JSON.stringify(consents),
    config: clean(data.config, 32),
    language: clean(data.language, 32),
    engine: clean(data.engine, 32),
  };
}

// Entries older than RETENTION_DAYS are deleted. Runs at most every few hours,
// on a normal request, so the log works without a scheduled job.
async function cleanup(env, now) {
  const days = Number(env.RETENTION_DAYS || 1095);
  if (!Number.isFinite(days) || days <= 0) return;
  const last = await env.DB.prepare("SELECT value FROM meta WHERE key = 'last_cleanup'").first();
  if (last && now - Number(last.value) < CLEANUP_EVERY_MS) return;
  const cutoff = new Date(now - days * 864e5).toISOString();
  await env.DB.batch([
    env.DB.prepare("DELETE FROM entries WHERE received_at < ?").bind(cutoff),
    env.DB.prepare("INSERT INTO meta (key, value) VALUES ('last_cleanup', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value").bind(String(now)),
  ]);
}

async function store(request, env, ctx) {
  const origin = request.headers.get("origin") || "";
  if (!originAllowed(env, origin)) return text("origin not allowed\n", 403, corsHeaders(origin));
  const body = await request.text();
  if (body.length > MAX_BODY) return text("too large\n", 413, corsHeaders(origin));
  const entry = parseEntry(body);
  if (!entry) return text("invalid entry\n", 400, corsHeaders(origin));
  const now = Date.now();
  await setup(env.DB);
  await env.DB.prepare(
    `INSERT INTO entries (consent_id, decided_at, received_at, type, consents, config, language, engine, origin)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(entry.consent_id, entry.decided_at, new Date(now).toISOString(), entry.type, entry.consents, entry.config, entry.language, entry.engine, origin)
    .run();
  ctx.waitUntil(cleanup(env, now).catch(() => {}));
  return text("ok\n", 202, corsHeaders(origin));
}

function authorized(request, url, env) {
  const expected = String(env.EXPORT_TOKEN || "");
  if (!expected) return false;
  const given = url.searchParams.get("token") || (request.headers.get("authorization") || "").replace(/^Bearer /, "");
  if (given.length !== expected.length) return false;
  let same = 0;
  for (let i = 0; i < expected.length; i++) same |= given.charCodeAt(i) ^ expected.charCodeAt(i);
  return same === 0;
}

const csvCell = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;

async function exportCsv(request, url, env) {
  if (!env.EXPORT_TOKEN) return text("Set the EXPORT_TOKEN secret in the Cloudflare dashboard (Settings -> Variables and Secrets) to enable the export.\n", 503);
  if (!authorized(request, url, env)) return text("wrong or missing token\n", 401);
  await setup(env.DB);
  const id = url.searchParams.get("id");
  const limit = Math.min(Number(url.searchParams.get("limit") || 10000), 50000);
  const query = id
    ? env.DB.prepare("SELECT * FROM entries WHERE consent_id = ? ORDER BY row_id DESC LIMIT ?").bind(id, limit)
    : env.DB.prepare("SELECT * FROM entries ORDER BY row_id DESC LIMIT ?").bind(limit);
  const { results } = await query.all();
  const columns = ["consent_id", "decided_at", "received_at", "type", "consents", "config", "language", "engine", "origin"];
  const rows = [columns.join(","), ...results.map((row) => columns.map((column) => csvCell(row[column])).join(","))];
  return new Response(rows.join("\n") + "\n", {
    headers: {
      "content-type": "text/csv; charset=utf-8",
      "content-disposition": `attachment; filename="consent-log-${new Date().toISOString().slice(0, 10)}.csv"`,
      "cache-control": "no-store",
    },
  });
}

async function status(env) {
  await setup(env.DB);
  const total = await env.DB.prepare("SELECT COUNT(*) AS count FROM entries").first();
  const oldest = await env.DB.prepare("SELECT received_at FROM entries ORDER BY row_id ASC LIMIT 1").first();
  return { entries: total ? total.count : 0, oldest: oldest ? oldest.received_at : null, retentionDays: Number(env.RETENTION_DAYS || 1095), origins: allowedOrigins(env) };
}

function page(info, hasToken) {
  const origins = info.origins.length ? info.origins.join(", ") : "any site (set ALLOWED_ORIGINS to restrict)";
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Consent log</title><style>
:root{color-scheme:light dark;--bg:#ffffff;--fg:#15171c;--muted:#4d5461;--line:#dde0e5;--accent:#1d4ed8}
@media (prefers-color-scheme:dark){:root{--bg:#15171c;--fg:#f3f4f6;--muted:#a8aeba;--line:#333a45;--accent:#7aa2ff}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,sans-serif}
main{max-width:640px;margin:0 auto;padding:48px 24px}
h1{font-size:28px;margin:0 0 8px}p{margin:0 0 16px;color:var(--muted)}
dl{display:grid;grid-template-columns:auto 1fr;gap:8px 16px;margin:24px 0;padding:16px;border:1px solid var(--line);border-radius:12px}
dt{color:var(--muted)}dd{margin:0}
form{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 16px}
input{flex:1 1 200px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:transparent;color:inherit;font:inherit}
button{padding:10px 18px;border:0;border-radius:999px;background:var(--accent);color:#fff;font:inherit;font-weight:600;cursor:pointer}
code{font-family:ui-monospace,monospace;font-size:.9em}
</style></head><body><main>
<h1>Consent log</h1>
<p>This is your Native CMP consent log. It stores one entry per consent decision, without IP addresses.</p>
<dl><dt>Entries</dt><dd>${info.entries}</dd><dt>Oldest entry</dt><dd>${info.oldest ? info.oldest.slice(0, 10) : "none yet"}</dd><dt>Kept for</dt><dd>${info.retentionDays} days</dd><dt>Accepts entries from</dt><dd>${origins}</dd></dl>
<h2>Export</h2>
${hasToken
  ? `<form action="/export.csv" method="get"><input name="token" type="password" placeholder="Export token" required><input name="id" placeholder="Consent ID (optional)"><button type="submit">Download CSV</button></form>`
  : `<p>Set the <code>EXPORT_TOKEN</code> secret in the Cloudflare dashboard under Settings → Variables and Secrets, then reload this page to download entries.</p>`}
<p>Point your site at this log by setting <code>consentLog: "${info.self}"</code> in your Native CMP configuration. Add a custom domain such as <code>consentlog.yourdomain.com</code> in the Cloudflare dashboard so it is not a third-party domain for your visitors.</p>
</main></body></html>`;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("origin") || "";
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(origin) });
    if (request.method === "POST") return store(request, env, ctx);
    if (request.method !== "GET") return text("method not allowed\n", 405);
    if (url.pathname === "/export.csv") return exportCsv(request, url, env);
    if (url.pathname === "/status") {
      const info = await status(env);
      return Response.json(info, { headers: { "cache-control": "no-store" } });
    }
    const info = await status(env);
    info.self = url.origin;
    return new Response(page(info, !!env.EXPORT_TOKEN), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
  },

  // optional: runs if a scheduled trigger is configured for this Worker
  async scheduled(event, env, ctx) {
    await setup(env.DB);
    ctx.waitUntil(cleanup(env, Date.now()));
  },
};
