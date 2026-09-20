"""Multilingual Consent Manager: service registry + translations (en, de, es)."""

import json

from ui import T, expr, js, CLOSE_ICON

SERVICES = [
    {"name": "consent-manager", "required": True},
    {"name": "google-analytics", "cookies": ["^_ga", "_gid", "^_gat"]},
    {"name": "meta-pixel", "cookies": ["_fbp", "_fbc"]},
    {"name": "youtube"},
    {"name": "google-maps"},
]


def purposes(t):
    return [
        {"id": "essential", "title": t["essential"], "description": t["essentialText"],
         "services": [{"name": "consent-manager", "title": t["cmpTitle"], "description": t["cmpText"]}]},
        {"id": "analytics", "title": t["analytics"], "description": t["analyticsText"],
         "services": [{"name": "google-analytics", "title": "Google Analytics", "description": t["gaText"]}]},
        {"id": "marketing", "title": t["marketing"], "description": t["marketingText"],
         "services": [{"name": "meta-pixel", "title": "Meta Pixel", "description": t["metaText"]}]},
        {"id": "media", "title": t["media"], "description": t["mediaText"],
         "services": [{"name": "youtube", "title": "YouTube", "description": t["ytText"]},
                      {"name": "google-maps", "title": "Google Maps", "description": t["mapsText"]}]},
    ]


EN = dict(
    essential="Essential", essentialText="Required for the website to work, for example to remember your privacy choices.",
    cmpTitle="Consent manager", cmpText="Stores your privacy choices in the cmp_consent cookie.",
    analytics="Analytics", analyticsText="Helps us understand how visitors use the website so we can improve it.",
    gaText="Collects pseudonymous usage statistics.",
    marketing="Marketing", marketingText="Measures the performance of our advertising and shows more relevant ads.",
    metaText="Measures the effectiveness of ads on Facebook and Instagram.",
    media="External media", mediaText="Loads content from third-party platforms such as videos and maps.",
    ytText="Plays embedded videos. YouTube may set cookies once a video loads.", mapsText="Shows interactive maps.",
)
DE = dict(
    essential="Essenziell", essentialText="Für den Betrieb der Website erforderlich, zum Beispiel um Ihre Datenschutz-Auswahl zu speichern.",
    cmpTitle="Consent-Manager", cmpText="Speichert Ihre Auswahl im Cookie cmp_consent.",
    analytics="Statistik", analyticsText="Hilft uns zu verstehen, wie Besucher die Website nutzen, damit wir sie verbessern können.",
    gaText="Erhebt pseudonyme Nutzungsstatistiken.",
    marketing="Marketing", marketingText="Misst den Erfolg unserer Werbung und zeigt relevantere Anzeigen.",
    metaText="Misst die Wirksamkeit von Anzeigen auf Facebook und Instagram.",
    media="Externe Medien", mediaText="Lädt Inhalte von Drittanbietern wie Videos und Karten.",
    ytText="Spielt eingebettete Videos ab. YouTube kann beim Laden Cookies setzen.", mapsText="Zeigt interaktive Karten.",
)
ES = dict(
    essential="Esenciales", essentialText="Necesarios para que el sitio web funcione, por ejemplo para recordar tu elección de privacidad.",
    cmpTitle="Gestor de consentimiento", cmpText="Guarda tu elección en la cookie cmp_consent.",
    analytics="Analítica", analyticsText="Nos ayuda a entender cómo se usa el sitio web para poder mejorarlo.",
    gaText="Recoge estadísticas de uso seudonimizadas.",
    marketing="Marketing", marketingText="Mide el rendimiento de nuestra publicidad y muestra anuncios más relevantes.",
    metaText="Mide la eficacia de los anuncios en Facebook e Instagram.",
    media="Contenido externo", mediaText="Carga contenido de plataformas de terceros, como vídeos y mapas.",
    ytText="Reproduce vídeos incrustados. YouTube puede instalar cookies al cargar un vídeo.", mapsText="Muestra mapas interactivos.",
)

