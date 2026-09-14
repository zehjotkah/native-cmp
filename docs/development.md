# Native CMP

Consent management for cookies, third-party scripts and embeds, built from native Webstudio instances.

- **UI**: native instances inside the shared **Consent Manager** Slot, styled with Craft composite Tokens (`consent-*`) and Global Root variables.
- **Data**: `consentServices` (technical setup) and `consentTranslations` (copy per language) on the Consent Manager root, rendered by nested Collections. The language follows each page's Language setting.
- **Engine**: ~18 KB minified (~7 KB gzipped) script in Project Settings → Custom Code. It runs once in `<head>`, before the body paints, and survives client-side navigation.

## Project layout in Webstudio

| Where | What |
| --- | --- |
| Project Settings → Custom Code | `cmpConfig`, critical CSS, engine, and consent-managed head scripts |
| Global Root → CSS variables | Craft theme and semantic variables (see below) |
| Slot **Consent Manager** | Service registry, plus one notice and preferences modal per language |
| Variable `consentServices` (on the Consent Manager root) | Technical service setup (JSON) |
| Variable `consentTranslations` (on the Consent Manager root) | Texts, purposes and service descriptions per language (JSON) |
| Home `/` | Marketing onepager: explains and demonstrates the CMP (live status, gates, code examples) |
| Home → **Used By** section | Logo marquee of sites that use Native CMP, right after the Hero. Two data sources on the section: the **Used By Logos** Assets resource (`usedByLogos`: every asset whose file name starts with `used-by-`, sorted by file name, so image URLs are right on the canvas, the published site and the local preview) and the `usedBy` JSON variable, which maps each logo file name to `{ "name", "url" }`. `name` is the logo's alt text, so it is the link name. Two Collections render the logos: the second list is an `aria-hidden` loop copy with `tabindex="-1"` links, so the scroll is seamless. Logos without a `usedBy` entry stay hidden. **Add a site**: upload `used-by-<site>.png` (or `.svg`) in Assets, then add `"used-by-<site>.png": { "name": "…", "url": "https://…/" }` to `usedBy`. Tokens `site-marquee`, `site-marquee-list` (40 s loop, 16 s on phones), `site-marquee-item`, `site-used-by-link` (grayscale until hover/focus), `site-used-by-logo`, `is-site-section-compact`. The Marquee Motion embed holds the keyframes, pauses on hover and focus, and shows a static centered row for `prefers-reduced-motion`. Source: `USED_BY` and `USED_BY_LOGOS` in `scripts/onepager.py`, inserted once by `scripts/used_by.py` |
| `/install` | **Install with AI** (recommended, first in navigation, hero and Install section): copyable prompt for Claude Code, Codex or Cursor, what the agent does (scan, block scripts and embeds, cookies and texts, privacy policy section, design, verification), three steps and the other ways to install. Source: `scripts/install_page.py`, copy in `scripts/comm.py` |
| `/generator` | Config generator: pick catalog services and enter their IDs, add custom services or import an existing config (JSON or a JavaScript config object, parsed without executing it). It produces copy buttons for the Custom Code, a paste-ready Consent Manager Slot with the generated variables, a Consent Gate per embed and the Privacy settings link |
| `/examples` | Service library: 23 ready-to-copy configurations (GA4, GTM + Consent Mode, Meta Pixel, Matomo, Plausible, Rybbit, YouTube, Maps, Calendly, …) plus a complete combined configuration |
| `/docs` | Complete documentation with sidebar navigation |
| `/de`, `/es`, `/ar` | The same Slot in German, Spanish and Arabic (right-to-left, native YouTube gate): only Page Settings → Language differs |
| `/privacy` | Second page for SPA navigation tests |
| `/contact` | Contact page with a native Webstudio **Form**: POST resource to the ELECOS n8n webhook (`https://n8n.elecos.de/webhook/submit`, `Content-Type: application/json`), form state in the `contactState` page variable (`initial`/`success`/`error` via `data-ws-show`), hidden `website` (= `system.origin`) and `formular` (`kontakt`) fields, and `Name`, `E-Mail`, `Nachricht` field names matching the existing n8n workflow |
| Starter and source links | The [Native CMP Starter](https://starter.nativecmp.com) is a separate Webstudio project with the engine, Consent Manager, a `/consent-preview` design page and YouTube/Vimeo gates, built with the installer. Its read-only share link (cloneable) and the GitHub repository are linked from the footer (**Starter**, **GitHub**), the fifth card in `/install` → Other ways, the docs (Overview license paragraph, Installation), `llms.txt` and `install.txt`. URLs: `GITHUB_URL`, `STARTER_URL`, `STARTER_CLONE_URL` in `scripts/comm.py` |
| Communication order | AI install → generator → examples → documentation, on Home (hero, Install section, FAQ), in the navigation, footer, docs (Installation section), generator and examples intros, and `llms.txt`. |
| `/install.txt`, `/install/steps.txt`, `/install/install.js`, `/llms.txt` | Text pages for AI agents, served with `.txt`/`.js` extensions because Cloudflare's bot challenge on Webstudio sites skips static-file extensions but blocks `.md`, `.json`, `.mjs` and HTML for non-browser clients. `install.txt` tells an agent with the Webstudio MCP how to install the CMP; `steps.txt` (JSON with the service catalog: detection patterns, cookies, descriptions in 10 languages, providers and privacy links; translation templates; privacy policy templates in en/de; generated by `scripts/install_bundle.py` from the live Consent Manager) contains CSS variables, 45 design tokens as typed style values, the Custom Code snippet, JSX per collection level, starter variables, theme variable roles, a localized Privacy settings link and gate templates (embed gate JSX, YouTube/Vimeo gate shells plus component props) with gate texts in 10 languages; `install.js` (`src/install.mjs`, save it as `.mjs` to run; `--contextual` sets `noNotice`) runs those steps through the Webstudio CLI (verified by installing on a temporary page and comparing the result instance by instance). Rebuild and publish all four with `python3 scripts/agent_docs.py` |
| `/legal-notice` | Legal notice (Impressum) of ELECOS UG (haftungsbeschränkt), linked from the footer |
| `/*` (404) | Not-found page with the shared header, footer and Consent Manager, links to home, generator, examples and docs; excluded from search |
| Asset `webstudio-native-cmp-logo.svg` | Brand logo in the Site Header (Image component, token `site-logo`: 48 px, 40 px on phones). Cropped copy of `Webstudio_Native_CMP_Logo.svg`, kept in `assets/`. |
| Slots **Site Header** / **Site Footer** | Shared on every site page. Menu links are Webstudio page links (`href` of type page), so the current page gets `aria-current="page"`, styled through the `site-nav-link` state. Privacy settings and Support labels use `data-cmp-lang` spans. |
| Builder preview | Custom Code doesn't run in the Builder. The Consent Manager root has `canvasPreview` (`off`/`notice`/`modal`) and `canvasLanguage` variables; the Canvas Helper embed's `code` is an expression of both and only acts while `html:not([data-cmp])`, i.e. on the canvas. The install bundle creates both variables and binds the helper after they exist (`consentManager.bindings`). |
| Mobile menu | From the tablet breakpoint down, the header shows a hamburger that opens Webstudio's native Radix **Sheet** (Dialog) with the page links (current page styled via `aria-current`) and the Privacy settings button as a `DialogClose`, so the sheet closes before the consent modal opens. Tokens `site-menu-*`, `is-site-desktop-only`, `site-visually-hidden`. The engine keeps focus inside the consent modal while other dialogs restore focus (v1.2.1). |
| SEO & GEO | Page titles, descriptions, 1200×630 Open Graph images (`assets/og/`, rendered by `tests/og.mjs`), site name, JSON-LD (`scripts/seo.py`: Organization, WebSite, SoftwareApplication, FAQPage on Home; WebApplication, CollectionPage, TechArticle, ContactPage), noindex for the placeholder privacy page, 404 and design preview, `/llms.txt`. The Webstudio audit reports 0 SEO findings. |
| Contextual consent only | Generator option (`noNotice: true`): no notice on page load; gates and the Privacy settings link ask for consent, and **Always allow** stores the decision right away (`data-cmp-mode="contextual"` on `<html>`). |
| Support payments | Voluntary PayPal payment link to ELECOS UG (standard payment, payer chooses the amount, not a donation) in the footer, the Home **Support** section and the generator output, to help cover running costs like the domain. No PayPal script or SDK loads on the site. The URL lives in `scripts/chrome.py` (`SUPPORT_URL`). |
| `/consent-preview` (draft) | Design frames that show the notice and modal inline on canvas |

**Add the Consent Manager Slot to every page**, or to a page template. On canvas, the fixed notice and modal stay hidden on normal pages and only the first language is shown; design them on `/consent-preview`.

## Services (`consentServices`)

```json
[
  { "name": "consent-manager", "required": true },
  { "name": "google-analytics", "cookies": ["^_ga", "_gid"], "default": false, "optOut": false,
    "onlyOnce": false, "contextualOnly": false, "dependsOn": [] }
]
```

| Field | Meaning |
| --- | --- |
| `name` | Service key used by `data-cmp-service`, `data-cmp-gate` and `data-cmp-status` |
| `cookies` | Cookies deleted when consent is missing or revoked. A pattern starting with `^` is a regex; otherwise it matches the exact name. Deletion is tried for the host, `.host` and parent domains. Patterns are joined with spaces, so don't put spaces inside a pattern. |
| `required` | Always on; the switch is disabled and the "Always active" badge is shown |
| `default` | Preselected in the modal before the visitor decides |
| `optOut` | Runs before the visitor decides, until they decline ("Active by default" badge) |
| `onlyOnce` | Activated scripts run at most once per page load, even across SPA navigation |
| `contextualOnly` | Not affected by "Accept all" / "Decline all"; only by its switch or a gate |
| `dependsOn` | Enabling this service enables the listed services; disabling one of them disables this service |

A service that appears in `consentTranslations` but not in `consentServices` gets default settings.

Changing the service list makes returning visitors see the notice again, including the "Our services have changed" message. Until they decide, no non-required service runs.

## Languages (`consentTranslations`)

One entry per language. The engine shows the entry that matches the page's **Page Settings → Language**, which Webstudio renders as `<html lang>`:

1. The exact tag (`de-at`).
2. The primary language (`de-AT` → `de`), or a regional entry for the same language.
3. `cmpConfig.fallbackLanguage`, else the first entry.

The match updates live when client-side navigation changes `lang`. Consent is shared across languages.

```json
[
  {
    "lang": "en",
    "privacyLabel": "privacy policy",
    "privacyUrl": "/privacy",
    "notice": { "title": "…", "text": "…", "changes": "…", "customize": "…", "decline": "…", "accept": "…" },
    "modal": { "title": "…", "text": "…", "close": "…", "toggleAll": "…", "alwaysActive": "…", "activeByDefault": "…",
               "service": "service", "services": "services", "decline": "…", "save": "…", "accept": "…" },
    "purposes": [
      { "id": "analytics", "title": "Analytics", "description": "…",
        "services": [{ "name": "google-analytics", "title": "Google Analytics", "description": "…" }] }
    ]
  }
]
```

The Slot contains English, German, Spanish and Arabic. To add a language, copy an entry and translate it; the design stays shared.

**Any language, right-to-left:**
- Any language code works.
- Each entry may set `"dir": "rtl"` or `"ltr"`. Otherwise the language wrapper's `dir` is detected from the code (`ar`, `arc`, `ckb`, `dv`, `fa`, `he`, `ku`, `ps`, `sd`, `ug`, `ur`, `yi`).
- Tokens mirror through flex and grid, logical properties and `:dir(rtl)` states (`consent-switch`, `consent-modal-close`).
- Set `dir="rtl"` on the Body of right-to-left pages for your own content.

**Generator language support:**
- Notice, modal, purpose and gate texts (`scripts/languages.py`) and descriptions for all 23 catalog services (`catalog.py`, `service_descriptions.py`) in en, de, es, fr, it, pt, nl, pl, ar and he.
- A translation editor for every language code, with RTL-aware inputs and "English – translate" markers.
- Gate copies in the chosen language.

For any other element, such as a footer link in a shared Slot, add `data-cmp-lang="de"`. Only elements matching the page language are shown.

Implementation note: the language Collection's item parameter is renamed to `language`, so the nested purpose and service Collections can read `language.modal.*`.

## Blocking scripts and embeds

Put the markup in an **HTML Embed**, or in Custom Code for head scripts.

```html
<!-- external script -->
<script type="text/plain" data-cmp-service="google-analytics" data-type="text/javascript"
        data-src="https://www.googletagmanager.com/gtag/js?id=G-XXXX"></script>

<!-- inline script: runs on consent -->
<script type="text/plain" data-cmp-service="google-analytics">gtag('config', 'G-XXXX');</script>

<!-- inline script: runs when consent is denied or revoked -->
<script type="text/plain" data-cmp-service="google-analytics" data-cmp-on="decline">…</script>

<!-- any markup: stamped on consent, removed on revoke (best for iframes/widgets) -->
<template data-cmp-service="youtube">
  <iframe src="https://www.youtube-nocookie.com/embed/ID" …></iframe>
</template>

<!-- in-place attribute swap (iframe, img, video, audio, source, embed, object, link) -->
<iframe data-cmp-service="youtube" data-src="https://…"></iframe>
<link rel="stylesheet" data-cmp-service="google-fonts" data-href="https://fonts.googleapis.com/…">
```

Activated scripts are appended to `<head>`. Identical external `src` URLs load only once per page load. Inline scripts run once per rendered element, so on SPA navigation a page's own embed runs again, just as it would without the CMP.

## Contextual consent gate

Gates have two modes:

- **Placeholder (default):** the content stays hidden until consent.
- **Interaction (`data-cmp-gate-mode="interaction"`):** the content stays visible. The first click inside `data-cmp-gate-content` is held back, the notice overlays the content, and after **Load content** or **Always allow** the click is replayed.
  - `data-cmp-action="dismiss"` or Escape closes the notice.
  - While the notice is open, the gate has `data-cmp-requested`.
  - Revoking consent stops a loaded native player (`about:blank`).

**Webstudio's YouTube and Vimeo components:** put them in an interaction-mode gate with `data-cmp-gate-content`.
- Turn off **Show preview**, **Autoplay** and **Preconnect**; for YouTube keep **Privacy enhanced mode** on, for Vimeo turn **Do not track** on.
- Upload your own Preview Image.
- With these settings nothing contacts YouTube or Vimeo before consent. The e2e suite checks this at the network level.

### Placeholder gate

Copy the **Consent Gate** from Home or `/consent-preview`:

```
div[data-cmp-gate="youtube"]            .consent-gate
├─ div[data-cmp-gate-notice]            .consent-gate-notice   (visible until consent)
│   ├─ button[data-cmp-action="accept-once"]
│   ├─ button[data-cmp-action="accept-always"][data-cmp-if="confirmed"]
│   └─ button[data-cmp-action="open-modal"]
└─ HtmlEmbed[data-cmp-gate-content]     .consent-gate-content  (template/iframe, shown on consent)
```

## Attribute API

| Attribute | Values |
| --- | --- |
| `data-cmp-action` (any element, anywhere on the site) | `accept-all`, `decline-all`, `save`, `open-modal`, `close`, `accept-once`, `accept-always`, `dismiss`, `reset` |
| `data-cmp-gate-mode` (gate wrapper) | `interaction` |
| `data-cmp-toggle` (checkbox) | `service:<name>`, `purpose:<id>`, `all` |
| `data-cmp-if` | Page-wide: `confirmed`, `unconfirmed`, `changed`. Row-level (closest service, purpose, status or gate): `required`, `not-required`, `opt-out`, `granted`, `denied` |
| `data-cmp-status="<service>"` | Live status element; gets `data-cmp-state` and drives `data-cmp-if="granted/denied"` children |
| `data-cmp-lang="<code>"` | Shown only when it matches the page language |
| `data-cmp-notice`, `data-cmp-modal`, `data-cmp-dialog` | Notice, modal and focus-trapped dialog regions |
| `data-cmp-preview="notice|modal"` | Design frame wrapper, shown inline on canvas |

State hooks for styling:

- On `<html>`: `data-cmp-open="notice|modal"`, `data-cmp-confirmed`, `data-cmp-changed`, `data-cmp-confirming`, `data-cmp-language`.
- On gates and managed elements: `data-cmp-state="granted|denied"`.

## Configuration (Custom Code)

```js
window.cmpConfig = {
  storage: "cookie",            // or "localStorage"
  storageName: "cmp_consent",
  cookieExpiresAfterDays: 365,
  cookieDomain: "",             // ".example.com" to share across subdomains
  default: false,
  mustConsent: false,           // open the modal instead of the notice
  noNotice: false,              // contextual consent only: no notice on page load
  confirmDelay: 800,
  dataLayer: false,             // push { event: "cmp_consent", cmp_consents } on decisions
  consentMode: {                // Google Consent Mode v2 (default "denied", updated on decisions)
    analytics_storage: ["google-analytics"],
    ad_storage: ["google-ads"], ad_user_data: ["google-ads"], ad_personalization: ["google-ads"],
  },
  fallbackLanguage: "",         // language when no translation matches <html lang>
  debug: false,
};
```

## JavaScript API

```js
cmp.show();                  // open preferences
cmp.getConsent("youtube");   // effective consent
cmp.getLanguage();           // resolved language, e.g. "de"
cmp.getConsents();
cmp.setConsent("youtube", true);
cmp.acceptAll(); cmp.declineAll(); cmp.reset();
cmp.on("save", ({ type, consents, changes }) => {});
// events: ready, change, save, service, init, modal, gate — also dispatched as `cmp:<event>` on document
```

## Craft design system

The Tokens follow [Craft](webstudio_craft.md). BEM structure is mapped onto Craft names:

| BEM | Craft Token |
| --- | --- |
| block `consent-notice` | `consent-notice` |
| element `consent-notice__title` | `consent-notice-title` |
| modifier `consent-button--primary` | `is-consent-button-primary` (always combined with `consent-button`) |

Consent tokens (`consent-*` and variant tokens `is-consent-*`) only read the namespaced **`--cmp-*` variables** defined in `scripts/theme.py` (41 variables: colors, radii including `--cmp-button-radius`, shadow, spacing, motion, layer, and typography knobs for headings and buttons). Each defaults to the matching Craft variable if the project defines it, otherwise to a neutral value: `--cmp-accent: var(--background-accent, #1d4ed8)`. `design.py` applies the same rules to the token definitions (`_apply_cmp_theme`).

This site's own `site-*` tokens keep the Craft theme and semantic variables (`--theme-*`, `--foreground-*`, `--background-*`, …), which the `--cmp-*` variables pick up.

Onepager Tokens use the `site-*` namespace (`site-section`, `is-site-section-muted`, `site-card`, `site-code`, …). They're not needed for the CMP itself. The live status chips (`consent-status`, `consent-status-label`, `is-consent-status-label-granted`) are part of the kit.

Accessibility:

- Default pairings meet WCAG 2.2 AA: body text ≥ 6.8:1, accent buttons 7.1:1, switch tracks ≥ 3.7:1.
- Focus rings use `--border-focus`.
- Switches are `input[type=checkbox][role=switch]` with a mixed state on purposes.
- The modal is `role="dialog"` with `aria-modal`, a focus trap, Escape to close and focus return.
- Required state is communicated by text badges, not color alone.

Exceptions:

- `--overlay-*` use `color-mix()`. In browsers without it, hover overlays and the scrim tint are skipped.
- `consent-preview` exists only for the draft design page.

## Development

```sh
python3 scripts/design.py        # regenerate Craft variables + Tokens payloads (.temp/)
python3 scripts/build_head.py    # rebuild dist/cmp-head.html from src/
# page generators: scripts/i18n.py (Slot), onepager.py (Home), examples.py (/examples), docs.py (/docs),
#                  generator.py + catalog.py + fragments.py + src/generator.js (/generator)
npx webstudio@latest update-project-settings --input-file .temp/project-settings.json

npx webstudio@latest sync && npx webstudio@latest preview --port 5188
cd tests && npm install && BASE_URL=http://127.0.0.1:5188 npm test   # 209 end-to-end checks (the contact form is checked without submitting)
```

Before running `update-project-settings`, add any head scripts you already keep in Custom Code to `dist/cmp-head.html`, below the marker comment. The command replaces the whole Custom Code.

`.webstudio/` contains the synced project data. Do not commit it.

## Config generator internals

- **Catalog**: `scripts/catalog.py` is rendered into the `generatorCatalog` variable on `/generator`. The page reads each service from `data-gen-*` attributes on the Collection rows.
- **Clipboard parts**: the Consent Manager, gate and link are Webstudio clipboard fragments (`{"@webstudio/instance/v0.1": …}`, validated against `webstudioFragment` from `@webstudio-is/sdk`). They are built by `scripts/fragments.py` from the synced project data.
- **Fresh IDs per copy**: every copied Consent Manager gets fresh instance, variable, prop and local style IDs. Otherwise Webstudio would link the paste to an existing Slot with the same IDs and ignore the generated variables.
- **Embed size limit**: HTML Embeds are limited to 50,000 characters, so the generator data (engine copy, fragments, base translations) is split into `script[type="application/json"][data-gen-chunk]` embeds. The logic embed reassembles them.
- **Paste test**: `tests/paste-test.mjs` pastes generated parts into a Builder page (needs a Builder URL in `.temp/builder-url.txt`).
