#!/usr/bin/env node
// SPDX-License-Identifier: AGPL-3.0-or-later
// Native CMP installer.
// Runs the steps from steps.txt (JSON) through the Webstudio CLI in a directory that is
// linked to a Webstudio project (`npx webstudio@latest link`). Guide: https://nativecmp.com/install.txt
//
//   curl -fsSL https://nativecmp.com/install/install.js -o native-cmp-install.mjs
//   node native-cmp-install.mjs [--page /] [--attach all|none|/a,/b] [--custom-code install|skip]
//                    [--services file.json] [--translations file.json]
//                    [--languages en,de] [--privacy-link-parent <instanceId>] [--contextual]
//                    [--bundle <url or file>] [--force]

import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const DEFAULT_BUNDLE = "https://nativecmp.com/install/steps.txt";

const args = { page: "/", attach: "all", "custom-code": "install", bundle: DEFAULT_BUNDLE, force: false, contextual: false };
for (let i = 2; i < process.argv.length; i++) {
  const key = process.argv[i].replace(/^--/, "");
  if (key === "force" || key === "contextual") args[key] = true;
  else args[key] = process.argv[++i];
}

const temp = mkdtempSync(join(tmpdir(), "native-cmp-"));
let callCount = 0;

// reads and updates that set absolute values are safe to repeat
const REPEATABLE = /^(list-|get-|verify-|search-|inspect-|update-design-token-styles|update-props|update-variable|bind-props)/;

function cli(tool, input, attempt = 1) {
  try {
    return run(tool, input);
  } catch (error) {
    // the Webstudio API intermittently answers "Unable to transform response from server"
    if (REPEATABLE.test(tool) && attempt < 6 && /MCP_TOOL_FAILED|ECONN|ETIMEDOUT|fetch failed|Unable to transform/i.test(error.message)) {
      execFileSync("sleep", [String(attempt * 3)]);
      return cli(tool, input, attempt + 1);
    }
    throw error;
  }
}

function run(tool, input) {
  const file = join(temp, `${++callCount}-${tool}.json`);
  writeFileSync(file, JSON.stringify(input ?? {}));
  let stdout;
  try {
    stdout = execFileSync("npx", ["--yes", "webstudio@latest", tool, "--input-file", file], { encoding: "utf8", maxBuffer: 256 * 1024 * 1024, stdio: ["ignore", "pipe", "pipe"] });
  } catch (error) {
    stdout = error.stdout || "";
    if (!stdout.trim().startsWith("{")) throw new Error(`${tool} failed: ${(error.stderr || error.message).slice(-1500)}`);
  }
  const result = JSON.parse(stdout);
  if (!result.ok) throw new Error(`${tool} failed: ${JSON.stringify(result.error).slice(0, 1500)}`);
  return { data: result.data, version: result.data?.version ?? result.meta?.session?.version };
}

const log = (...parts) => console.log("•", ...parts);

async function loadBundle(source) {
  if (/^https?:\/\//.test(source)) {
    const response = await fetch(source);
    if (!response.ok) throw new Error(`Could not download ${source}: ${response.status}`);
    return response.json();
  }
  return JSON.parse(readFileSync(source, "utf8"));
}

function listAll(tool, key, input = {}) {
  const items = [];
  let cursor;
  do {
    const { data } = cli(tool, { ...input, limit: 200, ...(cursor ? { cursor } : {}) });
    items.push(...(data[key] || []));
    cursor = data.nextCursor;
  } while (cursor);
  return items;
}

const pageInstances = (pagePath) => listAll("list-instances", "instances", { pagePath, maxDepth: 40 });

function descendant(instances, rootId, label) {
  const byId = new Map(instances.map((item) => [item.id, item]));
  const inside = (item) => {
    for (let current = item; current; current = byId.get(current.parentId)) if (current.id === rootId) return true;
    return false;
  };
  const match = instances.find((item) => item.label === label && inside(item));
  if (!match) throw new Error(`"${label}" not found below the Consent Manager root`);
  return match;
}

