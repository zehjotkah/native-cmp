"""Webstudio JSX fragments for Native CMP."""

import json

from design import TOKENS as _BASE, TOKENS_V2, TOKENS_V3, TOKENS_V4, TOKENS_V5, TOKENS_V6, TOKENS_V7, TOKENS_V8, TOKENS_V9

TOKENS = {**_BASE, **TOKENS_V2, **TOKENS_V3, **TOKENS_V4, **TOKENS_V5, **TOKENS_V6, **TOKENS_V7, **TOKENS_V8, **TOKENS_V9}


def css_value(value):
    return value.replace("`", "")


def T(*names):
    """Reference existing composite Tokens (conflictResolution "ours" keeps their styles)."""
    refs = []
    for name in names:
        prop, value = next(iter(TOKENS[name]["base"].items()))
        refs.append(f"token('{name}', css`{prop}: {css_value(value)};`)")
    return "ws:tokens={[" + ", ".join(refs) + "]}"


def js(value):
    return "{" + json.dumps(value) + "}"


def expr(code):
    return "{expression`" + code + "`}"


CLOSE_ICON = (
    "<svg viewBox='0 0 24 24' width='20' height='20' aria-hidden='true' focusable='false'>"
    "<path d='M6 6l12 12M18 6L6 18' stroke='currentColor' stroke-width='2' stroke-linecap='round' fill='none' />"
    "</svg>"
)

CANVAS_HELPER = (
    "<style>"
    "html:not([data-cmp]) [data-cmp-notice]:not([data-cmp-preview] *),"
    "html:not([data-cmp]) [data-cmp-modal]:not([data-cmp-preview] *){display:none}"
    '[data-cmp-preview="notice"] [data-cmp-modal],[data-cmp-preview="modal"] [data-cmp-notice]{display:none!important}'
    "</style>"
)

PRIVACY_URL = "/privacy"


def root_fragment():
    return f"""
<div ws:label='Consent Manager' data-cmp-root='' {T('consent')}>
  <HtmlEmbed ws:label='Canvas Helper' code={js(CANVAS_HELPER)} />
  <section ws:label='Consent Notice' data-cmp-notice='' role='region' aria-labelledby='consent-notice-title' {T('consent-notice')}>
    <div ws:label='Notice Body' {T('consent-notice-body')}>
      <h2 id='consent-notice-title' {T('consent-notice-title')}>We value your privacy</h2>
      <p {T('consent-notice-text')}>We use cookies and similar technologies for essential functions and, with your consent, for analytics, marketing and embedded media. You can change your choice at any time. Learn more in our <a href='{PRIVACY_URL}' {T('consent-link')}>privacy policy</a>.</p>
      <p data-cmp-if='changed' {T('consent-notice-changes')}>Our services have changed since your last visit. Please review your choice.</p>
    </div>
    <div ws:label='Notice Actions' {T('consent-notice-actions')}>
      <button type='button' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-ghost')}>Customize</button>
      <button type='button' data-cmp-action='decline-all' {T('consent-button', 'is-consent-button-secondary')}>Decline all</button>
      <button type='button' data-cmp-action='accept-all' {T('consent-button', 'is-consent-button-primary')}>Accept all</button>
    </div>
  </section>
  <div ws:label='Consent Modal' data-cmp-modal='' {T('consent-modal')}>
    <div ws:label='Scrim' data-cmp-action='close' aria-hidden='true' {T('consent-modal-scrim')}></div>
    <div ws:label='Dialog' data-cmp-dialog='' role='dialog' aria-modal='true' aria-labelledby='consent-modal-title' aria-describedby='consent-modal-text' tabindex='-1' {T('consent-modal-dialog')}>
      <header ws:label='Modal Header' {T('consent-modal-header')}>
        <h2 id='consent-modal-title' {T('consent-modal-title')}>Privacy settings</h2>
        <button type='button' data-cmp-action='close' aria-label='Close privacy settings' {T('consent-modal-close')}>{CLOSE_ICON}</button>
        <p id='consent-modal-text' {T('consent-modal-text')}>Choose which services we may use. Essential services are always active. You can change your choice at any time. Learn more in our <a href='{PRIVACY_URL}' {T('consent-link')}>privacy policy</a>.</p>
      </header>
      <div ws:label='Modal Body' {T('consent-modal-body')}>
        <ul ws:label='Purposes' {T('consent-purposes')}>
          <li ws:label='Toggle All' {T('consent-purpose', 'is-consent-purpose-all')}>
            <div {T('consent-purpose-header')}>
              <label for='consent-toggle-all' {T('consent-purpose-label')}>Enable or disable all services</label>
              <input type='checkbox' role='switch' id='consent-toggle-all' data-cmp-toggle='all' {T('consent-switch')} />
            </div>
          </li>
        </ul>
      </div>
      <footer ws:label='Modal Footer' {T('consent-modal-footer')}>
        <button type='button' data-cmp-action='decline-all' {T('consent-button', 'is-consent-button-secondary')}>Decline all</button>
        <button type='button' data-cmp-action='save' {T('consent-button', 'is-consent-button-secondary')}>Save selection</button>
        <button type='button' data-cmp-action='accept-all' {T('consent-button', 'is-consent-button-primary')}>Accept all</button>
      </footer>
    </div>
  </div>
</div>
"""


