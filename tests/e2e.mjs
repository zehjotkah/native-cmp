// End-to-end checks for Native CMP against the generated preview site.
// Usage: BASE_URL=http://127.0.0.1:5188 node e2e.mjs
import { chromium } from "playwright-core";
import { mkdirSync } from "node:fs";
import { webstudioFragment } from "@webstudio-is/sdk";

const WS_CLIPBOARD = "@webstudio/instance/v0.1";
const validFragment = (text) => {
  try {
    const envelope = JSON.parse(text);
    return webstudioFragment.safeParse(envelope[WS_CLIPBOARD]).success ? envelope[WS_CLIPBOARD] : null;
  } catch {
    return null;
  }
};

const BASE = process.env.BASE_URL ?? "http://127.0.0.1:5188";
const SHOTS = new URL("./screenshots/", import.meta.url).pathname;
mkdirSync(SHOTS, { recursive: true });

const results = [];
const check = (name, ok, detail = "") => {
  results.push({ name, ok });
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? `  (${detail})` : ""}`);
};

const browser = await chromium.launch({ channel: "chrome", headless: true });
// never send test pageviews to the site's own analytics
const newContext = browser.newContext.bind(browser);
browser.newContext = async (...args) => {
  const ctx = await newContext(...args);
  await ctx.route(/insight\.nativecmp\.com/, (route) => route.abort());
  return ctx;
};
const context = await browser.newContext({ viewport: { width: 1280, height: 860 } });
const page = await context.newPage();
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const videoRequests = [];
context.on("request", (request) => {
  if (/^https?:\/\/[^/]*(youtube|ytimg|googlevideo|vimeo)/.test(request.url())) videoRequests.push(request.url());
});
context.on("response", (response) => {
  if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`);
});
page.on("console", (msg) => {
  if (msg.type() === "error") errors.push(msg.text());
});

const shown = (selector, target = page) => target.locator(`${selector} >> visible=true`);
const visible = async (selector, target = page) => (await shown(selector, target).count()) > 0;
const click = (selector, target = page) => shown(selector, target).first().click();
const openServices = (purpose, target = page) =>
  target.evaluate((id) => document.querySelectorAll(`[data-cmp-purpose="${id}"] details`).forEach((el) => (el.open = true)), purpose);
const consentCookie = async () => {
  const cookie = (await context.cookies()).find((c) => c.name === "cmp_consent");
  return cookie ? JSON.parse(decodeURIComponent(cookie.value)) : null;
};
const demoLog = () => page.evaluate(() => window.cmpDemoLog ?? []);

// 1. first visit ------------------------------------------------------------
await page.goto(BASE + "/", { waitUntil: "networkidle" });
check("notice visible on first visit", await visible("[data-cmp-notice]"));
check("Klaro credited in a homepage text, not the footer", await page.evaluate(() => {
  const mentions = [...document.querySelectorAll("main p, main h1, main h2, footer")].filter((el) => el.textContent.includes("Klaro"));
  return mentions.length === 1 && mentions[0].tagName === "P" && mentions[0].textContent.startsWith("Inspired by Klaro") && !document.querySelector("footer").textContent.includes("Klaro");
}));
check("modal hidden on first visit", !(await visible("[data-cmp-modal]")));
check("html marked unconfirmed", (await page.getAttribute("html", "data-cmp-confirmed")) === "false");
check("gate notice visible", await visible("[data-cmp-gate-notice]"));
check("youtube iframe not in DOM", (await page.locator("iframe[src*='youtube']").count()) === 0);
check("native video visible before consent (interaction mode)", await visible("[data-cmp-gate='youtube'] [data-cmp-gate-content]"));
check("native video notice hidden until interaction", !(await visible("[data-cmp-gate='youtube'] [data-cmp-gate-notice]")));
check("no request to YouTube or Vimeo before consent", videoRequests.length === 0, videoRequests.slice(0, 2).join(" "));
check("analytics script blocked", !(await demoLog()).some((l) => l.startsWith("analytics:loaded")));
check("decline handler ran exactly once", (await demoLog()).filter((l) => l === "analytics:declined /").length === 1, JSON.stringify(await demoLog()));
check("no cookie before decision", (await consentCookie()) === null);
await page.screenshot({ path: SHOTS + "01-notice-desktop.png" });

// 2. modal open / escape -------------------------------------------------------
await click("[data-cmp-notice] [data-cmp-action='open-modal']");
check("modal opens", await visible("[data-cmp-modal] [data-cmp-dialog]"));
check("notice hidden while modal open", !(await visible("[data-cmp-notice]")));
check(
  "focus moved into dialog",
  await page.evaluate(() => document.activeElement.closest("[data-cmp-dialog]") !== null)
);
check("essential switch checked + disabled", await page.evaluate(() => {
  const input = [...document.querySelectorAll("[data-cmp-modal] input[data-cmp-toggle='purpose:essential']")].find((el) => el.offsetParent);
  return input.checked && input.disabled;
}));
check("analytics switch unchecked", !(await shown("[data-cmp-modal] input[data-cmp-toggle='purpose:analytics']").first().isChecked()));
check("scroll locked while modal open", (await page.getAttribute("html", "data-cmp-open")) === "modal");
await openServices("essential");
await openServices("media");
await page.screenshot({ path: SHOTS + "02-modal-desktop.png" });
await page.keyboard.press("Escape");
check("escape closes modal", !(await visible("[data-cmp-modal] [data-cmp-dialog]")));
check("notice back after closing unconfirmed modal", await visible("[data-cmp-notice]"));

// 3. partial consent via purpose toggle -------------------------------------------
await click("[data-cmp-notice] [data-cmp-action='open-modal']");
await click("[data-cmp-modal] label[for='consent-purpose-en-analytics']");
check("purpose toggle checks its service", await page.locator("input[data-cmp-toggle='service:google-analytics']").first().isChecked());
await openServices("media");
await click("[data-cmp-modal] input[data-cmp-toggle='service:youtube']");
check("media purpose indeterminate", await page.evaluate(() => document.querySelector("input[data-cmp-toggle='purpose:media']").indeterminate));
await click("[data-cmp-modal] input[data-cmp-toggle='service:youtube']");
await click("[data-cmp-modal] [data-cmp-action='save']");
let cookie = await consentCookie();
check("saved selection", cookie?.consents["google-analytics"] === true && cookie?.consents.youtube === false, JSON.stringify(cookie?.consents));
check("UI closed after save", !(await visible("[data-cmp-notice]")) && !(await visible("[data-cmp-modal] [data-cmp-dialog]")));
check("analytics script executed", (await demoLog()).includes("analytics:loaded /"));
check("analytics script executed exactly once", (await demoLog()).filter((l) => l === "analytics:loaded /").length === 1);
check("activated scripts appended to head", (await page.locator("head script[data-cmp-for='google-analytics']").count()) === 2);
check("live status shows analytics allowed", await visible("[data-cmp-status='google-analytics'] [data-cmp-if='granted']"));
check("live status shows youtube blocked", await visible("[data-cmp-status='youtube'] [data-cmp-if='denied']"));
check("only one status label per row", (await shown("[data-cmp-status='youtube'] [data-cmp-if]").count()) === 1);

// 4. contextual consent gate ------------------------------------------------------
const playButton = page.locator("[data-cmp-gate='youtube'] [data-cmp-gate-content] button").first();
await playButton.click();
check("play click shows consent overlay", await visible("[data-cmp-gate='youtube'] [data-cmp-gate-notice]"));
check("play click held back (no player yet)", (await page.locator("[data-cmp-gate='youtube'] iframe").count()) === 0 && videoRequests.length === 0);
check("focus moves into gate notice", await page.evaluate(() => !!document.activeElement.closest("[data-cmp-gate-notice]")));
await page.keyboard.press("Escape");
check("Escape dismisses gate notice", !(await visible("[data-cmp-gate='youtube'] [data-cmp-gate-notice]")));
await playButton.click();
await click("[data-cmp-gate='youtube'] [data-cmp-action='accept-once']");
await page.waitForSelector("[data-cmp-gate='youtube'] iframe[src*='youtube-nocookie']", { timeout: 10000 }).catch(() => {});
check("gate replays play click after accept", await visible("[data-cmp-gate='youtube'] iframe[src*='youtube-nocookie']"));
check("gate notice hidden after accept", !(await visible("[data-cmp-gate='youtube'] [data-cmp-gate-notice]")));
cookie = await consentCookie();
check("accept once is not persisted", cookie?.consents.youtube === false);

