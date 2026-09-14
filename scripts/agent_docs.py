"""Machine-readable docs for AI agents: /install.txt, /llms.txt and the install bundle text pages."""

import json
import pathlib

import install_bundle

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://nativecmp.com"


def install_md(bundle):
    manager = bundle["consentManager"]
    levels = "\n".join(
        f"   {i + 1}. below `{level['parentLabel']}`: data `{level['data']}`"
        + (f", then rename the item parameter to `{level['renameItemParameterTo']}`" if level["renameItemParameterTo"] else "")
        for i, level in enumerate(manager["collections"])
    )
    token_count = len(bundle["tokens"])
    var_count = len(bundle["cssVariables"])
    theme_rows = "\n".join(f"| `{name}` | `{bundle['cssVariables'][name]}` | {info['role']} |" for name, info in bundle["theme"]["variables"].items())
    typo_rows = "\n".join(f"| `{name}` | {role} |" for name, role in bundle["theme"]["typographyTokens"].items())
    placeholder_rows = "\n".join(f"| `{name}` | {role} |" for name, role in bundle["gates"]["placeholders"].items())
    languages = ", ".join(f"`{code}`" for code in bundle["translationTemplates"])
    catalog_rows = "\n".join(
        f"| `{c['id']}` | {c['title']} | {c['purpose']} | {c['placement']} | " + ", ".join(f"`{x}`" for x in c["detect"]["codeContains"][:3] + c["detect"]["components"]) + " |"
        for c in bundle["catalog"]
    )
    return f"""# Install Native CMP with the Webstudio MCP

> Instructions for AI agents (Claude Code, Codex, Cursor and others) connected to a Webstudio project through the Webstudio MCP or CLI. Follow them to add Native CMP, a free cookie, script and embed consent manager built from native Webstudio instances, to the user's project, and to connect everything that needs consent.

- Engine version: {bundle['engineVersion']}
- Minimum Webstudio CLI / MCP version: **{bundle['minimumCliVersion']}** (older versions ignore `conflictResolution`, see Troubleshooting)
- Install bundle (JSON, served as text): {SITE}/install/steps.txt
- Installer script: {SITE}/install/install.js
- Human documentation: {SITE}/docs · Config generator: {SITE}/generator · Service examples: {SITE}/examples

## What you do for the user

1. **Scan** the project for third-party scripts, embeds and videos and identify the services ({len(bundle['catalog'])} known services in `bundle.catalog`, anything else you describe yourself).
2. **Install** the engine, design tokens and the Consent Manager.
3. **Configure** every service with its cookies, purpose and descriptions in all site languages.
4. **Block** the existing scripts and **gate** the existing embeds and videos, so nothing loads before consent.
5. **Update the privacy policy** with a section per service, for the user to review.
6. **Theme** the consent UI with the site's own colors, radii and fonts.
7. **Verify** and report what you changed.

The consent manager runs entirely on the user's own site and sends nothing to a third party, so it adds no processor or external domain to the privacy policy.

**What the install adds:** {token_count} design tokens named `consent-*` and `is-consent-*`, {var_count} CSS variables named `--cmp-*`, the engine at the top of Project Settings → Custom Code, a shared Slot named "{manager['label']}" on the chosen pages, and four variables on its root (`consentServices`, `consentTranslations` and the Builder preview flags `canvasPreview`, `canvasLanguage`).

## Rules

- Work in the directory that is linked to the user's Webstudio project (`npx webstudio@latest link` with a share link that has build permissions). Check the CLI version with `npx webstudio@latest --version`.
- Download the bundle as a raw file, for example with `curl -fsSL`. Do not summarize or retype it: JSX, tokens and engine code must be passed unchanged.
- Existing design tokens, CSS variables and Custom Code are kept. Never remove code without replacing it by its blocked version, and never delete an embed before its gated copy is in place.
- Show the user your scan result and your plan before changing anything, and ask again before publishing. Summarize every change at the end.
- Privacy policy text is a draft for the user to review. Do not claim the result makes a site legally compliant, and verify provider details on the provider's page.

## 1. Ask the user

1. **Pages and languages**: which page gets the Consent Manager (default: Home; it then goes on every page as a shared Slot) and which languages the site uses (from each page's language setting).
2. **Notice or contextual consent**: after the scan, if the site only has embeds and videos and no consent-based scripts, propose **contextual consent only** (`noNotice: true`): no banner, the gates ask where the content is.
3. **Privacy policy page**: which page it is. You will add a section there.
4. **Design**: confirm the mapping of the site's colors, radius, shadow and fonts you propose in section 7.

## 2. Scan the project

Find everything that loads third-party content:

- **Custom Code**: `get-project-settings` → `meta.code`. Note every `<script>`, `<link>`, `<iframe>` and inline snippet except Native CMP's own blocks (`data-cmp-*`).
- **HTML Embeds and text**: `search-project` for each entry of `detect.codeContains` in `bundle.catalog` (for example `{{"query": "connect.facebook.net", "namespaces": ["props", "projectSettings"]}}`), plus `http` to catch unknown hosts. Each match names the instance and page.
- **Native components**: `list-pages`, then `list-instances` for each page (`maxDepth` high enough, page with `cursor`) and collect instances whose `component` is one of `detect.components` (`YouTube`, `Vimeo`). Text search doesn't find component types.
- **Forms and resources**: `search-project` with `"namespaces": ["resources"]`. Requests that run on the server (Webstudio form actions, data resources) don't need browser consent; mention them for the privacy policy only.

Match each finding to a catalog service. Extract the IDs from the existing code (measurement ID, pixel ID, video URL, map embed URL). A third-party script or embed that is not in the catalog becomes a custom service: choose a lowercase name, a purpose (`analytics`, `marketing`, `media` or `functional`), its cookie names if known, and a title and description per language.

Present the list to the user: service, where it was found, purpose, how it will be blocked. Wait for confirmation.

Known services:

| id | Service | Purpose | Blocking | Recognized by |
| --- | --- | --- | --- | --- |
{catalog_rows}

## 3. Install

Two equivalent paths. Agents should use the tool calls: they only need the bundle and work in sandboxes that refuse to run downloaded scripts. The installer script runs the same calls in one command.

### Tool calls (recommended for agents)

Load `{SITE}/install/steps.txt` (JSON) as `bundle`. Keep the ids you receive from each call. Send style updates one token per call.

1. **Page**: `list-pages` → the target page's `rootInstanceId` (the Body). `list-instances` with its `pagePath`: if an instance labelled `{manager['label']}` exists, don't install again; go to section 4 and update its variables.
2. **Breakpoint**: `list-breakpoints` → reuse the breakpoint with `maxWidth: {bundle['mobileBreakpoint']['maxWidth']}` and no `minWidth` or `condition`. If there is none: `create-breakpoint` with `bundle.mobileBreakpoint`.
3. **CSS variables**: `list-css-variables`, then `define-css-variable` with `{{"vars": {{…}}}}` containing the entries of `bundle.cssVariables` that don't exist yet. Their defaults read Craft variables when present, otherwise neutral values; section 7 maps them to the site.
4. **Design tokens**: `list-design-tokens` (page with `cursor`), then `create-design-token` with `{{"tokens": […]}}` for every entry of `bundle.tokens` whose `name` doesn't exist yet. Replace each `"breakpoint": "$mobileBreakpointId"` with the id from step 2.
5. **Custom Code**: `get-project-settings` → `meta.code`. If it contains `data-cmp-engine=`, replace its `<style data-cmp-critical>…</style>` and `<script data-cmp-engine="…">…</script>` blocks with the ones from `bundle.customCode` (this keeps `window.cmpConfig`). Otherwise put `bundle.customCode` at the very top, before any other script. For contextual consent only, set `noNotice: true` in `window.cmpConfig`. Save with `update-project-settings` `{{"meta": {{"code": "…"}}}}`.
6. **Consent Manager root**: `insert-fragment` with `{{"parentInstanceId": <Body id>, "conflictResolution": "ours", "fragment": bundle.consentManager.skeleton}}` → `rootInstanceIds[0]` is the root.
7. **Variables**: `create-variable` with `scopeInstanceId` = root for every entry of `bundle.consentManager.variables` (`{{"name": <key>, "value": <entry>}}`). `consentServices` and `consentTranslations` are replaced in section 4. Then `bind-props` for each entry of `bundle.consentManager.bindings`: find the instance with that `label` below the root and bind `name` to `{{"type": "expression", "value": expression}}`.
8. **Collections**, strictly in the order of `bundle.consentManager.collections`:
{levels}

   For each entry: `list-instances` on the page and find the instance whose `label` equals `parentLabel` below the root. Call `insert-collection` with `{{"parentInstanceId": <that id>, "insertIndex": insertIndex, "conflictResolution": "ours", "data": {{"type": "expression", "value": data}}, "itemFragment": itemFragment}}`. If `renameItemParameterTo` is set, rename the new item parameter before the next collection: `apply-patch` with `{{"baseVersion": <version from the insert-collection response>, "transactions": [{{"id": "rename-item", "payload": [{{"namespace": "dataSources", "patches": [{{"op": "replace", "path": [<itemParameterId>, "name"], "value": renameItemParameterTo}}]}}]}}]}}`.
9. **Check**: `verify-bindings` must report 0 findings.
10. **Shared Slot**: `extract-slot` with `{{"instanceSelector": [<root id>, <Body id>], "label": "{manager['label']}"}}` → response field `slotId`. Then `attach-slot` with `{{"sourceSlotId": <slotId>, "parentInstanceId": <Body id of the page>, "label": "{manager['label']}"}}` for every other HTML page.
11. **Privacy settings link**: `insert-fragment` with `bundle.privacySettingsLink` into the footer, `conflictResolution: "ours"`. It contains one `data-cmp-lang` span per language ({languages}); keep the site's languages.

### Installer script

```sh
curl -fsSL {SITE}/install/install.js -o native-cmp-install.mjs  # save as .mjs: it is an ES module
node native-cmp-install.mjs --page / --attach all
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--page <path>` | `/` | Page that receives the Consent Manager before it becomes a shared Slot. |
| `--attach all\\|none\\|/a,/b` | `all` | Pages that get the shared Slot as well. |
| `--services <file>` / `--translations <file>` | starter config | JSON arrays for `consentServices` / `consentTranslations`. |
| `--languages en,de` | all starter languages | Keep only these languages of the starter translations. |
| `--contextual` | off | Contextual consent only (`noNotice: true`). |
| `--privacy-link-parent <instanceId>` | none | Adds the localized Privacy settings button inside this instance. |
| `--custom-code install\\|skip` | `install` | Adds or updates the engine in Custom Code. |
| `--force` | off | Add a Consent Manager even if the page already has one. |
| `--bundle <url or file>` | `{SITE}/install/steps.txt` | Use another bundle. |

The installer reuses a matching breakpoint, never overwrites existing tokens or `--cmp-*` variables, keeps `window.cmpConfig`, stops after updating engine and tokens if the page already has a Consent Manager (unless `--force`), and retries transient server errors. It covers section 3 only: continue with section 4.

## 4. Configure services, cookies and texts

Build both variables from the scan and update them on the Consent Manager root (`list-variables`, then `update-variable` with `{{"type": "json", "value": …}}`):

- **`consentServices`**: `{{"name": "consent-manager", "required": true}}` plus one entry per service: `{{"name": <id>, "cookies": catalog.cookies}}`. Cookie names starting with `^` are patterns; they are deleted when the visitor declines. Add `"optOut": true` only if the user decides a cookieless tool may run until declined.
- **`consentTranslations`**: one entry per site language, starting from `bundle.translationTemplates[lang]` (all notice, dialog and purpose texts; `dir: "rtl"` for right-to-left). Set `privacyUrl` to the privacy policy path. Add each service to its purpose's `services` as `{{"name": <id>, "title": catalog.title, "description": catalog.descriptions[lang]}}`. Remove purposes without services, except `essential`. For languages without a template, translate the English one.
- **Google Consent Mode**: if the site uses Google tags, add `consentMode` to `window.cmpConfig` mapping each type in `catalog.consentMode` to its services, for example `{{"analytics_storage": ["google-analytics"]}}`.

## 5. Block scripts and gate embeds

Replace each finding by its consent-aware version. Keep the IDs from the existing code.

- **Custom Code scripts** (`placement: custom-code`): replace the original snippet in `meta.code` with `catalog.blockedMarkup`, filling `{{{{field}}}}` placeholders with the extracted values. Blocked scripts use `type="text/plain"`, `data-cmp-service` and `data-src` instead of `src`, and must stay below the engine. For custom services, convert the snippet the same way.
- **HTML Embeds** (`placement: embed-gate`): insert `bundle.gates.embed` directly before the embed (same parent, `insertIndex` of the embed, `conflictResolution: "ours"`), with `__EMBED__` set to the embed's code where each `src` becomes `data-src` and each iframe or script gets `data-cmp-service="<id>"`. Fill the text placeholders from `bundle.gates.texts[lang]`. After the gated copy exists, delete the original embed.
- **YouTube and Vimeo components** (`placement: video-gate`): wrap the component: `wrap-instance` with `{{"instanceSelector": [<component id>, <parent id>, …], "component": "ws:element", "tag": "div"}}`, then on the wrapper `update-props` with `data-cmp-gate` = `youtube` or `vimeo` and `data-cmp-gate-mode` = `interaction`, attach the tokens of the gate root in `bundle.gates.youtube.shell`, and insert the notice from the shell (the element with `data-cmp-gate-notice`, placeholders replaced) at index 0 of the wrapper. On the component set every entry of `componentProps` except `url` and `title` (preview, autoplay and preconnect off, privacy mode on), add `data-cmp-gate-content`, and attach `componentTokens`. Alternatively insert a new gate from the shell as described in `bundle.gates` and delete the original component.
- **Google Fonts**: suggest self-hosting the fonts as Webstudio assets instead of gating them; that removes the service.

`bundle.gates.placeholders` explains every placeholder:

| Placeholder | Replace with |
| --- | --- |
{placeholder_rows}

**Revoking consent**: iframes that use `data-src` with `data-cmp-service`, and players inside interaction gates, are unloaded immediately. Scripts that already ran stop on the next page load.

## 6. Privacy policy

Open the privacy policy page (`list-instances` with its `pagePath`) and add or update one section, in the page's language, using `bundle.privacyPolicy[lang]` (`en`, `de`; translate for other languages):

- A heading (`heading`) and the introduction (`intro`), with `{{storageName}}` and `{{days}}` from `window.cmpConfig` (defaults `cmp_consent`, 365) and `{{privacySettings}}` = the label of the Privacy settings link. Add the `consentManager` sentence.
- One paragraph per service from `service`: `title`, the purpose title, `provider`, the description, `cookies` (or `noCookies`) and `privacyUrl` from the catalog. For custom services, write the same fields yourself.
- Add a link or button with `data-cmp-action="open-modal"` to that section, so visitors can change their choice from the policy.

Reuse the page's existing heading and paragraph tokens so the section looks like the rest of the policy. If the policy already describes a service (for example from a previous consent tool), update that paragraph instead of adding a second one. Check each provider's current name and address on its privacy page, and tell the user to review the section before publishing.

## 7. Theme it

All consent tokens read only `--cmp-*` variables. Map them to the site, then review the result.

1. **Map variables.** For each variable, find the site's equivalent in `list-css-variables` and point the variable at it: `define-css-variable` with `{{"vars": {{"--cmp-accent": "var(--color-primary)", "--cmp-radius": "var(--radius)", "--cmp-heading-font": "var(--font-heading)"}}, "overwrite": true}}`. `overwrite: true` is required because the install already defined them. Keep a default only where the site has no equivalent.
2. **Use the knobs** before touching tokens: square design `--cmp-radius: 0`, `--cmp-radius-small: 0`, `--cmp-button-radius: 0` (keep `--cmp-radius-full` for switches); buttons `--cmp-button-border-width`, `--cmp-button-transform`, `--cmp-button-letter-spacing`, `--cmp-button-weight`, `--cmp-button-font`; headings `--cmp-heading-font`, `--cmp-heading-weight`, `--cmp-heading-transform`, `--cmp-heading-letter-spacing`.
3. **Adjust tokens only for what variables can't express.** Tokens are named `consent-*` and their variants `is-consent-*` (for example `is-consent-button-primary` carries the button colors and borders); include both prefixes. Use `update-design-token-styles`, one token per call; for variable references the typed form `{{"type": "var", "value": "fw-heading"}}` is the most reliable.
4. **Review visually.** Open the notice and the preferences dialog: in the Builder set the Consent Manager's `canvasPreview` variable to `notice` or `modal` (no effect on the published site; set it back to `off`), or open a preview page. Compare buttons, headings, radii, shadows and colors with a real page of the site at desktop width and at 390px.

| Variable | Default | Used for |
| --- | --- | --- |
{theme_rows}

Tokens that carry typography and button shape, if you need to go beyond the knobs:

| Token | Carries |
| --- | --- |
{typo_rows}

## 8. Verify and report

1. `verify-bindings` reports 0 findings.
2. `search-project` for every detected host again: each remaining match is a blocked script (`type="text/plain"`), a gated embed (`data-src`) or a privacy policy link.
3. If you can open a browser on a preview or staging build: before consent there are no requests to the detected hosts and no cookies other than the site's own; after **Accept all** the services load; the notice, dialog and gates look like the site at desktop width and at 390px.
4. Report to the user: the services and where they were, what was blocked or gated, the privacy policy section to review, the theme mapping, how to preview the dialog in the Builder (`canvasPreview`), and that publishing is their decision.

## Updating

- **Engine**: run the installer again (`node native-cmp-install.mjs --page <page with the Consent Manager>`), or repeat steps 2 to 5 of section 3 with the latest bundle.
- **New services**: repeat sections 2, 4, 5 and 6 for the new findings.
- **Contextual consent only**: set `noNotice: true` in `window.cmpConfig`.

## Troubleshooting

- `CONFLICT` during section 3 that lists the project's own token names: the CLI or MCP is older than {bundle['minimumCliVersion']} and ignores `conflictResolution`. Upgrade and repeat the step.
- `define-css-variable` answers `CONFLICT` for an existing name: pass `"overwrite": true`.
- `MCP_TOOL_FAILED: Unable to transform response from server`: the Webstudio API returns this intermittently, also for valid values. Wait a few seconds and repeat the same call; updates set absolute values, so repeating is safe. Check the result with `list-design-tokens` (`verbose: true`).
- `Unknown dependency "language"` or empty dialog rows: the Languages collection's item parameter was not renamed before the nested collections were inserted. Delete the Consent Manager root and repeat steps 6 to 8 of section 3.
- A service still loads before consent: its snippet still uses `src`, sits above the engine, or its `data-cmp-service` name doesn't match `consentServices`.
- Unstyled notice or gate: tokens were not created or were created without the mobile breakpoint id.
- The dialog doesn't match the site: section 7 was skipped or only partly applied; check both `consent-*` and `is-consent-*` tokens.
- The notice never appears: check `noNotice` and `mustConsent` in `window.cmpConfig`, and whether the page contains the Consent Manager Slot.
"""


