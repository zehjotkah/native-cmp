"""/privacy: the site's own privacy policy.

A draft for ELECOS to review, describing what nativecmp.com actually does:
Webstudio hosting behind Cloudflare, self-hosted Rybbit analytics, the consent
cookie, this site's own consent log, the contact form through n8n, and the
Google Maps demonstration further down the page. The demo gate and the managed
demo scripts stay on the page, because the end-to-end suite uses them to check
client-side navigation.
"""

from rich import txt, rich, table, callout, page_header, page_footer, intro
from ui import T, MANAGED_SCRIPTS, js

UPDATED = "20 September 2026"

def h2(text, id_=None):
    ident = f" id='{id_}'" if id_ else ""
    return f"<h2{ident} {T('site-docs-heading')}>{txt(text)}</h2>"


def h3(text):
    return f"<h3 {T('site-docs-subheading')}>{txt(text)}</h3>"


def p(text):
    return f"<p {T('site-body-text')}>{rich(text)}</p>"


def ul(items):
    return f"<ul {T('site-list')}>" + "".join(f"<li>{rich(item)}</li>" for item in items) + "</ul>"


def section(id_, title, blocks):
    return f"<section id='{id_}' ws:label='{title}' {T('site-docs-section')}>{h2(title, id_)}{''.join(blocks)}</section>"


CONTROLLER = section("controller", "Who is responsible", [
    p("ELECOS UG (haftungsbeschränkt), Hauptstr. 42, 16341 Panketal, Germany, represented by its managing director Cosimo Kroll, is the controller for this website. Email: [info@elecos.de](mailto:info@elecos.de). Full company details are in our [legal notice](/legal-notice)."),
    p("We have not appointed a data protection officer, because we are not required to."),
])

HOSTING = section("hosting", "Hosting and server logs", [
    p("This website is built and hosted with **Webstudio** (Webstudio Inc., USA) and delivered through **Cloudflare** (Cloudflare, Inc., USA, with servers in Europe). When you open a page, your browser necessarily sends your IP address, the requested address, the time, the referring page and your browser and operating system to those servers. This data is processed to deliver the site securely and to defend against attacks."),
    p("**Legal basis**: Art. 6(1)(f) GDPR, our legitimate interest in operating a secure and reliable website. Both providers process data for us as processors under Art. 28 GDPR, and transfers to the USA are covered by the EU standard contractual clauses and their EU-U.S. Data Privacy Framework certifications."),
])

COOKIES = section("cookies", "The consent cookie", [
    p("We set exactly one cookie of our own:"),
    table(["Cookie", "Purpose", "Stored for"], [
        ["`cmp_consent`", "Stores your privacy choice, your consent ID and the time of your decision, so we do not ask again on every page.", "365 days"],
    ]),
    p("This cookie is technically necessary to honour your choice. **Legal basis**: § 25(2) no. 2 TDDDG and Art. 6(1)(c)/(f) GDPR. It contains no identifier that we use to recognise you anywhere else."),
])

CONSENT_LOG = section("consent-log", "Consent log (proof of consent)", [
    p("We must be able to demonstrate that you consented (Art. 7(1) GDPR). When you accept, decline, save a selection or withdraw your consent, we store one entry on our own server at `consentlog.nativecmp.com`, a Cloudflare Worker with a database in the EU that we operate ourselves:"),
    ul([
        "your **consent ID**, a random value that is also in your `cmp_consent` cookie and shown in the privacy settings,",
        "the **time** of the decision,",
        "the **type** of decision (accept, decline, save, withdraw),",
        "**which services** you allowed or refused,",
        "a **fingerprint** of the service list and texts you were shown,",
        "the **page language** and the website the decision was made on.",
    ]),
    p("**We do not store your IP address**, the page URL or your user agent. Entries are deleted automatically after three years, the period in which claims could still be raised. **Legal basis**: Art. 6(1)(c) GDPR in conjunction with Art. 7(1) GDPR, our legal obligation to demonstrate consent."),
    p("If you want to know what is stored for you, send us your consent ID from the privacy settings and we will tell you, or delete it."),
])

ANALYTICS = section("analytics", "Website analytics", [
    p("We use **Rybbit**, an open-source analytics tool that we host ourselves on a server at Hetzner Online GmbH in Germany. No data goes to a third-party analytics provider."),
    p("Rybbit works **without cookies** and does not store IP addresses. Your IP address is used only briefly to derive an approximate location (country and region) and is then discarded. We see page views, referring pages, rough location, device type, browser and operating system, and anonymous session identifiers that cannot be traced back to you."),
    p("Because no information is stored on or read from your device and no personal profile is created, this runs without consent. **Legal basis**: Art. 6(1)(f) GDPR, our legitimate interest in understanding which pages are useful. You can object at any time by writing to [info@elecos.de](mailto:info@elecos.de)."),
])

