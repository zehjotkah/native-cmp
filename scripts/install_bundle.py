"""Build the agent install bundle (dist/install/steps.json) from the live Consent Manager.

The bundle contains everything an agent with the Webstudio MCP (or install.mjs)
needs to recreate the Consent Manager in another project: CSS variables, design
tokens, the Custom Code snippet, JSX fragments per collection level and starter
variables. It is generated from the synced project, so it never drifts from
what this site runs.
"""

import json
import pathlib
import re

import design
import theme
import fragments
import languages
import catalog
import providers
import service_descriptions

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "install"
VERSION = "@webstudio/instance/v0.1"
MOBILE_MAX_WIDTH = 479
MIN_CLI_VERSION = "0.298.0"  # conflictResolution on insert-collection

TYPOGRAPHY_TOKENS = {
    "consent-notice-title": "Notice heading",
    "consent-modal-title": "Preferences dialog heading",
    "consent-purpose-label": "Purpose names in the dialog",
    "consent-gate-title": "Consent Gate heading",
    "consent-button": "All buttons (size, weight, letter case, border width, radius)",
    "is-consent-button-primary": "Primary button colors and hover",
    "is-consent-button-secondary": "Outlined button colors and hover",
}


def encode_id(data_source_id):
    return "$ws$dataSource$" + data_source_id.replace("-", "__DASH__")


def template(text):
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


