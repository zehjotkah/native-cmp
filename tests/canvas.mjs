// Simulates the Builder canvas: same page, but without the Custom Code engine and critical CSS.
import { chromium } from "playwright-core";
const [name] = process.argv.slice(2);
const b = await chromium.launch({ channel: "chrome", headless: true });
const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
await p.route("http://127.0.0.1:5188/examples", async (route) => {
  const res = await route.fetch();
  let html = await res.text();
  html = html.replace(/<script data-cmp-engine="[^"]*">[\s\S]*?<\/script>/, "").replace(/<style data-cmp-critical>[\s\S]*?<\/style>/, "");
  route.fulfill({ response: res, body: html });
});
await p.route(/\.js$/, (r) => r.abort()); // no hydration: static canvas-like render
await p.route(/insight\.nativecmp\.com/, (r) => r.abort());
await p.goto("http://127.0.0.1:5188/examples", { waitUntil: "load" });
console.log(name, await p.evaluate(() => ({
  engine: document.documentElement.hasAttribute("data-cmp"),
  notice: [...document.querySelectorAll("[data-cmp-notice]")].some((el) => el.offsetParent || getComputedStyle(el).position === "fixed" && getComputedStyle(el).display !== "none"),
  modal: [...document.querySelectorAll("[data-cmp-modal]")].some((el) => getComputedStyle(el).display !== "none"),
  visibleLangs: [...document.querySelectorAll("[data-cmp-languages] > [data-cmp-lang], [data-cmp-lang]")].filter((el) => el.closest("[data-cmp-root]") && getComputedStyle(el).display !== "none").map((el) => el.getAttribute("data-cmp-lang")).filter((v, i, a) => a.indexOf(v) === i),
})));
await p.screenshot({ path: `screenshots/canvas-${name}.png` });
await b.close();
