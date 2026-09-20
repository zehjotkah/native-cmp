"""Marketing onepager for Native CMP (Home) and localized demo pages."""

import json

from ui import T, gate_fragment, MANAGED_SCRIPTS
from rich import txt
import comm


def code(text):
    return "{" + json.dumps(text) + "}"


def js(value):
    return "{" + json.dumps(value) + "}"


MAPS_EMBED = (
    "<template data-cmp-service='google-maps'><iframe src='https://www.google.com/maps?q=Palma%20de%20Mallorca&output=embed' title='Google Maps' "
    "style='display:block;width:100%;aspect-ratio:16/9;border:0' loading='lazy' referrerpolicy='no-referrer-when-downgrade'></iframe></template>"
)

STATUS_SERVICES = [
    ("consent-manager", "Consent manager"),
    ("google-analytics", "Google Analytics"),
    ("meta-pixel", "Meta Pixel"),
    ("youtube", "YouTube"),
    ("google-maps", "Google Maps"),
]


def status_row(name, title, granted="Allowed", denied="Blocked"):
    return f"""<div data-cmp-status='{name}' {T('consent-status')}>
  <span>{title}</span>
  <span data-cmp-if='granted' {T('consent-status-label', 'is-consent-status-label-granted')}>{granted}</span>
  <span data-cmp-if='denied' {T('consent-status-label')}>{denied}</span>
</div>"""


def status_panel(title, text, reset_label, granted="Allowed", denied="Blocked"):
    rows = "\n".join(status_row(n, t, granted, denied) for n, t in STATUS_SERVICES)
    return f"""
<div ws:label='Live Consent Panel' {T('site-panel')}>
  <p {T('site-eyebrow')}>{title}</p>
  {rows}
  <p {T('site-text')}>{text}</p>
  <div {T('site-actions')}>
    <button type='button' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-secondary')}>{reset_label[0]}</button>
    <button type='button' data-cmp-action='reset' {T('consent-link')}>{reset_label[1]}</button>
  </div>
</div>"""


def header(links=True):
    nav = ""
    if links:
        nav = f"""<nav aria-label='Sections' {T('site-nav')}>
      <a href='#how' {T('site-nav-link')}>How it works</a>
      <a href='#demo' {T('site-nav-link')}>Demo</a>
      <a href='#scripts' {T('site-nav-link')}>Scripts</a>
      <a href='#languages' {T('site-nav-link')}>Languages</a>
      <a href='#design' {T('site-nav-link')}>Design</a>
      <a href='#install' {T('site-nav-link')}>Install</a>
    </nav>"""
    return f"""
<header ws:label='Site Header' {T('site-header')}>
  <div {T('site-header-inner')}>
    <a href='/' {T('site-brand')}>Native CMP</a>
    {nav}
    <button type='button' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-secondary')}>Privacy settings</button>
  </div>
</header>"""


def card(title, text, extra=""):
    return f"""<div {T('site-card')}>{extra}<h3 {T('site-heading-small')}>{title}</h3><p {T('site-text')}>{text}</p></div>"""


def code_card(title, snippet, text):
    return f"""<div {T('site-card')}>
  <h3 {T('site-heading-small')}>{title}</h3>
  <pre {T('site-code')}><code {T('site-code-content')}>{code(snippet)}</code></pre>
  <p {T('site-text')}>{text}</p>
</div>"""


def section(id_, eyebrow, title, lead, body, muted=False, label=None):
    tokens = T("site-section", "is-site-section-muted") if muted else T("site-section")
    lead_html = f"<p {T('site-lead')}>{lead}</p>" if lead else ""
    return f"""
<section id='{id_}' ws:label='{label or eyebrow}' {tokens}>
  <div {T('site-container')}>
    <div {T('site-stack')}>
      <p {T('site-eyebrow')}>{eyebrow}</p>
      <h2 {T('site-heading')}>{title}</h2>
      {lead_html}
    </div>
    {body}
  </div>
</section>"""