class Bundle:
    def __init__(self, envelope=None, root=None):
        self.envelope = envelope or fragments.consent_manager(fragments.Project())[VERSION]
        self.inst = {i["id"]: i for i in self.envelope["instances"]}
        self.parent = {c["value"]: i["id"] for i in self.envelope["instances"] for c in i["children"] if c["type"] == "id"}
        self.props = {}
        for p in self.envelope["props"]:
            self.props.setdefault(p["instanceId"], []).append(p)
        self.sources = {s["id"]: s for s in self.envelope["styleSources"]}
        self.selections = {s["instanceId"]: s["values"] for s in self.envelope["styleSourceSelections"]}
        self.data_sources = {d["id"]: d for d in self.envelope["dataSources"]}
        if root:
            self.root = root
        else:
            slot = self.inst[self.envelope["children"][0]["value"]]
            fragment = self.inst[slot["children"][0]["value"]]
            self.root = fragment["children"][0]["value"]
        self.skipped = []
        self.deferred = None  # list: expression props that need the root variables are bound after they exist
        base = [b for b in self.envelope["breakpoints"] if "maxWidth" not in b and "minWidth" not in b]
        self.base_breakpoint = base[0]["id"]
        self.breakpoints = {b["id"]: b for b in self.envelope["breakpoints"]}

    # ------------------------------------------------------------ expressions

    def rewrite(self, code, names):
        def replace(match):
            data_source_id = match.group(1).replace("__DASH__", "-")
            if data_source_id in names:
                return names[data_source_id]
            source = self.data_sources.get(data_source_id)
            if not source:
                raise ValueError(f"unknown data source {data_source_id} in {code}")
            return source["name"]

        return re.sub(r"\$ws\$dataSource\$([A-Za-z0-9_]+)", replace, code)

    # -------------------------------------------------------------------- JSX

    def tokens_attr(self, instance_id):
        refs = []
        for source_id in self.selections.get(instance_id, []):
            source = self.sources[source_id]
            if source["type"] != "token":
                raise ValueError(f"local styles are not supported in the bundle ({instance_id})")
            # tokens are created beforehand; "ours" keeps them, so the css here is only a placeholder
            refs.append(f"token({json.dumps(source['name'])}, css`display: block;`)")
        return " ws:tokens={[" + ", ".join(refs) + "]}" if refs else ""

    def jsx(self, instance_id, names, collections):
        item = self.inst[instance_id]
        if item["component"] == "ws:collection":
            collections.append(instance_id)
            return ""
        if item["component"] == "ws:element":
            tag = item["tag"]
        elif item["component"] == "HtmlEmbed":
            tag = "HtmlEmbed"
        else:
            # template-backed components (YouTube, Vimeo) are inserted with insert-component instead
            self.skipped.append(instance_id)
            return ""
        attrs = ""
        if item.get("label"):
            attrs += f" ws:label={json.dumps(item['label'])}"
        for prop in self.props.get(instance_id, []):
            name, kind, value = prop["name"], prop["type"], prop["value"]
            if kind == "string":
                attrs += f" {name}={{{json.dumps(value, ensure_ascii=False)}}}"
            elif kind in ("boolean", "number"):
                attrs += f" {name}={{{json.dumps(value)}}}"
            elif kind == "expression":
                if self.deferred is not None and re.search(r"\$ws\$dataSource\$", value):
                    if not item.get("label"):
                        raise ValueError(f"deferred binding on {instance_id} needs a label")
                    self.deferred.append({"label": item["label"], "name": name, "expression": self.rewrite(value, names)})
                    continue
                attrs += f" {name}={{expression`{template(self.rewrite(value, names))}`}}"
            else:
                raise ValueError(f"unsupported prop type {kind} on {instance_id}")
        attrs += self.tokens_attr(instance_id)
        children = ""
        for child in item["children"]:
            if child["type"] == "text":
                children += "{" + json.dumps(child["value"], ensure_ascii=False) + "}"
            elif child["type"] == "expression":
                children += "{expression`" + template(self.rewrite(child["value"], names)) + "`}"
            elif child["type"] == "id":
                children += self.jsx(child["value"], names, collections)
        return f"<{tag}{attrs}>{children}</{tag}>"

    # ------------------------------------------------------------ collections

    def collection_info(self, collection_id):
        props = {p["name"]: p for p in self.props[collection_id]}
        parent = self.inst[self.parent[collection_id]]
        index = [c["value"] for c in parent["children"] if c["type"] == "id"].index(collection_id)
        return props, parent, index

    def steps(self):
        variables = {d["id"]: d["name"] for d in self.data_sources.values() if d["type"] == "variable"}
        collections = []
        self.deferred = []
        skeleton = self.jsx(self.root, variables, collections)
        self.bindings = self.deferred
        self.deferred = None
        levels = []
        queue = list(collections)
        while queue:
            collection_id = queue.pop(0)
            props, parent, index = self.collection_info(collection_id)
            item_param = props["item"]["value"]
            key_param = props["itemKey"]["value"] if "itemKey" in props else None
            final_name = self.data_sources[item_param]["name"]
            names = dict(variables)
            names[item_param] = "collectionItem"
            if key_param:
                names[key_param] = "collectionItemKey"
            nested = []
            item_root = self.inst[collection_id]["children"][0]["value"]
            item_fragment = self.jsx(item_root, names, nested)
            # the data expression is evaluated in the parent scope, where outer parameters keep their final names
            data = self.rewrite(props["data"]["value"], variables)
            if not parent.get("label"):
                raise ValueError(f"collection parent of {collection_id} needs a label")
            levels.append({
                "parentLabel": parent["label"],
                "insertIndex": index,
                "data": data,
                "itemFragment": item_fragment,
                "renameItemParameterTo": final_name if final_name != "collectionItem" else None,
            })
            queue.extend(nested)
        for level in levels:
            used_names = re.findall(r"\b(collectionItem|language)\b", level["itemFragment"])
            if "collectionItem" not in used_names:
                raise ValueError(f"item fragment below {level['parentLabel']} does not use collectionItem")
        return skeleton, levels

    # ----------------------------------------------------------------- tokens

    def tokens(self):
        out = []
        for source in self.envelope["styleSources"]:
            if source["type"] != "token":
                continue
            declarations = []
            for style in self.envelope["styles"]:
                if style["styleSourceId"] != source["id"]:
                    continue
                declaration = {"property": style["property"], "value": style["value"]}
                if style.get("state"):
                    declaration["state"] = style["state"]
                if style["breakpointId"] != self.base_breakpoint:
                    breakpoint = self.breakpoints[style["breakpointId"]]
                    if breakpoint.get("maxWidth") != MOBILE_MAX_WIDTH:
                        raise ValueError(f"unsupported breakpoint {breakpoint}")
                    declaration["breakpoint"] = "$mobileBreakpointId"
                declarations.append(declaration)
            out.append({"name": source["name"], "declarations": declarations})
        return out

    # -------------------------------------------------------------- variables

    def starter_variables(self):
        """This site's variables without the demo services: consent manager only, all languages and purposes."""
        sources = {d["name"]: d["value"] for d in self.data_sources.values() if d["type"] == "variable"}
        values = {name: value["value"] for name, value in sources.items()}
        services = [s for s in values["consentServices"] if s["name"] == "consent-manager"]
        translations = []
        for entry in values["consentTranslations"]:
            entry = json.loads(json.dumps(entry))
            for purpose in entry.get("purposes", []):
                purpose["services"] = [s for s in purpose.get("services", []) if s["name"] == "consent-manager"]
            entry["purposes"] = [p for p in entry.get("purposes", []) if p["services"]]
            translations.append(entry)
        out = {name: dict(value) for name, value in sources.items()}
        out["consentServices"] = {"type": "json", "value": services}
        out["consentTranslations"] = {"type": "json", "value": translations}
        return out