// 5. client-side navigation -------------------------------------------------------
await page.evaluate(() => (window.__spaMarker = true));
await click("footer a[href='/privacy']");
await page.waitForURL("**/privacy");
await page.waitForSelector("[data-cmp-gate='google-maps']");
await page.waitForTimeout(300);
const spa = await page.evaluate(() => window.__spaMarker === true);
check("navigation was client-side (SPA)", spa);
check("notice stays closed after navigation", !(await visible("[data-cmp-notice]")));
check("maps gate denied on new page", await visible("[data-cmp-gate='google-maps'] [data-cmp-gate-notice]"));
check("managed script re-activated on new page", (await demoLog()).includes("analytics:loaded /privacy"));
check("switches re-synced after remount", await page.evaluate(() =>
  document.querySelector("input[data-cmp-toggle='service:google-analytics']").checked &&
  !document.querySelector("input[data-cmp-toggle='service:google-maps']").checked
));
check("inline script ran once for the new page", (await demoLog()).filter((l) => l === "analytics:loaded /privacy").length === 1);

// 6. accept all from the modal on the second page ---------------------------------------
await click("nav [data-cmp-action='open-modal']");
check("modal opens after navigation", await visible("[data-cmp-modal] [data-cmp-dialog]"));
check("returning visitor sees saved switches", await page.locator("input[data-cmp-toggle='service:google-analytics']").first().isChecked());
await click("[data-cmp-modal] footer [data-cmp-action='accept-all']");
await page.waitForTimeout(1100);
cookie = await consentCookie();
check("accept all persisted", Object.values(cookie?.consents ?? {}).every(Boolean), JSON.stringify(cookie?.consents));
check("modal closed after confirm delay", !(await visible("[data-cmp-modal] [data-cmp-dialog]")));
check("maps gate granted without reload", await visible("[data-cmp-gate='google-maps'] iframe[src*='google.com/maps']"));

await page.goBack();
await page.waitForSelector("[data-cmp-gate='youtube']");
await page.waitForTimeout(300);
await page.locator("[data-cmp-gate='youtube'] [data-cmp-gate-content] button").first().click();
await page.waitForSelector("[data-cmp-gate='youtube'] iframe[src*='youtube-nocookie']", { timeout: 10000 }).catch(() => {});
check("granted native video plays without overlay", (await visible("[data-cmp-gate='youtube'] iframe[src*='youtube-nocookie']")) && !(await visible("[data-cmp-gate='youtube'] [data-cmp-gate-notice]")));

// 6b. returning visitor with consent: scripts run once after hydration ---------------
await page.goto(BASE + "/", { waitUntil: "networkidle" });
check("returning visitor: script runs exactly once", (await demoLog()).filter((l) => l === "analytics:loaded /").length === 1, JSON.stringify(await demoLog()));
await page.locator("[data-cmp-gate='youtube'] [data-cmp-gate-content] button").first().click();
await page.waitForSelector("[data-cmp-gate='youtube'] iframe[src*='youtube-nocookie']", { timeout: 10000 }).catch(() => {});
check("returning visitor: native video plays directly", await visible("[data-cmp-gate='youtube'] iframe[src*='youtube-nocookie']"));
check("returning visitor: notice hidden", !(await visible("[data-cmp-notice]")));

// 7. reset + decline removes cookies ----------------------------------------------
await page.evaluate(() => (document.cookie = "_ga=GA1.1.test; path=/"));
await click("nav [data-cmp-action='reset']");
check("reset reopens notice", await visible("[data-cmp-notice]"));
await click("[data-cmp-notice] [data-cmp-action='decline-all']");
cookie = await consentCookie();
check("decline all persisted", cookie && !cookie.consents["google-analytics"] && cookie.consents["consent-manager"] === true, JSON.stringify(cookie?.consents));
check("tracking cookie deleted on decline", !(await context.cookies()).some((c) => c.name === "_ga"));
check("revoke stops the native player", (await page.locator("iframe[src*='youtube-nocookie']").count()) === 0);

// 8. reload: no flash, stays closed -------------------------------------------------
await page.reload({ waitUntil: "domcontentloaded" });
check("returning visitor: notice hidden right after DOMContentLoaded", !(await visible("[data-cmp-notice]")));

// 9. changed service list re-asks ----------------------------------------------------
const stale = { consents: { "consent-manager": true, "google-analytics": true }, timestamp: new Date().toISOString(), version: 1 };
await context.addCookies([{ name: "cmp_consent", value: encodeURIComponent(JSON.stringify(stale)), url: BASE }]);
await page.goto(BASE + "/", { waitUntil: "networkidle" });
check("changed services reopen notice", await visible("[data-cmp-notice]"));
check("changes message visible", await visible("[data-cmp-notice] [data-cmp-if='changed']"));
check("unconfirmed consent not applied", !(await demoLog()).some((l) => l.startsWith("analytics:loaded")));

// 10. keyboard focus trap ---------------------------------------------------------------
await click("[data-cmp-notice] [data-cmp-action='open-modal']");
for (let i = 0; i < 40; i++) await page.keyboard.press("Tab");
check("focus trapped in dialog", await page.evaluate(() => document.activeElement.closest("[data-cmp-dialog]") !== null));
await page.keyboard.press("Escape");

// 10b. languages -----------------------------------------------------------------------
const lang = await browser.newContext({ viewport: { width: 1280, height: 860 } });
const lp = await lang.newPage();
lp.on("pageerror", (error) => errors.push(error.message));
await lp.goto(BASE + "/de", { waitUntil: "networkidle" });
check("de page: html language resolved", (await lp.getAttribute("html", "data-cmp-language")) === "de");
check("de page: German notice visible", await visible("[data-cmp-notice] >> text=Ihre Privatsphäre ist uns wichtig", lp));
check("de page: English notice hidden", !(await visible("[data-cmp-notice] >> text=We value your privacy", lp)));
const noticeBoxes = await lp.evaluate(() => [...document.querySelectorAll("[data-cmp-notice]")].filter((el) => el.getClientRects().length > 0).length);
check("de page: exactly one notice rendered", noticeBoxes === 1, String(noticeBoxes));
await click("[data-cmp-notice] [data-cmp-action='open-modal']", lp);
check("de page: German modal and services", (await visible("[data-cmp-dialog] >> text=Datenschutz-Einstellungen", lp)) && (await visible("[data-cmp-dialog] >> text=Externe Medien", lp)));
check("de page: required badge translated", await visible("[data-cmp-dialog] >> text=Immer aktiv", lp));
await lp.screenshot({ path: SHOTS + "05-modal-de.png" });
await lp.keyboard.press("Escape");
await click("a[href='/es']", lp);
await lp.waitForURL("**/es");
await lp.waitForTimeout(400);
check("SPA de → es switches language", (await lp.getAttribute("html", "data-cmp-language")) === "es" && (await visible("[data-cmp-notice] >> text=Tu privacidad nos importa", lp)));
await click("[data-cmp-notice] [data-cmp-action='accept-all']", lp);
check("es page: status labels translated", await visible("[data-cmp-status='youtube'] >> text=Permitido", lp));
await click("a[href='/']", lp);
await lp.waitForURL(BASE + "/");
await lp.waitForTimeout(400);
check("SPA es → en switches back", (await lp.getAttribute("html", "data-cmp-language")) === "en");
await click("header [data-cmp-action='open-modal']", lp);
check("en modal after language switch", await visible("[data-cmp-dialog] >> text=Privacy settings", lp));
check("consent shared across languages", await lp.evaluate(() => [...document.querySelectorAll("input[data-cmp-toggle='service:youtube']")].every((el) => el.checked)));
await lp.keyboard.press("Escape");
await lp.evaluate(() => (document.documentElement.lang = "de-AT"));
await lp.waitForTimeout(100);
check("regional tag falls back to primary language", (await lp.getAttribute("html", "data-cmp-language")) === "de");
await lp.evaluate(() => (document.documentElement.lang = "fr"));
await lp.waitForTimeout(100);
check("unknown language falls back to first entry", (await lp.getAttribute("html", "data-cmp-language")) === "en");
await lang.close();