def purpose_item():
    id_ = '"consent-purpose-" + collectionItem.id'
    count = 'collectionItem.services.length === 1 ? "1 service" : collectionItem.services.length + " services"'
    return f"""
<li ws:label='Purpose' data-cmp-purpose={expr('collectionItem.id')} {T('consent-purpose')}>
  <div ws:label='Purpose Header' {T('consent-purpose-header')}>
    <label for={expr(id_)} {T('consent-purpose-label')}>
      <span>{expr('collectionItem.title')}</span>
      <span ws:label='Required Badge' ws:show={expr('collectionItem.required ?? false')} {T('consent-badge')}>Always active</span>
    </label>
    <input type='checkbox' role='switch' id={expr(id_)} data-cmp-toggle={expr('"purpose:" + collectionItem.id')} aria-describedby={expr(id_ + ' + "-description"')} {T('consent-switch')} />
  </div>
  <p id={expr(id_ + ' + "-description"')} {T('consent-purpose-description')}>{expr('collectionItem.description')}</p>
  <details ws:label='Purpose Services' {T('consent-purpose-services')}>
    <summary {T('consent-purpose-summary')}>{expr(count)}</summary>
    <ul ws:label='Services' {T('consent-services')}></ul>
  </details>
</li>
"""


def service_item():
    id_ = '"consent-service-" + collectionItem.name'
    return f"""
<li ws:label='Service' data-cmp-service-def={expr('collectionItem.name')} data-cmp-required={expr('collectionItem.required ?? false')} data-cmp-default={expr('collectionItem.default ?? ""')} data-cmp-opt-out={expr('collectionItem.optOut ?? false')} data-cmp-only-once={expr('collectionItem.onlyOnce ?? false')} data-cmp-contextual-only={expr('collectionItem.contextualOnly ?? false')} data-cmp-cookies={expr('(collectionItem.cookies ?? []).join(" ")')} data-cmp-depends-on={expr('(collectionItem.dependsOn ?? []).join(" ")')} {T('consent-service')}>
  <div ws:label='Service Header' {T('consent-service-header')}>
    <label for={expr(id_)} {T('consent-service-label')}>
      <span>{expr('collectionItem.title')}</span>
      <span ws:label='Required Badge' ws:show={expr('collectionItem.required ?? false')} {T('consent-badge')}>Always active</span>
      <span ws:label='Opt-out Badge' ws:show={expr('collectionItem.optOut ?? false')} {T('consent-badge')}>Active by default</span>
    </label>
    <input type='checkbox' role='switch' id={expr(id_)} data-cmp-toggle={expr('"service:" + collectionItem.name')} aria-describedby={expr(id_ + ' + "-description"')} {T('consent-switch')} />
  </div>
  <p id={expr(id_ + ' + "-description"')} {T('consent-service-description')}>{expr('collectionItem.description')}</p>
</li>
"""


