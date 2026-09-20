"""Communication: installing with an AI agent first, then generator, examples, documentation."""

import json

from rich import txt, h3, p, ul
from ui import T

PAGE = {
    "install": "XatTUnspJHO07Ra0J3Sp9",
    "generator": "_z43E-i8iKE0_6Eev8Jyu",
    "examples": "CgtVEjmEeLrC6kfRxoPZD",
    "docs": "FCi6-VSonqxrmw79t5_ST",
}


# public source code and the cloneable starter project (read-only share link; View links can be cloned)
GITHUB_URL = "https://github.com/zehjotkah/native-cmp"
STARTER_URL = "https://starter.nativecmp.com"
STARTER_CLONE_URL = "https://p-efd5ae31-66d4-4782-b4df-f4715407ce01.apps.webstudio.is/?authToken=75f8486f-a6c5-431a-a442-4b102d1fbbb8&mode=preview"
STARTER_SUMMARY = "a Webstudio project with the engine, the Consent Manager, a Consent preview page and example gates already set up"
# optional consent log: a Cloudflare Worker the site owner deploys into their own account
LOG_SOURCE_URL = GITHUB_URL + "/tree/main/log"
LOG_DEPLOY_URL = "https://deploy.workers.cloudflare.com/?url=" + LOG_SOURCE_URL
LOG_DOMAIN_HINT = "Add a custom domain such as `consentlog.yourdomain.com` in the Cloudflare dashboard, so the log is not a third-party domain for your visitors."


def page_link(key):
    return "{new PageValue('" + PAGE[key] + "')}"


AGENT_SUMMARY = "Your AI agent finds every script and embed, blocks them until consent, configures cookies and texts, updates your privacy policy and matches your design."

HERO_LEAD = "A complete consent manager for cookies, third-party scripts and embeds, built from native Webstudio instances. " + AGENT_SUMMARY


def hero_actions():
    return f"""<div {T('site-actions')}>
  <a href={page_link('install')} {T('consent-button', 'is-consent-button-primary')}>{txt('Install with AI')}</a>
  <button type='button' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-secondary')}>{txt('Try the consent dialog')}</button>
  <a href={page_link('generator')} {T('consent-link')}>{txt('or use the generator')}</a>
</div>"""


WAYS = [
    ("install", "Recommended", "AI agent via Webstudio MCP", "The complete setup, done for you: " + "it scans your site, blocks every script and embed, configures cookies and texts, adds the privacy policy section and matches your design. You review and publish.", "Install with AI"),
    ("generator", None, "Config generator", "Pick your services, enter IDs and paste the result into Webstudio: Custom Code, Consent Manager, gates and link.", "Open the generator"),
    ("examples", None, "Service examples", "Copy-paste setups for 23 common services, from Google Analytics to Calendly.", "Browse examples"),
    ("docs", None, "Documentation", "Every attribute, variable, token and API, to build or extend it by hand.", "Read the docs"),
    (STARTER_URL, None, "Starter project", "Starting a new site? Clone a Webstudio project with Native CMP already installed and style it right on the canvas.", "Open the starter"),
]


def install_ways():
    cards = ""
    for i, (key, badge, title, text, cta) in enumerate(WAYS):
        tokens = ("site-card", "is-site-card-link") + (("is-site-card-featured",) if badge else ()) + (("is-site-card-wide",) if key.startswith("https://") else ())
        badge_html = f"<span {T('site-badge', 'is-site-badge-start')}>{txt(badge)}</span>" if badge else ""
        href = "{" + json.dumps(key) + "}" if key.startswith("https://") else page_link(key)
        cards += f"""<a href={href} {T(*tokens)}><span {T('site-card-number')}>{i + 1}</span>{badge_html}<h3 {T('site-heading-small')}>{txt(title)}</h3><p {T('site-text')}>{txt(text)}</p><span {T('consent-link')}>{txt(cta + ' →')}</span></a>"""
    return f"<div ws:label='Install Ways' {T('site-grid')}>{cards}</div>"


INSTALL_HEADING = "Five ways to install. One does it all for you."
INSTALL_LEAD = "Let your AI agent handle the whole setup, or pick the level of control you want. Everything stays inside your Webstudio project."

FAQ_ITEM = (
    "Can an AI agent install Native CMP?",
    "Yes, and it’s the recommended way. Connect Claude Code, Codex or Cursor to your project with the Webstudio MCP and point it to nativecmp.com/install.txt. "
    "It finds your third-party scripts and embeds, blocks them, configures cookies and texts, drafts the privacy policy section and matches your design. It asks before changing anything, and you publish.",
)


def agent_callout(lead="Faster with AI:"):
    return (
        f"<p ws:label='Agent Install' {T('site-callout')}><strong>{txt(lead)}</strong>{txt(' ' + AGENT_SUMMARY + ' ')}"
        f"<a href={page_link('install')} {T('consent-link')}>{txt('Install with AI')}</a></p>"
    )


def docs_blocks():
    return "".join([
        h3("Install with an AI agent (recommended)", "ai-install"),
        p("Connect Claude Code, Codex, Cursor or any agent to your project with the Webstudio MCP (`npx webstudio@latest link` with a Builder share link, then `npx webstudio@latest connect`) and ask it to follow [nativecmp.com/install.txt](https://nativecmp.com/install.txt). The agent:"),
        ul([
            "scans Custom Code, HTML Embeds and YouTube or Vimeo components and recognizes 23 common services,",
            "installs the engine, design tokens and the Consent Manager Slot on every page,",
            "configures each service with its cookies and descriptions in your site’s languages,",
            "blocks scripts and wraps embeds and videos in Consent Gates,",
            "adds a section per service to your privacy policy, for you to review,",
            "maps the consent UI to your colors, radii and fonts and verifies the result.",
        ]),
        p("It shows you its plan before changing anything and never publishes. See [Install with AI](/install) for the prompt. Prefer to do it yourself? Use the [generator](/generator), copy from the [examples](/examples) or follow the manual steps below."),
        p(f"Starting a new site? Clone the [Native CMP Starter]({STARTER_CLONE_URL}), {STARTER_SUMMARY}. See it live at [starter.nativecmp.com]({STARTER_URL})."),
        h3("Manual installation", "manual-install"),
    ])