// 10b-rtl. Arabic, right-to-left ---------------------------------------------------------
{
  const rc = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const rp = await rc.newPage();
  rp.on("pageerror", (error) => errors.push(error.message));
  await rp.goto(BASE + "/ar", { waitUntil: "networkidle" });
  check("ar: language resolved", (await rp.getAttribute("html", "data-cmp-language")) === "ar");
  check("ar: Arabic notice visible", await visible("[data-cmp-notice] >> text=نحن نحترم خصوصيتك", rp));
  check("ar: notice laid out right-to-left", await rp.evaluate(() => {
    const notice = [...document.querySelectorAll("[data-cmp-notice]")].find((el) => el.getClientRects().length);
    return getComputedStyle(notice).direction === "rtl" && notice.closest("[data-cmp-lang]").getAttribute("dir") === "rtl";
  }));
  check("ar: notice fits the viewport", await rp.evaluate(() => {
    const r = [...document.querySelectorAll("[data-cmp-notice]")].find((el) => el.getClientRects().length).getBoundingClientRect();
    return r.left >= 0 && r.right <= innerWidth + 1 && document.documentElement.scrollWidth <= innerWidth + 1;
  }));
  await click("[data-cmp-notice] [data-cmp-action='open-modal']", rp);
  check("ar: modal in Arabic", await visible("[data-cmp-dialog] >> text=إعدادات الخصوصية", rp));
  check("ar: switches mirrored", await rp.evaluate(() => {
    const input = [...document.querySelectorAll("[data-cmp-dialog] input[data-cmp-toggle]")].find((el) => el.offsetParent);
    return getComputedStyle(input).scale.startsWith("-1");
  }));
  check("ar: close button sits on the left", await rp.evaluate(() => {
    const dialog = [...document.querySelectorAll("[data-cmp-dialog]")].find((el) => el.offsetParent);
    const close = dialog.querySelector("[data-cmp-action='close']").getBoundingClientRect();
    const title = dialog.querySelector("h2").getBoundingClientRect();
    return close.right <= title.left + 1;
  }));
  await rp.screenshot({ path: SHOTS + "61-modal-ar-mobile.png" });
  await rp.keyboard.press("Escape");
  await click("[data-cmp-notice] [data-cmp-action='decline-all']", rp);
  const arGate = rp.locator("[data-cmp-gate='youtube']");
  await arGate.scrollIntoViewIfNeeded();
  await arGate.locator("[data-cmp-gate-content] button").first().click();
  check("ar: native gate notice in Arabic", await visible("[data-cmp-gate='youtube'] [data-cmp-gate-notice] >> text=تحميل المحتوى", rp));
  await rp.screenshot({ path: SHOTS + "62-gate-ar-mobile.png" });
  await rc.close();
}

// 10c. examples & docs pages --------------------------------------------------------------
const dc = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const dp = await dc.newPage();
dp.on("pageerror", (error) => errors.push(error.message));
await dp.goto(BASE + "/", { waitUntil: "networkidle" });
await click("[data-cmp-notice] [data-cmp-action='decline-all']", dp);
await dp.evaluate(() => (window.__spaMarker = true));
await click("header a[href='/examples']", dp);
await dp.waitForURL("**/examples");
await dp.waitForSelector("article#google-analytics");
check("examples: reached via SPA navigation", await dp.evaluate(() => window.__spaMarker === true));
check("examples: 23 service examples", (await dp.locator("article[id]").count()) === 23);
check("examples: complete configuration is valid JSON", await dp.evaluate(() => {
  const blocks = [...document.querySelectorAll("#complete-configuration pre")].map((pre) => pre.textContent);
  try { return blocks.length === 2 && blocks.every((text) => JSON.parse(text)); } catch { return false; }
}));
check("examples: every service entry is valid JSON", await dp.evaluate(() =>
  [...document.querySelectorAll("article[id]")].every((article) => { try { JSON.parse(article.querySelector("pre").textContent); return true; } catch { return false; } })
));
check("examples: code blocks do not wrap", await dp.evaluate(() => {
  const pre = document.querySelector("article#meta-pixel pre");
  return pre.scrollWidth > pre.clientWidth || getComputedStyle(pre.querySelector("code")).width !== "auto";
}));
check("examples: consent UI still closed after navigation", !(await visible("[data-cmp-notice]", dp)));
await dp.screenshot({ path: SHOTS + "30-examples.png" });
await click("header a[href='/docs']", dp);
await dp.waitForURL("**/docs");
await dp.waitForSelector("#javascript-api");
check("docs: 15 sections", (await dp.locator("[id] > h2").count()) >= 15);
check("docs: sidebar links resolve to sections", await dp.evaluate(() =>
  [...document.querySelectorAll("aside nav a[href^='#']")].every((a) => document.querySelector(a.getAttribute("href")))
));
check("docs: tables rendered", (await dp.locator("table").count()) >= 9);
await click("aside a[href='#consent-mode']", dp);
await dp.waitForTimeout(400);
check("docs: anchor scrolls below sticky header", await dp.evaluate(() => {
  const top = document.querySelector("#consent-mode").getBoundingClientRect().top;
  return top >= 60 && top < 200;
}));
check("docs: sidebar stays visible while scrolling", await dp.evaluate(() => document.querySelector("aside").getBoundingClientRect().top >= 0));
await dp.screenshot({ path: SHOTS + "31-docs.png" });
await click("footer [data-cmp-action='open-modal']", dp);
check("docs: privacy settings open from footer", await visible("[data-cmp-dialog]", dp));
await dc.close();

