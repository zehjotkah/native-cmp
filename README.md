# Native CMP

Free consent manager for [Webstudio](https://webstudio.is), built from native Webstudio instances.

It blocks third-party scripts, embeds and Webstudio's YouTube and Vimeo components until visitors consent. It keeps working across Webstudio's client-side navigation, supports any language including right-to-left, is styled with Craft design tokens and supports Google Consent Mode v2.

**Website and documentation: [nativecmp.com](https://nativecmp.com)**

## How it works

- **Engine**: one script in Project Settings → Custom Code (~7 KB gzipped). It runs in `<head>` before the page paints.
- **UI**: the notice and preferences modal are a shared **Consent Manager** Slot made of regular Webstudio elements, so you design them in the Builder.
- **Data**: the `consentServices` and `consentTranslations` variables hold the services, cookies and texts per language.
- **Proof of consent**: each decision gets a random consent ID, shown in the dialog. Set `consentLog` to your own [consent log](log/) to keep a record, without IP addresses.

## Install

- **Starter project**: [open the Native CMP Starter in Webstudio](https://p-efd5ae31-66d4-4782-b4df-f4715407ce01.apps.webstudio.is/?authToken=75f8486f-a6c5-431a-a442-4b102d1fbbb8&mode=preview) and click **Clone**. It has the engine, the Consent Manager on every page, a YouTube Consent Gate and a Privacy settings link, ready to theme. Live demo: [starter.nativecmp.com](https://starter.nativecmp.com)
- **With an AI agent (recommended for existing sites)**: [nativecmp.com/install](https://nativecmp.com/install). An agent connected to the Webstudio MCP scans your project, blocks scripts and embeds, configures cookies and texts, drafts the privacy policy section and matches your design.
- **Config generator**: [nativecmp.com/generator](https://nativecmp.com/generator) builds the configuration and paste-ready Webstudio parts.
- **Service examples**: [nativecmp.com/examples](https://nativecmp.com/examples) has ready-to-copy setups for 23 common services.
- **Documentation**: [nativecmp.com/docs](https://nativecmp.com/docs)

## Repository

| Folder | Contents |
| --- | --- |
| `src/` | Consent engine, default config, critical CSS, generator logic and the CLI installer |
| `dist/` | Ready-to-use builds: Custom Code snippet (`cmp-head.html`), agent install guide (`install.txt`), install bundle and installer (`install/`), `llms.txt` |
| `scripts/` | Python scripts that build the Consent Manager and the nativecmp.com pages in Webstudio |
| `log/` | Optional consent log: a Cloudflare Worker for proof of consent, deployed into your own account |
| `tests/` | End-to-end tests (Playwright) |
| `docs/` | [Development reference](docs/development.md): project layout, data format, attribute and JavaScript API, design tokens, build steps |
| `assets/` | Logos and Open Graph images |

## License

[GNU Affero General Public License v3.0](LICENSE). You can use, change and share Native CMP, including on commercial websites. If you distribute a modified version, or offer one to users over a network, you must publish its source code under the same license.

Made by [ELECOS UG (haftungsbeschränkt)](https://nativecmp.com/legal-notice).
