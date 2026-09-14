"""Service catalog for the config generator (single source for /generator)."""

PURPOSES = ["analytics", "marketing", "media", "functional"]
# PURPOSE_TEXT is derived from the language pack (languages.py)

from languages import LANGUAGES as _LANGUAGES

PURPOSE_TEXT = {
    pid: {code: tuple(pack["purposes"][pid]) for code, pack in _LANGUAGES.items()}
    for pid in ["essential"] + PURPOSES
}

IFRAME_STYLE = 'style="display:block;width:100%;aspect-ratio:16/9;border:0"'


def svc(id, title, purpose, placement, description, cookies=(), fields=(), markup="", consent_mode=(), note=""):
    return {
        "id": id,
        "title": title,
        "purpose": purpose,
        "placement": placement,  # "head" (Custom Code) or "embed" (HTML Embed inside a Consent Gate)
        "description": description["en"],
        "descriptionDe": description["de"],
        "descriptionEs": description["es"],
        "cookies": list(cookies),
        "consentMode": list(consent_mode),
        "fields": [{"id": f"{id}.{key}", "label": label, "placeholder": placeholder} for key, label, placeholder in fields],
        "markup": markup,
        "note": note,
    }


CATALOG = [
    svc("google-analytics", "Google Analytics 4", "analytics", "head",
        {"en": "Collects pseudonymous usage statistics.", "de": "Erhebt pseudonyme Nutzungsstatistiken.", "es": "Recoge estadísticas de uso seudonimizadas."},
        cookies=["^_ga", "_gid", "^_gat"], consent_mode=["analytics_storage"],
        fields=[("measurementId", "Measurement ID", "G-XXXXXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="google-analytics"
  data-src="https://www.googletagmanager.com/gtag/js?id={{measurementId}}"></script>
<script type="text/plain" data-cmp-service="google-analytics">
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag("js", new Date());
  gtag("config", "{{measurementId}}");
</script>'''),
    svc("matomo", "Matomo", "analytics", "head",
        {"en": "Collects pseudonymous visitor statistics.", "de": "Erhebt pseudonyme Besucherstatistiken.", "es": "Recoge estadísticas de visitantes seudonimizadas."},
        cookies=["^_pk_id", "^_pk_ses", "^_pk_ref"],
        fields=[("url", "Matomo URL", "https://analytics.example.com/"), ("siteId", "Site ID", "1")],
        markup='''<script type="text/plain" data-cmp-service="matomo">
  var _paq = window._paq = window._paq || [];
  _paq.push(["trackPageView"]);
  _paq.push(["enableLinkTracking"]);
  (function () {
    var u = "{{url}}";
    _paq.push(["setTrackerUrl", u + "matomo.php"]);
    _paq.push(["setSiteId", "{{siteId}}"]);
    var g = document.createElement("script");
    g.async = true; g.src = u + "matomo.js";
    document.head.appendChild(g);
  })();
</script>'''),
    svc("plausible", "Plausible Analytics", "analytics", "head",
        {"en": "Cookieless, privacy-friendly website statistics.", "de": "Cookielose, datenschutzfreundliche Website-Statistiken.", "es": "Estadísticas web sin cookies y respetuosas con la privacidad."},
        fields=[("domain", "Site domain", "example.com")],
        markup='''<script type="text/plain" data-cmp-service="plausible"
  data-domain="{{domain}}"
  data-src="https://plausible.io/js/script.js"></script>'''),
    svc("rybbit", "Rybbit", "analytics", "head",
        {"en": "Cookieless, privacy-friendly web and product analytics.", "de": "Cookielose, datenschutzfreundliche Web- und Produktanalyse.", "es": "Analítica web y de producto sin cookies y respetuosa con la privacidad."},
        fields=[("siteId", "Site ID", "YOUR_SITE_ID"), ("host", "Host (self-hosted instances)", "https://app.rybbit.io")],
        markup='''<script type="text/plain" data-cmp-service="rybbit" async
  data-src="{{host}}/api/script.js?siteId={{siteId}}"></script>''',
        note="Rybbit is cookieless and tracks client-side navigation automatically. Many sites run it without consent; if your own assessment allows that, set optOut so it runs until the visitor declines."),
    svc("microsoft-clarity", "Microsoft Clarity", "analytics", "head",
        {"en": "Session recordings and heatmaps to improve usability.", "de": "Sitzungsaufzeichnungen und Heatmaps zur Verbesserung der Bedienbarkeit.", "es": "Grabaciones de sesiones y mapas de calor para mejorar la usabilidad."},
        cookies=["_clck", "_clsk"], fields=[("projectId", "Project ID", "XXXXXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="microsoft-clarity">
  (function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
  })(window, document, "clarity", "script", "{{projectId}}");
</script>'''),
    svc("hotjar", "Hotjar", "analytics", "head",
        {"en": "Heatmaps, recordings and feedback surveys.", "de": "Heatmaps, Aufzeichnungen und Feedback-Umfragen.", "es": "Mapas de calor, grabaciones y encuestas de opinión."},
        cookies=["^_hj"], fields=[("siteId", "Site ID", "1234567")],
        markup='''<script type="text/plain" data-cmp-service="hotjar">
  (function(h,o,t,j,a,r){h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
  h._hjSettings={hjid:{{siteId}},hjsv:6};a=o.getElementsByTagName("head")[0];
  r=o.createElement("script");r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
  a.appendChild(r);})(window,document,"https://static.hotjar.com/c/hotjar-",".js?sv=");
</script>'''),
    svc("google-tag-manager", "Google Tag Manager", "marketing", "head",
        {"en": "Loads marketing and analytics tags configured in Google Tag Manager.", "de": "Lädt Marketing- und Statistik-Tags, die im Google Tag Manager konfiguriert sind.", "es": "Carga etiquetas de marketing y analítica configuradas en Google Tag Manager."},
        fields=[("containerId", "Container ID", "GTM-XXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="google-tag-manager">
  (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({"gtm.start":new Date().getTime(),event:"gtm.js"});
  var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!="dataLayer"?"&l="+l:"";
  j.async=true;j.src="https://www.googletagmanager.com/gtm.js?id="+i+dl;f.parentNode.insertBefore(j,f);
  })(window,document,"script","dataLayer","{{containerId}}");
</script>''',
        note="Blocked until consent. To load GTM before consent and let tags decide via Consent Mode, paste the original GTM snippet below the CMP code instead and enable Consent Mode."),
    svc("google-ads", "Google Ads", "marketing", "head",
        {"en": "Measures conversions from Google Ads campaigns and enables remarketing.", "de": "Misst Conversions aus Google-Ads-Kampagnen und ermöglicht Remarketing.", "es": "Mide conversiones de campañas de Google Ads y permite el remarketing."},
        cookies=["^_gcl"], consent_mode=["ad_storage", "ad_user_data", "ad_personalization"],
        fields=[("conversionId", "Conversion ID", "AW-XXXXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="google-ads"
  data-src="https://www.googletagmanager.com/gtag/js?id={{conversionId}}"></script>
<script type="text/plain" data-cmp-service="google-ads">
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag("js", new Date());
  gtag("config", "{{conversionId}}");
</script>'''),
    svc("meta-pixel", "Meta Pixel", "marketing", "head",
        {"en": "Measures the effectiveness of ads on Facebook and Instagram.", "de": "Misst die Wirksamkeit von Anzeigen auf Facebook und Instagram.", "es": "Mide la eficacia de los anuncios en Facebook e Instagram."},
        cookies=["_fbp", "_fbc"], fields=[("pixelId", "Pixel ID", "XXXXXXXXXXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="meta-pixel">
  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,"script","https://connect.facebook.net/en_US/fbevents.js");
  fbq("init", "{{pixelId}}");
  fbq("track", "PageView");
</script>'''),
    svc("linkedin-insight", "LinkedIn Insight Tag", "marketing", "head",
        {"en": "Conversion tracking and retargeting for LinkedIn ads.", "de": "Conversion-Tracking und Retargeting für LinkedIn-Anzeigen.", "es": "Seguimiento de conversiones y retargeting para anuncios de LinkedIn."},
        cookies=["li_fat_id", "li_giant", "ln_or"], fields=[("partnerId", "Partner ID", "XXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="linkedin-insight">
  window._linkedin_partner_id = "{{partnerId}}";
  window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
  window._linkedin_data_partner_ids.push(window._linkedin_partner_id);
</script>
<script type="text/plain" data-cmp-service="linkedin-insight"
  data-src="https://snap.licdn.com/li.lms-analytics/insight.min.js"></script>'''),
    svc("tiktok-pixel", "TikTok Pixel", "marketing", "head",
        {"en": "Measures the performance of TikTok ad campaigns.", "de": "Misst den Erfolg von TikTok-Werbekampagnen.", "es": "Mide el rendimiento de las campañas publicitarias de TikTok."},
        cookies=["_ttp", "_tt_enable_cookie"],
        markup='''<script type="text/plain" data-cmp-service="tiktok-pixel">
  /* Paste the base code from TikTok Events Manager here, unchanged. */
</script>'''),
    svc("pinterest-tag", "Pinterest Tag", "marketing", "head",
        {"en": "Conversion tracking and audiences for Pinterest ads.", "de": "Conversion-Tracking und Zielgruppen für Pinterest-Anzeigen.", "es": "Seguimiento de conversiones y audiencias para anuncios de Pinterest."},
        cookies=["_pin_unauth", "_epik", "_derived_epik", "^_pinterest_"],
        markup='''<script type="text/plain" data-cmp-service="pinterest-tag">
  /* Paste the Pinterest base code here, unchanged. */
</script>'''),
    svc("youtube", "YouTube", "media", "native",
        {"en": "Plays embedded videos. YouTube may set cookies once a video loads.", "de": "Spielt eingebettete Videos ab. YouTube kann beim Laden Cookies setzen.", "es": "Reproduce vídeos incrustados. YouTube puede instalar cookies al cargar un vídeo."},
        fields=[("url", "Video URL", "https://www.youtube.com/watch?v=aqz-KE-bpKQ")],
        note="Uses Webstudio’s native YouTube component in an interaction-mode Consent Gate."),
    svc("vimeo", "Vimeo", "media", "native",
        {"en": "Plays embedded videos hosted on Vimeo.", "de": "Spielt eingebettete Videos von Vimeo ab.", "es": "Reproduce vídeos incrustados alojados en Vimeo."},
        fields=[("url", "Video URL", "https://vimeo.com/76979871")],
        note="Uses Webstudio’s native Vimeo component in an interaction-mode Consent Gate."),
    svc("google-maps", "Google Maps", "media", "embed",
        {"en": "Shows interactive maps.", "de": "Zeigt interaktive Karten.", "es": "Muestra mapas interactivos."},
        fields=[("query", "Place or address", "Palma de Mallorca")],
        markup=f'''<template data-cmp-service="google-maps">
  <iframe src="https://www.google.com/maps?q={{{{query}}}}&output=embed" title="Google Maps"
    loading="lazy" referrerpolicy="no-referrer-when-downgrade" {IFRAME_STYLE}></iframe>
</template>'''),
    svc("spotify", "Spotify", "media", "embed",
        {"en": "Plays embedded tracks, albums and podcasts.", "de": "Spielt eingebettete Titel, Alben und Podcasts ab.", "es": "Reproduce canciones, álbumes y pódcasts incrustados."},
        fields=[("path", "Embed path", "track/4uLU6hMCjMI75M1A2tKUQC")],
        markup='''<template data-cmp-service="spotify">
  <iframe src="https://open.spotify.com/embed/{{path}}" title="Spotify player" height="152" loading="lazy"
    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
    style="display:block;width:100%;border:0;border-radius:12px"></iframe>
</template>'''),
    svc("instagram", "Instagram posts", "media", "embed",
        {"en": "Shows embedded Instagram posts.", "de": "Zeigt eingebettete Instagram-Beiträge.", "es": "Muestra publicaciones de Instagram incrustadas."},
        fields=[("postUrl", "Post URL", "https://www.instagram.com/p/POST_ID/")],
        markup='''<template data-cmp-service="instagram">
  <blockquote class="instagram-media" data-instgrm-permalink="{{postUrl}}"></blockquote>
  <script async src="https://www.instagram.com/embed.js"></script>
</template>'''),
    svc("google-fonts", "Google Fonts", "media", "head",
        {"en": "Loads web fonts from Google servers.", "de": "Lädt Web-Schriftarten von Google-Servern.", "es": "Carga fuentes web desde servidores de Google."},
        fields=[("family", "Font query", "Inter:wght@400;600")],
        markup='''<link rel="stylesheet" data-cmp-service="google-fonts"
  data-href="https://fonts.googleapis.com/css2?family={{family}}&display=swap">''',
        note="Self-hosting fonts as Webstudio Assets avoids this consent entirely."),
    svc("calendly", "Calendly", "functional", "embed",
        {"en": "Lets visitors book appointments directly on the page.", "de": "Ermöglicht Terminbuchungen direkt auf der Seite.", "es": "Permite reservar citas directamente en la página."},
        fields=[("url", "Scheduling URL", "https://calendly.com/YOUR_NAME/30min")],
        markup='''<template data-cmp-service="calendly">
  <div class="calendly-inline-widget" data-url="{{url}}" style="min-width:320px;height:700px"></div>
  <script src="https://assets.calendly.com/assets/external/widget.js" async></script>
</template>'''),
    svc("hubspot", "HubSpot", "functional", "head",
        {"en": "Chat, forms and visitor tracking for our CRM.", "de": "Chat, Formulare und Besucher-Tracking für unser CRM.", "es": "Chat, formularios y seguimiento de visitantes para nuestro CRM."},
        cookies=["__hstc", "hubspotutk", "__hssc", "__hssrc", "messagesUtk"], fields=[("portalId", "Hub ID", "XXXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="hubspot" id="hs-script-loader"
  data-src="https://js.hs-scripts.com/{{portalId}}.js"></script>'''),
    svc("intercom", "Intercom", "functional", "head",
        {"en": "Live chat and customer support messenger.", "de": "Live-Chat und Kundensupport-Messenger.", "es": "Chat en vivo y mensajería de atención al cliente."},
        cookies=["^intercom-"], fields=[("appId", "App ID", "XXXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="intercom">
  window.intercomSettings = { api_base: "https://api-iam.intercom.io", app_id: "{{appId}}" };
  /* followed by the Intercom loader snippet, unchanged */
</script>'''),
    svc("crisp", "Crisp", "functional", "head",
        {"en": "Live chat widget.", "de": "Live-Chat-Widget.", "es": "Widget de chat en vivo."},
        cookies=["^crisp-client"], fields=[("websiteId", "Website ID", "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")],
        markup='''<script type="text/plain" data-cmp-service="crisp">
  window.$crisp = [];
  window.CRISP_WEBSITE_ID = "{{websiteId}}";
  (function () { var s = document.createElement("script");
    s.src = "https://client.crisp.chat/l.js"; s.async = 1;
    document.head.appendChild(s); })();
</script>'''),
    svc("google-recaptcha", "Google reCAPTCHA", "functional", "embed",
        {"en": "Protects forms against spam and abuse.", "de": "Schützt Formulare vor Spam und Missbrauch.", "es": "Protege los formularios contra el spam y el abuso."},
        markup='''<script type="text/plain" data-cmp-service="google-recaptcha"
  data-src="https://www.google.com/recaptcha/api.js"></script>''',
        note="Place it in an HTML Embed next to the form and wrap the form in a Consent Gate."),
]


def grouped():
    return [
        {"id": pid, "title": PURPOSE_TEXT[pid]["en"][0], "description": PURPOSE_TEXT[pid]["en"][1], "services": [s for s in CATALOG if s["purpose"] == pid]}
        for pid in PURPOSES
    ]