def hero():
    badges = "".join(
        f"<span {T('site-badge')}>{b}</span>"
        for b in ["SPA-ready", "Craft tokens", "Multilingual", "Consent Mode v2", "No third-party requests"]
    )
    return f"""
<section ws:label='Hero' {T('site-section')}>
  <div {T('site-container')}>
    <div {T('site-split')}>
      <div {T('site-stack')}>
        <p {T('site-eyebrow')}>Native CMP</p>
        <h1 {T('site-heading-hero')}>Cookie consent that feels like Webstudio.</h1>
        <p {T('site-lead')}>A complete consent manager for cookies, third-party scripts and embeds. Built from native instances, styled with Craft tokens, translated by each page’s language and ready for client-side navigation.</p>
        {comm.hero_actions()}
        <div {T('site-actions')}>{badges}</div>
      </div>
      {status_panel("Your consent on this page", "Change a switch in the privacy settings. The status updates instantly, without a reload.", ("Change settings", "Reset consent"))}
    </div>
  </div>
</section>"""


# "Used by" marquee. In Webstudio, the Used By section has two data sources:
# - `usedByLogos`: Assets resource with every asset whose file name starts with "used-by-" (sorted by file name),
#   so image URLs are right on the canvas, the published site and the local preview.
# - `usedBy`: JSON variable mapping that file name to the site's name (logo alt text = link name) and URL.
# Add a site: upload `used-by-<site>.png|svg` in Assets, then add one entry to `usedBy`.
USED_BY = {
    "used-by-btb-steuerberatung.png": {"name": "BTB Steuerberatung", "url": "https://btb-steuerberatung.de/"},
    "used-by-ihr-maler-augsburg.svg": {"name": "Ihr Maler Augsburg", "url": "https://ihr-maler-augsburg.de/"},
    "used-by-ihr-maler-muenchen.svg": {"name": "Ihr Maler München", "url": "https://ihr-maler-muenchen.de/"},
    "used-by-ihr-maler-ulm.svg": {"name": "Ihr Maler Ulm", "url": "https://ihr-maler-ulm.de/"},
}

USED_BY_LOGOS = {
    "name": "Used By Logos",
    "dataSourceName": "usedByLogos",
    "query": {
        "result": "many",
        "where": {"field": ["name"], "operator": "startsWith", "value": {"type": "literal", "value": "used-by-"}},
        "sort": [{"field": ["name"], "direction": "asc"}],
        "limit": {"type": "literal", "value": 100},
        "output": {"mode": "fields", "includeMetadata": False, "fields": [["url"], ["name"], ["width"], ["height"]]},
        "content": {"mode": "none"},
    },
}

USED_BY_MOTION = (
    "<style>"
    "@keyframes site-marquee{to{transform:translateX(calc(-100% - var(--gap-l)))}}"
    "[data-site-marquee]:hover [data-site-marquee-list],[data-site-marquee]:focus-within [data-site-marquee-list]{animation-play-state:paused}"
    "@media (prefers-reduced-motion:reduce){"
    "[data-site-marquee]{flex-wrap:wrap;justify-content:center;mask-image:none}"
    "[data-site-marquee-list]{animation:none;flex-wrap:wrap;justify-content:center;min-width:0}"
    "[data-site-marquee-list][aria-hidden]{display:none}"
    "}"
    "</style>"
)


def used_by():
    """Section skeleton; scripts/used_by.py adds the data sources and one Collection per list."""
    return f"""
<section id='used-by' ws:label='Used By' {T('site-section', 'is-site-section-compact')}>
  <div {T('site-container')}>
    <h2 {T('site-eyebrow')}>Used by</h2>
    <HtmlEmbed ws:label='Marquee Motion' code={js(USED_BY_MOTION)} />
    <div ws:label='Marquee' data-site-marquee='' {T('site-marquee')}>
      <ul ws:label='Used By List' data-site-marquee-list='' {T('site-marquee-list')}></ul>
      <ul ws:label='Used By List (loop copy)' data-site-marquee-list='' aria-hidden='true' {T('site-marquee-list')}></ul>
    </div>
  </div>
</section>"""


