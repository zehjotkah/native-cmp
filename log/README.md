# Native CMP consent log

Optional proof of consent for [Native CMP](https://nativecmp.com). A small Cloudflare Worker with a database that stores one entry per consent decision, in **your own Cloudflare account**.

**It never stores IP addresses.** Each entry is linked to the random consent ID that Native CMP keeps in the visitor's `cmp_consent` cookie and shows in the preferences dialog.

## Set it up

[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/zehjotkah/native-cmp/tree/main/log)

Click the button, sign in to Cloudflare and confirm. Cloudflare copies this repository into your own GitHub account, creates the Worker and its database, and asks you for the export token.

Prefer the terminal, or the button is having a bad day?

```sh
git clone https://github.com/zehjotkah/native-cmp
cd native-cmp/log
npm install && npm run setup
```

`npm run setup` creates the database, writes its id into `wrangler.json`, generates an export token, stores it as a secret and deploys the Worker. It prints the token once: keep it in your password manager.

Either way, finish with these three steps:

1. **Use your own domain**: in the Cloudflare dashboard, add a custom domain such as `consentlog.yourdomain.com` to the Worker (Workers & Pages → `native-cmp-consent-log` → Settings → Domains & Routes). Otherwise the log is a third-party domain for your visitors, which you would have to declare separately.
2. **Restrict writers**: set `ALLOWED_ORIGINS` to your site, for example `https://example.com,https://www.example.com`. Without it, entries are accepted from any site and the origin is stored with each entry.
3. **Point your site at it**: in Webstudio, Project Settings → Custom Code:

   ```js
   window.cmpConfig = {
     consentLog: "https://consentlog.yourdomain.com",
   };
   ```

## What one entry contains

| Field | Example | |
| --- | --- | --- |
| `consent_id` | `c7f3aa11-4d2e-…` | The ID from the visitor's cookie |
| `decided_at` | `2026-09-20T10:15:31Z` | When they decided |
| `received_at` | `2026-09-20T10:15:31Z` | When the log stored it |
| `type` | `accept`, `decline`, `save`, `reset`, `api` | How the decision was made |
| `consents` | `{"google-analytics":false}` | What was allowed |
| `config` | `1k3f9x` | Fingerprint of the service list they saw |
| `language` | `de` | Which translation was shown |
| `engine` | `1.3.0` | Engine version |
| `origin` | `https://example.com` | Added by the log, not sent by the browser |

**Never stored**: IP address, page URL, user agent.

## Using it

- **Export**: open your log URL in a browser. The page shows how many entries exist and offers a CSV download, for everything or for one consent ID. The export needs the token.
- **Retention**: entries older than `RETENTION_DAYS` (1095, three years) are deleted automatically during normal writes. Change the value in the dashboard under Settings → Variables and Secrets.
- **Status**: `GET /status` returns the entry count, the oldest entry, retention and allowed origins as JSON.

## Settings

| Name | Default | |
| --- | --- | --- |
| `RETENTION_DAYS` | `1095` | How long entries are kept (in days; 1095 = three years) |
| `ALLOWED_ORIGINS` | empty | Comma-separated sites allowed to write, e.g. `https://example.com,https://www.example.com`; empty accepts any, and the origin is stored with every entry |
| `EXPORT_TOKEN` | — | Secret that protects the CSV export; without it the export is disabled |

## In your privacy policy

Name the log, for example:

> When you make a privacy choice, we store that choice together with a random ID, the time and the language on our own server (Cloudflare) for three years, so that we can demonstrate your consent. Your IP address is not stored.

## Development

```sh
npm install
npm run dev     # local Worker with a local database
npm test        # end-to-end checks against a local Worker
```

Licensed under AGPL-3.0-or-later, like the rest of Native CMP.