CONTACT = section("contact", "Contact form and email", [
    p("When you use our [contact form](/contact), we process the name, email address and message you enter, together with the page the form was sent from. The message reaches us by email. Your browser does not contact any third party while sending."),
    p("**Legal basis**: Art. 6(1)(b) GDPR when your request concerns a contract or its preparation, otherwise Art. 6(1)(f) GDPR, our legitimate interest in answering enquiries. We keep enquiries as long as we need them to answer you and for as long as statutory retention periods require, then delete them."),
    p("The same applies when you write to us directly at [info@elecos.de](mailto:info@elecos.de)."),
])

EMBEDS = section("embeds", "Embedded content", [
    p("This website demonstrates a consent manager, so it deliberately contains embedded content that is blocked until you allow it:"),
    ul([
        "**Google Maps** (Google Ireland Limited, Ireland) in the live demonstration on our homepage.",
        "**YouTube** and **Vimeo** videos in the documentation examples, using their privacy-enhanced modes.",
    ]),
    p("Nothing is loaded from those providers until you allow the service, either in the privacy settings or on the content itself. Once you do, your IP address and browser information reach the provider, which may set its own cookies and may transfer data to the USA. **Legal basis**: Art. 6(1)(a) GDPR and § 25(1) TDDDG, your consent, which you can withdraw at any time in the privacy settings."),
    p("The services listed in our privacy settings include **demonstration entries** such as Google Analytics and Meta Pixel. They exist to show how the consent manager works. Selecting them loads no tracking code: this site runs none. Two demonstration scripts write a line to your browser console when analytics is allowed, so we can verify that consent is honoured across pages."),
])

PAYPAL = section("payments", "Voluntary support via PayPal", [
    p("Our support links lead to PayPal (PayPal (Europe) S.à r.l. et Cie, S.C.A., Luxembourg). No PayPal script or button code runs on this website; the link simply opens PayPal in a new tab. Once there, PayPal's own [privacy statement](https://www.paypal.com/uk/legalhub/privacy-full) applies, and we receive only the information PayPal shows us about a payment."),
])

RIGHTS = section("rights", "Your rights", [
    p("Under the GDPR you have the right to:"),
    ul([
        "**access** the data we hold about you (Art. 15),",
        "have inaccurate data **corrected** (Art. 16),",
        "have data **deleted** (Art. 17),",
        "have processing **restricted** (Art. 18),",
        "receive your data in a **portable** format (Art. 20),",
        "**object** to processing based on legitimate interests (Art. 21), and",
        "**withdraw consent** at any time, without affecting what happened before (Art. 7(3)). Use the privacy settings link in the footer.",
    ]),
    p("Write to [info@elecos.de](mailto:info@elecos.de) to exercise any of these. You also have the right to complain to a supervisory authority, for example the data protection authority of the State of Brandenburg, where we are based."),
])

CHANGES = section("changes", "Changes to this policy", [
    p(f"We update this policy when the website changes. This version is from **{UPDATED}**."),
])

# The demo scripts render nothing: they are text/plain placeholders that only write
# to the console when analytics is allowed. The end-to-end suite uses them to check
# that consent survives client-side navigation to this page.
DEMO_SCRIPTS = f"""<HtmlEmbed ws:label='Managed Scripts (demo)' code={js(MANAGED_SCRIPTS)} />"""


def content():
    return "".join([
        CONTROLLER,
        HOSTING,
        COOKIES,
        CONSENT_LOG,
        ANALYTICS,
        CONTACT,
        EMBEDS,
        PAYPAL,
        RIGHTS,
        CHANGES,
        DEMO_SCRIPTS,
    ])


def main_fragment():
    return f"""
<main ws:label='Privacy Policy' {T('site-section')}>
  <div {T('site-container')}>
    <div {T('site-stack')}>
      <p {T('site-eyebrow')}>{txt('Privacy')}</p>
      <h1 {T('site-heading')}>{txt('Privacy policy')}</h1>
      <p {T('site-lead')}>{txt('What happens to your data on nativecmp.com: one consent cookie, cookieless analytics on our own server, a consent log without IP addresses, and embedded content that stays blocked until you allow it.')}</p>
      <p {T('site-help')}>{txt('Last updated: ' + UPDATED)}</p>
    </div>
    <div {T('site-docs-content')}>{content()}</div>
  </div>
</main>"""


def parts():
    return page_header("/privacy"), main_fragment(), page_footer()