TRANSLATIONS = [
    {
        "lang": "en",
        "privacyLabel": "privacy policy",
        "privacyUrl": "/privacy",
        "notice": {
            "title": "We value your privacy",
            "text": "We use cookies and similar technologies for essential functions and, with your consent, for analytics, marketing and embedded media. You can change your choice at any time. Learn more in our",
            "changes": "Our services have changed since your last visit. Please review your choice.",
            "customize": "Customize", "decline": "Decline all", "accept": "Accept all",
        },
        "modal": {
            "title": "Privacy settings",
            "text": "Choose which services we may use. Essential services are always active. You can change your choice at any time. Learn more in our",
            "close": "Close privacy settings", "toggleAll": "Enable or disable all services",
            "alwaysActive": "Always active", "activeByDefault": "Active by default",
            "service": "service", "services": "services",
            "decline": "Decline all", "save": "Save selection", "accept": "Accept all",
        },
        "purposes": purposes(EN),
    },
    {
        "lang": "de",
        "privacyLabel": "Datenschutzerklärung",
        "privacyUrl": "/privacy",
        "notice": {
            "title": "Ihre Privatsphäre ist uns wichtig",
            "text": "Wir verwenden Cookies und ähnliche Technologien für notwendige Funktionen und, mit Ihrer Einwilligung, für Statistik, Marketing und eingebettete Medien. Sie können Ihre Auswahl jederzeit ändern. Mehr dazu in unserer",
            "changes": "Unsere Dienste haben sich seit Ihrem letzten Besuch geändert. Bitte prüfen Sie Ihre Auswahl.",
            "customize": "Anpassen", "decline": "Alle ablehnen", "accept": "Alle akzeptieren",
        },
        "modal": {
            "title": "Datenschutz-Einstellungen",
            "text": "Wählen Sie, welche Dienste wir nutzen dürfen. Essenzielle Dienste sind immer aktiv. Sie können Ihre Auswahl jederzeit ändern. Mehr dazu in unserer",
            "close": "Datenschutz-Einstellungen schließen", "toggleAll": "Alle Dienste aktivieren oder deaktivieren",
            "alwaysActive": "Immer aktiv", "activeByDefault": "Standardmäßig aktiv",
            "service": "Dienst", "services": "Dienste",
            "decline": "Alle ablehnen", "save": "Auswahl speichern", "accept": "Alle akzeptieren",
        },
        "purposes": purposes(DE),
    },
    {
        "lang": "es",
        "privacyLabel": "política de privacidad",
        "privacyUrl": "/privacy",
        "notice": {
            "title": "Tu privacidad nos importa",
            "text": "Usamos cookies y tecnologías similares para funciones esenciales y, con tu consentimiento, para analítica, marketing y contenido incrustado. Puedes cambiar tu elección en cualquier momento. Más información en nuestra",
            "changes": "Nuestros servicios han cambiado desde tu última visita. Revisa tu elección.",
            "customize": "Personalizar", "decline": "Rechazar todo", "accept": "Aceptar todo",
        },
        "modal": {
            "title": "Configuración de privacidad",
            "text": "Elige qué servicios podemos usar. Los servicios esenciales están siempre activos. Puedes cambiar tu elección en cualquier momento. Más información en nuestra",
            "close": "Cerrar la configuración de privacidad", "toggleAll": "Activar o desactivar todos los servicios",
            "alwaysActive": "Siempre activo", "activeByDefault": "Activo por defecto",
            "service": "servicio", "services": "servicios",
            "decline": "Rechazar todo", "save": "Guardar selección", "accept": "Aceptar todo",
        },
        "purposes": purposes(ES),
    },
]

AR_SERVICES = dict(
    essential="أساسية", essentialText="ضرورية لعمل الموقع، مثل تذكّر اختيارات الخصوصية الخاصة بك.",
    cmpTitle="مدير الموافقة", cmpText="يحفظ اختيارات الخصوصية الخاصة بك في ملف تعريف الارتباط cmp_consent.",
    analytics="الإحصاءات", analyticsText="تساعدنا على فهم كيفية استخدام الزوار للموقع لتحسينه.",
    gaText="يجمع إحصاءات استخدام مستعارة الهوية.",
    marketing="التسويق", marketingText="تقيس أداء إعلاناتنا وتعرض إعلانات أكثر ملاءمة.",
    metaText="يقيس فعالية الإعلانات على فيسبوك وإنستغرام.",
    media="الوسائط الخارجية", mediaText="تحمّل محتوى من منصات خارجية مثل مقاطع الفيديو والخرائط.",
    ytText="يشغّل مقاطع الفيديو المضمّنة. قد يحفظ يوتيوب ملفات تعريف الارتباط عند تحميل الفيديو.", mapsText="يعرض خرائط تفاعلية.",
)


def _pack_entry(code, services_text):
    from languages import LANGUAGES
    pack = LANGUAGES[code]
    return {"lang": code, "dir": pack["dir"], "privacyLabel": pack["privacyLabel"], "privacyUrl": "/privacy",
            "notice": pack["notice"], "modal": pack["modal"], "purposes": purposes(services_text)}


TRANSLATIONS.append(_pack_entry("ar", AR_SERVICES))

# Direction: explicit "dir" wins, otherwise detected from the language code
DIR_EXPRESSION = 'language.dir ?? (["ar","arc","ckb","dv","fa","he","ku","ps","sd","ug","ur","yi"].includes(language.lang.split("-")[0].toLowerCase()) ? "rtl" : "ltr")'