def merge_tokens(*lists):
    seen, out = set(), []
    for tokens in lists:
        for token in tokens:
            if token["name"] not in seen:
                seen.add(token["name"])
                out.append(token)
    return out


def embed_gate():
    envelope = json.loads(fragments.gate_template(fragments.Project()))[VERSION]
    converter = Bundle(envelope, envelope["children"][0]["value"])
    return converter.jsx(converter.root, {}, []), converter.tokens()


def video_gate(service, provider):
    project = fragments.Project()
    envelope = json.loads(fragments.native_gate_template(project, service, provider))[VERSION]
    converter = Bundle(envelope, envelope["children"][0]["value"])
    shell = converter.jsx(converter.root, {}, [])
    assert len(converter.skipped) == 1, converter.skipped
    video = converter.inst[converter.skipped[0]]
    props = [{"name": p["name"], "type": p["type"], "value": p["value"]} for p in converter.props[video["id"]]]
    tokens = [converter.sources[s]["name"] for s in converter.selections.get(video["id"], []) if converter.sources[s]["type"] == "token"]
    # only the gate's own tokens: the video component's template parts keep Webstudio's defaults
    gate_tokens = [t for t in converter.tokens() if t["name"].startswith(("consent-", "is-consent-"))]
    parent = converter.inst[converter.parent[video["id"]]]
    assert parent["id"] == converter.root, "video must sit directly in the gate"
    return {
        "shell": shell,
        "component": video["component"],
        "componentInsertIndex": [c["value"] for c in parent["children"] if c["type"] == "id"].index(video["id"]),
        "componentProps": props,
        "componentTokens": tokens,
    }, gate_tokens


def gate_texts():
    return {code: languages.LANGUAGES[code]["gate"] for code in languages.ORDER}


def privacy_link():
    spans = "".join(
        f"<span data-cmp-lang={json.dumps(code)}>{{{json.dumps(languages.LANGUAGES[code]['gate']['settings'], ensure_ascii=False)}}}</span>"
        for code in languages.ORDER
    )
    return f"<button type=\"button\" data-cmp-action=\"open-modal\" ws:label=\"Privacy Settings Link\" ws:tokens={{[token(\"consent-link\", css`display: block;`)]}}>{spans}</button>"



def service_catalog():
    """Catalog services with detection hints, cookies, descriptions in every language and provider details."""
    out = []
    for service in catalog.CATALOG:
        patterns, components, provider, privacy_url = providers.SERVICES[service["id"]]
        descriptions = {"en": service["description"], "de": service["descriptionDe"], "es": service["descriptionEs"]}
        descriptions.update(service_descriptions.DESCRIPTIONS.get(service["id"], {}))
        out.append({
            "id": service["id"],
            "title": service["title"],
            "purpose": service["purpose"],
            "placement": {"head": "custom-code", "embed": "embed-gate", "native": "video-gate"}[service["placement"]],
            "detect": {"codeContains": patterns, "components": components},
            "cookies": service["cookies"],
            "consentMode": service["consentMode"],
            "fields": service["fields"],
            "blockedMarkup": service["markup"],
            "note": service["note"],
            "descriptions": descriptions,
            "provider": provider,
            "privacyUrl": privacy_url,
        })
    return out


