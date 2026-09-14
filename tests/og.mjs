// Renders 1200x630 Open Graph images into ../assets/og/ from an HTML template.
import { chromium } from "playwright-core";
import { readFileSync } from "node:fs";

const logo = readFileSync(new URL("../assets/native-cmp-logo.svg", import.meta.url), "utf8");
const IMAGES = [
  { file: "og-home", eyebrow: "Free for Webstudio", title: "Cookie consent, built natively in Webstudio.", text: "Scripts, embeds and videos stay blocked until visitors agree. SPA-ready, multilingual, styled with tokens." },
  { file: "og-install", eyebrow: "Install with AI", title: "Your AI agent sets it up for you.", text: "Finds and blocks scripts and embeds, configures cookies, updates your privacy policy and matches your design." },
  { file: "og-generator", eyebrow: "Config generator", title: "Your consent setup in minutes.", text: "Pick services, enter IDs, copy and paste the result into Webstudio." },
  { file: "og-examples", eyebrow: "Service examples", title: "23 services, ready to paste.", text: "Google Analytics, Tag Manager, Meta Pixel, YouTube, Maps, Rybbit and more." },
  { file: "og-docs", eyebrow: "Documentation", title: "Install, configure, translate, style.", text: "Attributes, variables, Consent Gates, JavaScript API and Google Consent Mode v2." },
  { file: "og-de", lang: "de", eyebrow: "Native CMP · Deutsch", title: "Cookie-Einwilligung, nativ in Webstudio.", text: "Skripte, Einbettungen und Videos bleiben blockiert, bis Besucher zustimmen." },
  { file: "og-es", lang: "es", eyebrow: "Native CMP · Español", title: "Consentimiento de cookies, nativo en Webstudio.", text: "Scripts, contenidos incrustados y vídeos bloqueados hasta que el visitante acepte." },
  { file: "og-ar", lang: "ar", dir: "rtl", eyebrow: "Native CMP · العربية", title: "موافقة ملفات تعريف الارتباط داخل Webstudio.", text: "تبقى النصوص البرمجية والمحتوى المضمّن ومقاطع الفيديو محظورة حتى يوافق الزائر." },
];

const html = (img) => `<!doctype html><html lang="${img.lang || "en"}" dir="${img.dir || "ltr"}"><head><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0}
body{width:1200px;height:630px;overflow:hidden;font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans Arabic",sans-serif;color:#15171c;
  background:radial-gradient(900px 500px at 100% 0%,rgba(29,78,216,.10),transparent 60%),#f3f4f6;display:grid;grid-template-columns:1fr 430px;column-gap:56px;padding:64px 72px}
.copy{display:grid;grid-template-rows:auto 1fr auto;min-width:0}.copy>div:nth-child(2){align-self:center;padding-block:24px}
.logo svg{width:250px;height:auto;display:block}
.eyebrow{margin:0 0 18px;font-size:22px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#1d4ed8}
[dir=rtl] .eyebrow{letter-spacing:0}
h1{margin:0;font-size:60px;line-height:1.05;letter-spacing:-.03em;font-weight:780}
[dir=rtl] h1{letter-spacing:0;line-height:1.3;font-size:54px}
p.text{margin:22px 0 0;font-size:26px;line-height:1.4;color:#4d5461}
.url{font-size:22px;font-weight:600;color:#4d5461}
.mock{align-self:center;display:grid;row-gap:18px}
.card{background:#fff;border:1px solid #dde0e5;border-radius:22px;box-shadow:0 24px 64px -12px rgba(0,0,0,.18);padding:28px}
.card h2{margin:0 0 10px;font-size:24px}
.line{height:12px;border-radius:6px;background:#dde0e5;margin-top:10px}
.btns{display:flex;gap:10px;margin-top:22px;justify-content:flex-end}
.btn{height:44px;border-radius:999px;border:2px solid #15171c;flex:0 0 120px}
.btn.primary{background:#1d4ed8;border-color:#1d4ed8}
.row{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-top:1px solid #dde0e5}
.row:first-of-type{border-top:0}
.row span{display:block;height:12px;width:150px;border-radius:6px;background:#dde0e5}
.sw{width:52px;height:30px;border-radius:999px;background:#6f7582;position:relative}
.sw::after{content:"";position:absolute;top:4px;inset-inline-start:4px;width:22px;height:22px;border-radius:50%;background:#fff}
.sw.on{background:#1d4ed8}.sw.on::after{inset-inline-start:26px}
</style></head><body>
<div class="copy">
  <div class="logo">${logo}</div>
  <div><p class="eyebrow">${img.eyebrow}</p><h1>${img.title}</h1><p class="text">${img.text}</p></div>
  <div class="url">nativecmp.com</div>
</div>
<div class="mock" aria-hidden="true">
  <div class="card"><h2>${img.dir === "rtl" ? "خصوصيتك مهمة" : img.lang === "de" ? "Ihre Privatsphäre" : img.lang === "es" ? "Tu privacidad" : "We value your privacy"}</h2><div class="line"></div><div class="line" style="width:80%"></div><div class="btns"><div class="btn"></div><div class="btn primary"></div></div></div>
  <div class="card"><div class="row"><span></span><div class="sw on"></div></div><div class="row"><span style="width:110px"></span><div class="sw"></div></div><div class="row"><span style="width:170px"></span><div class="sw on"></div></div></div>
</div>
</body></html>`;

const browser = await chromium.launch({ channel: "chrome", headless: true });
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
for (const img of IMAGES) {
  await page.setContent(html(img), { waitUntil: "load" });
  await page.screenshot({ path: new URL(`../assets/og/${img.file}.png`, import.meta.url).pathname });
}
await browser.close();
console.log(IMAGES.map((i) => i.file).join(", "));