const bundle = await loadBundle(args.bundle);
const manager = bundle.consentManager;
log(`${bundle.name} ${bundle.engineVersion}`);

// pages
const pages = listAll("list-pages", "pages");
const normalize = (path) => (path === "" || path === "/" ? "/" : path);
const target = pages.find((page) => normalize(page.path) === normalize(args.page));
if (!target) throw new Error(`Page ${args.page} not found`);
const targetPath = normalize(target.path);

const existing = pageInstances(targetPath).find((item) => item.label === manager.label);

// 1. mobile breakpoint
const breakpoints = listAll("list-breakpoints", "breakpoints");
let mobile = breakpoints.find((bp) => bp.maxWidth === bundle.mobileBreakpoint.maxWidth && bp.minWidth === undefined && !bp.condition);
if (!mobile) {
  const { data } = cli("create-breakpoint", bundle.mobileBreakpoint);
  mobile = { id: data.breakpointId || data.id };
  log("created breakpoint", bundle.mobileBreakpoint.label);
}

// 2. namespaced --cmp-* theme variables. Their defaults reference Craft variables when the project has them
//    (var(--background-accent, #1d4ed8)); map them to the project's own design afterwards (install.txt, "Theme it").
const existingVars = new Set(listAll("list-css-variables", "vars").map((item) => item.name));
const newVars = Object.fromEntries(Object.entries(bundle.cssVariables).filter(([name]) => !existingVars.has(name)));
if (Object.keys(newVars).length) cli("define-css-variable", { vars: newVars });
log(`--cmp-* theme variables: ${Object.keys(newVars).length} defined, ${Object.keys(bundle.cssVariables).length - Object.keys(newVars).length} already present`);

// 3. design tokens (existing tokens with the same name are kept)
const tokenNames = new Set(listAll("list-design-tokens", "tokens").map((token) => token.name));
const missing = bundle.tokens
  .filter((token) => !tokenNames.has(token.name))
  .map((token) => ({
    name: token.name,
    declarations: token.declarations.map((declaration) => (declaration.breakpoint ? { ...declaration, breakpoint: mobile.id } : declaration)),
  }));
if (missing.length) cli("create-design-token", { tokens: missing });
log(`design tokens: ${missing.length} created, ${bundle.tokens.length - missing.length} already present`);


// 4. Custom Code
if (args["custom-code"] !== "skip") {
  const { data } = cli("get-project-settings", {});
  const current = data.meta?.code ?? data.projectSettings?.meta?.code ?? "";
  let code;
  if (current.includes("data-cmp-engine=")) {
    const css = bundle.customCode.match(/<style data-cmp-critical>[\s\S]*?<\/style>/)[0];
    const engine = bundle.customCode.match(/<script data-cmp-engine="[^"]*">[\s\S]*?<\/script>/)[0];
    code = current.replace(/<style data-cmp-critical>[\s\S]*?<\/style>/, () => css).replace(/<script data-cmp-engine="[^"]*">[\s\S]*?<\/script>/, () => engine);
  } else {
    code = bundle.customCode + (current ? "\n\n" + current : "");
  }
  if (args.contextual) {
    // contextual consent only: no notice on page load, gates and the settings link ask for consent
    code = /noNotice:\s*(true|false)/.test(code)
      ? code.replace(/noNotice:\s*(true|false)/, "noNotice: true")
      : code.replace("window.cmpConfig = {", "window.cmpConfig = {\n  noNotice: true,");
  }
  if (code !== current) {
    cli("update-project-settings", { meta: { code } });
    log("Custom Code updated (your cmpConfig and other code are kept)");
  } else log("Custom Code already up to date");
}

if (existing && !args.force) {
  console.log(`
The page ${targetPath} already has a "${manager.label}". Engine, tokens and CSS variables are up to date;
the Consent Manager itself was left unchanged. Update its consentServices and consentTranslations variables,
or pass --force to add another one.`);
  process.exit(0);
}

