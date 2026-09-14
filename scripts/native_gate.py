"""Interaction-mode Consent Gates around Webstudio's native YouTube and Vimeo components."""

import ws
from rich import txt
from ui import T
from languages import LANGUAGES

COMPONENTS = {
    "youtube": {
        "component": "YouTube",
        "provider": "YouTube",
        # nothing may contact YouTube before consent
        "props": [("showPreview", "boolean", False), ("autoplay", "boolean", False), ("preconnect", "boolean", False), ("privacyEnhancedMode", "boolean", True)],
    },
    "vimeo": {
        "component": "Vimeo",
        "provider": "Vimeo",
        "props": [("showPreview", "boolean", False), ("autoplay", "boolean", False), ("doNotTrack", "boolean", True)],
    },
}


def gate_shell(service, title, lang="en"):
    pack = LANGUAGES[lang]["gate"]
    provider = COMPONENTS[service]["provider"]
    return f"""
<div ws:label='Consent Gate ({provider})' data-cmp-gate='{service}' data-cmp-gate-mode='interaction' {T('consent-gate')}>
  <div ws:label='Gate Notice' data-cmp-gate-notice='' role='group' aria-label={txt(title)} {T('consent-gate-notice', 'is-consent-gate-overlay')}>
    <p {T('consent-gate-title')}>{txt(title)}</p>
    <p {T('consent-gate-text')}>{txt(pack['text'].replace('{provider}', provider))}</p>
    <div {T('consent-gate-actions')}>
      <button type='button' data-cmp-action='accept-once' {T('consent-button', 'is-consent-button-primary')}>{txt(pack['load'])}</button>
      <button type='button' data-cmp-action='accept-always' data-cmp-if='confirmed' {T('consent-button', 'is-consent-button-secondary')}>{txt(pack['always'].replace('{provider}', provider))}</button>
      <button type='button' data-cmp-action='dismiss' {T('consent-button', 'is-consent-button-ghost')}>{txt(pack['cancel'])}</button>
    </div>
    <button type='button' data-cmp-action='open-modal' {T('consent-link')}>{txt(pack['settings'])}</button>
  </div>
</div>"""


def create(parent_id, service, url, title, lang="en", index=None):
    """Insert a native video gate under parent_id and return the gate instance id."""
    config = COMPONENTS[service]
    payload = {"parentInstanceId": parent_id, "conflictResolution": "ours", "fragment": gate_shell(service, title, lang)}
    if index is not None:
        payload["insertIndex"] = index
    gate = ws.call("insert-fragment", payload)["rootInstanceIds"][0]
    inserted = ws.call("insert-component", {"parentInstanceId": gate, "component": config["component"]})
    video = (inserted.get("rootInstanceIds") or inserted.get("instanceIds"))[0]
    updates = [
        {"instanceId": video, "name": "url", "type": "string", "value": url},
        {"instanceId": video, "name": "title", "type": "string", "value": title},
        {"instanceId": video, "name": "data-cmp-gate-content", "type": "string", "value": ""},
    ] + [{"instanceId": video, "name": name, "type": kind, "value": value} for name, kind, value in config["props"]]
    ws.call("update-props", {"updates": updates})
    tokens = {t["name"]: t["id"] for t in ws.call("list-design-tokens", {"limit": 200})["tokens"]}
    ws.call("attach-design-token", {"designTokenId": tokens["consent-video"], "instanceIds": [video], "position": "before-local"})
    return gate, video
