"""Legal notice (Impressum) page."""

from rich import txt
from ui import T


def detail_card(title, lines, lang="de"):
    body = "".join(
        (f"<span lang='{lang}' style={{{{display: 'block'}}}}>{line}</span>")
        for line in lines
    )
    return f"<div {T('site-card')}><h2 {T('site-heading-small')}>{txt(title)}</h2><p {T('site-text')}>{body}</p></div>"


def page():
    email = "<a href='mailto:info@elecos.de' " + T('consent-link') + ">info@elecos.de</a>"
    cards = "".join([
        f"<div {T('site-card')}><h2 {T('site-heading-small')}>Provider</h2><address lang='de' style={{{{fontStyle: 'normal'}}}} {T('site-text')}>"
        + "".join(f"<span style={{{{display: 'block'}}}}>{txt(line)}</span>" for line in ["ELECOS UG (haftungsbeschränkt)", "Hauptstr. 42", "16341 Panketal", "Deutschland"])
        + "</address></div>",
        f"<div {T('site-card')}><h2 {T('site-heading-small')}>Contact</h2><p {T('site-text')}><span lang='de'>{txt('E-Mail: ')}</span>{email}</p></div>",
        detail_card("Represented by", [txt("Vertreten durch den Geschäftsführer: Cosimo Kroll")]),
        detail_card("Register entry", [txt("Registergericht: Amtsgericht Frankfurt (Oder)"), txt("Registernummer: HRB 18855 FF")]),
        detail_card("VAT ID", [txt("Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:"), txt("DE345721414")]),
    ])
    return f"""
<main ws:label='Legal Notice' {T('site-section')}>
  <div {T('site-container')}>
    <div {T('site-stack')}>
      <p {T('site-eyebrow')}>{txt('Legal notice · Impressum')}</p>
      <h1 {T('site-heading')}>Legal notice</h1>
      <p {T('site-lead')}>{txt('Native CMP is a project by ELECOS UG (haftungsbeschränkt).')}</p>
    </div>
    <div {T('site-grid', 'is-site-grid-wide')}>{cards}</div>
  </div>
</main>"""