// 10d. config generator --------------------------------------------------------------------
{
  const { readFileSync } = await import("node:fs");
  const gc = await browser.newContext({ viewport: { width: 1440, height: 900 }, permissions: ["clipboard-read", "clipboard-write"] });
  const gp = await gc.newPage();
  gp.on("pageerror", (error) => errors.push(error.message));
  await gp.goto(BASE + "/generator", { waitUntil: "networkidle" });
  await click("[data-cmp-notice] [data-cmp-action='decline-all']", gp);
  const out = (name) => gp.locator(`[data-gen-output="${name}"]`).textContent();
  const outJson = async (name) => JSON.parse(await out(name));
  await gp.waitForFunction(() => document.querySelector('[data-gen-output="custom-code"]').textContent.includes("data-cmp-engine"));
  check("generator: catalog has 23 services", (await gp.locator("[data-gen-row]").count()) === 23);
  check("generator: default output is only the consent manager", (await outJson("services")).length === 1);
  check("generator: fields hidden until selected", !(await visible("[data-gen-row='google-analytics'] [data-gen-fields]", gp)));

  await gp.locator("input[data-gen-service='google-analytics']").check();
  check("generator: fields shown after selecting", await visible("[data-gen-row='google-analytics'] [data-gen-fields]", gp));
  await gp.locator("[data-gen-field='google-analytics.measurementId']").fill("G-TEST12345");
  await gp.locator("input[data-gen-service='youtube']").check();
  await gp.locator("[data-gen-field='youtube.url']").fill("https://www.youtube.com/watch?v=abcDEF12345");
  await gp.locator("input[data-gen-service='google-maps']").check();
  await gp.locator("[data-gen-field='google-maps.query']").fill("Berlin Mitte");
  let code = await out("custom-code");
  check("generator: Custom Code ships the --cmp-* theme with Craft fallbacks", code.includes("--cmp-accent:var(--background-accent, #1d4ed8)") && !code.includes("--theme-accent"));
  check("generator: Custom Code excludes this site's own analytics", !code.includes("insight.nativecmp.com") && !code.includes("91dc1cbbaee5"));
  check("generator: head script uses entered ID", code.includes("gtag/js?id=G-TEST12345") && code.includes('data-cmp-service="google-analytics"'));
  check("generator: embeds are not in Custom Code", !code.includes("maps?q="));
  check("generator: embed card with entered place", await gp.evaluate(() => [...document.querySelectorAll("[data-gen-output-list='embeds'] .gen-card pre")].some((pre) => pre.textContent.includes("maps?q=Berlin Mitte"))));
  check("generator: Custom Code includes theme defaults", code.includes("<style data-cmp-theme>:where(html){--cmp-background"));
  await gp.locator("body").click({ position: { x: 5, y: 5 } });
  await gp.waitForTimeout(100);
  await gp.locator("[data-gen-embed='Google Maps'] button", { hasText: "Copy Consent Gate" }).click();
  await gp.waitForTimeout(300);
  const gateText = await gp.evaluate(() => navigator.clipboard.readText());
  const gate = validFragment(gateText);
  if (!gate) {
    try {
      const parsed = JSON.parse(gateText);
      console.log("gate debug:", JSON.stringify(webstudioFragment.safeParse(parsed[WS_CLIPBOARD]).error?.issues?.slice(0, 3)));
    } catch (error) {
      console.log("gate debug: not JSON", error.message, gateText.slice(0, 160));
    }
  }
  check("generator: gate clipboard is a valid Webstudio fragment", !!gate);
  check("generator: gate targets the service with the embed", !!gate && gate.props.some((p) => p.name === "data-cmp-gate" && p.value === "google-maps") && gate.props.some((p) => p.name === "code" && p.value.includes("maps?q=Berlin Mitte")));
  check("generator: gate texts name the provider", !!gate && JSON.stringify(gate.instances).includes("Always allow Google Maps"));
  await gp.locator("[data-gen-embed='YouTube'] button", { hasText: "Copy Consent Gate" }).click();
  await gp.waitForTimeout(200);
  const nativeGate = validFragment(await gp.evaluate(() => navigator.clipboard.readText()));
  check("generator: native YouTube gate is a valid fragment", !!nativeGate);
  check("generator: native gate uses interaction mode", !!nativeGate && nativeGate.props.some((p) => p.name === "data-cmp-gate-mode" && p.value === "interaction"));
  const ytInstance = nativeGate && nativeGate.instances.find((i) => i.component === "YouTube");
  const ytProp = (name) => nativeGate && nativeGate.props.find((p) => p.instanceId === ytInstance.id && p.name === name);
  check("generator: native YouTube component configured privacy-safe", !!ytInstance && ytProp("url").value === "https://www.youtube.com/watch?v=abcDEF12345" && ytProp("showPreview").value === false && ytProp("autoplay").value === false && ytProp("preconnect").value === false && ytProp("privacyEnhancedMode").value === true);
  await click("[data-gen-copy='link']", gp);
  await gp.waitForTimeout(200);
  const link = validFragment(await gp.evaluate(() => navigator.clipboard.readText()));
  check("generator: privacy link clipboard is a valid fragment", !!link && link.props.some((p) => p.name === "data-cmp-action" && p.value === "open-modal"));
  const services = await outJson("services");
  check("generator: services JSON", services.some((s) => s.name === "google-analytics" && s.cookies.includes("^_ga")) && services.some((s) => s.name === "youtube"));

  await gp.locator("[data-gen-language-pick]").selectOption("de");
  await click("[data-gen-action='add-language']", gp);
  await gp.locator("input[data-gen-option='consentMode']").check();
  const translations = await outJson("translations");
  const de = translations.find((t) => t.lang === "de");
  check("generator: German translations", translations.length >= 2 && de.purposes.some((p) => p.title === "Statistik" && p.services[0].description === "Erhebt pseudonyme Nutzungsstatistiken."));
  code = await out("custom-code");
  await gp.locator("[data-gen-language-pick]").selectOption("fr");
  await click("[data-gen-action='add-language']", gp);
  await gp.locator("[data-gen-language-code]").fill("tr");
  await click("[data-gen-action='add-language']", gp);
  await gp.locator("[data-gen-language-code]").fill("AR");
  await click("[data-gen-action='add-language']", gp);
  let langs = await outJson("translations");
  check("generator: built-in French texts", langs.find((t) => t.lang === "fr")?.notice.title === "Nous respectons votre vie privée");
  check("generator: any language code accepted", langs.some((t) => t.lang === "tr") && langs.find((t) => t.lang === "tr").notice.title === "We value your privacy");
  const serviceText = (lang, name) => langs.find((t) => t.lang === lang)?.purposes.flatMap((p) => p.services).find((s) => s.name === name)?.description;
  check("generator: French service descriptions", serviceText("fr", "google-analytics") === "Collecte des statistiques d’utilisation pseudonymisées.");
  check("generator: Arabic service descriptions", serviceText("ar", "youtube") === "يشغّل مقاطع الفيديو المضمّنة. قد يحفظ يوتيوب ملفات تعريف الارتباط عند تحميل الفيديو.");
  check("generator: catalog descriptions not marked for translation", (await gp.locator("[data-gen-t='ar::service.google-maps.description'].gen-input-fallback").count()) === 0 && (await gp.locator("[data-gen-t='fr::service.google-analytics.description'].gen-input-fallback").count()) === 0);
  check("generator: RTL detected for Arabic", langs.find((t) => t.lang === "ar")?.dir === "rtl" && langs.find((t) => t.lang === "fr")?.dir === "ltr");
  check("generator: editor marks untranslated texts", (await gp.locator("details[data-gen-editor-language='tr'] .gen-badge").count()) > 10);
  await gp.locator("details[data-gen-editor-language='tr'] summary").click();
  await gp.locator("[data-gen-t='tr::notice.title']").fill("Gizliliğinize önem veriyoruz");
  langs = await outJson("translations");
  check("generator: edited translation in output", langs.find((t) => t.lang === "tr").notice.title === "Gizliliğinize önem veriyoruz");
  check("generator: editor keeps focus while typing", await gp.evaluate(() => document.activeElement?.getAttribute("data-gen-t") === "tr::notice.title"));
  check("generator: RTL editor inputs", await gp.locator("[data-gen-t='ar::notice.title']").getAttribute("dir") === "rtl");
  await gp.locator("[data-gen-embed='YouTube'] select, [data-gen-output-list='embeds'] select[data-gen-option='gateLanguage']").first().selectOption("ar");
  await gp.waitForTimeout(100);
  await gp.locator("[data-gen-embed='YouTube'] button", { hasText: "Copy Consent Gate" }).click();
  await gp.waitForTimeout(200);
  const arabicText = await gp.evaluate(() => navigator.clipboard.readText());
  const arabicGate = validFragment(arabicText);
  if (!arabicGate || !JSON.stringify(arabicGate.instances).includes("تحميل المحتوى")) console.log("arabic gate debug:", !!arabicGate, arabicText.includes("تحميل المحتوى"), arabicText.slice(0, 80), await gp.evaluate(() => window.cmpGenerator.state().options));
  check("generator: gate texts localized", !!arabicGate && JSON.stringify(arabicGate.instances).includes("تحميل المحتوى"));
  await gp.locator("[data-gen-remove-language='fr']").click();
  check("generator: language removed", !(await outJson("translations")).some((t) => t.lang === "fr"));
  check("generator: consent mode mapping", /"analytics_storage": \[\s*"google-analytics"\s*\]/.test(code));

  await gp.locator("[data-gen-custom='title']").fill("Booking Widget");
  await gp.locator("[data-gen-custom='cookies']").fill("^_bw, bw_session");
  await gp.locator("[data-gen-custom='purpose']").selectOption("functional");
  await click("[data-gen-action='add-custom']", gp);
  check("generator: custom service added", (await outJson("services")).some((s) => s.name === "booking-widget" && s.cookies.length === 2));
  check("generator: custom service listed", (await gp.locator("[data-gen-custom-list] .gen-custom-row").count()) === 1);

  const sample = readFileSync("/Users/cosimokroll/Documents/GitHub/klaro/dist/config.js", "utf8");
  await gp.locator("[data-gen-import]").fill(sample);
  await click("[data-gen-action='import']", gp);
  const importMessage = await gp.locator("[data-gen-import-message]").textContent();
  check("generator: JavaScript config imported", /Imported 10 services/.test(importMessage), importMessage);
  const imported = await outJson("services");
  check("generator: known services matched to catalog", ["matomo", "youtube", "intercom"].every((name) => imported.filter((s) => s.name === name).length === 1));
  check("generator: regex cookies converted", imported.some((s) => s.name === "matomo" && s.cookies.includes("^_pk_.*$")));
  check("generator: functions in pasted config not executed", await gp.evaluate(() => !window.__executed));

  await gp.locator("[data-gen-import]").fill("[{ name: 'x', onInit: function () { window.__executed = true } }] trailing garbage");
  await click("[data-gen-action='import']", gp);
  check("generator: pasted code never runs", await gp.evaluate(() => !window.__executed));
  await gp.locator("[data-gen-import]").fill("{ broken: ");
  await click("[data-gen-action='import']", gp);
  check("generator: invalid input shows an error", await gp.locator("[data-gen-import-message][data-gen-error]").count() === 1);

  await gp.locator("[data-gen-output='services']").evaluate((node) => (node.closest("details").open = true));
  await click("[data-gen-copy='services']", gp);
  await gp.waitForTimeout(200);
  const clip = await gp.evaluate(() => navigator.clipboard.readText());
  check("generator: copy button copies output", clip === (await out("services")));
  await click("[data-gen-copy='component']", gp);
  await gp.waitForTimeout(300);
  const component = validFragment(await gp.evaluate(() => navigator.clipboard.readText()));
  check("generator: Consent Manager clipboard is a valid Webstudio fragment", !!component);
  const referencedIds = component ? [...JSON.stringify(component.props).matchAll(/\$ws\$dataSource\$([A-Za-z0-9_]+)/g)].map((m) => m[1].replaceAll("__DASH__", "-")) : [];
  const fragmentSources = new Set((component?.dataSources || []).map((source) => source.id));
  check("generator: Consent Manager clipboard keeps Builder preview flags wired", !!component && ["canvasPreview", "canvasLanguage"].every((name) => component.dataSources.some((source) => source.name === name)) && referencedIds.length > 0 && referencedIds.every((id) => fragmentSources.has(id)), [...new Set(referencedIds.filter((id) => !fragmentSources.has(id)))].join(","));
  check("generator: component is a Slot with the full UI", !!component && component.instances[0].component === "Slot" && component.instances.length > 40 && component.styleSources.some((s) => s.name === "consent-notice"));
  const variable = (name) => component && component.dataSources.find((d) => d.type === "variable" && d.name === name);
  check("generator: component carries generated services", !!component && JSON.stringify(variable("consentServices").value.value) === JSON.stringify(await outJson("services")));
  check("generator: component carries generated translations", !!component && JSON.stringify(variable("consentTranslations").value.value) === JSON.stringify(await outJson("translations")));
  check("generator: component expressions only reference included data", !!component && (() => {
    const ids = new Set(component.dataSources.map((d) => d.id));
    const refs = JSON.stringify(component.props.concat(component.instances)).match(/\$ws\$dataSource\$[\w-]+/g) || [];
    return refs.every((ref) => ids.has(ref.slice("$ws$dataSource$".length).replaceAll("__DASH__", "-")));
  })());

  code = await out("custom-code");
  await gp.reload({ waitUntil: "networkidle" });
  await gp.waitForFunction(() => document.querySelector('[data-gen-output="custom-code"]').textContent.includes("data-cmp-engine"));
  check("generator: state survives reload", (await out("custom-code")) === code && (await gp.locator("input[data-gen-service='google-analytics']").isChecked()));
  await gp.screenshot({ path: SHOTS + "40-generator.png" });

  // the generated snippet must actually work on a blank page
  const test = await gc.newPage();
  test.on("pageerror", (error) => errors.push("generated: " + error.message));
  await test.goto("about:blank");
  check("engine survives blocked cookies", await test.evaluate((snippet) => {
    const frame = document.createElement("iframe");
    frame.setAttribute("sandbox", "allow-scripts");
    frame.srcdoc = snippet.replace("<\/head>", "<\/head>") ;
    return new Promise((resolve) => { window.addEventListener("message", (e) => resolve(e.data === "ok")); frame.srcdoc = `<html><head>${snippet}</head><body><script>try{cmp.acceptAll();cmp.reset();parent.postMessage("ok","*")}catch(e){parent.postMessage("fail","*")}<\/script></body></html>`; document.body.appendChild(frame); setTimeout(() => resolve(false), 4000); });
  }, code));
  const blank = `<!doctype html><html lang="de"><head>${code}</head><body><div hidden data-cmp-service-def="google-analytics" data-cmp-cookies="^_ga"></div><div hidden data-cmp-service-def="consent-manager" data-cmp-required="true"></div></body></html>`;
  await test.route("http://generated.test/**", (route) => route.request().url() === "http://generated.test/" ? route.fulfill({ contentType: "text/html", body: blank }) : route.abort());
  await test.goto("http://generated.test/");
  await test.waitForFunction(() => window.cmp && window.cmp.getServices().length === 2);
  check("generated snippet: engine boots", await test.evaluate(() => window.cmp.version === "1.3.0" && document.documentElement.getAttribute("data-cmp") === "ready"));
  check("generated snippet: consent mode default sent", await test.evaluate(() => (window.dataLayer || []).some((e) => e[0] === "consent" && e[1] === "default" && e[2].analytics_storage === "denied")));
  check("generated snippet: GA blocked before consent", await test.evaluate(() => !document.querySelector("head script[data-cmp-for='google-analytics']")));
  await test.evaluate(() => window.cmp.acceptAll());
  check("generated snippet: GA activated after consent", await test.evaluate(() => !!document.querySelector("head script[data-cmp-for='google-analytics'][src*='G-TEST12345']")));
  await test.close();

  // contextual consent only
  await gp.locator("[data-gen-option='mustConsent']").check();
  await gp.locator("[data-gen-option='noNotice']").check();
  await gp.waitForTimeout(300);
  const contextualCode = await out("custom-code");
  check("generator: contextual-only option sets noNotice and clears mustConsent", /noNotice"?\s*:\s*true/.test(contextualCode) && !/mustConsent"?\s*:\s*true/.test(contextualCode) && !(await gp.locator("[data-gen-option='mustConsent']").isChecked()));
  const ctx = await gc.newPage();
  const contextualPage = `<!doctype html><html lang="en"><head>${contextualCode}</head><body>
    <div hidden data-cmp-service-def="youtube"></div><div hidden data-cmp-service-def="consent-manager" data-cmp-required="true"></div>
    <section data-cmp-notice>notice</section>
    <div data-cmp-gate="youtube"><div data-cmp-gate-notice><button data-cmp-action="accept-once">Load</button><button id="always" data-cmp-action="accept-always" data-cmp-if="confirmed">Always</button></div><div data-cmp-gate-content><iframe data-cmp-service="youtube" data-src="about:blank#video"></iframe></div></div>
  </body></html>`;
  await ctx.route("http://contextual.test/**", (route) => route.request().url() === "http://contextual.test/" ? route.fulfill({ contentType: "text/html", body: contextualPage }) : route.abort());
  await ctx.goto("http://contextual.test/");
  await ctx.waitForFunction(() => window.cmp && document.documentElement.getAttribute("data-cmp") === "ready");
  check("contextual mode: no notice on page load", await ctx.evaluate(() => !document.documentElement.hasAttribute("data-cmp-open") && document.documentElement.getAttribute("data-cmp-mode") === "contextual" && !document.querySelector("[data-cmp-notice]").offsetParent));
  check("contextual mode: Always allow visible before any decision", await ctx.locator("#always").isVisible());
  await ctx.locator("#always").click();
  const contextualState = await ctx.evaluate(() => ({ confirmed: window.cmp.isConfirmed(), youtube: window.cmp.getConsent("youtube"), cookie: document.cookie, src: document.querySelector("iframe").getAttribute("src") }));
  check("contextual mode: Always allow stores the decision", contextualState.confirmed && contextualState.youtube && contextualState.src === "about:blank#video", JSON.stringify(contextualState));
  await ctx.close();
  await gp.locator("[data-gen-option='noNotice']").uncheck();

  await click("[data-gen-action='reset']", gp);
  check("generator: reset clears selection", (await outJson("services")).length === 1);
  await gc.close();
}

