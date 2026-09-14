// Records computed styles of the consent UI so a refactor can be proven visually identical.
import { chromium } from "playwright-core";
import { writeFileSync } from "node:fs";
const out = process.argv[2];
const BASE = "http://127.0.0.1:5188";
const PROPS = ["color", "background-color", "background-image", "border-top-width", "border-top-color", "border-top-left-radius", "border-bottom-right-radius", "box-shadow", "font-family", "font-size", "font-weight", "text-transform", "letter-spacing", "line-height", "padding-top", "padding-left", "margin-top", "gap", "row-gap", "column-gap", "width", "height", "z-index", "transition-duration", "transition-timing-function", "outline-color", "outline-width", "outline-offset", "opacity", "display", "position"];
const b = await chromium.launch({ channel: "chrome", headless: true });
const result = {};
for (const [name, width] of [["desktop", 1280], ["mobile", 390]]) {
  const ctx = await b.newContext({ viewport: { width, height: 900 } });
  await ctx.route(/insight\.nativecmp\.com|youtube|google|ytimg|vimeo/, (r) => r.abort());
  const p = await ctx.newPage();
  await p.goto(BASE + "/", { waitUntil: "networkidle" });
  const grab = async (label) => {
    result[`${name}:${label}`] = await p.evaluate((PROPS) => {
      const pick = (sel) => [...document.querySelectorAll(sel)].filter((el) => el.offsetParent || getComputedStyle(el).position === "fixed").slice(0, 3);
      const sels = ["[data-cmp-notice]", "[data-cmp-notice] h2, [data-cmp-notice] p", "[data-cmp-notice] button", "[data-cmp-dialog]", "[data-cmp-modal] [data-cmp-dialog] h2", "[data-cmp-dialog] button", "[data-cmp-dialog] input[role=switch]", "[data-cmp-dialog] [data-cmp-purpose]", "[data-cmp-dialog] summary", "[data-cmp-dialog] [data-cmp-if]", "[data-cmp-gate]", "[data-cmp-gate] [data-cmp-gate-notice]", "[data-cmp-gate] button", "[data-cmp-status]", "[data-cmp-modal] > div:first-child"];
      const o = {};
      for (const sel of sels) pick(sel).forEach((el, i) => { const cs = getComputedStyle(el); o[`${sel}#${i}`] = Object.fromEntries(PROPS.map((k) => [k, cs.getPropertyValue(k)])); const before = getComputedStyle(el, "::before"); if (before.content !== "none") o[`${sel}#${i}::before`] = Object.fromEntries(PROPS.map((k) => [k, before.getPropertyValue(k)])); });
      return o;
    }, PROPS);
  };
  await grab("notice");
  await p.locator("[data-cmp-notice] [data-cmp-action='open-modal'] >> visible=true").click();
  await p.waitForTimeout(400);
  await p.locator("[data-cmp-dialog] input[role=switch] >> visible=true").nth(1).focus();
  await grab("modal");
  await ctx.close();
}
writeFileSync(out, JSON.stringify(result, null, 1));
console.log("snapshot", out, Object.values(result).reduce((n, o) => n + Object.keys(o).length, 0), "elements");
await b.close();
