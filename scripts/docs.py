"""/docs: complete documentation for Native CMP."""

from ui import T
import comm
from rich import txt, rich, p, ul, code, callout, table, h3, page_header, page_footer
import theme


THEME_TABLE = table(["Variable", "Default", "Used for"], [
    [f"`{name}`", f"`{theme.css_value(name)}`", role] for name, (craft, default, role) in theme.CMP_VARIABLES.items()
])

HEAD_SNIPPET = '''<!-- Native CMP: configuration -->
<script>
window.cmpConfig = {
  storageName: "cmp_consent",
  cookieExpiresAfterDays: 365,
};
</script>
<style data-cmp-critical>/* critical CSS */</style>
<script data-cmp-engine="1.1.0">/* engine */</script>
<!-- Consent-managed head scripts go below this line -->'''

SECTIONS = [
    ("overview", "Overview", [
        p("Native CMP is a consent manager for cookies, third-party scripts and embeds, built from regular Webstudio building blocks. There is no external service, dashboard or vendor script: everything lives in your project and can be edited in the Builder."),
        ul([
            "**Engine**: a small script in Project Settings → Custom Code. It reads the stored decision before the page paints, blocks and activates third-party code, deletes cookies and keeps everything in sync during client-side navigation.",
            "**Consent Manager Slot**: the notice, preferences modal, purposes and switches as native instances, shared across all pages.",
            "**Variables**: `consentServices` describes what each service does technically; `consentTranslations` holds all copy per language.",
            "**Attributes**: behavior is wired with `data-cmp-*` attributes, so any element you design can open the settings, show a status or wait for consent.",
            "**Craft tokens**: every part of the UI is a composite Token backed by semantic CSS variables.",
        ]),
        callout("The CMP gives you technical building blocks for a GDPR- and ePrivacy-friendly setup: prior blocking, granular purposes, equally prominent choices, revocation and cookie cleanup. Whether a site is compliant also depends on its texts, services and privacy policy."),
    ]),
    ("installation", "Installation", [
        comm.docs_blocks(),
        h3("1. Add the engine"),
        p("Open **Project Settings → Custom Code** and paste the CMP snippet at the very top, before any analytics or tag manager code. It contains three parts:"),
        code(HEAD_SNIPPET, "Custom Code"),
        h3("2. Add the Consent Manager Slot"),
        p("Copy the **Consent Manager** Slot to every page. On new projects, add it to your page template so new pages include it automatically. The Slot is shared: editing it on one page updates every page."),
        h3("3. Configure services and copy"),
        p("Select the Consent Manager root instance and edit the `consentServices` and `consentTranslations` variables in the Data panel. The [examples](/examples) contain ready-made entries for the most common services."),
        h3("4. Block third-party code"),
        p("Change existing scripts and embeds so they only run with consent (see [Blocking scripts & embeds](#blocking)) and add a **Privacy settings** link to your footer with `data-cmp-action=\"open-modal\"`."),
        h3("5. Publish and test"),
        p("Open the site in a private window. The notice must appear, nothing tracked should load before a decision, and your choice must survive reloads and page changes. `cmp.getConsents()` in the browser console shows the current state."),
    ]),
    ("how-it-works", "How it works", [
        ul([
            "**Before the first paint**: the engine runs in `<head>`, reads the `cmp_consent` cookie and sets state attributes on `<html>`. The critical CSS uses them to show or hide the notice immediately, so returning visitors never see a flash.",
            "**After the page is parsed**: the engine reads the service definitions from the Slot, validates the stored decision, activates allowed scripts and embeds, and renders switches, gates and status indicators.",
            "**During client-side navigation**: Webstudio remounts page content on every route change. A `MutationObserver` notices new consent-related elements and re-syncs them. Consent state lives in the engine, not in the page, so it survives navigation.",
            "**No double execution**: React may re-create embed content (for example right after hydration). The engine remembers what it has already executed per embed container, so scripts never run twice.",
        ]),
        h3("Effective consent"),
        p("A service is active when it is `required`, when the visitor accepted it once in a gate, or when it has consent and the decision is confirmed. Services marked `optOut` also run before a decision, until the visitor declines them."),
        h3("Changed services"),
        p("If the service list changes after a visitor decided, the stored decision becomes unconfirmed: the notice opens again with the “services changed” message, and non-required services stay blocked until the visitor decides again."),
    ]),
    ("configuration", "Configuration", [
        p("Set options in `window.cmpConfig` at the top of the Custom Code snippet. All options are optional."),
        table(["Option", "Default", "Description"], [
            ["`storage`", "`\"cookie\"`", "Where the decision is stored: `\"cookie\"` or `\"localStorage\"`."],
            ["`storageName`", "`\"cmp_consent\"`", "Cookie or localStorage key."],
            ["`cookieExpiresAfterDays`", "`365`", "Lifetime of the consent cookie."],
            ["`cookieDomain`", "`\"\"`", "Set e.g. `\".example.com\"` to share consent across subdomains."],
            ["`cookiePath`", "`\"/\"`", "Path of the consent cookie."],
            ["`default`", "`false`", "Preselection for services without their own `default`."],
            ["`mustConsent`", "`false`", "Open the preferences modal instead of the notice. It can’t be closed until the visitor decides."],
            ["`noNotice`", "`false`", "Contextual consent only: no notice on page load. Consent Gates, Privacy settings links and the JavaScript API ask for consent. See [Contextual consent only](#contextual-consent)."],
            ["`confirmDelay`", "`800`", "Milliseconds the modal stays visible after Accept all / Decline all, so visitors see the switches change."],
            ["`consentMode`", "`null`", "Google Consent Mode v2 mapping, see [Google Consent Mode & GTM](#consent-mode)."],
            ["`consentModeDefaults`", "`null`", "Extra fields for `gtag(\"consent\", \"default\", …)`, e.g. `{ security_storage: \"granted\" }`."],
            ["`dataLayer`", "`false`", "Push `{ event: \"cmp_consent\", cmp_type, cmp_consents }` to `window.dataLayer` on every decision."],
            ["`fallbackLanguage`", "`\"\"`", "Language shown when no translation matches the page. Defaults to the first entry."],
            ["`debug`", "`false`", "Log service definitions and cookie deletions to the console."],
        ]),
        h3("Contextual consent only", "contextual-consent"),
        p("Set `noNotice: true` if you only want to protect embeds such as YouTube or Google Maps and don’t need a notice on page load. The generator calls this **Contextual consent only**. Visitors allow a provider right where its content appears: **Load content** allows it for the current page, **Always allow** stores the decision straight away. The Privacy settings link still opens the full preferences."),
        p("In this mode the root gets `data-cmp-mode=\"contextual\"`, and **Always allow** buttons are visible before any decision. Head scripts such as analytics stay blocked until visitors enable them in the preferences, so use it for sites without consent-based tracking. `mustConsent` takes precedence if both are set."),
        h3("Stored value"),
        p("The cookie contains URL-encoded JSON: `{ \"consents\": { \"google-analytics\": true, … }, \"timestamp\": \"2026-09-13T10:00:00.000Z\", \"version\": 1 }`. The timestamp documents when the decision was made."),
    ]),
    ("services", "Services", [
        p("`consentServices` is a JSON array on the Consent Manager root. It is rendered as a hidden Service Registry that the engine reads."),
        code('''[
  { "name": "consent-manager", "required": true },
  { "name": "google-analytics", "cookies": ["^_ga", "_gid", "^_gat"] },
  { "name": "youtube" },
  { "name": "chat", "optOut": true, "dependsOn": ["google-analytics"] }
]''', "consentServices"),
        table(["Field", "Type", "Description"], [
            ["`name`", "string", "Unique key. Referenced by `data-cmp-service`, `data-cmp-gate`, `data-cmp-status` and translations. Use lowercase and dashes."],
            ["`required`", "boolean", "Always active. The switch is disabled and the “Always active” badge is shown."],
            ["`default`", "boolean", "Preselected in the preferences modal before the visitor decides."],
            ["`optOut`", "boolean", "Runs before a decision, until the visitor declines. Shows “Active by default”."],
            ["`cookies`", "string[]", "Cookies deleted when consent is missing or revoked. Patterns starting with `^` are regular expressions (`^_ga` matches `_ga_ABC123`); other values match exactly. No spaces inside a pattern."],
            ["`onlyOnce`", "boolean", "Accept scripts run at most once per page load, even across client-side navigation."],
            ["`contextualOnly`", "boolean", "Ignored by Accept all / Decline all. Only its switch or a Consent Gate changes it."],
            ["`dependsOn`", "string[]", "Enabling this service enables the listed services; disabling one of them disables this service."],
        ]),
        callout("Cookie deletion works for first-party cookies the browser lets JavaScript see: the current host, the host with a leading dot and every parent domain, on path `/` and the current path. HttpOnly cookies and cookies on third-party domains can’t be removed from the page."),
    ]),
    ("languages", "Languages & translations", [
        p("`consentTranslations` contains one entry per language. The Slot renders one notice and modal per entry and the engine shows the one matching the page language from **Page Settings → Language** (rendered as `<html lang>`)."),
        code('''[
  {
    "lang": "en",
    "dir": "ltr",
    "privacyLabel": "privacy policy",
    "privacyUrl": "/privacy",
    "notice": {
      "title": "We value your privacy",
      "text": "We use cookies … Learn more in our",
      "changes": "Our services have changed since your last visit.",
      "customize": "Customize", "decline": "Decline all", "accept": "Accept all"
    },
    "modal": {
      "title": "Privacy settings", "text": "Choose which services we may use …",
      "close": "Close privacy settings", "toggleAll": "Enable or disable all services",
      "alwaysActive": "Always active", "activeByDefault": "Active by default",
      "service": "service", "services": "services",
      "decline": "Decline all", "save": "Save selection", "accept": "Accept all"
    },
    "purposes": [
      {
        "id": "analytics", "title": "Analytics", "description": "…",
        "services": [
          { "name": "google-analytics", "title": "Google Analytics", "description": "…" }
        ]
      }
    ]
  }
]''', "consentTranslations"),
        h3("Language matching"),
        ul([
            "Exact match, case-insensitive: `de-AT` → `de-at`.",
            "Primary language: `de-AT` → `de`, or a regional entry of the same language.",
            "`cmpConfig.fallbackLanguage`, otherwise the first entry.",
        ]),
        p("The language updates live when client-side navigation changes `<html lang>`. Consent is shared across languages. Purposes group services in the modal; a purpose switch toggles all its non-required services and shows a mixed state when only some are active."),
        h3("Any language", "any-language"),
        ul([
            "Add an entry with any language code: `fr`, `pt-BR`, `tr`, `fa`, …. The engine doesn’t need a list of supported languages.",
            "The [generator](/generator) includes built-in notice, modal, purpose and gate texts and descriptions for all 23 catalog services in English, German, Spanish, French, Italian, Portuguese, Dutch, Polish, Arabic and Hebrew.",
            "For other codes the generator starts from English and marks every field **English – translate** in its translation editor. The editor also imports translations from pasted configurations.",
        ]),
        h3("Right-to-left languages", "rtl"),
        p("Each entry may set `\"dir\": \"rtl\"` or `\"ltr\"`. Without it, the Consent Manager detects right-to-left from the language code: `ar`, `arc`, `ckb`, `dv`, `fa`, `he`, `ku`, `ps`, `sd`, `ug`, `ur` and `yi`. The language wrapper gets the matching `dir` attribute, so the notice, modal and switches mirror automatically."),
        ul([
            "Layouts use flex and grid, which follow the writing direction.",
            "Tokens that need explicit mirroring use logical properties or the `:dir(rtl)` state. For example, `consent-switch` mirrors its thumb and `consent-modal-close` uses `margin-inline-end`.",
            "Set `dir=\"rtl\"` on the Body of right-to-left pages too, so your own page content mirrors as well. See the [Arabic demo](/ar).",
        ]),
        h3("Other translated elements"),
        p("Add `data-cmp-lang=\"de\"` to any element, for example a footer link in a shared Slot, to show it only on German pages."),
    ]),
    ("blocking", "Blocking scripts & embeds", [
        p("Mark third-party code with `data-cmp-service`. Put it in Custom Code (runs once per visit) or an HTML Embed (runs on the pages that contain it)."),
        h3("External scripts"),
        code('''<script type="text/plain" data-cmp-service="google-analytics"
  data-src="https://www.googletagmanager.com/gtag/js?id=G-XXXX"></script>''', "HTML"),
        p("`type=\"text/plain\"` stops the browser from running the script. On consent the engine inserts a real copy into `<head>` with all other attributes (`id`, `data-*`, `nonce`, `async`). Use `data-type` to restore a type such as `module`. The same external URL is only loaded once per page load."),
        h3("Inline scripts and decline handlers"),
        code('''<script type="text/plain" data-cmp-service="google-analytics">
  gtag("config", "G-XXXX");
</script>
<script type="text/plain" data-cmp-service="google-analytics" data-cmp-on="decline">
  window["ga-disable-G-XXXX"] = true;
</script>''', "HTML"),
        p("Inline scripts run when consent is granted, again after a revoke followed by a new consent, and once for every page that renders them. `data-cmp-on=\"decline\"` runs a script when the service is denied or revoked."),
        h3("Templates for iframes and widgets"),
        code('''<template data-cmp-service="youtube">
  <iframe src="https://www.youtube-nocookie.com/embed/VIDEO_ID" title="Video"></iframe>
</template>''', "HTML Embed"),
        p("Everything inside a `<template>` is inert. On consent the content is inserted after the template (scripts go to `<head>`); on revoke it is removed again. This is the most robust option for iframes, widgets and social embeds."),
        h3("Attribute swapping"),
        code('''<iframe data-cmp-service="vimeo" data-src="https://player.vimeo.com/video/ID"></iframe>
<img data-cmp-service="tracker" data-src="https://example.com/pixel.gif" alt="">
<link rel="stylesheet" data-cmp-service="google-fonts" data-href="https://fonts.googleapis.com/…">''', "HTML"),
        p("For other elements the engine copies `data-src`, `data-srcset`, `data-href`, `data-poster` and `data-data` into the real attributes on consent and removes them on revoke (iframes switch to `about:blank`). Iframes, images, video, audio, embed and object elements stay hidden until granted. Stylesheet links are added to and removed from `<head>`."),
        callout("For YouTube and Vimeo, use Webstudio’s native components inside an interaction-mode Consent Gate (see [Consent Gates](#gates)). Turn off **Show preview**, **Autoplay** and **Preconnect** first: with those settings on, the components contact YouTube or Vimeo as soon as the page loads."),
        h3("Element state"),
        p("Every managed element gets `data-cmp-state=\"granted\"` or `\"denied\"`, which you can use for styling."),
    ]),
    ("gates", "Consent Gates", [
        p("A Consent Gate lets visitors allow a single service right where its content appears. Gates have two modes."),
        h3("Placeholder mode (default)"),
        p("The content stays hidden behind a designed placeholder until the visitor allows the service. Use it for HTML embeds such as maps, social posts and widgets."),
        code('''<div data-cmp-gate="google-maps">                 <!-- consent-gate -->
  <div data-cmp-gate-notice>                       <!-- visible until consent -->
    <p>Google Maps</p>
    <button data-cmp-action="accept-once">Load content</button>
    <button data-cmp-action="accept-always" data-cmp-if="confirmed">Always allow Google Maps</button>
    <button data-cmp-action="open-modal">Privacy settings</button>
  </div>
  <div data-cmp-gate-content>                      <!-- HTML Embed with a template -->
    <template data-cmp-service="google-maps">…</template>
  </div>
</div>''', "Structure"),
        h3("Interaction mode", "interaction-mode"),
        p("The content stays visible and works like a normal component until someone interacts with it. The first click inside `data-cmp-gate-content` is held back and the notice appears on top. After **Load content** or **Always allow**, the original click continues automatically, so a video starts playing right away."),
        code('''<div data-cmp-gate="youtube" data-cmp-gate-mode="interaction">   <!-- consent-gate -->
  <div data-cmp-gate-notice>                       <!-- consent-gate-notice + is-consent-gate-overlay -->
    <p>YouTube video</p>
    <button data-cmp-action="accept-once">Load content</button>
    <button data-cmp-action="accept-always" data-cmp-if="confirmed">Always allow YouTube</button>
    <button data-cmp-action="dismiss">Cancel</button>
    <button data-cmp-action="open-modal">Privacy settings</button>
  </div>
  YouTube component with data-cmp-gate-content     <!-- consent-video -->
</div>''', "Structure"),
        ul([
            "Focus moves into the notice when it opens. **Cancel** (`dismiss`) or Escape closes it and returns focus to the element that was clicked.",
            "While the notice is open, the gate has `data-cmp-requested` and grows to at least 300 px (400 px on phones), so the notice never gets cut off.",
            "Visitors who already allowed the service interact with the content directly.",
            "If consent is revoked while a native player is loaded, the engine stops it (`about:blank`). It can be played again after the next page load.",
            "Interaction mode works for anything that only loads on click, for example your own **Load map** button.",
        ]),
        h3("Webstudio’s YouTube and Vimeo components", "native-video"),
        p("Put the component inside an interaction-mode gate, add `data-cmp-gate-content` to it in Settings → Attributes, and use these settings:"),
        table(["Setting", "YouTube", "Vimeo", "Why"], [
            ["Show preview", "Off", "Off", "On loads the thumbnail from `img.youtube.com`, or calls `vimeo.com/api` and loads from `vimeocdn.com`."],
            ["Autoplay", "Off", "Off", "On loads the player immediately."],
            ["Preconnect", "Off", "–", "On opens a connection to YouTube on page load."],
            ["Privacy enhanced mode", "On", "–", "Uses `youtube-nocookie.com` once the player loads."],
            ["Do not track", "–", "On", "Asks Vimeo not to track the session."],
            ["Preview Image", "Your own upload", "Your own upload", "Self-hosted thumbnails need no consent."],
        ]),
        callout("The [generator](/generator) copies ready-made YouTube and Vimeo gates with these settings and your video URL. The tests confirm that no request reaches YouTube, Vimeo or their image servers before consent."),
        h3("Accept once and always"),
        ul([
            "**Load content** (`accept-once`) grants consent for the current page view only; nothing is stored.",
            "**Always allow** (`accept-always`) stores consent for this service. It is only offered after the visitor made a first decision, so a single click in a gate never counts as a decision about all other services.",
            "Buttons outside a gate can target a service with `data-cmp-name=\"youtube\"`.",
        ]),
    ]),
    ("attributes", "Attribute reference", [
        h3("Actions"),
        table(["Value of data-cmp-action", "Effect"], [
            ["`accept-all`", "Grant all services (except `contextualOnly`), save and close."],
            ["`decline-all`", "Deny all non-required services, save and close."],
            ["`save`", "Save the current switch positions and close."],
            ["`open-modal`", "Open the preferences modal. Works on any element on any page."],
            ["`close`", "Close the modal. Unsaved switch changes are discarded for returning visitors. Ignored when `mustConsent` requires a decision."],
            ["`accept-once`", "Allow the service of the closest gate for this page view."],
            ["`accept-always`", "Allow and store the service of the closest gate."],
            ["`dismiss`", "Close an interaction-mode gate notice without deciding."],
            ["`reset`", "Delete the stored decision and show the notice again."],
        ]),
        h3("Structure and bindings"),
        table(["Attribute", "Used on", "Purpose"], [
            ["`data-cmp-notice`", "Notice region", "Shown while the notice is open."],
            ["`data-cmp-modal`", "Modal wrapper", "Shown while the preferences modal is open."],
            ["`data-cmp-dialog`", "Dialog element", "Receives focus; Tab is trapped inside."],
            ["`data-cmp-toggle`", "Checkbox", "`service:<name>`, `purpose:<id>` or `all`."],
            ["`data-cmp-purpose`", "Purpose row", "Groups service rows for purpose switches and badges."],
            ["`data-cmp-service-item`", "Service row", "Connects a translated row to a service."],
            ["`data-cmp-service-def`", "Registry item", "Technical service definition (rendered from `consentServices`)."],
            ["`data-cmp-service`", "Script, template, link, iframe…", "Blocked until the service is granted."],
            ["`data-cmp-on`", "Script", "`accept` (default) or `decline`."],
            ["`data-cmp-gate`", "Gate wrapper", "Service name of a Consent Gate."],
            ["`data-cmp-gate-mode`", "Gate wrapper", "`interaction`: keep the content visible and hold back the first click until consent."],
            ["`data-cmp-gate-notice` / `data-cmp-gate-content`", "Gate children", "Notice and gated content."],
            ["`data-cmp-requested`", "Gate wrapper (set by the engine)", "An interaction-mode notice is open."],
            ["`data-cmp-status`", "Any element", "Live status of a service; sets `data-cmp-state`."],
            ["`data-cmp-lang`", "Any element", "Only shown when it matches the page language."],
            ["`data-cmp-preview`", "Design frame", "`notice` or `modal`: shows the fixed UI inline for designing."],
        ]),
        h3("Conditional visibility"),
        table(["data-cmp-if", "Visible when"], [
            ["`confirmed` / `unconfirmed`", "The visitor has (not) made a decision."],
            ["`changed`", "The service list changed since the stored decision."],
            ["`required` / `not-required`", "The closest service or purpose is (not) required."],
            ["`opt-out`", "The closest service is opt-out."],
            ["`granted` / `denied`", "The closest service, status or gate is (not) active."],
        ]),
        h3("State on <html>"),
        table(["Attribute", "Values"], [
            ["`data-cmp`", "`loading` until the page is parsed, then `ready`."],
            ["`data-cmp-open`", "`notice` or `modal` while one is open."],
            ["`data-cmp-confirmed`", "`true` or `false`."],
            ["`data-cmp-changed`", "Present when services changed."],
            ["`data-cmp-confirming`", "Present during the confirm delay."],
            ["`data-cmp-language`", "Resolved language, e.g. `de`."],
        ]),
    ]),
    ("javascript-api", "JavaScript API & events", [
        code('''cmp.show();                          // open the preferences modal
cmp.showNotice(); cmp.hide();
cmp.getConsent("youtube");           // effective consent: true / false
cmp.getConsents();                   // { "google-analytics": true, … }
cmp.isConfirmed();                   // visitor has decided
cmp.getServices();                   // parsed service definitions
cmp.getLanguage();                   // "en"
cmp.setConsent("youtube", true);     // change and save (pass false as 3rd argument to skip saving)
cmp.acceptAll(); cmp.declineAll(); cmp.save(); cmp.reset();
cmp.refresh();                       // re-sync after custom DOM changes

const off = cmp.on("save", ({ type, consents, changes }) => {});
document.addEventListener("cmp:service", (event) => console.log(event.detail));''', "JavaScript"),
        table(["Event", "Detail", "Fires when"], [
            ["`ready`", "consents", "Service definitions were read after the first page load."],
            ["`change`", "consents", "A switch changed (not yet saved)."],
            ["`save`", "`{ type, consents, changes }`", "A decision was stored. `type` is `accept`, `decline`, `save`, `contextual-accept` or `api`."],
            ["`service`", "`{ name, consent, service }`", "A service’s effective consent changed."],
            ["`init`", "`{ service }`", "A service was seen for the first time."],
            ["`modal`", "`{ open }`", "The preferences modal opened or closed."],
            ["`gate`", "`{ name, requested }`", "An interaction-mode gate held back a click and opened its notice."],
        ]),
        p("Every event is also dispatched on `document` as `cmp:<event>`."),
    ]),
    ("consent-mode", "Google Consent Mode & GTM", [
        p("Map Google consent types to your services. The engine sends `gtag(\"consent\", \"default\")` with all mapped types denied as soon as it runs, and `gtag(\"consent\", \"update\")` whenever effective consent changes. A type is granted when any of its services is active."),
        code('''window.cmpConfig = {
  consentMode: {
    analytics_storage: ["google-analytics"],
    ad_storage: ["google-ads"],
    ad_user_data: ["google-ads"],
    ad_personalization: ["google-ads"],
  },
  consentModeDefaults: { security_storage: "granted" },
  dataLayer: true,
};''', "Custom Code"),
        ul([
            "Place Google Tag Manager or gtag **below** the CMP snippet, so the default command is queued first.",
            "With `dataLayer: true`, GTM receives a `cmp_consent` event with `cmp_consents` for custom triggers.",
            "To block GTM completely until consent, mark its script like any other service instead.",
        ]),
    ]),
    ("design", "Design & Craft tokens", [
        p("Every consent token reads a namespaced set of **`--cmp-*` variables** on Global Root. Restyle the whole consent UI there, or edit a single token in the Style panel. Each variable defaults to the matching Craft variable when your project has one (e.g. `--cmp-accent: var(--background-accent, #1d4ed8)`), so Craft projects match automatically. In any other project, point them at your own variables."),
        h3("Theme variables", "theme-variables"),
        THEME_TABLE,
        callout("Tokens are named `consent-*` and variant tokens `is-consent-*` (Craft modifiers, always combined with their base token). When you restyle tokens directly, include both prefixes: the button borders and colors live in `is-consent-button-primary` and `is-consent-button-secondary`."),
        h3("Composite tokens"),
        table(["Block", "Elements and variants"], [
            ["`consent-notice`", "`consent-notice-body`, `consent-notice-title`, `consent-notice-text`, `consent-notice-changes`, `consent-notice-actions`"],
            ["`consent-modal`", "`consent-modal-scrim`, `consent-modal-dialog`, `consent-modal-header`, `consent-modal-title`, `consent-modal-close`, `consent-modal-text`, `consent-modal-body`, `consent-modal-footer`"],
            ["`consent-purposes`", "`consent-purpose`, `is-consent-purpose-all`, `consent-purpose-header`, `consent-purpose-label`, `consent-purpose-description`, `consent-purpose-services`, `consent-purpose-summary`"],
            ["`consent-services`", "`consent-service`, `consent-service-header`, `consent-service-label`, `consent-service-description`"],
            ["`consent-button`", "`is-consent-button-primary`, `is-consent-button-secondary`, `is-consent-button-ghost`"],
            ["`consent-switch`", "States: `:checked`, `:indeterminate`, `:disabled`, `:focus-visible`, `::before` (thumb)"],
            ["`consent-gate`", "`consent-gate-notice`, `consent-gate-title`, `consent-gate-text`, `consent-gate-actions`, `consent-gate-content`"],
            ["`consent-status`", "`consent-status-label`, `is-consent-status-label-granted`"],
            ["Others", "`consent`, `consent-language`, `consent-link`, `consent-badge`, `consent-preview`, `is-consent-preview-modal`"],
        ]),
        h3("Designing in the Builder", "builder-preview"),
        p("Custom Code doesn’t run in the Builder, so the engine is missing there: the fixed notice and preferences dialog stay hidden and only the first language is shown. To edit them, select the **Consent Manager** root, open the **Data** panel and set the Builder preview variables:"),
        table(["Variable", "Values", "Effect in the Builder"], [
            ["`canvasPreview`", "`off`, `notice`, `modal`, `hide`", "Shows the notice or the preferences dialog on the canvas, on every page with the Consent Manager Slot. With `off`, a small hint in the corner of the canvas points to this variable; `hide` removes the hint."],
            ["`canvasLanguage`", "empty or a language code, e.g. `de`", "Shows that translation instead of the first one, including `data-cmp-lang` labels elsewhere on the page."],
        ]),
        p("Select elements on the canvas or in the Navigator and edit texts in `consentTranslations`, styles in the `consent-*` tokens. The flags only act while the engine is absent, so the published site is unaffected even if you forget to switch them back to `off`. Gates always show both their notice and content in the Builder."),
    ]),
    ("accessibility", "Accessibility", [
        ul([
            "Default color pairs meet WCAG 2.2 AA: body text ≥ 6.8:1, accent buttons 7.1:1, switch tracks ≥ 3.7:1 against their backgrounds.",
            "The modal is a `role=\"dialog\"` with `aria-modal`, labelled by its title and described by its text. Focus moves into it, Tab is trapped, Escape closes it and focus returns to the opener.",
            "Switches are native checkboxes with `role=\"switch\"`; purpose switches expose a mixed state. Every switch has a visible label and a description.",
            "Required and opt-out states are communicated with text badges, not color alone. Focus rings use `--border-focus`.",
            "The notice is a labelled region that doesn’t steal focus, so keyboard and screen reader users can keep reading the page.",
        ]),
        callout("Automated audits may report that `role=\"switch\"` needs `aria-checked`. For native checkboxes the checked state is exposed by the browser, and adding a static `aria-checked` would be wrong."),
    ]),
    ("troubleshooting", "Troubleshooting", [
        table(["Symptom", "Check"], [
            ["The notice never appears", "Is the CMP snippet in Custom Code and is the Consent Manager Slot on the page? Was a decision already stored? Run `cmp.reset()`."],
            ["A script doesn’t run after consent", "Does `data-cmp-service` exactly match a `name` in `consentServices`? Is the original `type` `text/plain`? Check `document.head` for a script with `data-cmp-for`."],
            ["A script runs before consent", "The original tag must not have a JavaScript `type`, and the URL must be in `data-src`, not `src`."],
            ["An embed appears twice or stays empty", "Use a `<template>` inside an HTML Embed rather than an iframe with `data-src` next to other markup."],
            ["Tracking cookies remain after declining", "Compare cookie names with the `cookies` patterns. Cookies on other domains or HttpOnly cookies can’t be deleted by JavaScript."],
            ["Wrong language", "Check Page Settings → Language and `cmp.getLanguage()`; add a matching entry to `consentTranslations`."],
            ["A native video contacts YouTube or Vimeo before consent", "Turn off Show preview, Autoplay and Preconnect on the component, and check that it has `data-cmp-gate-content` inside a gate with `data-cmp-gate-mode=\"interaction\"`."],
            ["A right-to-left language shows left-to-right", "Add `\"dir\": \"rtl\"` to its entry, or use a language code from the right-to-left list."],
            ["The notice reopens for returning visitors", "The service list changed. This is intentional: new services need a new decision."],
            ["Want to debug", "Set `debug: true` in `cmpConfig` and watch the console."],
        ]),
    ]),
    ("migration", "Migrating from other consent managers", [
        ul([
            "Remove the old consent manager’s script and its styles from Custom Code.",
            "Recreate your services in `consentServices` and your copy in `consentTranslations`.",
            "Replace attributes on blocked elements: `data-name=\"x\"` → `data-cmp-service=\"x\"`. `type=\"text/plain\"`, `data-src`, `data-href` and `data-type` work as before.",
            "Replace `show()` calls with `cmp.show()` and callbacks with `cmp.on(\"service\", …)`.",
            "Use a new `storageName` if the old manager used the same cookie name, so visitors are asked once with the new UI.",
        ]),
    ]),
]