// 10e. site chrome: page links, current link, shared content width ---------------------------
{
  const lc = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const lp = await lc.newPage();
  lp.on("pageerror", (error) => errors.push(error.message));
  const siteNav = () => lp.evaluate(() => [...document.querySelectorAll("body > header nav a, header[class] nav[aria-label='Main'] a")].map((a) => ({ text: a.textContent, href: a.getAttribute("href"), current: a.getAttribute("aria-current") })));
  await lp.goto(BASE + "/", { waitUntil: "networkidle" });
  let nav = await siteNav();
  check("header nav has no anchor links and no Home link", nav.length === 4 && nav[0].text === "AI install" && nav.every((link) => !link.href.includes("#")) && !nav.some((link) => link.text === "Home"), JSON.stringify(nav));
  check("logo links home", await lp.evaluate(() => { const logo = document.querySelector("nav[aria-label='Main']").parentElement.querySelector("a img"); return !!logo && logo.closest("a").getAttribute("href") === "/" && logo.alt === "Native CMP"; }));
  check("menu sits on the right next to the button", await lp.evaluate(() => {
    const nav = document.querySelector("nav[aria-label='Main']"); const button = nav.parentElement.querySelector("button");
    return button.getBoundingClientRect().left - nav.getBoundingClientRect().right < 60;
  }));
  check("favicon is the feather", await lp.evaluate(() => [...document.querySelectorAll("link[rel~='icon']")].some((l) => /favicon/.test(l.href))));
  await lp.evaluate(() => (window.__spaMarker = true));
  await lp.locator("nav[aria-label='Main'] a", { hasText: "Docs" }).click();
  await lp.waitForURL("**/docs");
  await lp.waitForTimeout(300);
  nav = await siteNav();
  check("page link navigates client-side", await lp.evaluate(() => window.__spaMarker === true));
  check("current link follows navigation", nav.filter((link) => link.current === "page").map((link) => link.text).join() === "Docs");
  check("current link is styled", await lp.evaluate(() => {
    const link = document.querySelector("nav[aria-label='Main'] a[aria-current='page']");
    return getComputedStyle(link).textDecorationLine.includes("underline") && getComputedStyle(link).fontWeight >= 600;
  }));
  for (const width of [1440, 800, 390]) {
    await lp.setViewportSize({ width, height: 900 });
    const edges = {};
    for (const path of ["/", "/examples", "/docs", "/generator", "/privacy"]) {
      await lp.goto(BASE + path, { waitUntil: "networkidle" });
      edges[path] = await lp.evaluate(() => {
        const left = (el) => Math.round(el.getBoundingClientRect().left);
        const right = (el) => Math.round(el.getBoundingClientRect().right);
        const inner = document.querySelector("nav[aria-label='Main']").parentElement;
        const content = document.querySelector("aside[ws\\:label], aside") && location.pathname === "/docs" ? document.querySelector("aside") : document.querySelector("fieldset") || document.querySelector("main h1") || document.querySelector("main");
        const footer = document.querySelector("footer span");
        const brand = inner.querySelector("a");
        return { header: left(brand), content: left(content), footer: left(footer), headerRight: right(inner.lastElementChild) };
      });
    }
    const lefts = Object.values(edges).flatMap((e) => [e.header, e.content, e.footer]);
    check(`content, header and footer share edges at ${width}px`, new Set(lefts).size === 1 && new Set(Object.values(edges).map((e) => e.headerRight)).size === 1, JSON.stringify(edges));
  }
  await lp.setViewportSize({ width: 390, height: 844 });
  await lp.goto(BASE + "/examples", { waitUntil: "networkidle" });
  const burger = lp.locator("header button[aria-haspopup='dialog']");
  check("mobile header: hamburger instead of inline nav and settings button", (await burger.isVisible()) && !(await lp.locator("header nav[aria-label='Main']").isVisible()) && !(await lp.locator("header > div > button[data-cmp-action='open-modal']").isVisible()) && (await lp.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)));
  check("mobile header: hamburger has an accessible name", (await lp.locator("header").getByRole("button", { name: "Open menu", exact: true }).count()) === 1);
  await burger.click();
  const sheet = lp.locator("[role='dialog']").filter({ has: lp.locator("nav[aria-label='Main']") });
  await sheet.waitFor();
  check("mobile menu: sheet lists page links with current page", (await sheet.locator("nav a").count()) === 4 && (await sheet.locator("nav a").first().innerText()) === "AI install" && (await sheet.locator("a[aria-current='page']").innerText()) === "Examples");
  await lp.keyboard.press("Escape");
  await sheet.waitFor({ state: "hidden" });
  check("mobile menu: Escape closes and returns focus", await lp.evaluate(() => document.activeElement?.getAttribute("aria-haspopup") === "dialog"));
  await burger.click();
  await sheet.locator("button[data-cmp-action='open-modal']").click();
  await sheet.waitFor({ state: "hidden" });
  await lp.waitForTimeout(300);
  check("mobile menu: Privacy settings closes the sheet and focuses the consent modal", await lp.evaluate(() => document.documentElement.getAttribute("data-cmp-open") === "modal" && !!document.activeElement?.closest("[data-cmp-modal]")));
  await lp.keyboard.press("Escape");
  await lp.waitForTimeout(200);
  check("mobile menu: closing the modal returns focus to the hamburger", await lp.evaluate(() => document.documentElement.getAttribute("data-cmp-open") !== "modal" && document.activeElement?.getAttribute("aria-haspopup") === "dialog"));
  await burger.click();
  await sheet.locator("a", { hasText: "Docs" }).click();
  await lp.waitForURL("**/docs");
  await lp.waitForTimeout(300);
  check("mobile menu: navigating closes the sheet", !(await sheet.isVisible()) && (await lp.evaluate(() => getComputedStyle(document.body).pointerEvents !== "none")));
  await lp.screenshot({ path: SHOTS + "80-header-mobile.png" });
  await lc.close();
}

