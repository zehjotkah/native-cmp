"""SEO and GEO: page metadata, social images, JSON-LD structured data."""

import json

import onepager

SITE = "https://nativecmp.com"
NAME = "Native CMP"

# uploaded 1200x630 images (assets/og/*.png)
OG = {
    "install": "bla37ZgrnV_6194XNRBPi",
    "home": "h0Z_S0GM7tv920OJSrlwM",
    "generator": "fzcyz9-w8xYWjrX4IOjx7",
    "examples": "P8X7kewWlIVm3VhydWTBy",
    "docs": "Yaq14xcNrPJzcOK077SW-",
    "de": "nQVeA_wQPRiOU9H8uMaJ9",
    "es": "VQ2I84X5y-Xmtamwor6aj",
    "ar": "wQ11m_w8Eq2beCOSGaZww",
}

PAGES = {
    "subridMvnfjVeM7rVa1Zi": dict(
        path="/",
        title="Cookie Consent for Webstudio – Native CMP",
        description="Free cookie consent manager built from native Webstudio elements. Blocks scripts, embeds and videos until consent. Multilingual, SPA-ready, Consent Mode v2.",
        image="home",
    ),
    "XatTUnspJHO07Ra0J3Sp9": dict(
        path="/install",
        title="Install with AI – Native CMP",
        description="Let your AI agent install Native CMP via the Webstudio MCP: it blocks scripts and embeds, configures cookies, updates your privacy policy and matches your design.",
        image="install",
    ),
    "_z43E-i8iKE0_6Eev8Jyu": dict(
        path="/generator",
        title="Consent Config Generator – Native CMP",
        description="Generate a complete cookie consent setup for Webstudio: pick services, enter IDs or import an existing config, then paste the result into your project.",
        image="generator",
    ),
    "CgtVEjmEeLrC6kfRxoPZD": dict(
        path="/examples",
        title="Consent Examples for 23 Services – Native CMP",
        description="Copy-paste consent configurations for Google Analytics, Tag Manager, Meta Pixel, Matomo, Rybbit, YouTube, Google Maps, Calendly and more.",
        image="examples",
    ),
    "FCi6-VSonqxrmw79t5_ST": dict(
        path="/docs",
        title="Documentation – Native CMP",
        description="Install, configure, translate and style Native CMP: services, data attributes, Consent Gates, JavaScript API and Google Consent Mode v2.",
        image="docs",
    ),
    "N1koTflC0j37ziK9rEmAT": dict(
        path="/de",
        title="Cookie-Einwilligung für Webstudio – Native CMP",
        description="Kostenloser Consent-Manager aus nativen Webstudio-Elementen: blockiert Skripte, Einbettungen und Videos bis zur Einwilligung. Mehrsprachig und SPA-fähig.",
        image="de",
    ),
    "9jgJs8-KMgnK-xBwzyJHI": dict(
        path="/es",
        title="Consentimiento de cookies para Webstudio – Native CMP",
        description="Gestor de consentimiento gratuito hecho con elementos nativos de Webstudio: bloquea scripts, contenidos incrustados y vídeos hasta obtener el consentimiento.",
        image="es",
    ),
    "GRHHqi98ExIMWH8twjH5N": dict(
        path="/ar",
        title="Native CMP بالعربية",
        description="مدير موافقة ملفات تعريف الارتباط لـ Webstudio بدعم كامل للغة العربية والكتابة من اليمين إلى اليسار.",
        image="ar",
    ),
    "qSsMOvYn_n-SQIoP-B4u3": dict(
        path="/contact",
        title="Contact – Native CMP",
        description="Questions, bug reports or feature ideas for Native CMP? Send us a message.",
        image="home",
    ),
    "VcCFjAiKvdSRt4MolxgMh": dict(
        path="/legal-notice",
        title="Legal notice – Native CMP",
        description="Legal notice (Impressum) for Native CMP, a project by ELECOS UG (haftungsbeschränkt).",
        image="home",
    ),
    # placeholder policy: keep out of search results until the real policy is written
    "6ZWZC6kYCVoWV1mVi8U1e": dict(
        path="/privacy",
        title="Privacy policy – Native CMP",
        description="How nativecmp.com handles your data: one consent cookie, cookieless analytics on our own server, a consent log without IP addresses, and embedded content blocked until you allow it.",
        image="home",
    ),
    "oVOM84zbCgkvIXFcFQCMu": dict(
        path="/*",
        title="Page not found – Native CMP",
        description="This page doesn’t exist.",
        image="home",
        exclude=True,
    ),
    "9HbIPAyRCFOCn9QAlLySo": dict(
        path="/consent-preview",
        title="Consent design preview – Native CMP",
        description="Design frames of the consent notice and preferences modal.",
        image="home",
        exclude=True,
    ),
}

ORGANIZATION = {
    "@type": "Organization",
    "@id": SITE + "/#organization",
    "name": "ELECOS UG (haftungsbeschränkt)",
    "url": "https://elecos.de",
    "email": "info@elecos.de",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Hauptstr. 42",
        "postalCode": "16341",
        "addressLocality": "Panketal",
        "addressCountry": "DE",
    },
}