def sidebar():
    links = "".join(f"<a href='#{sid}' {T('site-docs-nav-link')}>{txt(title)}</a>" for sid, title, _ in SECTIONS)
    return f"""
<aside ws:label='Docs Sidebar' {T('site-docs-sidebar')}>
  <p {T('site-docs-nav-title')}>On this page</p>
  <nav aria-label='Documentation' {T('site-docs-nav')}>
    {links}
    <a href='/examples' {T('site-docs-nav-link')}>Service examples →</a>
  </nav>
</aside>"""


def section(sid, title, blocks):
    return f"""
<section id='{sid}' ws:label='{title.replace("&", "and")}' {T('site-docs-section')}>
  <h2 {T('site-docs-heading')}>{txt(title)}</h2>
  {''.join(blocks)}
</section>"""


def layout():
    return f"""
<main ws:label='Documentation' {T('site-docs-layout')}>
  {sidebar()}
  <div ws:label='Docs Content' {T('site-docs-content')}>
    <header {T('site-stack')}>
      <p {T('site-eyebrow')}>Documentation</p>
      <h1 {T('site-heading')}>Native CMP</h1>
      <p {T('site-lead')}>{rich('Everything you need to install, configure, translate, style and extend the consent manager. Looking for ready-made service setups? See the [examples](/examples).')}</p>
    </header>
  </div>
</main>"""


def parts():
    return page_header("/docs"), layout(), [section(*s) for s in SECTIONS], page_footer()