PURPOSES = [
    {
        "id": "essential",
        "title": "Essential",
        "description": "Required for the website to work, for example to remember your privacy choices. These services cannot be disabled.",
        "required": True,
        "services": [
            {
                "name": "consent-manager",
                "title": "Consent manager",
                "description": "Stores your privacy choices in the cmp_consent cookie.",
                "required": True,
            }
        ],
    },
    {
        "id": "analytics",
        "title": "Analytics",
        "description": "Helps us understand how visitors use the website so we can improve it.",
        "services": [
            {
                "name": "google-analytics",
                "title": "Google Analytics",
                "description": "Collects pseudonymous usage statistics.",
                "cookies": ["^_ga", "_gid", "^_gat"],
            }
        ],
    },
    {
        "id": "marketing",
        "title": "Marketing",
        "description": "Measures the performance of our advertising and shows more relevant ads.",
        "services": [
            {
                "name": "meta-pixel",
                "title": "Meta Pixel",
                "description": "Measures the effectiveness of ads on Facebook and Instagram.",
                "cookies": ["_fbp", "_fbc"],
            }
        ],
    },
    {
        "id": "media",
        "title": "External media",
        "description": "Loads content from third-party platforms such as videos and maps.",
        "services": [
            {
                "name": "youtube",
                "title": "YouTube",
                "description": "Plays embedded videos. YouTube may set cookies once a video loads.",
            },
            {
                "name": "google-maps",
                "title": "Google Maps",
                "description": "Shows interactive maps.",
            },
        ],
    },
]


def gate_fragment(service="youtube", title="YouTube video", provider="YouTube", embed=None):
    embed = embed or (
        f"<template data-cmp-service='{service}'>"
        "<iframe src='https://www.youtube-nocookie.com/embed/aqz-KE-bpKQ' title='YouTube video' "
        "style='display:block;width:100%;aspect-ratio:16/9;border:0' "
        "allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' allowfullscreen></iframe>"
        "</template>"
    )
    return f"""
<div ws:label='Consent Gate' data-cmp-gate='{service}' {T('consent-gate')}>
  <div ws:label='Gate Notice' data-cmp-gate-notice='' {T('consent-gate-notice')}>
    <p {T('consent-gate-title')}>{title}</p>
    <p {T('consent-gate-text')}>This content is provided by {provider}. Loading it may set cookies and transfer data to {provider}.</p>
    <div {T('consent-gate-actions')}>
      <button type='button' data-cmp-action='accept-once' {T('consent-button', 'is-consent-button-primary')}>Load content</button>
      <button type='button' data-cmp-action='accept-always' data-cmp-if='confirmed' {T('consent-button', 'is-consent-button-secondary')}>Always allow {provider}</button>
    </div>
    <button type='button' data-cmp-action='open-modal' {T('consent-link')}>Privacy settings</button>
  </div>
  <HtmlEmbed ws:label='Gate Content' data-cmp-gate-content='' code={js(embed)} {T('consent-gate-content')} />
</div>
"""


MANAGED_SCRIPTS = (
    '<script type="text/plain" data-cmp-service="google-analytics">'
    'window.cmpDemoLog = (window.cmpDemoLog || []).concat("analytics:loaded " + location.pathname);'
    'console.info("[demo] Google Analytics loaded on " + location.pathname);'
    "</script>"
    '<script type="text/plain" data-cmp-service="google-analytics" data-cmp-on="decline">'
    'window.cmpDemoLog = (window.cmpDemoLog || []).concat("analytics:declined " + location.pathname);'
    'console.info("[demo] Google Analytics declined");'
    "</script>"
)


def demo_fragment(title, intro, gate):
    return f"""
<main ws:label='Demo Content' ws:style={{css`display: grid; row-gap: 32px; max-width: 880px; margin-left: auto; margin-right: auto; padding-top: 64px; padding-bottom: 200px; padding-left: 24px; padding-right: 24px;`}}>
  <header ws:style={{css`display: grid; row-gap: 12px;`}}>
    <h1 ws:style={{css`margin-top: 0; margin-bottom: 0; font-size: 40px; line-height: 1.1;`}}>{title}</h1>
    <p ws:style={{css`margin-top: 0; margin-bottom: 0; color: var(--foreground-secondary); font-size: 18px;`}}>{intro}</p>
    <nav ws:label='Demo Navigation' ws:style={{css`display: flex; flex-wrap: wrap; column-gap: 16px; row-gap: 8px;`}}>
      <a href='/' {T('consent-link')}>Home</a>
      <a href='/privacy' {T('consent-link')}>Privacy policy</a>
      <button type='button' data-cmp-action='open-modal' {T('consent-link')}>Privacy settings</button>
      <button type='button' data-cmp-action='reset' {T('consent-link')}>Reset consent</button>
    </nav>
  </header>
  {gate}
  <HtmlEmbed ws:label='Managed Scripts (demo)' code={js(MANAGED_SCRIPTS)} />
</main>
"""
