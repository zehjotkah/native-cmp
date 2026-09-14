"""Build Webstudio clipboard fragments (@webstudio/instance/v0.1) from the synced project data.

Pasting such a fragment in the Webstudio Builder inserts the instances with their
props, variables, tokens and styles, exactly like copying them from another project.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION = "@webstudio/instance/v0.1"


def load_build():
    data = json.loads((ROOT / ".webstudio" / "data.json").read_text())
    build = data["build"]

    def vals(x):
        x = x if isinstance(x, list) else list(x.values())
        return [i[1] if isinstance(i, list) else i for i in x]

    return {
        "instances": vals(build["instances"]),
        "props": vals(build["props"]),
        "dataSources": vals(build["dataSources"]),
        "resources": vals(build["resources"]),
        "styleSourceSelections": vals(build["styleSourceSelections"]),
        "styleSources": vals(build["styleSources"]),
        "styles": vals(build["styles"]),
        "breakpoints": vals(build["breakpoints"]),
        "pages": vals(build["pages"]["pages"]),
    }


class Project:
    def __init__(self):
        self.b = load_build()
        self.inst = {i["id"]: i for i in self.b["instances"]}
        self.parent = {}
        for i in self.b["instances"]:
            for child in i["children"]:
                if child["type"] == "id":
                    self.parent[child["value"]] = i["id"]

    def subtree(self, root):
        out, stack = [], [root]
        while stack:
            node = stack.pop()
            out.append(node)
            stack += [c["value"] for c in self.inst[node]["children"] if c["type"] == "id"]
        return out

    def selector(self, instance_id):
        path = [instance_id]
        while path[-1] in self.parent:
            path.append(self.parent[path[-1]])
        return path

    def fragment(self, root):
        ids = set(self.subtree(root))
        selections = [s for s in self.b["styleSourceSelections"] if s["instanceId"] in ids]
        source_ids = {v for s in selections for v in s["values"]}
        styles = [s for s in self.b["styles"] if s["styleSourceId"] in source_ids]
        breakpoint_ids = {s["breakpointId"] for s in styles}
        base = [bp for bp in self.b["breakpoints"] if "minWidth" not in bp and "maxWidth" not in bp and "condition" not in bp]
        breakpoint_ids |= {bp["id"] for bp in base}
        return {
            "children": [{"type": "id", "value": root}],
            "instances": [self.inst[i] for i in self.subtree(root)],
            "assets": [],
            "dataSources": [d for d in self.b["dataSources"] if d.get("scopeInstanceId") in ids],
            "resources": [r for r in self.b["resources"] if any(p["type"] == "resource" and p["value"] == r["id"] for p in self.b["props"] if p["instanceId"] in ids)],
            "props": [p for p in self.b["props"] if p["instanceId"] in ids],
            "breakpoints": [bp for bp in self.b["breakpoints"] if bp["id"] in breakpoint_ids],
            "styleSourceSelections": selections,
            "styleSources": [s for s in self.b["styleSources"] if s["id"] in source_ids],
            "styles": styles,
        }

    def envelope(self, root):
        return {VERSION: {**self.fragment(root), "instanceSelector": self.selector(root)}}

    def find(self, predicate):
        return [i for i in self.b["instances"] if predicate(i)]

    def prop(self, instance_id, name):
        for p in self.b["props"]:
            if p["instanceId"] == instance_id and p["name"] == name:
                return p
        return None


def home_body(project):
    return [p for p in project.b["pages"] if p["path"] == ""][0]["rootInstanceId"]


def consent_manager(project):
    body = home_body(project)
    slot = [c["value"] for c in project.inst[body]["children"] if c["type"] == "id" and project.inst[c["value"]]["component"] == "Slot"
            and project.inst[c["value"]].get("label") == "Consent Manager"][0]
    return project.envelope(slot)


def _gate_id(project, root_path, predicate):
    body = [p for p in project.b["pages"] if p["path"] == root_path][0]["rootInstanceId"]
    nodes = set(project.subtree(body))
    return [i["id"] for i in project.b["instances"] if i["id"] in nodes and predicate(i)][0]


def _replace_exact(text, mapping):
    for old, new in mapping:
        needle = json.dumps(old)
        assert needle in text, old
        text = text.replace(needle, json.dumps(new))
    return text


def gate_template(project):
    """HTML-embed gate (from the Google Maps demo) with localized placeholders."""
    gate = _gate_id(project, "", lambda i: (project.prop(i["id"], "data-cmp-gate") or {}).get("value") == "google-maps")
    envelope = project.envelope(gate)
    fragment = envelope[VERSION]
    embed = [i for i in fragment["instances"] if i["component"] == "HtmlEmbed"][0]
    for p in fragment["props"]:
        if p["instanceId"] == embed["id"] and p["name"] == "code":
            p["value"] = "__EMBED__"
    text = json.dumps(envelope, ensure_ascii=False)
    text = _replace_exact(text, [
        ("This content is provided by Google Maps. Loading it may set cookies and transfer data to Google Maps.", "__TEXT__"),
        ("Always allow Google Maps", "__ALWAYS__"),
        ("Load content", "__LOAD__"),
        ("Privacy settings", "__SETTINGS__"),
        ("Google Maps", "__TITLE__"),
        ("google-maps", "__SERVICE__"),
    ])
    return text


def native_gate_template(project, service, provider):
    gate = _gate_id(project, "/consent-preview", lambda i: (project.prop(i["id"], "data-cmp-gate") or {}).get("value") == service
                    and (project.prop(i["id"], "data-cmp-gate-mode") or {}).get("value") == "interaction")
    envelope = project.envelope(gate)
    fragment = envelope[VERSION]
    video = [i for i in fragment["instances"] if i["component"] in ("YouTube", "Vimeo")][0]
    for p in fragment["props"]:
        if p["instanceId"] == video["id"] and p["name"] == "url":
            p["value"] = "__URL__"
    text = json.dumps(envelope, ensure_ascii=False)
    text = _replace_exact(text, [
        (f"This content is provided by {provider}. Loading it may set cookies and transfer data to {provider}.", "__TEXT__"),
        (f"Always allow {provider}", "__ALWAYS__"),
        ("Load content", "__LOAD__"),
        ("Cancel", "__CANCEL__"),
        ("Privacy settings", "__SETTINGS__"),
        (f"{provider} video", "__TITLE__"),
    ])
    return text


def privacy_link(project):
    button = _gate_id(project, "/consent-preview", lambda i: i.get("label") == "Privacy Settings Link")
    return project.envelope(button)


def build():
    project = Project()
    return {
        "consentManager": consent_manager(project),
        "gate": gate_template(project),
        "nativeGates": {
            "youtube": native_gate_template(project, "youtube", "YouTube"),
            "vimeo": native_gate_template(project, "vimeo", "Vimeo"),
        },
        "link": json.dumps(privacy_link(project), ensure_ascii=False),
    }


if __name__ == "__main__":
    result = build()
    manager = result["consentManager"][VERSION]
    print("consent manager:", len(manager["instances"]), "instances,", len(manager["styles"]), "styles,", len(json.dumps(result["consentManager"])) // 1024, "KB")
    print("gate:", len(result["gate"]) // 1024, "KB", "native:", {k: len(v) // 1024 for k, v in result["nativeGates"].items()}, "link:", len(result["link"]), "bytes")
    (ROOT / ".temp" / "fragments.json").write_text(json.dumps(result))