def llms_txt():
    return f"""# Native CMP

> Free cookie, script and embed consent manager built from native Webstudio instances. It blocks third-party scripts, embeds and Webstudio's YouTube and Vimeo components until visitors consent, works with Webstudio's client-side navigation, supports any language including right-to-left, is styled with Craft design tokens and supports Google Consent Mode v2. An AI agent connected to the Webstudio MCP can install it completely: it finds and blocks third-party scripts and embeds, configures cookies and texts, drafts the privacy policy section and matches the site's design. Made by ELECOS UG (haftungsbeschränkt).

The engine runs from Project Settings → Custom Code; the notice and preferences modal are a shared Slot built from regular Webstudio elements, configured with the `consentServices` and `consentTranslations` variables.

## Install with an AI agent (recommended)

- [Install with AI]({SITE}/install): what the agent does and the prompt to use
- [Install guide for agents]({SITE}/install.txt): scan the project, install, configure services and cookies, block scripts and embeds, update the privacy policy, match the design, verify
- [Install bundle]({SITE}/install/steps.txt): tokens, CSS variables, Custom Code and JSX fragments as JSON (served as text)
- [Installer script]({SITE}/install/install.js): runs the bundle through the Webstudio CLI

## Do it yourself

- [Config generator]({SITE}/generator): builds a complete configuration and Webstudio clipboard fragments
- [Service examples]({SITE}/examples): ready-to-copy configurations for 23 common services
- [Documentation]({SITE}/docs): installation, configuration, services, languages, blocking scripts and embeds, Consent Gates, attributes, JavaScript API, Consent Mode, design tokens

## Optional

- [Contact]({SITE}/contact)
- [Legal notice]({SITE}/legal-notice)
"""


