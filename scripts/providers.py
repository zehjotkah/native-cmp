"""Agent data for the catalog services: how to recognize them in a project, who provides them,
and privacy policy text templates. Used by install_bundle.py.

Provider names and privacy links are starting points; agents are told to verify them on the linked page.
"""

GOOGLE = ("Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Ireland", "https://policies.google.com/privacy")
META = ("Meta Platforms Ireland Limited, Merrion Road, Dublin 4, D04 X2K5, Ireland", "https://www.facebook.com/privacy/policy/")

# id: (substrings found in Custom Code or HTML Embed code, Webstudio components, provider, privacy policy)
SERVICES = {
    "google-analytics": (["gtag/js?id=G-", "google-analytics.com", "gtag('config', 'G-", 'gtag("config", "G-'], [], *GOOGLE),
    "matomo": (["matomo.js", "piwik.js", "_paq.push"], [], "The operator of your Matomo instance (self-hosted, or InnoCraft Ltd. for Matomo Cloud)", "https://matomo.org/privacy-policy/"),
    "plausible": (["plausible.io/js", "plausible.js"], [], "Plausible Insights OÜ, Västriku tn 2, 50403 Tartu, Estonia", "https://plausible.io/privacy"),
    "rybbit": (["rybbit", "/api/script.js?siteId="], [], "The operator of your Rybbit instance (self-hosted, or Rybbit Cloud)", "https://rybbit.com"),
    "microsoft-clarity": (["clarity.ms/tag", "clarity(\"set\""], [], "Microsoft Ireland Operations Limited, One Microsoft Place, South County Business Park, Leopardstown, Dublin 18, Ireland", "https://privacy.microsoft.com/privacystatement"),
    "hotjar": (["static.hotjar.com", "hotjar.com/c/hotjar"], [], "Hotjar Ltd., Dragonara Business Centre, 5th Floor, Dragonara Road, Paceville St Julian's STJ 3141, Malta", "https://www.hotjar.com/legal/policies/privacy/"),
    "google-tag-manager": (["googletagmanager.com/gtm.js", "GTM-"], [], *GOOGLE),
    "google-ads": (["gtag/js?id=AW-", "googleadservices.com", "'AW-", '"AW-'], [], *GOOGLE),
    "meta-pixel": (["connect.facebook.net", "fbq("], [], *META),
    "linkedin-insight": (["snap.licdn.com", "_linkedin_partner_id"], [], "LinkedIn Ireland Unlimited Company, Wilton Plaza, Wilton Place, Dublin 2, Ireland", "https://www.linkedin.com/legal/privacy-policy"),
    "tiktok-pixel": (["analytics.tiktok.com", "ttq.load"], [], "TikTok Technology Limited, 10 Earlsfort Terrace, Dublin, D02 T380, Ireland", "https://www.tiktok.com/legal/page/eea/privacy-policy/en"),
    "pinterest-tag": (["s.pinimg.com/ct/core.js", "pintrk("], [], "Pinterest Europe Limited, Palmerston House, 2nd Floor, Fenian Street, Dublin 2, Ireland", "https://policy.pinterest.com/privacy-policy"),
    "youtube": (["youtube.com/embed", "youtube-nocookie.com", "youtu.be/"], ["YouTube"], *GOOGLE),
    "vimeo": (["player.vimeo.com"], ["Vimeo"], "Vimeo.com, Inc., 330 West 34th Street, 5th Floor, New York, NY 10001, USA", "https://vimeo.com/privacy"),
    "google-maps": (["google.com/maps/embed", "maps.googleapis.com", "maps.google."], [], *GOOGLE),
    "spotify": (["open.spotify.com/embed"], [], "Spotify AB, Regeringsgatan 19, 111 53 Stockholm, Sweden", "https://www.spotify.com/legal/privacy-policy/"),
    "instagram": (["instagram.com/embed", "instagram.com/p/", "instgrm."], [], *META),
    "google-fonts": (["fonts.googleapis.com", "fonts.gstatic.com"], [], *GOOGLE),
    "calendly": (["calendly.com"], [], "Calendly LLC, 115 E Main St, Ste A1B, Buford, GA 30518, USA", "https://calendly.com/legal/privacy-notice"),
    "hubspot": (["js.hs-scripts.com", "hs-scripts.com", "hsforms.net"], [], "HubSpot Ireland Limited, 2nd Floor, 30 North Wall Quay, Dublin 1, Ireland", "https://legal.hubspot.com/privacy-policy"),
    "intercom": (["widget.intercom.io", "intercomSettings"], [], "Intercom R&D Unlimited Company, 2nd Floor, Stephen Court, 18-21 St. Stephen's Green, Dublin 2, Ireland", "https://www.intercom.com/legal/privacy"),
    "crisp": (["client.crisp.chat", "$crisp"], [], "Crisp IM SAS, 2 Boulevard de Launay, 44100 Nantes, France", "https://crisp.chat/en/privacy/"),
    "google-recaptcha": (["google.com/recaptcha", "recaptcha/api.js", "gstatic.com/recaptcha"], [], *GOOGLE),
}

PRIVACY_POLICY = {
    "en": {
        "heading": "Consent management and third-party services",
        "intro": "We use Native CMP to ask for and store your consent. It runs on our own website and does not transfer data to third parties. When you make a choice, it is stored in the cookie “{storageName}” for {days} days. You can change or withdraw your consent at any time via “{privacySettings}”; withdrawing does not affect processing that took place before.",
        "consentManager": "Storing your choice is necessary to document your consent (Art. 6(1)(c) GDPR in conjunction with Art. 7(1) GDPR).",
        "service": "{title} ({purpose}). Provider: {provider}. {description} We only load this service with your consent. Legal basis: Art. 6(1)(a) GDPR{extraLegalBasis}. Cookies: {cookies}. Further information: {privacyUrl}",
        "noCookies": "none set by this integration",
        "extraLegalBasis": "",
    },
    "de": {
        "heading": "Einwilligungsverwaltung und Dienste von Drittanbietern",
        "intro": "Wir verwenden Native CMP, um Ihre Einwilligung einzuholen und zu speichern. Das Tool läuft auf unserer eigenen Website und übermittelt keine Daten an Dritte. Wenn Sie eine Auswahl treffen, wird sie im Cookie „{storageName}“ für {days} Tage gespeichert. Sie können Ihre Einwilligung jederzeit über „{privacySettings}“ ändern oder widerrufen; die Rechtmäßigkeit der bis dahin erfolgten Verarbeitung bleibt unberührt.",
        "consentManager": "Die Speicherung Ihrer Auswahl ist erforderlich, um Ihre Einwilligung nachzuweisen (Art. 6 Abs. 1 lit. c DSGVO i. V. m. Art. 7 Abs. 1 DSGVO).",
        "service": "{title} ({purpose}). Anbieter: {provider}. {description} Wir laden diesen Dienst nur mit Ihrer Einwilligung. Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO{extraLegalBasis}. Cookies: {cookies}. Weitere Informationen: {privacyUrl}",
        "noCookies": "keine durch diese Einbindung",
        "extraLegalBasis": ", § 25 Abs. 1 TDDDG",
    },
}