SOFTWARE = {
    "@type": "SoftwareApplication",
    "@id": SITE + "/#software",
    "name": NAME,
    "url": SITE + "/",
    "description": "Cookie, script and embed consent manager built from native Webstudio instances. Blocks third-party scripts, embeds and native YouTube and Vimeo components until visitors consent; SPA-ready, multilingual with right-to-left support, styled with Webstudio design tokens, supports Google Consent Mode v2.",
    "applicationCategory": "DeveloperApplication",
    "operatingSystem": "Web",
    "isAccessibleForFree": True,
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
    "publisher": {"@id": SITE + "/#organization"},
    "featureList": [
        "Prior blocking of scripts, iframes, images and links",
        "Consent Gates for embeds and native YouTube and Vimeo components",
        "Granular purposes and services with required, default, opt-out and onlyOnce flags",
        "Works with Webstudio client-side navigation",
        "Multilingual by page language, including right-to-left languages",
        "Google Consent Mode v2",
        "JavaScript API and DOM events",
        "Complete installation by an AI agent through the Webstudio MCP: scan, blocking, cookies, privacy policy section and design",
        "Config generator with import of existing consent configs",
    ],
}


def page_node(page_id, schema_type, extra=None):
    meta = PAGES[page_id]
    url = SITE + ("/" if meta["path"] == "/" else meta["path"])
    node = {
        "@type": schema_type,
        "@id": url + "#webpage",
        "url": url,
        "name": meta["title"],
        "description": meta["description"],
        "isPartOf": {"@id": SITE + "/#website"},
        "about": {"@id": SITE + "/#software"},
        "publisher": {"@id": SITE + "/#organization"},
    }
    node.update(extra or {})
    return node


def home_graph():
    return {
        "@context": "https://schema.org",
        "@graph": [
            ORGANIZATION,
            {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": NAME, "inLanguage": "en", "publisher": {"@id": SITE + "/#organization"}},
            SOFTWARE,
            page_node("subridMvnfjVeM7rVa1Zi", "WebPage", {"inLanguage": "en"}),
            {
                "@type": "FAQPage",
                "@id": SITE + "/#faq",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in onepager.FAQ
                ],
            },
        ],
    }


def graph(nodes):
    return {"@context": "https://schema.org", "@graph": nodes}


def install_graph():
    import install_page
    node = page_node("XatTUnspJHO07Ra0J3Sp9", "WebPage", {"inLanguage": "en"})
    howto = {
        "@type": "HowTo",
        "@id": SITE + "/install#howto",
        "name": "Install Native CMP with an AI agent",
        "description": PAGES["XatTUnspJHO07Ra0J3Sp9"]["description"],
        "tool": [{"@type": "HowToTool", "name": "Webstudio MCP or CLI 0.298 or newer"}, {"@type": "HowToTool", "name": "AI coding agent such as Claude Code, Codex or Cursor"}],
        "step": [{"@type": "HowToStep", "position": i + 1, "name": t, "text": d.replace("`", "")} for i, (t, d) in enumerate(install_page.STEPS)],
    }
    return graph([node, howto])


STRUCTURED = {
    "XatTUnspJHO07Ra0J3Sp9": install_graph,
    "subridMvnfjVeM7rVa1Zi": home_graph,
    "_z43E-i8iKE0_6Eev8Jyu": lambda: graph([page_node("_z43E-i8iKE0_6Eev8Jyu", "WebPage", {"inLanguage": "en", "mainEntity": {
        "@type": "WebApplication", "name": "Native CMP config generator", "url": SITE + "/generator",
        "applicationCategory": "DeveloperApplication", "operatingSystem": "Web", "browserRequirements": "Requires JavaScript",
        "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}})]),
    "CgtVEjmEeLrC6kfRxoPZD": lambda: graph([page_node("CgtVEjmEeLrC6kfRxoPZD", "CollectionPage", {"inLanguage": "en"})]),
    "FCi6-VSonqxrmw79t5_ST": lambda: graph([page_node("FCi6-VSonqxrmw79t5_ST", "WebPage", {"inLanguage": "en", "mainEntity": {
        "@type": "TechArticle", "headline": "Native CMP documentation", "url": SITE + "/docs",
        "about": {"@id": SITE + "/#software"}, "publisher": {"@id": SITE + "/#organization"}, "inLanguage": "en"}})]),
    "qSsMOvYn_n-SQIoP-B4u3": lambda: graph([page_node("qSsMOvYn_n-SQIoP-B4u3", "ContactPage", {"inLanguage": "en"})]),
    "6ZWZC6kYCVoWV1mVi8U1e": lambda: graph([page_node("6ZWZC6kYCVoWV1mVi8U1e", "WebPage", {"inLanguage": "en"})]),
}


def json_ld_embed(page_id):
    data = json.dumps(STRUCTURED[page_id](), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{data}</script>'