def used_by_item(copy=False):
    """Collection item over `usedByLogos.data`; logos without a `usedBy` entry are hidden."""
    site = "usedBy[collectionItem.name]"
    focus = " tabindex='-1'" if copy else ""
    return f"""<li ws:label='Used By Item' ws:show={{expression`{site} != null`}} {T('site-marquee-item')}>
  <a href={{expression`{site}.url`}} target='_blank' rel='noopener'{focus} {T('site-used-by-link')}>
    <Image src={{expression`collectionItem.url`}} alt={{expression`{site}.name`}} width={{expression`collectionItem.width`}} height={{expression`collectionItem.height`}} sizes='240px' {T('site-used-by-logo')} />
  </a>
</li>"""


def how():
    n = lambda i: f"<span {T('site-card-number')}>{i}</span>"
    body = f"""<div {T('site-grid')}>
  {card("Engine in Custom Code", "An 18 KB script in Project Settings → Custom Code decides before the first paint, blocks scripts until consent is given and keeps working across page transitions.", n(1))}
  {card("UI as a Slot", "The notice, preferences modal and switches are regular Webstudio instances in one shared Slot. Select, restyle and rearrange them on the canvas.", n(2))}
  {card("Data in variables", "consentServices holds the technical setup, consentTranslations the copy for every language. Collections render purposes and services.", n(3))}
</div>"""
    return section("how", "How it works", "Three native pieces. No black box.", "Inspired by Klaro and built natively for Webstudio, everything lives in your project: no external dashboard, no script from a vendor CDN, nothing hidden behind an iframe.", body, muted=True)


def demo():
    body = f"""<div {T('site-grid', 'is-site-grid-wide')}>
  {gate_fragment()}
  {gate_fragment("google-maps", "Google Maps", "Google Maps", MAPS_EMBED)}
</div>"""
    return section("demo", "Live demo", "Embeds wait for consent.", "YouTube and Google Maps load only after the visitor agrees, once or permanently. Until then, no request reaches Google. Try it, then watch the status panel above.", body)


def scripts():
    cards = [
        code_card("Script tags", '<script type="text/plain"\n  data-cmp-service="google-analytics"\n  data-src="https://www.googletagmanager.com/gtag/js?id=G-XXXX">\n</script>', "Set type to text/plain and name the service. The engine runs the script as soon as consent is given."),
        code_card("Iframes and widgets", '<template data-cmp-service="youtube">\n  <iframe src="https://www.youtube-nocookie.com/embed/…"></iframe>\n</template>', "Wrap any markup in a template inside an HTML Embed. It is inserted on consent and removed again when consent is revoked."),
        code_card("Decline handlers", '<script type="text/plain"\n  data-cmp-service="google-analytics"\n  data-cmp-on="decline">\n  gtag("consent", "update", { analytics_storage: "denied" });\n</script>', "Run code when a service is declined or revoked. Google Consent Mode v2 is also built in via the config."),
        code_card("Actions anywhere", '<button data-cmp-action="open-modal">\n  Privacy settings\n</button>', "Add data-cmp-action to any element in a footer, menu or rich text: open-modal, accept-all, decline-all, save, reset."),
    ]
    body = f"<div {T('site-grid', 'is-site-grid-wide')}>" + "".join(cards) + "</div>"
    return section("scripts", "Scripts & embeds", "Block anything with one attribute.", "Third-party code keeps working the way you pasted it. You only tell the engine which service it belongs to.", body, muted=True)


