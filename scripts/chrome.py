"""Shared site header and footer (Slots) with page-referenced links."""

from comm import GITHUB_URL, STARTER_URL
from rich import txt
from ui import T

PAGES = {
    "home": "subridMvnfjVeM7rVa1Zi",
    "generator": "_z43E-i8iKE0_6Eev8Jyu",
    "examples": "CgtVEjmEeLrC6kfRxoPZD",
    "docs": "FCi6-VSonqxrmw79t5_ST",
    "privacy": "6ZWZC6kYCVoWV1mVi8U1e",
    "legal": "VcCFjAiKvdSRt4MolxgMh",
    "contact": "qSsMOvYn_n-SQIoP-B4u3",
    "install": "XatTUnspJHO07Ra0J3Sp9",
}

PRIVACY_SETTINGS = [("en", "Privacy settings"), ("de", "Datenschutz-Einstellungen"), ("es", "Configuración de privacidad"), ("ar", "إعدادات الخصوصية")]


def page(key):
    return "{new PageValue('" + PAGES[key] + "')}"


def localized(pairs):
    return "".join(f"<span data-cmp-lang='{lang}'>{txt(label)}</span>" for lang, label in pairs)


MENU_LINKS = [("install", "AI install"), ("generator", "Generator"), ("examples", "Examples"), ("docs", "Docs")]
MENU_TEXT = {
    "open": [("en", "Open menu"), ("de", "Menü öffnen"), ("es", "Abrir menú"), ("ar", "فتح القائمة")],
    "close": [("en", "Close menu"), ("de", "Menü schließen"), ("es", "Cerrar menú"), ("ar", "إغلاق القائمة")],
    "title": [("en", "Menu"), ("de", "Menü"), ("es", "Menú"), ("ar", "القائمة")],
}
MENU_ICON = (
    "<svg viewBox='0 0 24 24' aria-hidden='true' focusable='false' " + T('site-menu-icon') + ">"
    "<path d='M4 7h16M4 12h16M4 17h16' stroke='currentColor' stroke-width='2' stroke-linecap='round' fill='none' />"
    "</svg>"
)
CLOSE_ICON = (
    "<svg viewBox='0 0 24 24' aria-hidden='true' focusable='false' " + T('site-menu-icon') + ">"
    "<path d='M6 6l12 12M18 6L6 18' stroke='currentColor' stroke-width='2' stroke-linecap='round' fill='none' />"
    "</svg>"
)


def hidden_label(pairs):
    return "".join(f"<span data-cmp-lang='{lang}' {T('site-visually-hidden')}>{txt(label)}</span>" for lang, label in pairs)


def mobile_menu():
    links = "".join(f"<a href={page(key)} {T('site-menu-link')}>{txt(label)}</a>" for key, label in MENU_LINKS)
    return f"""
<Dialog ws:label='Mobile Menu'>
  <DialogTrigger ws:label='Menu Button'>
    <button type='button' {T('site-menu-button')}>{MENU_ICON}{hidden_label(MENU_TEXT['open'])}</button>
  </DialogTrigger>
  <DialogOverlay ws:label='Menu Overlay' {T('site-menu-overlay')}>
    <DialogContent ws:label='Menu Sheet' {T('site-menu-sheet')}>
      <div {T('site-menu-header')}>
        <DialogTitle ws:label='Menu Title' {T('site-menu-title')}>{localized(MENU_TEXT['title'])}</DialogTitle>
        <DialogClose ws:label='Menu Close' {T('site-menu-close')}>{CLOSE_ICON}{hidden_label(MENU_TEXT['close'])}</DialogClose>
      </div>
      <nav aria-label='Main' {T('site-menu-nav')}>{links}</nav>
      <DialogClose ws:label='Menu Privacy Settings' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-secondary', 'is-consent-button-block')}>{localized(PRIVACY_SETTINGS)}</DialogClose>
    </DialogContent>
  </DialogOverlay>
</Dialog>"""


def header():
    links = "".join(
        f"<a href={page(key)} {T('site-nav-link')}>{txt(label)}</a>"
        for key, label in MENU_LINKS
    )
    return f"""
<header ws:label='Site Header' {T('site-header')}>
  <div {T('site-header-inner')}>
    <a href={page('home')} {T('site-brand')}><Image src={{new AssetValue('rbTshEC0xy_MKR7Z9Gq6B')}} alt='Native CMP' width={{1236}} height={{378}} loading='eager' {T('site-logo')} /></a>
    <nav aria-label='Main' {T('site-nav')}>{links}</nav>
    <button type='button' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-secondary', 'is-site-desktop-only')}>{localized(PRIVACY_SETTINGS)}</button>
    {mobile_menu()}
  </div>
</header>"""


# plain PayPal payment link (no SDK); the payer enters the amount
SUPPORT_URL = "https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=info%40elecos.de&item_name=Support+Native+CMP&currency_code=EUR&no_shipping=1"
SUPPORT = [("en", "Support the project"), ("de", "Projekt unterstützen"), ("es", "Apoyar el proyecto"), ("ar", "ادعم المشروع")]


def support_link(tokens=("consent-link",), pairs=SUPPORT):
    return f"<a href='{SUPPORT_URL}' target='_blank' rel='noopener noreferrer' {T(*tokens)}>{localized(pairs)}</a>"


def footer():
    href = lambda target: f"'{target}'" if target.startswith("https://") else page(target)
    links = "".join(
        f"<a href={href(target)} {T('consent-link')}>{txt(label)}</a>"
        for target, label in [("install", "AI install"), ("generator", "Generator"), ("examples", "Examples"), ("docs", "Documentation"), (STARTER_URL, "Starter"), (GITHUB_URL, "GitHub"), ("contact", "Contact"), ("privacy", "Privacy policy"), ("legal", "Legal notice")]
    )
    return f"""
<footer ws:label='Site Footer' {T('site-footer')}>
  <span>{txt('Native CMP · a project by ELECOS UG (haftungsbeschränkt)')}</span>
  <nav aria-label='Footer' {T('site-actions')}>
    {links}
    {support_link()}
    <button type='button' data-cmp-action='open-modal' {T('consent-link')}>{localized(PRIVACY_SETTINGS)}</button>
    <button type='button' data-cmp-action='reset' {T('consent-link')}>Reset consent</button>
  </nav>
</footer>"""