CANVAS_HELPER = (
    "<style>"
    "html:not([data-cmp]) [data-cmp-notice]:not([data-cmp-preview] *),"
    "html:not([data-cmp]) [data-cmp-modal]:not([data-cmp-preview] *){display:none}"
    '[data-cmp-preview="notice"] [data-cmp-modal],[data-cmp-preview="modal"] [data-cmp-notice]{display:none!important}'
    "html:not([data-cmp]) [data-cmp-lang] ~ [data-cmp-lang]{display:none}"
    "</style>"
)


def registry_item():
    return f"""
<div ws:label='Service Definition' hidden={{true}} data-cmp-service-def={expr('collectionItem.name')} data-cmp-required={expr('collectionItem.required ?? false')} data-cmp-default={expr('collectionItem.default ?? ""')} data-cmp-opt-out={expr('collectionItem.optOut ?? false')} data-cmp-only-once={expr('collectionItem.onlyOnce ?? false')} data-cmp-contextual-only={expr('collectionItem.contextualOnly ?? false')} data-cmp-cookies={expr('(collectionItem.cookies ?? []).join(" ")')} data-cmp-depends-on={expr('(collectionItem.dependsOn ?? []).join(" ")')}></div>
"""


def language_item():
    # authored with `collectionItem`; the parameter is renamed to `language` afterwards
    L = "collectionItem"
    lid = lambda base: expr(f'"{base}-" + {L}.lang')
    return f"""
<div ws:label='Language' data-cmp-lang={expr(L + '.lang')} lang={expr(L + '.lang')} {T('consent-language')}>
  <section ws:label='Consent Notice' data-cmp-notice='' role='region' aria-labelledby={lid('consent-notice-title')} {T('consent-notice')}>
    <div ws:label='Notice Body' {T('consent-notice-body')}>
      <h2 id={lid('consent-notice-title')} {T('consent-notice-title')}>{expr(L + '.notice.title')}</h2>
      <p {T('consent-notice-text')}>{expr(L + '.notice.text')} <a href={expr(L + '.privacyUrl')} {T('consent-link')}>{expr(L + '.privacyLabel')}</a>.</p>
      <p data-cmp-if='changed' {T('consent-notice-changes')}>{expr(L + '.notice.changes')}</p>
    </div>
    <div ws:label='Notice Actions' {T('consent-notice-actions')}>
      <button type='button' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-ghost')}>{expr(L + '.notice.customize')}</button>
      <button type='button' data-cmp-action='decline-all' {T('consent-button', 'is-consent-button-secondary')}>{expr(L + '.notice.decline')}</button>
      <button type='button' data-cmp-action='accept-all' {T('consent-button', 'is-consent-button-primary')}>{expr(L + '.notice.accept')}</button>
    </div>
  </section>
  <div ws:label='Consent Modal' data-cmp-modal='' {T('consent-modal')}>
    <div ws:label='Scrim' data-cmp-action='close' aria-hidden='true' {T('consent-modal-scrim')}></div>
    <div ws:label='Dialog' data-cmp-dialog='' role='dialog' aria-modal='true' aria-labelledby={lid('consent-modal-title')} aria-describedby={lid('consent-modal-text')} tabindex='-1' {T('consent-modal-dialog')}>
      <header ws:label='Modal Header' {T('consent-modal-header')}>
        <h2 id={lid('consent-modal-title')} {T('consent-modal-title')}>{expr(L + '.modal.title')}</h2>
        <button type='button' data-cmp-action='close' aria-label={expr(L + '.modal.close')} {T('consent-modal-close')}>{CLOSE_ICON}</button>
        <p id={lid('consent-modal-text')} {T('consent-modal-text')}>{expr(L + '.modal.text')} <a href={expr(L + '.privacyUrl')} {T('consent-link')}>{expr(L + '.privacyLabel')}</a>.</p>
      </header>
      <div ws:label='Modal Body' {T('consent-modal-body')}>
        <ul ws:label='Purposes' {T('consent-purposes')}>
          <li ws:label='Toggle All' {T('consent-purpose', 'is-consent-purpose-all')}>
            <div {T('consent-purpose-header')}>
              <label for={lid('consent-toggle-all')} {T('consent-purpose-label')}>{expr(L + '.modal.toggleAll')}</label>
              <input type='checkbox' role='switch' id={lid('consent-toggle-all')} data-cmp-toggle='all' {T('consent-switch')} />
            </div>
          </li>
        </ul>
      </div>
      <footer ws:label='Modal Footer' {T('consent-modal-footer')}>
        <p ws:label='Consent ID' data-cmp-if='confirmed' {T('consent-id')}><span>{expr(L + '.modal.consentId')}</span><span data-cmp-consent-id='' {T('consent-id-value')}></span></p>
        <button type='button' data-cmp-action='decline-all' {T('consent-button', 'is-consent-button-secondary')}>{expr(L + '.modal.decline')}</button>
        <button type='button' data-cmp-action='save' {T('consent-button', 'is-consent-button-secondary')}>{expr(L + '.modal.save')}</button>
        <button type='button' data-cmp-action='accept-all' {T('consent-button', 'is-consent-button-primary')}>{expr(L + '.modal.accept')}</button>
      </footer>
    </div>
  </div>
</div>
"""