def languages():
    snippet = '[\n  { "lang": "en", "notice": { "title": "We value your privacy" } },\n  { "lang": "de", "notice": { "title": "Ihre Privatsphäre ist uns wichtig" } },\n  { "lang": "es", "notice": { "title": "Tu privacidad nos importa" } }\n]'
    body = f"""<div {T('site-grid', 'is-site-grid-wide')}>
  <div {T('site-card')}>
    <h3 {T('site-heading-small')}>Try it now</h3>
    <p {T('site-text')}>These pages only differ in Page Settings → Language. Open one and the notice, modal and service descriptions switch language during client-side navigation.</p>
    <div {T('site-actions')}>
      <a href='/de' lang='de' {T('consent-button', 'is-consent-button-secondary')}>Deutsch</a>
      <a href='/es' lang='es' {T('consent-button', 'is-consent-button-secondary')}>Español</a>
      <button type='button' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-ghost')}>Open modal in English</button>
    </div>
    <p {T('site-text')}>Regional tags fall back to their language (de-AT → de). Unknown languages show the first entry, or the fallbackLanguage from the config.</p>
  </div>
  {code_card("consentTranslations", snippet, "Add a language by adding one entry. Service titles and descriptions are translated per purpose in the same entry.")}
</div>"""
    return section("languages", "Multilingual", "Speaks your page’s language.", "The consent UI follows the language set in each page’s settings. There is nothing to wire up per page.", body)


def design():
    cards = [
        code_card("Theme variables", "--theme-accent: #1d4ed8;\n--theme-surface: #f3f4f6;\n--theme-foreground: #15171c;\n--theme-control: #6f7582;", "Change a handful of values on Global Root to rebrand every occurrence."),
        code_card("Semantic layer", "--background-accent\n--foreground-on-accent\n--overlay-scrim\n--border-focus", "Tokens only consume semantic variables, following the Craft architecture."),
        code_card("Composite tokens", "consent-notice\nconsent-notice-title\nconsent-button\nis-consent-button-primary", "BEM structure in Craft naming: blocks, elements and is- variants you can edit in the Style panel."),
        card("Accessible by default", "WCAG 2.2 AA contrast pairs, visible focus rings, a real focus trap, Escape to close, native switch semantics and badges that don’t rely on color alone."),
    ]
    body = f"<div {T('site-grid', 'is-site-grid-wide')}>" + "".join(cards) + "</div>"
    return section("design", "Craft design system", "Styled with tokens you already know.", "Every part of the consent UI is a composite token backed by Craft semantic variables. Use your own theme, or restyle a single token.", body, muted=True)


def features():
    items = [
        ("Accept, decline, customize", "Equal-weight buttons, granular purposes and a preferences modal."),
        ("Purposes and services", "Required, default, opt-out, onlyOnce and dependsOn per service."),
        ("Cookie cleanup", "Declined services lose their cookies, including parent-domain cookies."),
        ("Change detection", "New services reopen the notice; nothing new runs until the visitor decides."),
        ("Contextual consent", "Load an embed once, or always allow its provider, right where it appears."),
        ("No flash, no reload", "Decisions apply instantly, and returning visitors never see a flicker."),
        ("Google Consent Mode v2", "Default denied, then updates mapped to your services."),
        ("JavaScript API", "cmp.show(), cmp.getConsent(), cmp.on(\"save\") and DOM events."),
    ]
    body = f"<div {T('site-grid')}>" + "".join(card(t, d) for t, d in items) + "</div>"
    return section("features", "Everything included", "What you’d expect from a consent manager, and more.", "", body)


def agent_callout(lead="Faster with AI:"):
    return comm.agent_callout(lead)


def install():
    return section("install", "Install", comm.INSTALL_HEADING, comm.INSTALL_LEAD, comm.install_ways(), muted=True)


