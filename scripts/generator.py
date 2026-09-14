"""/generator: configuration generator page (native UI + behavior embed)."""

import json
import pathlib
import re
import subprocess

import catalog
from chrome import SUPPORT_URL
import design
import theme
import fragments
import i18n
import languages
import service_descriptions
from ui import T
from rich import txt, rich, intro, page_header, page_footer

ROOT = pathlib.Path(__file__).resolve().parent.parent

GENERATOR_CSS = """
html[data-cmp] [data-gen-row]:not([data-gen-selected]) [data-gen-fields]{display:none}
[data-gen-error]{color:var(--foreground-warning)!important}
.gen-card{display:grid;gap:8px;padding:14px 16px;border:1px solid var(--border-default);border-radius:var(--radius-small);background:var(--background-primary);min-width:0}
.gen-card-header{display:flex;align-items:center;justify-content:space-between;gap:8px}
.gen-card h4{margin:0;font-size:15px;font-weight:650}
.gen-card p,.gen-note,.gen-empty{margin:0;font-size:13px;line-height:1.5;color:var(--foreground-secondary)}
.gen-card pre{margin:0;padding:12px 14px;border-radius:var(--radius-small);background:var(--background-inverse);color:var(--foreground-inverse);font:12.5px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;overflow:auto;white-space:pre}
.gen-copy{display:inline-flex;align-items:center;gap:8px}
.gen-button{min-height:32px;padding:4px 14px;border:1px solid var(--border-control);border-radius:var(--radius-full);background:var(--background-primary);color:var(--foreground-primary);font:600 13px/1.2 inherit;font-family:inherit;cursor:pointer}
.gen-button:hover{background-image:linear-gradient(var(--overlay-interaction-hover),var(--overlay-interaction-hover))}
.gen-button:focus-visible{outline:var(--focus-width) solid var(--border-focus);outline-offset:var(--focus-offset)}
.gen-status{font-size:13px;font-weight:600;color:var(--foreground-accent)}
.gen-button-primary{background:var(--background-accent);border-color:var(--background-accent);color:var(--foreground-on-accent)}
.gen-button-primary:hover{background-image:linear-gradient(var(--overlay-on-accent-hover),var(--overlay-on-accent-hover))}
.gen-card-actions{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px}
.gen-card summary{cursor:pointer;font-size:13px;font-weight:600;color:var(--foreground-accent);width:fit-content}
.gen-card details[open] summary{margin-bottom:8px}
.gen-custom-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 14px;border:1px solid var(--border-default);border-radius:var(--radius-small);background:var(--background-secondary);font-size:14px}
.gen-muted{color:var(--foreground-secondary)}
.gen-chip{display:inline-flex;align-items:center;gap:6px;padding:4px 6px 4px 12px;border:1px solid var(--border-default);border-radius:var(--radius-full);background:var(--background-secondary);font-size:14px}
.gen-chip-remove{width:26px;height:26px;border:0;border-radius:var(--radius-full);background:transparent;color:var(--foreground-secondary);font-size:18px;line-height:1;cursor:pointer}
.gen-chip-remove:hover{background-image:linear-gradient(var(--overlay-interaction-hover),var(--overlay-interaction-hover))}
.gen-chip-remove:focus-visible,.gen-input:focus-visible{outline:var(--focus-width) solid var(--border-focus);outline-offset:0}
.gen-language{border:1px solid var(--border-default);border-radius:var(--radius-small);background:var(--background-primary)}
.gen-language>summary{cursor:pointer;padding:12px 14px;font-size:15px}
.gen-language[open]>summary{border-bottom:1px solid var(--border-default)}
.gen-editor-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px;padding:14px}
.gen-editor-actions{display:flex;align-items:end}
.gen-field{display:grid;gap:4px;align-content:start;min-width:0}
.gen-inline{grid-template-columns:auto minmax(0,220px);align-items:center;gap:8px}
.gen-field-label{display:flex;flex-wrap:wrap;align-items:center;gap:6px;font-size:13px;font-weight:600;color:var(--foreground-primary)}
.gen-badge{padding:0 6px;border-radius:var(--radius-full);background:var(--background-secondary);border:1px solid var(--border-default);font-size:11px;font-weight:600;color:var(--foreground-warning)}
.gen-input{width:100%;min-height:38px;margin:0;padding:7px 10px;border:1px solid var(--border-control);border-radius:var(--radius-small);background:var(--background-primary);color:var(--foreground-primary);font:inherit;font-size:14px;line-height:1.4}
textarea.gen-input{resize:vertical}
.gen-input-fallback{border-style:dashed}
""".strip()


