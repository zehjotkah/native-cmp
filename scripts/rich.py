"""Shared JSX helpers for documentation-style pages."""

import json
import re

from ui import T


def txt(value):
    return "{" + json.dumps(value) + "}"


INLINE = re.compile(r"(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*)")


def rich(text, code_tokens=("site-inline-code",)):
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("`"):
            out.append(f"<code {T(*code_tokens)}>{txt(part[1:-1])}</code>")
        elif part.startswith("["):
            label, href = re.match(r"\[([^\]]+)\]\(([^)]+)\)", part).groups()
            out.append(f"<a href='{href}' {T('consent-link')}>{txt(label)}</a>")
        elif part.startswith("**"):
            out.append(f"<strong>{txt(part[2:-2])}</strong>")
        else:
            out.append(txt(part))
    return "".join(out)


def p(text, token="site-body-text"):
    return f"<p {T(token)}>{rich(text)}</p>"


def ul(items):
    return f"<ul {T('site-list')}>" + "".join(f"<li>{rich(i)}</li>" for i in items) + "</ul>"


def code(snippet, label=None):
    head = f"<p {T('site-code-label')}>{txt(label)}</p>" if label else ""
    return head + f"<pre {T('site-code', 'is-site-code-full')}><code {T('site-code-content')}>{txt(snippet)}</code></pre>"


def callout(text):
    return f"<p {T('site-callout')}>{rich(text, ('site-inline-code', 'is-site-inline-code-contrast'))}</p>"


def table(headers, rows):
    head = "".join(f"<th scope='col' {T('site-table-header')}>{txt(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td {T('site-table-cell')}>{rich(c)}</td>" for c in row) + "</tr>" for row in rows)
    return f"<div {T('site-table-wrapper')}><table {T('site-table')}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def h3(text, id_=None):
    ident = f" id='{id_}'" if id_ else ""
    return f"<h3{ident} {T('site-docs-subheading')}>{rich(text)}</h3>"


def page_header(current):
    links = [("/", "Home"), ("/generator", "Generator"), ("/examples", "Examples"), ("/docs", "Docs")]
    nav = "".join(
        f"<a href='{href}' {T('site-nav-link')}" + (" aria-current='page'" if href == current else "") + f">{label}</a>"
        for href, label in links
    )
    return f"""
<header ws:label='Site Header' {T('site-header')}>
  <div {T('site-header-inner')}>
    <a href='/' {T('site-brand')}>Native CMP</a>
    <nav aria-label='Main' {T('site-nav')}>{nav}</nav>
    <button type='button' data-cmp-action='open-modal' {T('consent-button', 'is-consent-button-secondary')}>Privacy settings</button>
  </div>
</header>"""


def page_footer():
    return f"""
<footer ws:label='Site Footer' {T('site-footer')}>
  <span>Native CMP</span>
  <nav aria-label='Footer' {T('site-actions')}>
    <a href='/generator' {T('consent-link')}>Generator</a>
    <a href='/examples' {T('consent-link')}>Examples</a>
    <a href='/docs' {T('consent-link')}>Documentation</a>
    <a href='/privacy' {T('consent-link')}>Privacy policy</a>
    <button type='button' data-cmp-action='open-modal' {T('consent-link')}>Privacy settings</button>
  </nav>
</footer>"""


def intro(eyebrow, title, lead):
    return f"""
<section ws:label='Page Intro' {T('site-section')}>
  <div {T('site-container')}>
    <div {T('site-stack')}>
      <p {T('site-eyebrow')}>{txt(eyebrow)}</p>
      <h1 {T('site-heading-hero')}>{txt(title)}</h1>
      <p {T('site-lead')}>{rich(lead)}</p>
    </div>
  </div>
</section>"""