FAQ = [
    ("Can an AI agent install Native CMP?", "Yes, and it’s the recommended way. Connect Claude Code, Codex or Cursor to your project with the Webstudio MCP and point it to nativecmp.com/install.txt. It finds your third-party scripts and embeds, blocks them, configures cookies and texts, drafts the privacy policy section and matches your design. It asks before changing anything, and you publish."),
    ("Does it work with client-side navigation?", "Yes. The engine runs once and watches the page. Consent state, switches, gates, languages and scripts re-sync whenever Webstudio swaps page content, and scripts never run twice."),
    ("Can I use Webstudio’s YouTube and Vimeo components?", "Yes. Place them in an interaction-mode Consent Gate and turn off Show preview, Autoplay and Preconnect. The video stays visible; the first click asks for consent and then starts the video."),
    ("Which languages are supported?", "Any. Add an entry per language code to consentTranslations. The generator includes texts for English, German, Spanish, French, Italian, Portuguese, Dutch, Polish, Arabic and Hebrew, and right-to-left languages mirror automatically."),
    ("Can I prove that someone consented?", "Yes. Every decision is stored in the visitor’s browser with a random consent ID, which the preferences dialog shows. For a record you keep yourself, deploy the optional consent log to your own Cloudflare account in one click and set its URL in the config: one entry per decision, with the consent ID, time, choices and language, and never an IP address. See Proof of consent in the documentation."),
    ("Is it GDPR compliant?", "It gives you the building blocks: prior blocking, granular purposes, equally prominent accept and decline buttons, easy revocation and cookie cleanup. Compliance also depends on your texts, services and privacy policy."),
    ("Can I use Google Tag Manager or Consent Mode?", "Yes. Map consent types to services with consentMode in the config. The engine sends the default and update commands, and can push decisions to the dataLayer."),
    ("Does it load anything from a third party?", "No. The engine, copy and styles all live in your Webstudio project."),
    ("What happens when I add a service later?", "Returning visitors see the notice again with a short note that services changed. Nothing new runs until they decide."),
    ("How do I show the settings again?", "Add data-cmp-action=\"open-modal\" to any link or button, or call cmp.show()."),
]


def faq():
    qa = FAQ
    items = "".join(
        f"<details {T('site-faq')}><summary {T('site-faq-question')}>{q}</summary><p {T('site-text')}>{a}</p></details>" for q, a in qa
    )
    body = f"<div>{items}</div>"
    return section("faq", "FAQ", "Questions, answered.", "", body)


def support():
    from chrome import SUPPORT_URL
    body = f"""<div {T('site-card')}>
  <p {T('site-text')}>Native CMP is free and stays free: the engine, the generator, the examples and the documentation. If it’s useful to you, you can chip in to cover the running costs like the domain.</p>
  <div {T('site-actions')}>
    <a href='{SUPPORT_URL}' target='_blank' rel='noopener noreferrer' {T('consent-button', 'is-consent-button-primary')}>Chip in via PayPal</a>
  </div>
  <p {T('site-help')}>Payments are voluntary, you choose the amount, and they don’t unlock anything. They go to ELECOS UG (haftungsbeschränkt), the company behind the project, and are not tax-deductible donations. PayPal opens in a new tab; nothing from PayPal loads on this site.</p>
</div>"""
    return section("support", "Support", "Help cover the costs.", "", body, muted=True)

def footer():
    return f"""
<footer ws:label='Site Footer' {T('site-footer')}>
  <span>Native CMP</span>
  <nav aria-label='Footer' {T('site-actions')}>
    <a href='/privacy' {T('consent-link')}>Privacy policy</a>
    <button type='button' data-cmp-action='open-modal' {T('consent-link')}>Privacy settings</button>
    <button type='button' data-cmp-action='reset' {T('consent-link')}>Reset consent</button>
  </nav>
</footer>"""


def onepager_parts():
    return [
        header(),
        "<main ws:label='Onepager'>" + hero() + used_by() + how() + demo() + scripts() + languages() + design() + features() + install() + faq() + support() + "</main>",
        footer(),
        f"<HtmlEmbed ws:label='Managed Scripts (demo)' code={js(MANAGED_SCRIPTS)} />",
    ]