def engine_parts():
    head = (ROOT / "dist" / "cmp-head.html").read_text()
    css = re.search(r"<style data-cmp-critical>(.*?)</style>", head, re.S).group(1)
    engine = re.search(r'<script data-cmp-engine="([^"]+)">(.*?)</script>', head, re.S)
    return css, engine.group(1), engine.group(2)


def data_payload():
    css, version, engine = engine_parts()
    return {
        "css": css,
        "version": version,
        "engine": engine,
        "languages": languages.LANGUAGES,
        "languageOrder": languages.ORDER,
        "rtl": languages.RTL_LANGUAGES,
        "purposeOrder": catalog.PURPOSES,
        "serviceDescriptions": service_descriptions_payload(),
        "themeCss": ":where(html){" + ";".join(f"{k}:{v}" for k, v in theme.definitions().items()) + "}",
        "fragments": fragments_payload(),
    }


def service_descriptions_payload():
    """All catalog descriptions per service and language (en/de/es from the catalog, others from service_descriptions.py)."""
    out = {}
    for service in catalog.CATALOG:
        texts = {"en": service["description"], "de": service["descriptionDe"], "es": service["descriptionEs"]}
        texts.update(service_descriptions.DESCRIPTIONS.get(service["id"], {}))
        out[service["id"]] = texts
    return out


def fragments_payload():
    return fragments.build()


CHUNK_SIZE = 45000