def translation_templates():
    """A complete consentTranslations entry per language, with every purpose and the consent manager itself."""
    out = {}
    for code in languages.ORDER:
        pack = languages.LANGUAGES[code]
        purposes = []
        for pid in ["essential"] + catalog.PURPOSES:
            title, description = pack["purposes"][pid]
            services = [{"name": "consent-manager", **pack["consentManager"]}] if pid == "essential" else []
            purposes.append({"id": pid, "title": title, "description": description, "services": services})
        entry = {"lang": code, "privacyLabel": pack["privacyLabel"], "privacyUrl": "/privacy", "notice": pack["notice"], "modal": pack["modal"], "purposes": purposes}
        if pack["dir"] == "rtl":
            entry["dir"] = "rtl"
        out[code] = entry
    return out


def build():
    bundle = Bundle()
    skeleton, levels = bundle.steps()
    embed, embed_tokens = embed_gate()
    youtube, youtube_tokens = video_gate("youtube", "YouTube")
    vimeo, vimeo_tokens = video_gate("vimeo", "Vimeo")
    tokens = merge_tokens(bundle.tokens(), embed_tokens, youtube_tokens, vimeo_tokens)
    head = (ROOT / "dist" / "cmp-head.html").read_text()
    engine_version = re.search(r'data-cmp-engine="([^"]+)"', head).group(1)
    data = {
        "name": "Native CMP",
        "engineVersion": engine_version,
        "minimumCliVersion": MIN_CLI_VERSION,
        "docs": "https://nativecmp.com/install.txt",
        "mobileBreakpoint": {"label": "Mobile portrait", "maxWidth": MOBILE_MAX_WIDTH},
        "cssVariables": theme.definitions(),
        "tokens": tokens,
        "theme": {
            "variables": {name: {"craft": craft, "default": default, "role": role} for name, (craft, default, role) in theme.CMP_VARIABLES.items()},
            "tokenPrefixes": ["consent-", "is-consent-"],
            "typographyTokens": TYPOGRAPHY_TOKENS,
        },
        "customCode": head,
        "consentManager": {
            "label": "Consent Manager",
            "skeleton": skeleton,
            "collections": levels,
            "variables": bundle.starter_variables(),
            "bindings": bundle.bindings,
        },
        "privacySettingsLink": privacy_link(),
        "catalog": service_catalog(),
        "translationTemplates": translation_templates(),
        "privacyPolicy": providers.PRIVACY_POLICY,
        "gates": {
            "placeholders": {
                "__SERVICE__": "service name from consentServices, e.g. google-maps",
                "__TITLE__": "heading, e.g. Google Maps",
                "__TEXT__": "texts[lang].text with {provider} replaced",
                "__LOAD__": "texts[lang].load",
                "__ALWAYS__": "texts[lang].always with {provider} replaced",
                "__CANCEL__": "texts[lang].cancel",
                "__SETTINGS__": "texts[lang].settings",
                "__EMBED__": "the embed code with src moved to data-src and data-cmp-service added, e.g. <iframe data-cmp-service=\"google-maps\" data-src=\"https://www.google.com/maps/embed?pb=...\" title=\"Map\" loading=\"lazy\"></iframe>",
                "__URL__": "video URL",
            },
            "texts": gate_texts(),
            "embed": embed,
            "youtube": youtube,
            "vimeo": vimeo,
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=1)
    (OUT / "steps.json").write_text(text)
    return data, len(text)


if __name__ == "__main__":
    data, size = build()
    print("steps.json", size // 1024, "KB,", len(data["tokens"]), "tokens,", len(data["consentManager"]["collections"]), "collections")
    for level in data["consentManager"]["collections"]:
        print(" -", level["parentLabel"], "data:", level["data"], "rename:", level["renameItemParameterTo"], len(level["itemFragment"]) // 1024, "KB")