// 10f. legal notice, 404, donation, Rybbit -------------------------------------------------
{
  const xc = await browser.newContext({ viewport: { width: 1280, height: 860 } });
  const xp = await xc.newPage();
  const legal = await xp.goto(BASE + "/legal-notice", { waitUntil: "networkidle" });
  const legalText = await xp.locator("main").innerText();
  check("legal notice: page with company details", legal.status() === 200 && ["ELECOS UG (haftungsbeschränkt)", "Hauptstr. 42", "16341 Panketal", "Cosimo Kroll", "HRB 18855 FF", "Amtsgericht Frankfurt (Oder)", "DE345721414", "info@elecos.de"].every((t) => legalText.includes(t)));
  check("footer: legal notice page link", (await xp.locator("footer a", { hasText: "Legal notice" }).getAttribute("href")) === "/legal-notice");
  const support = xp.locator("footer a[href^='https://www.paypal.com/cgi-bin/webscr?cmd=_xclick']");
  check("footer: support link opens PayPal payment in a new tab", (await support.count()) === 1 && (await support.getAttribute("target")) === "_blank" && (await support.getAttribute("href")).includes("business=info%40elecos.de") && (await support.innerText()).trim() === "Support the project");
  check("no PayPal requests before click", !(await xp.evaluate(() => performance.getEntriesByType("resource").some((r) => /paypal/i.test(r.name)))));
  const missing = await xp.goto(BASE + "/this-page-does-not-exist", { waitUntil: "networkidle" });
  check("404: status, heading and home link", missing.status() === 404 && (await xp.locator("h1").innerText()).includes("Page not found") && (await xp.locator("main a", { hasText: "Go to the homepage" }).getAttribute("href")) === "/");
  check("404: shared header and footer, no template badge", (await xp.locator("header nav[aria-label='Main'] a").count()) === 4 && (await xp.locator("footer nav[aria-label='Footer']").count()) === 1 && (await xp.locator("text=Built with Webstudio").count()) === 0);
  check("404: footer at viewport bottom", await xp.evaluate(() => Math.abs(document.querySelector("footer").getBoundingClientRect().bottom - innerHeight) < 2));
  await xp.screenshot({ path: SHOTS + "90-404.png" });
  check("site analytics: own Rybbit loads outside the CMP", (await xp.evaluate(() => [...document.querySelectorAll("script[src*='insight.nativecmp.com']")].filter((el) => !el.hasAttribute("data-cmp-service") && el.getAttribute("data-site-id") === "91dc1cbbaee5").length)) === 1);
  // SEO & GEO
  const seoPages = ["/", "/install", "/generator", "/examples", "/docs", "/de", "/es", "/ar", "/contact", "/legal-notice"];
  const seoIssues = [];
  for (const path of seoPages) {
    await xp.goto(BASE + path, { waitUntil: "domcontentloaded" });
    const meta = await xp.evaluate(() => ({
      title: document.title,
      description: document.querySelector("meta[name='description']")?.content || "",
      image: document.querySelector("meta[property='og:image']")?.content || "",
      card: document.querySelector("meta[property='twitter:card']")?.content,
      h1: document.querySelectorAll("h1").length,
      lang: document.documentElement.lang,
      robots: document.querySelector("meta[name='robots']")?.content || "",
    }));
    if (!meta.title || meta.title.length > 70 || meta.description.length < 50 || meta.description.length > 170 || !/og-.*\.png/.test(meta.image) || meta.card !== "summary_large_image" || meta.h1 !== 1 || !meta.lang || meta.robots.includes("noindex")) seoIssues.push(path + " " + JSON.stringify(meta));
  }
  check("seo: title, description, OG image, one h1 and lang on indexable pages", seoIssues.length === 0, seoIssues.join(" | "));
  await xp.goto(BASE + "/", { waitUntil: "domcontentloaded" });
  const ld = await xp.evaluate(() => [...document.querySelectorAll("script[type='application/ld+json']")].map((el) => JSON.parse(el.textContent)));
  const types = ld.flatMap((d) => d["@graph"] || [d]).map((n) => n["@type"]);
  check("seo: home JSON-LD with software, organization, website and FAQ", ["SoftwareApplication", "Organization", "WebSite", "FAQPage"].every((t) => types.includes(t)) && !JSON.stringify(ld).toLowerCase().includes("klaro"), types.join(","));
  check("seo: FAQ JSON-LD matches the visible FAQ", await xp.evaluate((data) => {
    const faq = data.flatMap((d) => d["@graph"] || [d]).find((n) => n["@type"] === "FAQPage");
    const visible = [...document.querySelectorAll("#faq summary")].map((el) => el.textContent.trim());
    return faq.mainEntity.length === visible.length && faq.mainEntity.every((q, i) => q.name === visible[i]);
  }, ld));
  const privacy = await xp.goto(BASE + "/privacy", { waitUntil: "domcontentloaded" });
  check("seo: placeholder privacy page and 404 are noindex", (await xp.locator("meta[name='robots']").getAttribute("content")).includes("noindex") && privacy.status() === 200);
  const sitemap = await (await xp.request.get(BASE + "/sitemap.xml")).text();
  check("seo: sitemap lists indexable pages only", ["/install", "/generator", "/examples", "/docs", "/contact"].every((path) => sitemap.includes(path + "</loc>")) && !sitemap.includes("/privacy<") && !sitemap.includes("/consent-preview<"));

  // theme knobs: overriding --cmp-* variables restyles the consent UI
  const themed = await xc.newPage();
  await themed.goto(BASE + "/", { waitUntil: "networkidle" });
  await themed.addStyleTag({ content: ":root{--cmp-accent:#0073b3;--cmp-radius:0;--cmp-button-radius:0;--cmp-button-border-width:2px;--cmp-button-transform:uppercase;--cmp-heading-font:Georgia,serif;--cmp-heading-transform:uppercase}" });
  await themed.evaluate(() => window.cmp.show());
  await themed.waitForTimeout(300);
  const knobs = await themed.evaluate(() => {
    const dialog = [...document.querySelectorAll("[data-cmp-dialog]")].find((el) => el.offsetParent);
    const primary = getComputedStyle(dialog.querySelector("[data-cmp-action='accept-all']"));
    const title = getComputedStyle(dialog.querySelector("h2"));
    return { dialogRadius: getComputedStyle(dialog).borderTopLeftRadius, bg: primary.backgroundColor, radius: primary.borderTopLeftRadius, border: primary.borderTopWidth, transform: primary.textTransform, font: title.fontFamily, titleTransform: title.textTransform, switchRadius: getComputedStyle(dialog.querySelector("input[role=switch]")).borderTopLeftRadius };
  });
  check("theme: --cmp-* knobs restyle dialog, buttons and headings (switch stays round)", knobs.dialogRadius === "0px" && knobs.bg === "rgb(0, 115, 179)" && knobs.radius === "0px" && knobs.border === "2px" && knobs.transform === "uppercase" && knobs.font.startsWith("Georgia") && knobs.titleTransform === "uppercase" && knobs.switchRadius === "999px", JSON.stringify(knobs));
  await themed.close();

  // Builder canvas: no engine, flags at their defaults
  const canvas = await xc.newPage();
  await canvas.route(BASE + "/examples", async (route) => {
    const res = await route.fetch();
    const html = (await res.text()).replace(/<script data-cmp-engine="[^"]*">[\s\S]*?<\/script>/, "").replace(/<style data-cmp-critical>[\s\S]*?<\/style>/, "");
    route.fulfill({ response: res, body: html });
  });
  await canvas.route(/\.js$/, (route) => route.abort());
  await canvas.goto(BASE + "/examples", { waitUntil: "load" });
  check("builder preview: flags off hide notice and dialog, first language only", await canvas.evaluate(() => !document.documentElement.hasAttribute("data-cmp")
    && [...document.querySelectorAll("[data-cmp-notice], [data-cmp-modal]")].every((el) => getComputedStyle(el).display === "none")
    && [...new Set([...document.querySelectorAll("[data-cmp-root] [data-cmp-lang]")].filter((el) => getComputedStyle(el).display !== "none").map((el) => el.getAttribute("data-cmp-lang")))].join() === "en"));
  await canvas.close();

  // agent install guide
  const text = async (path) => { const r = await xp.request.get(BASE + path); return { status: r.status(), type: r.headers()["content-type"] || "", body: await r.text() }; };
  const guide = await text("/install.txt");
  const llms = await text("/llms.txt");
  const bundleFile = await text("/install/steps.txt");
  const installer = await text("/install/install.js");
  const bundle = JSON.parse(bundleFile.body);
  check("agents: install.txt and llms.txt served as text", guide.status === 200 && guide.type.startsWith("text/plain") && guide.body.startsWith("# Install Native CMP") && llms.status === 200 && llms.body.includes("/install.txt") && !/klaro/i.test(guide.body + llms.body));
  check("agents: bundle matches the running engine", bundle.engineVersion === (await xp.evaluate(() => window.cmp.version)) && bundle.tokens.length > 30 && bundle.consentManager.collections.length === 4 && bundle.customCode.includes("data-cmp-engine") && !bundle.customCode.includes("insight.nativecmp.com"));
  const bundleRefs = new Set([...JSON.stringify(bundle.tokens).matchAll(/"type":"var","value":"([^"]+)"|var\((--[a-z0-9-]+)/g)].map((m) => m[1] || m[2].slice(2)));
  check("agents: bundle tokens only read defined --cmp-* variables", bundleRefs.size > 20 && [...bundleRefs].every((name) => name.startsWith("cmp-") && ("--" + name) in bundle.cssVariables) && Object.keys(bundle.cssVariables).every((name) => name.startsWith("--cmp-")), [...bundleRefs].filter((n) => !n.startsWith("cmp-")).join(","));
  check("agents: installer script served intact", installer.status === 200 && installer.body.startsWith("#!/usr/bin/env node") && installer.body.includes("insert-collection"));
  await xp.goto(BASE + "/docs", { waitUntil: "networkidle" });
  check("agents: docs start with the AI install and link the guide", (await xp.locator("#installation a[href='https://nativecmp.com/install.txt']").count()) === 1 && (await xp.locator("#installation h3").first().innerText()).startsWith("Install with an AI agent"));

  // communication: AI install first, then generator, examples, docs, starter
  await xp.goto(BASE + "/", { waitUntil: "networkidle" });
  const ways = await xp.locator("#install [data-ws-label='Install Ways'] > a, #install a h3").allInnerTexts();
  const heroPrimary = await xp.locator("main section").first().locator("a").first();
  check("home: hero primary action is Install with AI", (await heroPrimary.innerText()) === "Install with AI" && (await heroPrimary.getAttribute("href")) === "/install");
  check("home: install ways ordered AI, generator, examples, docs, starter", await xp.evaluate(() => {
    const titles = [...document.querySelectorAll("#install a h3")].map((h) => h.textContent.trim());
    const starter = [...document.querySelectorAll("#install a")].find((a) => a.textContent.includes("Starter project"));
    return JSON.stringify(titles) === JSON.stringify(["AI agent via Webstudio MCP", "Config generator", "Service examples", "Documentation", "Starter project"]) && starter?.getAttribute("href") === "https://starter.nativecmp.com";
  }));
  check("home: FAQ answers the AI install question first", (await xp.locator("#faq summary").first().innerText()) === "Can an AI agent install Native CMP?");
  const installPage = await xp.goto(BASE + "/install", { waitUntil: "networkidle" });
  check("install page: prompt names the guide and asks for a plan first", installPage.status() === 200 && await xp.evaluate(() => {
    const prompt = document.getElementById("agent-prompt")?.textContent || "";
    return prompt.includes("https://nativecmp.com/install.txt") && prompt.includes("privacy policy") && prompt.includes("before you change anything");
  }));
  check("install page: seven capabilities, three steps, four alternatives", (await xp.locator("main section").nth(1).locator("h3").count()) === 7 && (await xp.locator("main section").nth(2).locator("h3").count()) === 3 && (await xp.locator("main section").nth(3).locator("a[href='/generator'], a[href='/examples'], a[href='/docs']").count()) === 3 && (await xp.locator("main section").nth(3).locator("a[href*='apps.webstudio.is']").count()) === 1);
  check("install page: nav marks AI install as current", (await xp.locator("header nav[aria-label='Main'] a[aria-current='page']").innerText()) === "AI install");
  for (const path of ["/generator", "/examples"]) {
    await xp.goto(BASE + path, { waitUntil: "domcontentloaded" });
    check(`${path}: points to the AI install first`, (await xp.locator("main section").first().locator("a[href='/install']").count()) === 1);
  }

  const contact = await xp.goto(BASE + "/contact", { waitUntil: "networkidle" });
  const form = xp.locator("main form");
  const formInfo = await form.evaluate((f) => ({
    method: f.getAttribute("method"),
    enctype: f.getAttribute("enctype"),
    website: f.querySelector("input[name='website']")?.value,
    formular: f.querySelector("input[name='formular']")?.value,
    required: ["Name", "E-Mail", "Nachricht"].map((n) => f.querySelector(`[name='${n}']`)?.required),
    labels: [...f.querySelectorAll("label[for]")].every((l) => document.getElementById(l.htmlFor)),
    messages: f.querySelectorAll("[role='alert'], [role='status']").length,
  }));
  check("contact: native form with n8n field names", contact.status() === 200 && formInfo.method === "post" && formInfo.enctype === "multipart/form-data" && formInfo.formular === "kontakt" && formInfo.required.every(Boolean) && formInfo.labels, JSON.stringify(formInfo));
  check("contact: hidden website field carries the site origin", !!formInfo.website && new URL(formInfo.website).host === new URL(BASE).host, formInfo.website);
  check("contact: success and error messages hidden initially", formInfo.messages === 0 && (await xp.locator("main button[type='submit']").innerText()).includes("Send message"));
  check("footer: contact page link", (await xp.locator("footer nav[aria-label='Footer'] a", { hasText: "Contact" }).getAttribute("href")) === "/contact");
  await xp.screenshot({ path: SHOTS + "91-contact.png", fullPage: true });
  await xp.goto(BASE + "/", { waitUntil: "networkidle" });
  check("home: support section with PayPal payment link", (await xp.locator("#support a[href*='paypal.com/cgi-bin/webscr']").count()) === 1 && (await xp.locator("#support").innerText()).includes("not tax-deductible"));
  await xp.goto(BASE + "/de", { waitUntil: "networkidle" });
  check("footer: support link localized on /de", (await xp.locator("footer a[href*='paypal.com'] >> visible=true").innerText()).trim() === "Projekt unterstützen");
  await xp.goto(BASE + "/examples", { waitUntil: "networkidle" });
  check("examples: Rybbit card", (await xp.locator("article#rybbit").innerText()).includes("app.rybbit.io/api/script.js?siteId="));
  await xp.goto(BASE + "/generator", { waitUntil: "networkidle" });
  check("generator: support note", (await xp.locator("[data-gen-root] a[href*='paypal.com/cgi-bin/webscr']").count()) === 1);
  const row = xp.locator("[data-gen-row]", { hasText: "Rybbit" });
  await row.locator("input[type=checkbox]").first().check();
  await xp.locator("[data-gen-field='rybbit.siteId']").fill("abc123");
  await xp.locator("[data-gen-field='rybbit.siteId']").blur();
  await xp.waitForTimeout(300);
  const out = await xp.locator("[data-gen-output='custom-code']").innerText();
  check("generator: Rybbit head script with site ID", out.includes('data-cmp-service="rybbit"') && out.includes("https://app.rybbit.io/api/script.js?siteId=abc123"));
  await xc.close();
}

// 11. mobile ---------------------------------------------------------------------------
const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
const phone = await mobile.newPage();
await phone.goto(BASE + "/", { waitUntil: "networkidle" });
await phone.screenshot({ path: SHOTS + "03-notice-mobile.png" });
await click("[data-cmp-notice] [data-cmp-action='open-modal']", phone);
await phone.screenshot({ path: SHOTS + "04-modal-mobile.png" });
check("mobile modal fits viewport", await phone.evaluate(() => {
  const r = [...document.querySelectorAll("[data-cmp-dialog]")].find((el) => el.offsetParent).getBoundingClientRect();
  return r.left >= 0 && r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1;
}));

await phone.goto(BASE + "/generator", { waitUntil: "networkidle" });
await phone.evaluate(() => window.cmp.hide());
await phone.locator("input[data-gen-service='google-analytics']").check();
await phone.locator("summary", { hasText: "Updating an existing installation" }).click();
await phone.waitForTimeout(400);
check("mobile generator: update section doesn't overflow (only code blocks scroll)", await phone.evaluate(() => {
  const vw = document.documentElement.clientWidth;
  const details = [...document.querySelectorAll("details")].find((d) => d.open && d.textContent.includes("Updating an existing installation"));
  const tooWide = [...details.querySelectorAll("*")].filter((el) => !el.closest("pre") && el.getBoundingClientRect().right > vw + 1);
  return document.documentElement.scrollWidth <= vw && tooWide.length === 0;
}));

// consent log: consent ID in the dialog and one entry per decision, without an IP address
{
  const lc = await browser.newContext({ viewport: { width: 1280, height: 860 } });
  const lp = await lc.newPage();
  const logged = [];
  await lp.route("https://consentlog.test/**", async (route) => {
    logged.push(JSON.parse(route.request().postData() || "{}"));
    await route.fulfill({ status: 202, body: "ok", headers: { "access-control-allow-origin": "*" } });
  });
  await lp.addInitScript(() => {
    // the site assigns window.cmpConfig itself, so add the setting as it is assigned
    let value;
    Object.defineProperty(window, "cmpConfig", {
      configurable: true,
      get: () => value,
      set: (next) => {
        value = { ...next, consentLog: "https://consentlog.test/" };
      },
    });
    window.cmpConfig = {};
    // sendBeacon is invisible to request interception: record it and let the engine fall back to fetch
    window.__beacons = [];
    navigator.sendBeacon = (url) => {
      window.__beacons.push(String(url));
      return false;
    };
  });
  await lp.goto(BASE + "/", { waitUntil: "networkidle" });
  check("consent log: nothing is sent before a decision", logged.length === 0);

  await lp.locator('[data-cmp-notice] [data-cmp-action="accept-all"]:visible').first().click();
  await lp.waitForFunction(() => window.cmp.isConfirmed());
  await lp.waitForTimeout(500);
  const entry = logged[0] || {};
  const id = await lp.evaluate(() => window.cmp.getConsentId());
  check("consent log: one entry per decision, with the consent ID", logged.length === 1 && entry.id === id && id.length >= 16, `entries=${logged.length}`);
  check("consent log: entry has time, type, choices, config and language", /^\d{4}-\d{2}-\d{2}T/.test(entry.time) && entry.type === "accept" && entry.consents && entry.consents["consent-manager"] === true && !!entry.config && !!entry.language && entry.engine === "1.3.0");
  check("consent log: no IP address, page URL or user agent is sent", !JSON.stringify(entry).match(/\b\d{1,3}(\.\d{1,3}){3}\b|http|Mozilla/));

  const cookieId = await lp.evaluate(() => {
    const raw = document.cookie.split("; ").find((c) => c.startsWith("cmp_consent="));
    return JSON.parse(decodeURIComponent(raw.split("=").slice(1).join("=")))?.id;
  });
  check("consent log: the consent ID is stored in the cookie", cookieId === id);

  await lp.evaluate(() => window.cmp.show());
  await lp.waitForTimeout(300);
  const shown = await lp.evaluate(() => {
    const el = [...document.querySelectorAll("[data-cmp-modal] [data-cmp-consent-id]")].find((n) => n.offsetParent !== null);
    const row = el?.closest("[data-cmp-if]");
    return { text: el?.textContent || "", label: row?.textContent || "" };
  });
  check("consent log: the dialog shows the consent ID with a label", shown.text === id && shown.label.includes("Your consent ID"));

  await lp.locator('[data-cmp-modal] [data-cmp-action="save"]:visible').first().click();
  await lp.waitForTimeout(400);
  check("consent log: saving in the dialog logs another entry with the same ID", logged.length === 2 && logged[1].id === id && logged[1].type === "save", `entries=${logged.length}`);

  await lp.evaluate(() => window.cmp.reset());
  await lp.waitForTimeout(400);
  check("consent log: withdrawing logs a reset entry before the ID is dropped", logged.length === 3 && logged[2].type === "reset" && logged[2].id === id);
  const afterReset = await lp.evaluate(() => window.cmp.getConsentId());
  check("consent log: a new decision after reset gets a new consent ID", afterReset === "");

  // a site without the setting must send nothing at all
  const np = await lc.newPage();
  const stray = [];
  await np.route("https://consentlog.test/**", async (route) => {
    stray.push(route.request().url());
    await route.fulfill({ status: 202, body: "ok" });
  });
  await np.goto(BASE + "/", { waitUntil: "networkidle" });
  await np.locator('[data-cmp-notice] [data-cmp-action="accept-all"]:visible').first().click();
  await np.waitForTimeout(400);
  check("consent log: off by default", stray.length === 0);
  check("consent log: sent with sendBeacon so a decision is never delayed", (await lp.evaluate(() => window.__beacons.length)) === 3);
  await lc.close();
}

const relevantErrors = errors.filter((e) => !/youtube|google|favicon|ERR_|net::|Failed to load resource: the server responded with a status of 404/i.test(e) || /^4\d\d http(?!.*favicon)/.test(e));
check("no page errors", relevantErrors.length === 0, relevantErrors.slice(0, 3).join(" | "));

await browser.close();
const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
process.exit(failed.length ? 1 : 0);