def embed_codes():
    """Return (logic embed code, [data chunk embed codes]); each stays below Webstudio's 50,000 character limit."""
    data = json.dumps(data_payload(), ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/").replace("<!--", "\\u003C!--")
    chunks = []
    position = 0
    while position < len(data):
        end = min(position + CHUNK_SIZE, len(data))
        # never split inside an escape sequence
        while end < len(data) and data[end - 1] == "\\":
            end -= 1
        chunks.append(data[position:end])
        position = end
    chunk_codes = [f'<script type="application/json" data-gen-chunk="{i}">{chunk}</script>' for i, chunk in enumerate(chunks)]
    source = (ROOT / "src" / "generator.js").read_text()
    tmp = ROOT / ".temp" / "generator.build.js"
    tmp.write_text(source)
    minified = subprocess.run(
        ["npx", "--yes", "esbuild@0.25.0", str(tmp), "--minify", "--target=es2017", "--legal-comments=none", "--charset=utf8"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    logic = f"<style>{GENERATOR_CSS}</style><script>{minified}</script>"
    for code in [logic, *chunk_codes]:
        assert len(code) < 50000, len(code)
    return logic, chunk_codes


def expr(code):
    return "{expression`" + code + "`}"


def purpose_item():
    return f"""
<div ws:label='Purpose Group' {T('site-purpose-group')}>
  <h2 {T('site-heading-small')}>{expr('collectionItem.title')}</h2>
  <p {T('site-help')}>{expr('collectionItem.description')}</p>
  <div ws:label='Catalog Services' {T('site-purpose-group')}></div>
</div>"""


def service_item():
    c = "collectionItem"
    cookies_expr = expr("(collectionItem.cookies ?? []).join(' ')")
    consent_expr = expr("(collectionItem.consentMode ?? []).join(' ')")
    attrs = " ".join([
        f"data-gen-row={expr(c + '.id')}",
        f"data-gen-title={expr(c + '.title')}",
        f"data-gen-purpose={expr(c + '.purpose')}",
        f"data-gen-placement={expr(c + '.placement')}",
        f"data-gen-description={expr(c + '.description')}",
        f"data-gen-description-de={expr(c + '.descriptionDe')}",
        f"data-gen-description-es={expr(c + '.descriptionEs')}",
        "data-gen-cookies=" + cookies_expr,
        "data-gen-consent-mode=" + consent_expr,
        f"data-gen-markup={expr(c + '.markup')}",
        f"data-gen-note={expr(c + '.note')}",
    ])
    return f"""
<div ws:label='Catalog Service' {attrs} {T('site-option')}>
  <label {T('site-option-label')}>
    <input type='checkbox' data-gen-service={expr(c + '.id')} {T('site-checkbox')} />
    <span {T('site-option-text')}>
      <span {T('site-label')}>{expr(c + '.title')}</span>
      <span {T('site-help')}>{expr(c + '.description')}</span>
    </span>
  </label>
  <div ws:label='Service Fields' data-gen-fields='' {T('site-option-fields')}></div>
</div>"""


def field_item():
    c = "collectionItem"
    return f"""
<label ws:label='Service Field' {T('site-field')}>
  <span {T('site-help')}>{expr(c + '.label')}</span>
  <input type='text' data-gen-field={expr(c + '.id')} placeholder={expr(c + '.placeholder')} autocomplete='off' spellcheck='false' {T('site-input')} />
</label>"""


ENGLISH_NAMES = {"en": "English", "de": "German", "es": "Spanish", "fr": "French", "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "pl": "Polish", "ar": "Arabic", "he": "Hebrew"}


def language_names():
    names = [ENGLISH_NAMES[code] for code in languages.ORDER]
    return ", ".join(names[:-1]) + " and " + names[-1]


def language_options():
    return "".join(f"<option value='{code}'>{txt(languages.LANGUAGES[code]['name'] + ' (' + code + ')')}</option>" for code in languages.ORDER)


def field(label, input_html, help_text=None):
    help_html = f"<span {T('site-help')}>{rich(help_text)}</span>" if help_text else ""
    return f"<label {T('site-field')}><span {T('site-label')}>{txt(label)}</span>{input_html}{help_html}</label>"


def text_input(attr, placeholder="", type_="text"):
    return f"<input type='{type_}' {attr} placeholder='{placeholder}' autocomplete='off' spellcheck='false' {T('site-input')} />"


def checkbox(attr, label, help_text=None):
    help_html = f"<span {T('site-help')}>{rich(help_text)}</span>" if help_text else ""
    return f"""<label {T('site-option', 'site-option-label')}><input type='checkbox' {attr} {T('site-checkbox')} /><span {T('site-option-text')}><span {T('site-label')}>{txt(label)}</span>{help_html}</span></label>"""


def steps():
    purposes = "".join(f"<option value='{pid}'>{txt(catalog.PURPOSE_TEXT[pid]['en'][0])}</option>" for pid in catalog.PURPOSES)
    return f"""
<div ws:label='Generator Steps' {T('site-generator-steps')}>
  <fieldset ws:label='Step Services' {T('site-fieldset')}>
    <legend {T('site-legend')}>1. Choose services</legend>
    <p {T('site-help')}>{rich('Select the services your site uses and enter their IDs. Empty fields use the placeholder, which you can replace later.')}</p>
    <div ws:label='Catalog' {T('site-generator-steps')}></div>
  </fieldset>

  <fieldset ws:label='Step Custom' {T('site-fieldset')}>
    <legend {T('site-legend')}>2. Add your own services</legend>
    <p {T('site-help')}>{rich('For services that aren’t in the catalog. Cookie patterns starting with `^` are regular expressions.')}</p>
    <div {T('site-form-grid')}>
      {field('Title', text_input("data-gen-custom='title'", 'Booking widget'))}
      {field('Service key', text_input("data-gen-custom='name'", 'booking-widget'), 'Optional. Used in `data-cmp-service`.')}
      {field('Purpose', f"<select data-gen-custom='purpose' {T('site-input')}>{purposes}</select>")}
      {field('Cookies', text_input("data-gen-custom='cookies'", '^_bw, bw_session'))}
    </div>
    {field('Description', text_input("data-gen-custom='description'", 'Lets visitors book tables online.'))}
    <div {T('site-form-grid')}>
      {checkbox("data-gen-custom='required'", 'Required', 'Always active, can’t be declined.')}
      {checkbox("data-gen-custom='optOut'", 'Active by default', 'Runs until the visitor declines.')}
    </div>
    <div {T('site-actions')}>
      <button type='button' data-gen-action='add-custom' {T('consent-button', 'is-consent-button-secondary')}>Add service</button>
      <span data-gen-custom-message='' role='status' {T('site-help')}></span>
    </div>
    <div ws:label='Custom Services List' data-gen-custom-list='' {T('site-purpose-group')}></div>
  </fieldset>

  <fieldset ws:label='Step Import' {T('site-fieldset')}>
    <legend {T('site-legend')}>3. Import an existing configuration</legend>
    <p {T('site-help')}>{rich('Paste a `consentServices` array, `consentTranslations`, or a Klaro config (the JavaScript object with a `services` array, including translations, purposes, regex cookie patterns and storage options). Known services are matched to the catalog, all others become custom services. The text is parsed as data and never executed.')}</p>
    <textarea data-gen-import='' rows='8' spellcheck='false' aria-label='Configuration to import' placeholder='[ {{ "name": "matomo", "cookies": ["^_pk_"] }} ]' {T('site-input', 'is-site-input-code')}></textarea>
    <div {T('site-actions')}>
      <button type='button' data-gen-action='import' {T('consent-button', 'is-consent-button-secondary')}>Import</button>
      <span data-gen-import-message='' role='status' {T('site-help')}></span>
    </div>
  </fieldset>

  <fieldset ws:label='Step Languages' {T('site-fieldset')}>
    <legend {T('site-legend')}>4. Languages</legend>
    <p {T('site-help')}>{rich('Add every language your site uses, matching each page’s **Language** setting. Built-in texts exist for ' + language_names() + '. Any other code (for example `tr`, `pt-BR` or `fa`) starts from English for you to translate. Right-to-left languages are detected automatically. The first language is the fallback.')}</p>
    <div {T('site-form-grid')}>
      {field('Built-in language', f"<select data-gen-language-pick='' {T('site-input')}>{language_options()}</select>")}
      {field('Or any language code', text_input("data-gen-language-code=''", 'tr, pt-BR, fa'))}
    </div>
    <div {T('site-actions')}>
      <button type='button' data-gen-action='add-language' {T('consent-button', 'is-consent-button-secondary')}>Add language</button>
      <span data-gen-language-message='' role='status' {T('site-help')}></span>
    </div>
    <div ws:label='Selected Languages' data-gen-language-list='' {T('site-actions')}></div>
  </fieldset>

  <fieldset ws:label='Step Translations' {T('site-fieldset')}>
    <legend {T('site-legend')}>5. Translations</legend>
    <p {T('site-help')}>{rich('Every text of the notice, the preferences modal, the purposes and your services, per language. Fields marked **English – translate** have no built-in translation yet. Inputs follow each language’s writing direction.')}</p>
    <div ws:label='Translation Editor' data-gen-translation-editor='' {T('site-purpose-group')}></div>
  </fieldset>

  <fieldset ws:label='Step Options' {T('site-fieldset')}>
    <legend {T('site-legend')}>6. Options</legend>
    <div {T('site-form-grid')}>
      {field('Privacy policy URL', text_input("data-gen-option='privacyUrl'", '/privacy'))}
      {field('Consent cookie name', text_input("data-gen-option='storageName'", 'cmp_consent'))}
      {field('Cookie lifetime (days)', text_input("data-gen-option='cookieExpiresAfterDays'", '365', 'number'))}
      {field('Cookie domain', text_input("data-gen-option='cookieDomain'", '.example.com'), 'Optional. Shares consent across subdomains.')}
    </div>
    <div {T('site-form-grid')}>
      {checkbox("data-gen-option='noNotice'", 'Contextual consent only', 'No notice on page load. Visitors allow YouTube, Maps and other embeds where they appear, or in the Privacy settings. Head scripts such as analytics stay blocked until visitors enable them there.')}
      {checkbox("data-gen-option='mustConsent'", 'Require a decision', 'Opens the preferences modal instead of the notice.')}
      {checkbox("data-gen-option='consentMode'", 'Google Consent Mode v2', 'Maps Google Analytics and Google Ads automatically.')}
      {checkbox("data-gen-option='dataLayer'", 'dataLayer events', 'Pushes `cmp_consent` for Google Tag Manager.')}
    </div>
    <div {T('site-actions')}>
      <button type='button' data-gen-action='reset' {T('consent-button', 'is-consent-button-ghost')}>Reset generator</button>
    </div>
  </fieldset>
</div>"""


def copy_row(name, label, primary=False):
    variant = "is-consent-button-primary" if primary else "is-consent-button-secondary"
    return f"""<span {T('site-actions')}>
      <button type='button' data-gen-copy='{name}' {T('consent-button', variant)}>{txt(label)}</button>
      <span data-gen-copy-status='{name}' aria-live='polite' {T('site-status-text')}></span>
    </span>"""


def step(number, title, text, body):
    return f"""
<div ws:label='Install Step {number}' {T('site-output-block')}>
  <h3 {T('site-heading-small')}>{txt(f'{number}. {title}')}</h3>
  <p {T('site-help')}>{rich(text)}</p>
  {body}
</div>"""


def code_output(name):
    return f"<pre {T('site-code', 'is-site-code-full', 'is-site-code-scroll')}><code data-gen-output='{name}' {T('site-code-content')}></code></pre>"


def output_panel():
    return f"""
<aside ws:label='Generator Output' aria-label='Generated configuration' {T('site-generator-output')}>
  <div {T('site-stack')}>
    <h2 {T('site-docs-heading')}>Install your consent manager</h2>
    <p data-gen-summary='' {T('site-help')}></p>
    <p {T('site-help')}>{rich('Each **Copy** button puts one part on your clipboard. Parts marked **paste in Webstudio** are real Webstudio instances: select the target in the Navigator or on the canvas and press ⌘/Ctrl + V.')}</p>
  </div>
  {step(1, 'Custom Code', 'Open **Project Settings → Custom Code** and paste this at the very top. It contains the engine, the `--cmp-*` theme variables (they pick up Craft variables automatically) and your blocked head scripts. Publish once so it takes effect.', copy_row('custom-code', 'Copy Custom Code', True) + code_output('custom-code'))}
  <div data-gen-output-list='notes' {T('site-purpose-group')}></div>
  {step(2, 'Consent Manager component', '**Paste in Webstudio:** select the **Body** of a page and paste. You get the notice and preferences modal as a shared **Slot**, with your services and translations already filled in. Then copy that Slot and paste it on every other page, or add it to your page template. Each copy from the generator creates a new Consent Manager; if one is already installed, update its variables instead (see below).', copy_row('component', 'Copy Consent Manager', True))}
  {step(3, 'Consent Gates for embeds and videos', '**Paste in Webstudio:** select the element where the video, map or widget should appear and paste its gate. YouTube and Vimeo use Webstudio’s native components: the video stays visible and the consent notice appears when the visitor clicks play. Other embeds show a placeholder until the visitor allows the service.', f"<div data-gen-output-list='embeds' {T('site-purpose-group')}></div>")}
  {step(4, 'Privacy settings link', '**Paste in Webstudio:** select your footer and paste. Visitors must be able to change their choice at any time; the button opens the preferences modal on every page.', copy_row('link', 'Copy Privacy settings link'))}
  <details ws:label='Update Existing Installation' {T('site-output-block')}>
    <summary {T('consent-purpose-summary')}>Updating an existing installation?</summary>
    <p {T('site-help')}>{rich('If the Consent Manager is already on your site, you only need the variables. Select its root instance, open the **Data** panel and replace the value of each variable. Update the Custom Code too if you added head scripts.')}</p>
    <div {T('site-output-header')}><h4 {T('site-label')}>consentServices</h4>{copy_row('services', 'Copy')}</div>
    {code_output('services')}
    <div {T('site-output-header')}><h4 {T('site-label')}>consentTranslations</h4>{copy_row('translations', 'Copy')}</div>
    {code_output('translations')}
  </details>
  <p ws:label='Support' {T('site-help')}>{txt('Saved you some time? ')}<a href='{SUPPORT_URL}' target='_blank' rel='noopener noreferrer' {T('consent-link')}>{txt('Help cover the project’s costs via PayPal')}</a></p>
</aside>"""


def layout():
    return f"""
<section ws:label='Generator' data-gen-root='' {T('site-generator-layout')}>
  {steps()}
  {output_panel()}
</section>"""


def parts():
    head = page_header("/generator")
    top = intro(
        "Config generator",
        "Build your consent configuration.",
        "Pick services, add your own or import an existing configuration. You get the Custom Code snippet, both variables and every embed, ready to paste. Everything runs in your browser; nothing is uploaded.",
    )
    return head, top, layout(), page_footer()
