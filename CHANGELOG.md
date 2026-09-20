# Changelog

## 1.3.0 — 2026-09-20

**Proof of consent.** Every decision now gets a random consent ID, and an optional consent log records decisions in your own Cloudflare account.

- **Consent ID**: stored in the `cmp_consent` cookie, shown in the preferences dialog ("Your consent ID") in all ten built-in languages, and available as `cmp.getConsentId()`.
- **`consentLog` setting**: when set to your log's URL, the engine sends one entry per decision with `navigator.sendBeacon`: consent ID, time, type, choices, a fingerprint of the service list and the language. No IP address, page URL or user agent. Off by default.
- **Consent log Worker** (`log/`): a Cloudflare Worker with a D1 database, deployed with one click into your own account. Automatic deletion after `RETENTION_DAYS` (3 years), an origin allowlist, a CSV export protected by a token, and its own end-to-end tests.
- **Everywhere else**: a "Proof of consent" step in the generator, a section in the documentation and on the examples page, a Home FAQ entry, an optional step for AI agents in `install.txt`, `--consent-log` in the installer script, and both in the starter project.
- **Fix**: the engine no longer writes text into the page before a framework has hydrated it.

## 1.2.1

Focus stays inside the consent dialog while other dialogs, such as the mobile menu, restore focus themselves.
