import { chromium } from "playwright-core";
const b = await chromium.launch({ channel: "chrome", headless: true });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
await p.route(/insight\.nativecmp\.com|youtube|google|ytimg/, (r) => r.abort());
await p.goto("http://127.0.0.1:5188/", { waitUntil: "networkidle" });
await p.addStyleTag({ content: `:root{--cmp-accent:#0073B3;--cmp-radius:0;--cmp-button-radius:0;--cmp-button-border-width:2px;--cmp-button-transform:uppercase;--cmp-button-letter-spacing:0.02em;--cmp-heading-font:Georgia,serif;--cmp-heading-transform:uppercase;--cmp-heading-weight:700;--cmp-shadow:none}` });
await p.locator("[data-cmp-notice] [data-cmp-action='open-modal'] >> visible=true").click();
await p.waitForTimeout(400);
console.log(await p.evaluate(() => {
  const d = [...document.querySelectorAll("[data-cmp-dialog]")].find((el) => el.offsetParent);
  const cs = (el, ...props) => Object.fromEntries(props.map((k) => [k, getComputedStyle(el).getPropertyValue(k)]));
  return {
    dialog: cs(d, "border-top-left-radius", "box-shadow"),
    title: cs(d.querySelector("h2"), "font-family", "text-transform", "font-weight"),
    primary: cs(d.querySelector("[data-cmp-action='accept-all']"), "background-color", "border-top-left-radius", "border-top-width", "text-transform", "letter-spacing"),
    secondary: cs(d.querySelector("[data-cmp-action='decline-all']"), "border-top-width", "border-top-left-radius"),
    switchRadius: getComputedStyle(d.querySelector("input[role=switch]")).borderTopLeftRadius,
  };
}));
await p.screenshot({ path: "screenshots/knobs-modal.png" });
await b.close();
