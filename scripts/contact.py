"""Contact page: native Webstudio Form posting to the ELECOS n8n webhook (same setup as the other ELECOS sites)."""

from rich import txt
from ui import T

WEBHOOK = "https://n8n.elecos.de/webhook/submit"
STATE = "contactState"


def field(label, control):
    return f"<div {T('site-field')}>{label}{control}</div>"


def page():
    privacy = "{new PageValue('6ZWZC6kYCVoWV1mVi8U1e')}"
    form = f"""
<Form ws:label='Contact Form' method='post' enctype='multipart/form-data' {T('site-form')}>
  <p ws:label='Form Error' role='alert' {T('site-form-message', 'is-site-form-message-error')}>{txt('Your message could not be sent. Please reload the page and try again, or email us at info@elecos.de.')}</p>
  <div ws:label='Form Body' {T('site-form')}>
    <input ws:label='Hidden Website' type='hidden' name='website' required={{true}} />
    <input ws:label='Hidden Form' type='hidden' name='formular' value='kontakt' />
    {field(f"<label for='contact-name' {T('site-label')}>{txt('Name *')}</label>", f"<input id='contact-name' type='text' name='Name' autocomplete='name' placeholder='Your name' required={{true}} {T('site-input')} />")}
    {field(f"<label for='contact-email' {T('site-label')}>{txt('Email *')}</label>", f"<input id='contact-email' type='email' name='E-Mail' autocomplete='email' placeholder='you@example.com' required={{true}} {T('site-input')} />")}
    {field(f"<label for='contact-message' {T('site-label')}>{txt('Message *')}</label>", f"<textarea id='contact-message' name='Nachricht' placeholder='Your question, bug report or idea' required={{true}} {T('site-input', 'is-site-input-textarea')}></textarea>")}
    <p {T('site-help')}>{txt('We use your details only to answer your request. More in our ')}<a href={privacy} {T('consent-link')}>{txt('privacy policy')}</a>{txt('.')}</p>
    <div {T('site-actions')}><button type='submit' {T('consent-button', 'is-consent-button-primary')}>{txt('Send message')}</button></div>
  </div>
  <p ws:label='Form Success' role='status' {T('site-form-message')}>{txt('Thanks! Your message has been sent. We’ll get back to you as soon as we can.')}</p>
</Form>"""
    return f"""
<main ws:label='Contact' {T('site-section')}>
  <div {T('site-container')}>
    <div {T('site-split', 'is-site-split-top')}>
      <div {T('site-stack')}>
        <p {T('site-eyebrow')}>{txt('Contact')}</p>
        <h1 {T('site-heading-hero')}>{txt('Get in touch.')}</h1>
        <p {T('site-lead')}>{txt('Questions about setup, a bug, a feature idea or a service you’d like to see in the catalog? Send us a message.')}</p>
        <p {T('site-text')}>{txt('Prefer email? Write to ')}<a href='mailto:info@elecos.de' {T('consent-link')}>info@elecos.de</a>{txt('.')}</p>
      </div>
      <div {T('site-card')}>{form}</div>
    </div>
  </div>
</main>"""
