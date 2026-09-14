window.cmpConfig = {
  storage: "cookie", // "cookie" or "localStorage"
  storageName: "cmp_consent",
  cookieExpiresAfterDays: 365,
  cookieDomain: "", // ".example.com" shares consent across subdomains
  default: false, // default for services without "default" in the consentPurposes variable
  mustConsent: false, // true: open the preferences modal instead of the notice
  noNotice: false, // true: contextual only, no notice on page load (gates, links and API ask for consent)
  dataLayer: false, // true: push { event: "cmp_consent" } to window.dataLayer
  // Google Consent Mode v2: map consent types to service names
  // consentMode: {
  //   analytics_storage: ["google-analytics"],
  //   ad_storage: ["google-ads"],
  //   ad_user_data: ["google-ads"],
  //   ad_personalization: ["google-ads"],
  // },
};
