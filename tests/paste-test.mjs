import { chromium } from "playwright-core";
import { readFileSync } from "node:fs";
const b = await chromium.launch({ channel: "chrome" });
const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, permissions: ["clipboard-read", "clipboard-write"] });

// 1. produce clipboard payloads with the generator (local preview)
const g = await ctx.newPage();
await g.goto("http://127.0.0.1:5188/generator", { waitUntil: "networkidle" });
await g.evaluate(() => localStorage.removeItem("cmp-generator-v1"));
await g.reload({ waitUntil: "networkidle" });
await g.locator("input[data-gen-service='google-analytics']").check();
await g.locator("[data-gen-field='google-analytics.measurementId']").fill("G-PASTE123");
await g.locator("input[data-gen-service='vimeo']").check();
await g.locator("[data-gen-field='vimeo.videoId']").fill("123456789");
await g.locator("input[data-gen-option='language:de']").check();
const payloads = {
  component: await g.evaluate(() => window.cmpGenerator.component()),
  gate: await g.evaluate(async () => {
    document.querySelector("[data-gen-embed='Vimeo'] .gen-button-primary").click();
    await new Promise((r) => setTimeout(r, 300));
    return navigator.clipboard.readText();
  }),
};
payloads.link = await g.evaluate(async () => {
  document.querySelector("[data-gen-copy='link']").click();
  await new Promise((r) => setTimeout(r, 300));
  return navigator.clipboard.readText();
});
console.log("payload sizes", Object.fromEntries(Object.entries(payloads).map(([k, v]) => [k, v.length])));

// 2. paste into the Builder (reload before each paste so <body> is selected)
const w = await ctx.newPage();
for (const name of (process.env.ONLY ? process.env.ONLY.split(",") : ["component", "gate", "link"])) {
  await w.goto(readFileSync("../.temp/builder-url.txt", "utf8"), { waitUntil: "domcontentloaded", timeout: 60000 });
  await w.waitForSelector("text=Navigator", { timeout: 60000 });
  await w.waitForTimeout(7000);
  await w.evaluate((text) => navigator.clipboard.writeText(text), payloads[name]);
  await w.keyboard.press("ControlOrMeta+V");
  await w.waitForTimeout(6000);
  console.log("pasted", name);
}
await w.screenshot({ path: "screenshots/51-builder-pasted.png" });
await b.close();