def build():
    bundle, _ = install_bundle.build()
    files = {
        "/install.txt": install_md(bundle),
        "/llms.txt": llms_txt(),
        "/install/steps.txt": (ROOT / "dist" / "install" / "steps.json").read_text(),
        "/install/install.js": (ROOT / "src" / "install.mjs").read_text(),
    }
    out = ROOT / "dist"
    (out / "install.txt").write_text(files["/install.txt"])
    (out / "llms.txt").write_text(files["/llms.txt"])
    (out / "install" / "install.mjs").write_text(files["/install/install.js"])
    return files


PAGE_NAMES = {
    "/install.txt": "Agent install guide (install.txt)",
    "/llms.txt": "llms.txt",
    "/install/steps.txt": "Install bundle (steps.txt)",
    "/install/install.js": "Installer script (install.js)",
}


def publish():
    import ws

    files = build()
    pages = {p["path"]: p for p in ws.call("list-pages", {})["pages"]}
    for path, content in files.items():
        meta = {"documentType": "text", "content": json.dumps(content, ensure_ascii=False), "excludePageFromSearch": path != "/llms.txt" and path != "/install.txt"}
        if path in pages:
            ws.call("update-page", {"pageId": pages[path]["id"], "values": {"meta": meta}})
        else:
            ws.call("create-page", {"name": PAGE_NAMES[path], "path": path, "title": json.dumps(PAGE_NAMES[path]), "meta": meta})
        print(path, len(content.encode()) // 1024, "KB")


if __name__ == "__main__":
    publish()
