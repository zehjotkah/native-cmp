"""/examples: ready-to-copy configurations for common services."""

import json

from ui import T
from rich import txt, rich, p, ul, code, callout, intro, page_header, page_footer

PURPOSES = {
    "analytics": ("Analytics", "Help us understand how visitors use the website so we can improve it."),
    "marketing": ("Marketing", "Measure the performance of our advertising and show more relevant ads."),
    "media": ("External media", "Load content from third-party platforms such as videos, maps and social posts."),
    "functional": ("Functional", "Enable features such as live chat, scheduling and spam protection."),
}

# id, title, purpose, description, service entry, markup, note
SERVICES = [
    # analytics -----------------------------------------------------------------
    dict(
        id="google-analytics", title="Google Analytics 4", purpose="analytics",
        description="Collects pseudonymous usage statistics.",
        service={"name": "google-analytics", "cookies": ["^_ga", "_gid", "^_gat"]},
        where="Custom Code or HTML Embed",
        markup='''<script type="text/plain" data-cmp-service="google-analytics"
  data-src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script type="text/plain" data-cmp-service="google-analytics">
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag("js", new Date());
  gtag("config", "G-XXXXXXXXXX");
</script>''',
        note="GA4 enhanced measurement tracks client-side page changes automatically. Put the snippet in Custom Code so it runs once per visit, not on every page.",
    ),
    dict(
        id="matomo", title="Matomo", purpose="analytics",
        description="Self-hosted or cloud analytics with pseudonymous visitor statistics.",
        service={"name": "matomo", "cookies": ["^_pk_id", "^_pk_ses", "^_pk_ref"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="matomo">
  var _paq = window._paq = window._paq || [];
  _paq.push(["trackPageView"]);
  _paq.push(["enableLinkTracking"]);
  (function () {
    var u = "https://analytics.example.com/";
    _paq.push(["setTrackerUrl", u + "matomo.php"]);
    _paq.push(["setSiteId", "1"]);
    var g = document.createElement("script");
    g.async = true; g.src = u + "matomo.js";
    document.head.appendChild(g);
  })();
</script>''',
        note="For client-side page changes, add `_paq.push([\"setCustomUrl\", location.href], [\"trackPageView\"])` to an accept script on each page, or track route changes in your Matomo Tag Manager.",
    ),
    dict(
        id="plausible", title="Plausible Analytics", purpose="analytics",
        description="Cookieless, privacy-friendly website statistics.",
        service={"name": "plausible"},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="plausible"
  data-domain="example.com"
  data-src="https://plausible.io/js/script.js"></script>''',
        note="Cookieless tools are often used without consent. If your own assessment allows that, set `\"optOut\": true`: the script then runs until the visitor declines it.",
    ),
    dict(
        id="rybbit", title="Rybbit", purpose="analytics",
        description="Cookieless, privacy-friendly web and product analytics.",
        service={"name": "rybbit"},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="rybbit" async
  data-src="https://app.rybbit.io/api/script.js?siteId=YOUR_SITE_ID"></script>''',
        note="Rybbit is open source, cookieless and tracks client-side navigation automatically. Many sites use it without consent; if your own assessment allows that, set `\"optOut\": true` so it runs until the visitor declines. Self-hosted? Replace `app.rybbit.io` with your instance.",
    ),
    dict(
        id="microsoft-clarity", title="Microsoft Clarity", purpose="analytics",
        description="Session recordings and heatmaps to improve usability.",
        service={"name": "microsoft-clarity", "cookies": ["_clck", "_clsk"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="microsoft-clarity">
  (function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
  })(window, document, "clarity", "script", "XXXXXXXXXX");
</script>''',
        note=None,
    ),
    dict(
        id="hotjar", title="Hotjar", purpose="analytics",
        description="Heatmaps, recordings and feedback surveys.",
        service={"name": "hotjar", "cookies": ["^_hj"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="hotjar">
  (function(h,o,t,j,a,r){h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
  h._hjSettings={hjid:1234567,hjsv:6};a=o.getElementsByTagName("head")[0];
  r=o.createElement("script");r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
  a.appendChild(r);})(window,document,"https://static.hotjar.com/c/hotjar-",".js?sv=");
</script>''',
        note=None,
    ),
    # marketing ---------------------------------------------------------------
    dict(
        id="google-tag-manager", title="Google Tag Manager + Consent Mode v2", purpose="marketing",
        description="Loads marketing and analytics tags configured in Google Tag Manager.",
        service={"name": "google-ads", "cookies": ["^_gcl"]},
        multi=[{"name": "google-analytics", "cookies": ["^_ga", "_gid", "^_gat"]}, {"name": "google-ads", "cookies": ["^_gcl"]}],
        where="Custom Code, below the CMP snippet",
        markup='''<script>
  window.cmpConfig = {
    // …your other options
    consentMode: {
      analytics_storage: ["google-analytics"],
      ad_storage: ["google-ads"],
      ad_user_data: ["google-ads"],
      ad_personalization: ["google-ads"],
    },
  };
</script>
<!-- CMP critical CSS + engine -->
<!-- Google Tag Manager, unchanged -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({"gtm.start":new Date().getTime(),event:"gtm.js"});
var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!="dataLayer"?"&l="+l:"";
j.async=true;j.src="https://www.googletagmanager.com/gtm.js?id="+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,"script","dataLayer","GTM-XXXXXXX");</script>''',
        note="The engine sends `consent default` (all denied) before GTM loads, then `consent update` on every decision. In GTM, rely on built-in consent checks or the `cmp_consent` dataLayer event (`dataLayer: true`). Loading GTM before consent is a legal decision; to block GTM entirely, use `type=\"text/plain\"` and `data-cmp-service` on its script instead.",
    ),
    dict(
        id="google-ads", title="Google Ads (gtag)", purpose="marketing",
        description="Measures conversions from Google Ads campaigns and enables remarketing.",
        service={"name": "google-ads", "cookies": ["^_gcl"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="google-ads"
  data-src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"></script>
<script type="text/plain" data-cmp-service="google-ads">
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag("js", new Date());
  gtag("config", "AW-XXXXXXXXX");
</script>''',
        note=None,
    ),
    dict(
        id="meta-pixel", title="Meta Pixel", purpose="marketing",
        description="Measures the effectiveness of ads on Facebook and Instagram.",
        service={"name": "meta-pixel", "cookies": ["_fbp", "_fbc"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="meta-pixel">
  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,"script","https://connect.facebook.net/en_US/fbevents.js");
  fbq("init", "XXXXXXXXXXXXXXX");
  fbq("track", "PageView");
</script>''',
        note=None,
    ),
    dict(
        id="linkedin-insight", title="LinkedIn Insight Tag", purpose="marketing",
        description="Conversion tracking and retargeting for LinkedIn ads.",
        service={"name": "linkedin-insight", "cookies": ["li_fat_id", "li_giant", "ln_or"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="linkedin-insight">
  window._linkedin_partner_id = "XXXXXXX";
  window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
  window._linkedin_data_partner_ids.push(window._linkedin_partner_id);
</script>
<script type="text/plain" data-cmp-service="linkedin-insight"
  data-src="https://snap.licdn.com/li.lms-analytics/insight.min.js"></script>''',
        note=None,
    ),
    dict(
        id="tiktok-pixel", title="TikTok Pixel", purpose="marketing",
        description="Measures the performance of TikTok ad campaigns.",
        service={"name": "tiktok-pixel", "cookies": ["_ttp", "_tt_enable_cookie"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="tiktok-pixel">
  /* Paste the base code from TikTok Events Manager here, unchanged, e.g.
     !function (w, d, t) { … ttq.load("XXXXXXXXXXXXXXXXXXXX"); ttq.page(); }(window, document, "ttq"); */
</script>''',
        note="Any vendor snippet works the same way: keep the code as it is and only change the opening `<script>` tag.",
    ),
    dict(
        id="pinterest-tag", title="Pinterest Tag", purpose="marketing",
        description="Conversion tracking and audiences for Pinterest ads.",
        service={"name": "pinterest-tag", "cookies": ["_pin_unauth", "_epik", "_derived_epik", "^_pinterest_"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="pinterest-tag">
  /* Paste the Pinterest base code here, unchanged, e.g.
     !function(e){ … }("https://s.pinimg.com/ct/core.js");
     pintrk("load", "XXXXXXXXXXXXX"); pintrk("page"); */
</script>''',
        note=None,
    ),
    # media -------------------------------------------------------------------------
    dict(
        id="youtube", title="YouTube", purpose="media",
        description="Plays embedded videos. YouTube may set cookies once a video loads.",
        service={"name": "youtube"},
        where="Webstudio’s YouTube component in an interaction-mode Consent Gate",
        markup='''Consent Gate            data-cmp-gate="youtube"
                        data-cmp-gate-mode="interaction"
├─ Gate Notice          data-cmp-gate-notice (overlay)
└─ YouTube component    data-cmp-gate-content
     URL                    https://www.youtube.com/watch?v=VIDEO_ID
     Show preview           off
     Autoplay               off
     Preconnect             off
     Privacy enhanced mode  on
     Preview Image          your own thumbnail''',
        note="The video stays visible. When the visitor clicks play, the consent notice appears on top; after **Load content** the video starts. Copy a ready-made gate from the [generator](/generator), see [Consent Gates](/docs#native-video).",
    ),
    dict(
        id="vimeo", title="Vimeo", purpose="media",
        description="Plays embedded videos hosted on Vimeo.",
        service={"name": "vimeo"},
        where="Webstudio’s Vimeo component in an interaction-mode Consent Gate",
        markup='''Consent Gate            data-cmp-gate="vimeo"
                        data-cmp-gate-mode="interaction"
├─ Gate Notice          data-cmp-gate-notice (overlay)
└─ Vimeo component      data-cmp-gate-content
     URL                    https://vimeo.com/VIDEO_ID
     Show preview           off
     Autoplay               off
     Do not track           on
     Preview Image          your own thumbnail''',
        note="With **Show preview** on, the component calls the Vimeo API and loads the thumbnail from Vimeo before any consent. Copy a ready-made gate from the [generator](/generator).",
    ),
    dict(
        id="google-maps", title="Google Maps", purpose="media",
        description="Shows interactive maps.",
        service={"name": "google-maps"},
        where="HTML Embed inside a Consent Gate",
        markup='''<template data-cmp-service="google-maps">
  <iframe src="https://www.google.com/maps?q=Palma%20de%20Mallorca&output=embed"
    title="Google Maps" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
    style="display:block;width:100%;aspect-ratio:16/9;border:0"></iframe>
</template>''',
        note=None,
    ),
    dict(
        id="spotify", title="Spotify", purpose="media",
        description="Plays embedded tracks, albums and podcasts.",
        service={"name": "spotify"},
        where="HTML Embed inside a Consent Gate",
        markup='''<template data-cmp-service="spotify">
  <iframe src="https://open.spotify.com/embed/track/TRACK_ID"
    title="Spotify player" height="152" loading="lazy"
    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
    style="display:block;width:100%;border:0;border-radius:12px"></iframe>
</template>''',
        note=None,
    ),
    dict(
        id="instagram", title="Instagram posts", purpose="media",
        description="Shows embedded Instagram posts.",
        service={"name": "instagram"},
        where="HTML Embed inside a Consent Gate",
        markup='''<template data-cmp-service="instagram">
  <blockquote class="instagram-media"
    data-instgrm-permalink="https://www.instagram.com/p/POST_ID/"></blockquote>
  <script async src="https://www.instagram.com/embed.js"></script>
</template>''',
        note="Scripts inside a template run when the template is inserted, so widget loaders find their markup.",
    ),
    dict(
        id="google-fonts", title="Google Fonts (CDN)", purpose="media",
        description="Loads web fonts from Google servers.",
        service={"name": "google-fonts"},
        where="Custom Code",
        markup='''<link rel="stylesheet" data-cmp-service="google-fonts"
  data-href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap">''',
        note="Better: upload the font files to Webstudio Assets. Self-hosted fonts need no consent and never flash a fallback font.",
    ),
    # functional ----------------------------------------------------------------------
    dict(
        id="calendly", title="Calendly", purpose="functional",
        description="Lets visitors book appointments directly on the page.",
        service={"name": "calendly"},
        where="HTML Embed inside a Consent Gate",
        markup='''<template data-cmp-service="calendly">
  <div class="calendly-inline-widget"
    data-url="https://calendly.com/YOUR_NAME/30min"
    style="min-width:320px;height:700px"></div>
  <script src="https://assets.calendly.com/assets/external/widget.js" async></script>
</template>''',
        note=None,
    ),
    dict(
        id="hubspot", title="HubSpot", purpose="functional",
        description="Chat, forms and visitor tracking for our CRM.",
        service={"name": "hubspot", "cookies": ["__hstc", "hubspotutk", "__hssc", "__hssrc", "messagesUtk"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="hubspot" id="hs-script-loader"
  data-src="https://js.hs-scripts.com/XXXXXXXX.js"></script>''',
        note=None,
    ),
    dict(
        id="intercom", title="Intercom", purpose="functional",
        description="Live chat and customer support messenger.",
        service={"name": "intercom", "cookies": ["^intercom-"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="intercom">
  window.intercomSettings = { api_base: "https://api-iam.intercom.io", app_id: "XXXXXXXX" };
  /* followed by the Intercom loader snippet, unchanged */
</script>''',
        note=None,
    ),
    dict(
        id="crisp", title="Crisp", purpose="functional",
        description="Live chat widget.",
        service={"name": "crisp", "cookies": ["^crisp-client"]},
        where="Custom Code",
        markup='''<script type="text/plain" data-cmp-service="crisp">
  window.$crisp = [];
  window.CRISP_WEBSITE_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX";
  (function () { var s = document.createElement("script");
    s.src = "https://client.crisp.chat/l.js"; s.async = 1;
    document.head.appendChild(s); })();
</script>''',
        note=None,
    ),
    dict(
        id="google-recaptcha", title="Google reCAPTCHA", purpose="functional",
        description="Protects forms against spam and abuse.",
        service={"name": "google-recaptcha"},
        where="HTML Embed next to the form",
        markup='''<script type="text/plain" data-cmp-service="google-recaptcha"
  data-src="https://www.google.com/recaptcha/api.js"></script>''',
        note="Wrap the form in a Consent Gate so visitors can allow reCAPTCHA right where they need it.",
    ),
]


def service_json(entry):
    return json.dumps(entry, indent=2, ensure_ascii=False)


def translation_json(entry):
    return json.dumps({"name": entry["service"]["name"], "title": entry["title"].split(" + ")[0], "description": entry["description"]}, indent=2, ensure_ascii=False)


def example_card(entry):
    purpose_title = PURPOSES[entry["purpose"]][0]
    cookies = sorted({c for svc in (entry.get("multi") or [entry["service"]]) for c in svc.get("cookies", [])})
    cookie_line = p("Cookies removed on decline: " + ", ".join(f"`{c}`" for c in cookies), "site-text") if cookies else p("No first-party cookies to remove.", "site-text")
    note = callout(entry["note"]) if entry.get("note") else ""
    label = 'Structure · ' if entry['id'] in ('youtube', 'vimeo') else 'Markup · '
    return f"""
<article id='{entry['id']}' ws:label='{entry['title']}' {T('site-example')}>
  <div {T('site-example-column')}>
    <span {T('site-badge')}>{txt(purpose_title)}</span>
    <h3 {T('site-heading-small')}>{txt(entry['title'])}</h3>
    {p(entry['description'], 'site-text')}
    {cookie_line}
    {code(json.dumps(entry['multi'], indent=2) if entry.get('multi') else service_json(entry['service']), 'consentServices')}
    {'' if entry.get('multi') else code(translation_json(entry), 'consentTranslations → purposes[' + entry['purpose'] + '].services')}
  </div>
  <div {T('site-example-column')}>
    {code(entry['markup'], label + entry['where'])}
    {note}
  </div>
</article>"""


def intro_section():
    chips = "".join(
        f"<a href='#{key}' {T('site-badge')}>{txt(title)}</a>" for key, (title, _) in PURPOSES.items()
    ) + f"<a href='#complete-configuration' {T('site-badge')}>Complete configuration</a>"
    steps = f"""
<div {T('site-grid')}>
  <div {T('site-card')}><span {T('site-card-number')}>1</span><h2 {T('site-heading-small')}>Add the service</h2>{p('Copy the `consentServices` entry into the variable on the Consent Manager root.', 'site-text')}</div>
  <div {T('site-card')}><span {T('site-card-number')}>2</span><h2 {T('site-heading-small')}>Describe it</h2>{p('Add the `consentTranslations` entry to the matching purpose, once per language.', 'site-text')}</div>
  <div {T('site-card')}><span {T('site-card-number')}>3</span><h2 {T('site-heading-small')}>Block the code</h2>{p('Paste the markup into Custom Code or an HTML Embed and replace the placeholder IDs.', 'site-text')}</div>
</div>"""
    return f"""
<section ws:label='How to use the examples' {T('site-section', 'is-site-section-muted')}>
  <div {T('site-container')}>
    <div {T('site-actions')}>{chips}</div>
    {steps}
    {callout('These examples are technical starting points, not legal advice. Check each vendor’s current snippet and cookie list, and describe services accurately in your privacy policy. More details are in the [documentation](/docs).')}
  </div>
</section>"""


def purpose_section(key, muted):
    title, description = PURPOSES[key]
    cards = "".join(example_card(e) for e in SERVICES if e["purpose"] == key)
    tokens = T("site-section", "is-site-section-muted") if muted else T("site-section")
    return f"""
<section id='{key}' ws:label='{title}' {tokens}>
  <div {T('site-container')}>
    <div {T('site-stack')}>
      <p {T('site-eyebrow')}>{txt('Purpose · ' + key)}</p>
      <h2 {T('site-heading')}>{txt(title)}</h2>
      <p {T('site-lead')}>{txt(description)}</p>
    </div>
    {cards}
  </div>
</section>"""


def complete_config():
    services = [{"name": "consent-manager", "required": True}]
    seen = {"consent-manager"}
    for e in SERVICES:
        if e["service"]["name"] not in seen:
            seen.add(e["service"]["name"])
            services.append(e["service"])
    purposes = [{"id": "essential", "title": "Essential", "description": "Required for the website to work, for example to remember your privacy choices.",
                 "services": [{"name": "consent-manager", "title": "Consent manager", "description": "Stores your privacy choices in the cmp_consent cookie."}]}]
    for key, (title, description) in PURPOSES.items():
        items, names = [], set()
        for e in SERVICES:
            if e["purpose"] == key and e["service"]["name"] not in names:
                names.add(e["service"]["name"])
                items.append({"name": e["service"]["name"], "title": e["title"].split(" + ")[0].replace(" (gtag)", "").replace(" (CDN)", ""), "description": e["description"]})
        purposes.append({"id": key, "title": title, "description": description, "services": items})
    body = f"""
<div {T('site-grid', 'is-site-grid-wide')}>
  <div {T('site-example-column')}>{code(json.dumps(services, indent=2), 'consentServices')}</div>
  <div {T('site-example-column')}>{code(json.dumps(purposes, indent=2, ensure_ascii=False), 'consentTranslations[0].purposes (English)')}</div>
</div>
{callout('Only keep the services you actually use. Every listed service appears in the preferences modal, and removing or adding services asks returning visitors for consent again.')}"""
    return f"""
<section id='complete-configuration' ws:label='Complete configuration' {T('site-section', 'is-site-section-muted')}>
  <div {T('site-container')}>
    <div {T('site-stack')}>
      <p {T('site-eyebrow')}>{txt('Copy & paste')}</p>
      <h2 {T('site-heading')}>Complete configuration</h2>
      <p {T('site-lead')}>All services on this page combined. Start here, then delete what you don’t need.</p>
    </div>
    {body}
  </div>
</section>"""


def parts():
    sections = [
        intro("Service library", "Examples for the services you actually use.", "Copy-paste configurations for {n} common services: analytics, marketing pixels, embeds and widgets. Each example includes the service entry, its description and the blocked markup.".format(n=len(SERVICES))),
        intro_section(),
    ]
    for i, key in enumerate(PURPOSES):
        sections.append(purpose_section(key, muted=bool(i % 2)))
    sections.append(complete_config())
    return page_header("/examples"), sections, page_footer()