// 5. Consent Manager
const inserted = cli("insert-fragment", { parentInstanceId: target.rootInstanceId, conflictResolution: "ours", fragment: manager.skeleton });
const rootId = inserted.data.rootInstanceIds[0];
const variables = { ...manager.variables };
if (args.languages) {
  const keep = args.languages.split(",").map((code) => code.trim().toLowerCase());
  variables.consentTranslations = { ...variables.consentTranslations, value: variables.consentTranslations.value.filter((entry) => keep.includes(entry.lang)) };
}
if (args.services) variables.consentServices = { type: "json", value: JSON.parse(readFileSync(args.services, "utf8")) };
if (args.translations) variables.consentTranslations = { type: "json", value: JSON.parse(readFileSync(args.translations, "utf8")) };
for (const [name, value] of Object.entries(variables)) {
  cli("create-variable", { scopeInstanceId: rootId, name, value });
}
// props that read the root variables (e.g. the Builder preview flags of the Canvas Helper)
if (manager.bindings?.length) {
  const instances = pageInstances(targetPath);
  cli("bind-props", {
    bindings: manager.bindings.map((binding) => ({
      instanceId: descendant(instances, rootId, binding.label).id,
      name: binding.name,
      binding: { type: "expression", value: binding.expression },
    })),
  });
}
log("Consent Manager root, variables and Builder preview flags created");

for (const level of manager.collections) {
  const parent = descendant(pageInstances(targetPath), rootId, level.parentLabel);
  const result = cli("insert-collection", {
    parentInstanceId: parent.id,
    insertIndex: level.insertIndex,
    conflictResolution: "ours",
    data: { type: "expression", value: level.data },
    itemFragment: level.itemFragment,
  });
  if (level.renameItemParameterTo) {
    cli("apply-patch", {
      baseVersion: result.version,
      transactions: [{ id: `rename-${level.renameItemParameterTo}`, payload: [{ namespace: "dataSources", patches: [{ op: "replace", path: [result.data.itemParameterId, "name"], value: level.renameItemParameterTo }] }] }],
    });
  }
  log(`collection in "${level.parentLabel}"`);
}

const verification = cli("verify-bindings", {}).data;
if (verification.summary?.findings) console.warn("verify-bindings findings:", JSON.stringify(verification.findings).slice(0, 1500));

// 6. shared Slot on every page
const slot = cli("extract-slot", { instanceSelector: [rootId, target.rootInstanceId], label: manager.label }).data;
const slotId = slot.slotId;
log("Consent Manager converted to a shared Slot");

const attachPaths =
  args.attach === "none" ? [] : args.attach === "all" ? pages.map((page) => normalize(page.path)).filter((path) => path !== targetPath) : args.attach.split(",").map(normalize);
for (const path of attachPaths) {
  const page = pages.find((item) => normalize(item.path) === path);
  if (!page) continue;
  try {
    cli("attach-slot", { sourceSlotId: slotId, parentInstanceId: page.rootInstanceId, label: manager.label });
    log("attached to", path);
  } catch (error) {
    console.warn(`skipped ${path}: ${error.message.slice(0, 200)}`);
  }
}

// 7. optional Privacy settings link
if (args["privacy-link-parent"]) {
  cli("insert-fragment", { parentInstanceId: args["privacy-link-parent"], conflictResolution: "ours", fragment: bundle.privacySettingsLink });
  log("Privacy settings link added");
}

console.log(`
Installed. Not finished yet:
1. Theme it: the consent UI uses neutral defaults unless the project has Craft variables. Map the --cmp-*
   variables to the project's own colors, radii, shadow and fonts (install.txt, section "Theme it").
2. Review it visually: open the notice and the preferences dialog (Builder: canvasPreview = modal) and compare
   buttons, headings, radii and colors with a real page, at desktop width and at 390px.
3. Add services, translations and gates (https://nativecmp.com/generator) and a Privacy settings link in the footer.
4. Publish.`);