def purpose_item():
    pid = 'language.lang + "-" + collectionItem.id'
    count = 'collectionItem.services.length + " " + (collectionItem.services.length === 1 ? language.modal.service : language.modal.services)'
    return f"""
<li ws:label='Purpose' data-cmp-purpose={expr('collectionItem.id')} {T('consent-purpose')}>
  <div ws:label='Purpose Header' {T('consent-purpose-header')}>
    <label for={expr('"consent-purpose-" + ' + pid)} {T('consent-purpose-label')}>
      <span>{expr('collectionItem.title')}</span>
      <span ws:label='Required Badge' data-cmp-if='required' {T('consent-badge')}>{expr('language.modal.alwaysActive')}</span>
    </label>
    <input type='checkbox' role='switch' id={expr('"consent-purpose-" + ' + pid)} data-cmp-toggle={expr('"purpose:" + collectionItem.id')} aria-describedby={expr('"consent-purpose-description-" + ' + pid)} {T('consent-switch')} />
  </div>
  <p id={expr('"consent-purpose-description-" + ' + pid)} {T('consent-purpose-description')}>{expr('collectionItem.description')}</p>
  <details ws:label='Purpose Services' {T('consent-purpose-services')}>
    <summary {T('consent-purpose-summary')}>{expr(count)}</summary>
    <ul ws:label='Services' {T('consent-services')}></ul>
  </details>
</li>
"""


def service_item():
    sid = 'language.lang + "-" + collectionItem.name'
    return f"""
<li ws:label='Service' data-cmp-service-item={expr('collectionItem.name')} {T('consent-service')}>
  <div ws:label='Service Header' {T('consent-service-header')}>
    <label for={expr('"consent-service-" + ' + sid)} {T('consent-service-label')}>
      <span>{expr('collectionItem.title')}</span>
      <span ws:label='Required Badge' data-cmp-if='required' {T('consent-badge')}>{expr('language.modal.alwaysActive')}</span>
      <span ws:label='Opt-out Badge' data-cmp-if='opt-out' {T('consent-badge')}>{expr('language.modal.activeByDefault')}</span>
    </label>
    <input type='checkbox' role='switch' id={expr('"consent-service-" + ' + sid)} data-cmp-toggle={expr('"service:" + collectionItem.name')} aria-describedby={expr('"consent-service-description-" + ' + sid)} {T('consent-switch')} />
  </div>
  <p id={expr('"consent-service-description-" + ' + sid)} {T('consent-service-description')}>{expr('collectionItem.description')}</p>
</li>
"""


if __name__ == "__main__":
    print(json.dumps(TRANSLATIONS)[:200])


# Builder preview flags. The Canvas Helper only acts while the engine is absent (html:not([data-cmp])),
# which is the Builder canvas; on the published site the engine sets data-cmp before the first paint.
CANVAS_VARIABLES = {"canvasPreview": "off", "canvasLanguage": ""}
CANVAS_HELPER_EXPRESSION = (
    '"<style>html:not([data-cmp]) [data-cmp-notice]:not([data-cmp-preview] *)"'
    ' + (canvasPreview === "notice" ? ":not(*)" : "")'
    ' + ",html:not([data-cmp]) [data-cmp-modal]:not([data-cmp-preview] *)"'
    ' + (canvasPreview === "modal" ? ":not(*)" : "")'
    ' + "{display:none}[data-cmp-preview=\\"notice\\"] [data-cmp-modal],[data-cmp-preview=\\"modal\\"] [data-cmp-notice]{display:none!important}html:not([data-cmp]) "'
    ' + (canvasLanguage ? "[data-cmp-lang]:not([data-cmp-lang=\\"" + canvasLanguage + "\\" i])" : "[data-cmp-lang] ~ [data-cmp-lang]")'
    ' + "{display:none}"'
    # Builder-only hint (data-ws-id exists only on the canvas), hidden with canvasPreview "hide"
    ' + (canvasPreview === "notice" || canvasPreview === "modal" || canvasPreview === "hide" ? "" : "[data-ws-id][data-cmp-root]:not([data-cmp-preview] *)::after{content:\\"Consent Manager hidden in the Builder · Data → canvasPreview: notice or modal\\";position:fixed;right:12px;bottom:12px;z-index:2147483000;padding:6px 12px;border-radius:999px;background:#15171c;color:#fff;font:600 12px/1.3 system-ui,sans-serif;pointer-events:none}")'
    ' + "</style>"'
)