LOCALIZED = {
    "de": dict(
        eyebrow="Native CMP · Deutsch",
        title="Einwilligung in der Sprache der Seite.",
        lead="Diese Seite hat in den Seiteneinstellungen die Sprache „de“. Hinweis, Einstellungen und Dienstbeschreibungen erscheinen deshalb automatisch auf Deutsch.",
        panel=("Ihre Einwilligung", "Ändern Sie einen Schalter in den Datenschutz-Einstellungen – der Status aktualisiert sich sofort.", ("Einstellungen ändern", "Einwilligung zurücksetzen"), "Erlaubt", "Blockiert"),
        gate=("Google Maps", "Google Maps"),
        back="Zurück zur englischen Seite",
    ),
    "es": dict(
        eyebrow="Native CMP · Español",
        title="Consentimiento en el idioma de la página.",
        lead="Esta página tiene el idioma «es» en su configuración. Por eso el aviso, la configuración y las descripciones de los servicios aparecen automáticamente en español.",
        panel=("Tu consentimiento", "Cambia un interruptor en la configuración de privacidad: el estado se actualiza al instante.", ("Cambiar configuración", "Restablecer consentimiento"), "Permitido", "Bloqueado"),
        gate=("Google Maps", "Google Maps"),
        back="Volver a la página en inglés",
    ),
}


LOCALIZED["ar"] = dict(
    eyebrow="Native CMP · العربية",
    title="موافقة بلغة الصفحة واتجاهها.",
    lead="لغة هذه الصفحة في الإعدادات هي «ar». لذلك تظهر نافذة الموافقة والإعدادات ووصف الخدمات بالعربية ومن اليمين إلى اليسار تلقائيًا.",
    panel=("موافقتك", "غيّر أي مفتاح في إعدادات الخصوصية وستتحدّث الحالة فورًا.", ("تغيير الإعدادات", "إعادة تعيين الموافقة"), "مسموح", "محظور"),
    gate=("Google Maps", "Google Maps"),
    back="العودة إلى الصفحة الإنجليزية",
)


def localized_page(lang):
    t = LOCALIZED[lang]
    title, text, labels, granted, denied = t["panel"]
    return f"""
<main ws:label='Localized Demo' {T('site-section')}>
  <div {T('site-container')}>
    <div {T('site-split')}>
      <div {T('site-stack')}>
        <p {T('site-eyebrow')}>{t['eyebrow']}</p>
        <h1 {T('site-heading-hero')}>{t['title']}</h1>
        <p {T('site-lead')}>{t['lead']}</p>
        <div {T('site-actions')}>
          <a href='/' {T('consent-button', 'is-consent-button-secondary')}>← {t['back']}</a>
          <a href='/de' lang='de' {T('consent-link')}>Deutsch</a>
          <a href='/es' lang='es' {T('consent-link')}>Español</a>
          <a href='/ar' lang='ar' {T('consent-link')}>العربية</a>
        </div>
      </div>
      {status_panel(title, text, labels, granted, denied)}
    </div>
  </div>
</main>"""


def not_found():
    from chrome import page
    return f"""
<main ws:label='Not Found' {T('site-section')}>
  <div {T('site-container')}>
    <div {T('site-stack')}>
      <p {T('site-eyebrow')}>{txt('Error 404')}</p>
      <h1 {T('site-heading-hero')}>{txt('Page not found.')}</h1>
      <p {T('site-lead')}>{txt('This page doesn’t exist or has moved. Pick up where you want to go:')}</p>
      <div {T('site-actions')}>
        <a href={page('home')} {T('consent-button', 'is-consent-button-primary')}>{txt('Go to the homepage')}</a>
        <a href={page('generator')} {T('consent-button', 'is-consent-button-secondary')}>{txt('Config generator')}</a>
        <a href={page('examples')} {T('consent-button', 'is-consent-button-secondary')}>{txt('Examples')}</a>
        <a href={page('docs')} {T('consent-button', 'is-consent-button-secondary')}>{txt('Documentation')}</a>
      </div>
    </div>
  </div>
</main>"""
