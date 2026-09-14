"""/install: installing Native CMP with an AI agent through the Webstudio MCP (the recommended way)."""

import json

from rich import txt
from ui import T

PROMPT = (
    "Install Native CMP in this Webstudio project by following https://nativecmp.com/install.txt. "
    "Find all third-party scripts, embeds and videos, block them until consent, configure cookies and texts for our languages, "
    "add the matching section to our privacy policy and match the consent banner to our design. "
    "Show me what you found and your plan before you change anything."
)

DOES = [
    ("Finds every third-party service", "Scans Custom Code, HTML Embeds and YouTube or Vimeo components. Recognizes 23 common services and describes anything else it finds."),
    ("Blocks scripts and embeds", "Rewrites tracking scripts so they wait for consent and wraps maps, calendars and videos in Consent Gates. Nothing loads before a decision."),
    ("Configures cookies and texts", "Adds each service with its cookies, which are deleted when visitors decline, and writes purposes and descriptions in your site’s languages."),
    ("Updates your privacy policy", "Adds a section for every service with provider, purpose, cookies and legal basis, in your policy’s design, ready for you to review."),
    ("Matches your design", "Maps the banner and dialog to your colors, radii and fonts, then compares them with your pages on desktop and mobile."),
    ("Checks its work", "Verifies bindings, confirms nothing loads early and reports every change. It asks before changing anything, and publishing stays your decision."),
]

STEPS = [
    ("Connect your agent", "In your project folder, link your Webstudio project with a Builder share link that can edit (`npx webstudio@latest link`) and add the Webstudio MCP to Claude Code, Codex, Cursor or VS Code (`npx webstudio@latest connect`)."),
    ("Paste the prompt", "Your agent reads the install guide, scans the project and shows you what it found. Confirm the plan and answer a few questions: languages, privacy policy page, design."),
    ("Review and publish", "Open the dialog in the Builder, read the new privacy policy section and publish when you’re happy."),
]

COPY_SCRIPT = (
    "<script>(function(){if(window.__cmpCopy)return;window.__cmpCopy=1;"
    "document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-copy-from]');if(!b)return;"
    "var s=document.getElementById(b.getAttribute('data-copy-from'));if(!s||!navigator.clipboard)return;"
    "navigator.clipboard.writeText(s.textContent.trim()).then(function(){var l=b.querySelector('[data-copy-label]');if(!l)return;"
    "var t=l.textContent;l.textContent=b.getAttribute('data-copied')||'Copied';setTimeout(function(){l.textContent=t},2000)})})})();</script>"
)


def inline(text):
    """`code` spans inside card texts."""
    parts = text.split("`")
    return "".join(txt(part) if i % 2 == 0 else f"<code {T('site-inline-code')}>{txt(part)}</code>" for i, part in enumerate(parts))


def page():
    number = lambda i: f"<span {T('site-card-number')}>{i}</span>"
    does = "".join(f"<div {T('site-card')}><h3 {T('site-heading-small')}>{txt(t)}</h3><p {T('site-text')}>{txt(d)}</p></div>" for t, d in DOES)
    steps = "".join(f"<div {T('site-card')}>{number(i + 1)}<h3 {T('site-heading-small')}>{txt(t)}</h3><p {T('site-text')}>{inline(d)}</p></div>" for i, (t, d) in enumerate(STEPS))
    others = "".join(
        f"<a href={{new PageValue('{page_id}')}} {T('site-card', 'is-site-card-link')}><span {T('site-card-number')}>{n}</span><h3 {T('site-heading-small')}>{txt(t)}</h3><p {T('site-text')}>{txt(d)}</p></a>"
        for n, page_id, t, d in [
            (2, "_z43E-i8iKE0_6Eev8Jyu", "Config generator", "Pick services, enter IDs and paste the result into Webstudio yourself."),
            (3, "CgtVEjmEeLrC6kfRxoPZD", "Service examples", "Copy-paste setups for 23 common services, from Google Analytics to Calendly."),
            (4, "FCi6-VSonqxrmw79t5_ST", "Documentation", "Every attribute, variable, token and API, to build it by hand."),
        ]
    )
    return f"""
<main ws:label='Install with AI'>
  <section ws:label='Install Hero' {T('site-section')}>
    <div {T('site-container')}>
      <div {T('site-stack')}>
        <p {T('site-eyebrow')}>{txt('Install with AI · recommended')}</p>
        <h1 {T('site-heading-hero')}>{txt('Your AI agent sets it up for you.')}</h1>
        <p {T('site-lead')}>{txt('Connect your coding agent to Webstudio, paste one prompt and review the result. It finds every script and embed, blocks them, configures cookies, updates your privacy policy and matches your design.')}</p>
      </div>
      <div ws:label='Prompt' {T('site-card')}>
        <p {T('site-label')}>{txt('Prompt for Claude Code, Codex or Cursor')}</p>
        <p id='agent-prompt' {T('site-prompt')}>{txt(PROMPT)}</p>
        <div {T('site-actions')}>
          <button type='button' data-copy-from='agent-prompt' data-copied='Copied' {T('consent-button', 'is-consent-button-primary')}><span data-copy-label=''>{txt('Copy prompt')}</span></button>
          <a href='/install.txt' target='_blank' rel='noopener' {T('consent-link')}>{txt('Read the agent guide')}</a>
        </div>
        <p {T('site-help')}>{inline('Requires the Webstudio MCP or CLI 0.298 or newer. Your agent needs to read the guide and call Webstudio tools.')}</p>
      </div>
      <HtmlEmbed ws:label='Copy Script' code={json.dumps(COPY_SCRIPT)} />
    </div>
  </section>
  <section ws:label='What the agent does' {T('site-section', 'is-site-section-muted')}>
    <div {T('site-container')}>
      <div {T('site-stack')}>
        <p {T('site-eyebrow')}>{txt('What the agent does')}</p>
        <h2 {T('site-heading')}>{txt('The whole job, not just the banner.')}</h2>
        <p {T('site-lead')}>{txt('Installing a consent manager is the easy part. Connecting every script, embed, cookie and policy text is where the work is. That is what your agent takes over.')}</p>
      </div>
      <div {T('site-grid')}>{does}</div>
    </div>
  </section>
  <section ws:label='How it works' {T('site-section')}>
    <div {T('site-container')}>
      <div {T('site-stack')}>
        <p {T('site-eyebrow')}>{txt('How it works')}</p>
        <h2 {T('site-heading')}>{txt('Three steps, a few minutes.')}</h2>
      </div>
      <div {T('site-grid')}>{steps}</div>
      <p {T('site-callout')}>{txt('Your agent shows you what it found before it changes anything, and it never publishes. The privacy policy section is a draft: review it, because the legal responsibility for your site stays with you.')}</p>
    </div>
  </section>
  <section ws:label='Other ways' {T('site-section', 'is-site-section-muted')}>
    <div {T('site-container')}>
      <div {T('site-stack')}>
        <p {T('site-eyebrow')}>{txt('Prefer to do it yourself?')}</p>
        <h2 {T('site-heading')}>{txt('Three more ways to install.')}</h2>
      </div>
      <div {T('site-grid')}>{others}</div>
    </div>
  </section>
</main>"""
