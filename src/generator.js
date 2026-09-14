/*!
 * SPDX-License-Identifier: AGPL-3.0-or-later
 *
 * Native CMP: configuration generator.
 * Reads the service catalog from the page (data-gen-* attributes rendered by
 * Webstudio Collections), keeps state in localStorage and writes copy-ready output.
 */
(function () {
  "use strict";

  // generator data is split across <script type="application/json" data-gen-chunk> embeds
  function loadData() {
    var parts = {};
    [].forEach.call(document.querySelectorAll("script[data-gen-chunk]"), function (node) {
      parts[node.getAttribute("data-gen-chunk")] = node.textContent;
    });
    var keys = Object.keys(parts).sort(function (a, b) { return a - b; });
    if (!keys.length || Number(keys[keys.length - 1]) + 1 !== keys.length) return null;
    try {
      return JSON.parse(keys.map(function (key) { return parts[key]; }).join(""));
    } catch (error) {
      console.error("[cmp generator] could not read generator data", error);
      return null;
    }
  }

  var D = loadData();
  if (!D) return;

  var STORAGE_KEY = "cmp-generator-v2";
  var FLAGS = ["required", "default", "optOut", "onlyOnce", "contextualOnly"];
  var PURPOSE_IDS = ["essential"].concat(D.purposeOrder);
  var doc = document;

  /* ------------------------------------------------------------------ state */

  function defaults() {
    return {
      selected: {},
      fields: {},
      overrides: {},
      custom: [],
      translations: {},
      dirs: {},
      options: {
        languages: ["en"],
        gateLanguage: "",
        privacyUrl: "/privacy",
        storageName: "cmp_consent",
        cookieExpiresAfterDays: 365,
        cookieDomain: "",
        storage: "cookie",
        mustConsent: false,
        noNotice: false,
        consentMode: false,
        dataLayer: false,
      },
    };
  }

  function load() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return defaults();
      var data = JSON.parse(raw);
      var base = defaults();
      for (var key in base) if (data[key] === undefined) data[key] = base[key];
      for (var option in base.options) if (data.options[option] === undefined) data.options[option] = base.options[option];
      return data;
    } catch (error) {
      return defaults();
    }
  }

  var state = window.__cmpGeneratorState || (window.__cmpGeneratorState = load());

  function save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (error) {}
  }

  /* ---------------------------------------------------------------- helpers */

  function $$(selector, scope) {
    return [].slice.call((scope || doc).querySelectorAll(selector));
  }

  function words(value) {
    return String(value || "").split(/[\s,]+/).filter(Boolean);
  }

  function slug(value) {
    return String(value || "")
      .replace(/([a-z0-9])([A-Z])/g, "$1-$2")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function compact(value) {
    return String(value || "").toLowerCase().replace(/[^a-z0-9]/g, "");
  }

  function json(value) {
    return JSON.stringify(value, null, 2);
  }

  function el(tag, attrs, children) {
    var node = doc.createElement(tag);
    for (var key in attrs || {}) {
      if (attrs[key] === undefined || attrs[key] === null) continue;
      if (key === "text") node.textContent = attrs[key];
      else if (key === "value") node.value = attrs[key];
      else node.setAttribute(key, attrs[key]);
    }
    (children || []).forEach(function (child) {
      if (child) node.appendChild(typeof child === "string" ? doc.createTextNode(child) : child);
    });
    return node;
  }

  function unchanged(node, value) {
    var signature = JSON.stringify(value);
    if (node.__genSignature === signature) return true;
    node.__genSignature = signature;
    return false;
  }

  /* -------------------------------------------------------------- languages */

  function normalizeLanguage(value) {
    var parts = String(value || "").trim().replace(/_/g, "-").split("-").filter(Boolean);
    if (!parts.length || !/^[a-z]{2,3}$/i.test(parts[0])) return "";
    return parts
      .map(function (part, index) {
        if (index === 0) return part.toLowerCase();
        return part.length === 2 ? part.toUpperCase() : part.toLowerCase();
      })
      .join("-");
  }

  function primary(lang) {
    return String(lang).split("-")[0].toLowerCase();
  }

  function pack(lang) {
    return D.languages[lang] || D.languages[primary(lang)] || null;
  }

  function languageName(lang) {
    var known = pack(lang);
    if (D.languages[lang]) return D.languages[lang].name;
    try {
      var names = new Intl.DisplayNames([lang, "en"], { type: "language" });
      return names.of(lang) || lang;
    } catch (error) {
      return known ? known.name + " (" + lang + ")" : lang;
    }
  }

  function direction(lang) {
    var chosen = state.dirs[lang];
    if (chosen === "rtl" || chosen === "ltr") return chosen;
    var known = pack(lang);
    if (known) return known.dir;
    return D.rtl.indexOf(primary(lang)) !== -1 ? "rtl" : "ltr";
  }

  function lookup(object, path) {
    return path.split(".").reduce(function (value, key) {
      return value && value[key] !== undefined ? value[key] : undefined;
    }, object);
  }

  /* ---------------------------------------------------------------- catalog */

  function catalog() {
    var seen = {};
    return $$("[data-gen-row]")
      .map(function (row) {
        return {
          id: row.getAttribute("data-gen-row"),
          title: row.getAttribute("data-gen-title") || "",
          purpose: row.getAttribute("data-gen-purpose") || "functional",
          placement: row.getAttribute("data-gen-placement") || "head",
          description: {
            en: row.getAttribute("data-gen-description") || "",
            de: row.getAttribute("data-gen-description-de") || "",
            es: row.getAttribute("data-gen-description-es") || "",
          },
          cookies: words(row.getAttribute("data-gen-cookies")),
          consentMode: words(row.getAttribute("data-gen-consent-mode")),
          markup: row.getAttribute("data-gen-markup") || "",
          note: row.getAttribute("data-gen-note") || "",
        };
      })
      .filter(function (service) {
        if (!service.id || seen[service.id]) return false;
        seen[service.id] = true;
        return true;
      });
  }

  function fieldValue(id) {
    var value = state.fields[id];
    if (value) return value;
    var input = doc.querySelector('[data-gen-field="' + id + '"]');
    return input ? input.getAttribute("placeholder") || "" : "";
  }

  function fill(service) {
    return service.markup.replace(/\{\{(\w+)\}\}/g, function (_, key) {
      return fieldValue(service.id + "." + key);
    });
  }

  var ALIASES = {
    ga: "google-analytics", ga4: "google-analytics", googleanalytics4: "google-analytics", universalanalytics: "google-analytics",
    gtm: "google-tag-manager", tagmanager: "google-tag-manager",
    adwords: "google-ads", googleadwords: "google-ads",
    facebook: "meta-pixel", facebookpixel: "meta-pixel", fbpixel: "meta-pixel", metapixel: "meta-pixel",
    piwik: "matomo", clarity: "microsoft-clarity", linkedin: "linkedin-insight", linkedininsighttag: "linkedin-insight",
    tiktok: "tiktok-pixel", pinterest: "pinterest-tag", gmaps: "google-maps", maps: "google-maps",
    fonts: "google-fonts", recaptcha: "google-recaptcha", youtubenocookie: "youtube",
  };

  function matchCatalog(name, services) {
    var key = compact(name);
    var alias = ALIASES[key];
    for (var i = 0; i < services.length; i++) {
      if (compact(services[i].id) === key || services[i].id === alias) return services[i];
    }
    return null;
  }

  /* ----------------------------------------------------------- translations */
  // Every visible string has a key. Values come from the visitor's edits,
  // then the built-in language pack, then English.

  function translationKeys(services) {
    var selected = services.filter(function (service) { return state.selected[service.id]; });
    var purposes = { essential: true };
    var items = [{ name: "consent-manager", purpose: "essential" }];
    selected.forEach(function (service) {
      purposes[service.purpose] = true;
      items.push({ name: service.id, purpose: service.purpose, catalog: service });
    });
    state.custom.forEach(function (custom) {
      var purpose = custom.purpose || "functional";
      purposes[purpose] = true;
      items.push({ name: custom.name, purpose: purpose, custom: custom });
    });
    var purposeList = PURPOSE_IDS.filter(function (id) { return purposes[id]; }).concat(
      Object.keys(purposes).filter(function (id) { return PURPOSE_IDS.indexOf(id) === -1; })
    );
    return { purposes: purposeList, items: items };
  }

  function defaultText(lang, key, context) {
    var parts = key.split(".");
    var packFor = pack(lang);
    var english = D.languages.en;
    if (parts[0] === "purpose") {
      var id = parts[1];
      var index = parts[2] === "title" ? 0 : 1;
      var own = packFor && packFor.purposes[id];
      if (own) return { value: own[index], fallback: false };
      if (english.purposes[id]) return { value: english.purposes[id][index], fallback: lang !== "en" };
      return { value: index === 0 ? id.charAt(0).toUpperCase() + id.slice(1).replace(/-/g, " ") : "", fallback: lang !== "en" };
    }
    if (parts[0] === "service") {
      var name = parts.slice(1, -1).join(".");
      var field = parts[parts.length - 1];
      var item = context && context[name];
      if (name === "consent-manager") {
        var cm = (packFor || english).consentManager[field];
        return { value: cm, fallback: !packFor };
      }
      if (item && item.catalog) {
        if (field === "title") return { value: item.catalog.title, fallback: false };
        var known = D.serviceDescriptions[name] || {};
        var described = known[lang] || known[primary(lang)] || item.catalog.description[lang] || item.catalog.description[primary(lang)];
        return { value: described || item.catalog.description.en, fallback: !described && lang !== "en" };
      }
      if (item && item.custom) {
        return { value: field === "title" ? item.custom.title || item.custom.name : item.custom.description || "", fallback: lang !== "en" };
      }
      return { value: "", fallback: false };
    }
    if (key === "privacyUrl") return { value: state.options.privacyUrl || "/privacy", fallback: false };
    var fromPack = packFor ? lookup(packFor, key) : undefined;
    if (fromPack !== undefined) return { value: fromPack, fallback: false };
    return { value: lookup(english, key), fallback: lang !== "en" };
  }

  function text(lang, key, context) {
    var edited = state.translations[lang] && state.translations[lang][key];
    if (typeof edited === "string") return edited;
    return defaultText(lang, key, context).value;
  }

  function setText(lang, key, value) {
    state.translations[lang] = state.translations[lang] || {};
    state.translations[lang][key] = value;
  }

  var UI_KEYS = [
    ["notice.title", "Notice · Title"],
    ["notice.text", "Notice · Text (the privacy link follows it)", true],
    ["notice.changes", "Notice · Services changed", true],
    ["notice.customize", "Notice · Customize button"],
    ["notice.decline", "Notice · Decline button"],
    ["notice.accept", "Notice · Accept button"],
    ["modal.title", "Modal · Title"],
    ["modal.text", "Modal · Text (the privacy link follows it)", true],
    ["modal.close", "Modal · Close button label"],
    ["modal.toggleAll", "Modal · Toggle all"],
    ["modal.alwaysActive", "Modal · Always active badge"],
    ["modal.activeByDefault", "Modal · Active by default badge"],
    ["modal.service", "Modal · “service” (singular)"],
    ["modal.services", "Modal · “services” (plural)"],
    ["modal.decline", "Modal · Decline button"],
    ["modal.save", "Modal · Save button"],
    ["modal.accept", "Modal · Accept button"],
    ["privacyLabel", "Privacy policy link text"],
    ["privacyUrl", "Privacy policy URL"],
  ];

  function editorFields(keys) {
    var fields = UI_KEYS.map(function (entry) {
      return { key: entry[0], label: entry[1], long: !!entry[2] };
    });
    keys.purposes.forEach(function (id) {
      fields.push({ key: "purpose." + id + ".title", label: "Purpose " + id + " · Title" });
      fields.push({ key: "purpose." + id + ".description", label: "Purpose " + id + " · Description", long: true });
    });
    keys.items.forEach(function (item) {
      fields.push({ key: "service." + item.name + ".title", label: "Service " + item.name + " · Title" });
      fields.push({ key: "service." + item.name + ".description", label: "Service " + item.name + " · Description", long: true });
    });
    return fields;
  }

  /* ----------------------------------------------------------------- output */

  function cleanFlags(source, target) {
    FLAGS.forEach(function (flag) {
      if (source[flag]) target[flag] = true;
    });
    if (source.dependsOn && source.dependsOn.length) target.dependsOn = source.dependsOn;
    return target;
  }

  function build() {
    var services = catalog();
    var selected = services.filter(function (service) { return state.selected[service.id]; });
    var languages = state.options.languages.length ? state.options.languages : ["en"];
    var keys = translationKeys(services);
    var context = {};
    keys.items.forEach(function (item) { context[item.name] = item; });

    // consentServices
    var entries = [{ name: "consent-manager", required: true }];
    function addEntry(entry) {
      if (!entries.some(function (existing) { return existing.name === entry.name; })) entries.push(entry);
    }
    selected.forEach(function (service) {
      var override = state.overrides[service.id] || {};
      var entry = { name: service.id };
      var cookies = override.cookies && override.cookies.length ? override.cookies : service.cookies;
      if (cookies.length) entry.cookies = cookies;
      addEntry(cleanFlags(override, entry));
    });
    state.custom.forEach(function (custom) {
      var entry = { name: custom.name };
      if (custom.cookies && custom.cookies.length) entry.cookies = custom.cookies;
      addEntry(cleanFlags(custom, entry));
    });

    // consentTranslations
    var translations = languages.map(function (lang) {
      var t = function (key) { return text(lang, key, context); };
      var entry = {
        lang: lang,
        dir: direction(lang),
        privacyLabel: t("privacyLabel"),
        privacyUrl: t("privacyUrl"),
        notice: {},
        modal: {},
        purposes: [],
      };
      UI_KEYS.forEach(function (item) {
        var key = item[0];
        if (key.indexOf("notice.") === 0) entry.notice[key.slice(7)] = t(key);
        if (key.indexOf("modal.") === 0) entry.modal[key.slice(6)] = t(key);
      });
      entry.purposes = keys.purposes.map(function (id) {
        return {
          id: id,
          title: t("purpose." + id + ".title"),
          description: t("purpose." + id + ".description"),
          services: keys.items
            .filter(function (item) { return item.purpose === id; })
            .map(function (item) {
              return { name: item.name, title: t("service." + item.name + ".title"), description: t("service." + item.name + ".description") };
            }),
        };
      });
      return entry;
    });

    // cmpConfig
    var options = state.options;
    var config = {
      storageName: options.storageName || "cmp_consent",
      cookieExpiresAfterDays: Number(options.cookieExpiresAfterDays) || 365,
    };
    if (options.storage === "localStorage") config.storage = "localStorage";
    if (options.cookieDomain) config.cookieDomain = options.cookieDomain;
    if (options.noNotice) config.noNotice = true;
    else if (options.mustConsent) config.mustConsent = true;
    if (options.dataLayer) config.dataLayer = true;
    if (languages[0] !== "en") config.fallbackLanguage = languages[0];
    if (options.consentMode) {
      var map = {};
      selected.forEach(function (service) {
        service.consentMode.forEach(function (type) {
          (map[type] = map[type] || []).push(service.id);
        });
      });
      state.custom.forEach(function (custom) {
        var known = matchCatalog(custom.name, services);
        if (known) known.consentMode.forEach(function (type) {
          (map[type] = map[type] || []).push(custom.name);
        });
      });
      if (Object.keys(map).length) config.consentMode = map;
    }

    var headSnippets = selected
      .filter(function (service) { return service.placement === "head" && service.markup; })
      .map(function (service) { return "<!-- " + service.title + " -->\n" + fill(service); });

    var customCode = [
      "<!-- Native CMP: configuration -->",
      "<script>",
      "window.cmpConfig = " + json(config) + ";",
      "</script>",
      "<style data-cmp-theme>" + D.themeCss + "</style>",
      "<style data-cmp-critical>" + D.css + "</style>",
      '<script data-cmp-engine="' + D.version + '">' + D.engine + "</script>",
      "<!-- Consent-managed head scripts -->",
      headSnippets.length ? headSnippets.join("\n\n") : "<!-- Add consent-managed scripts here -->",
    ].join("\n");

    var gateLanguage = languages.indexOf(options.gateLanguage) !== -1 ? options.gateLanguage : languages[0];
    var embeds = selected
      .filter(function (service) { return (service.placement === "embed" || service.placement === "native") && (service.markup || D.fragments.nativeGates[service.id]); })
      .map(function (service) {
        if (service.placement === "native") {
          return {
            title: service.title,
            native: true,
            text: "Paste where the video should appear. The gate contains Webstudio’s " + service.title + " component, set up so nothing loads before consent: the visitor clicks play, allows " + service.title + " and the video starts. Upload your own thumbnail to its Preview Image.",
            // generated on copy: fresh ids must not change the render signature
            gate: function () { return nativeGateClipboard(service, gateLanguage); },
            gateKey: service.id + ":" + gateLanguage + ":" + fieldValue(service.id + ".url"),
            note: service.note,
          };
        }
        var code = fill(service);
        return {
          title: service.title,
          text: "Select the element where the " + service.title + " content should appear and paste the gate. It already contains your embed code.",
          code: code,
          gate: function () { return gateClipboard(service, code, gateLanguage); },
          gateKey: service.id + ":" + gateLanguage + ":" + code,
          note: service.note,
        };
      });
    state.custom.forEach(function (custom) {
      embeds.push({
        title: custom.title || custom.name,
        text: "Mark the existing script or embed of this service.",
        code:
          '<script type="text/plain" data-cmp-service="' + custom.name + '" data-src="https://…"></script>\n\n' +
          '<template data-cmp-service="' + custom.name + '">\n  <!-- iframe or widget markup -->\n</template>',
      });
    });

    return {
      entries: entries,
      translationData: translations,
      customCode: customCode,
      services: json(entries),
      translations: json(translations),
      embeds: embeds,
      gateLanguage: gateLanguage,
      count: entries.length,
      languages: languages,
      keys: keys,
      context: context,
      notes: selected.filter(function (service) { return service.note && service.placement === "head"; }),
    };
  }

  /* -------------------------------------------------- Webstudio clipboard */
  // Webstudio pastes text/plain JSON in the "@webstudio/instance/v0.1" format.

  function jsonString(value) {
    return JSON.stringify(String(value)).slice(1, -1);
  }

  function gateStrings(lang, provider) {
    var strings = (pack(lang) || D.languages.en).gate;
    return {
      load: strings.load,
      always: strings.always.replace("{provider}", provider),
      settings: strings.settings,
      cancel: strings.cancel,
      text: strings.text.split("{provider}").join(provider),
    };
  }

  function replaceAll(template, map) {
    Object.keys(map).forEach(function (key) {
      template = template.split(key).join(jsonString(map[key]));
    });
    return template;
  }

  function gateClipboard(service, code, lang) {
    var strings = gateStrings(lang, service.title);
    return replaceAll(D.fragments.gate, {
      __SERVICE__: service.id,
      __TITLE__: service.title,
      __TEXT__: strings.text,
      __ALWAYS__: strings.always,
      __LOAD__: strings.load,
      __SETTINGS__: strings.settings,
      __EMBED__: code,
    });
  }

  function nativeGateClipboard(service, lang) {
    var strings = gateStrings(lang, service.title);
    var envelope = replaceAll(D.fragments.nativeGates[service.id], {
      __TITLE__: service.title,
      __TEXT__: strings.text,
      __ALWAYS__: strings.always,
      __LOAD__: strings.load,
      __CANCEL__: strings.cancel,
      __SETTINGS__: strings.settings,
      __URL__: fieldValue(service.id + ".url"),
    });
    return JSON.stringify(withFreshIds(JSON.parse(envelope)));
  }

  var ID_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_";

  function newId(previous) {
    var bytes = new Uint8Array(21);
    (window.crypto || window.msCrypto).getRandomValues(bytes);
    var id = "";
    for (var i = 0; i < bytes.length; i++) id += ID_ALPHABET[bytes[i] % ID_ALPHABET.length];
    return previous.indexOf("fx_") === 0 ? "fx_" + id : id;
  }

  function escapeRegExp(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  // Webstudio links a pasted Slot to an existing Slot with the same ids. Fresh ids
  // make every copy a new Consent Manager carrying the generated variables.
  function withFreshIds(envelope) {
    var fragment = envelope[Object.keys(envelope)[0]];
    var ids = [];
    fragment.instances.forEach(function (item) { ids.push(item.id); });
    fragment.dataSources.forEach(function (item) { ids.push(item.id); });
    fragment.props.forEach(function (item) { ids.push(item.id); });
    fragment.styleSources.forEach(function (item) { if (item.type === "local") ids.push(item.id); });
    var serialized = JSON.stringify(envelope);
    ids.sort(function (a, b) { return b.length - a.length; }).forEach(function (id) {
      var replacement = newId(id);
      serialized = serialized
        .replace(new RegExp(escapeRegExp(JSON.stringify(id)), "g"), JSON.stringify(replacement))
        .replace(new RegExp(escapeRegExp("$ws$dataSource$" + id.replace(/-/g, "__DASH__")) + "(?![\\w])", "g"), "$$ws$$dataSource$$" + replacement);
    });
    return JSON.parse(serialized);
  }

  function componentClipboard() {
    var result = build();
    var envelope = withFreshIds(D.fragments.consentManager);
    var fragment = envelope[Object.keys(envelope)[0]];
    fragment.dataSources.forEach(function (source) {
      if (source.type !== "variable") return;
      if (source.name === "consentServices") source.value = { type: "json", value: result.entries };
      if (source.name === "consentTranslations") source.value = { type: "json", value: result.translationData };
    });
    return JSON.stringify(envelope);
  }

  /* ----------------------------------------------------------------- render */

  function setOutput(name, value) {
    $$('[data-gen-output="' + name + '"]').forEach(function (node) {
      if (node.textContent !== value) node.textContent = value;
    });
  }

  function copyButton(getText, label, variant) {
    var status = el("span", { class: "gen-status", "aria-live": "polite" });
    var button = el("button", { type: "button", class: "gen-button" + (variant === "primary" ? " gen-button-primary" : ""), text: label || "Copy" });
    button.addEventListener("click", function () {
      copy(getText(), status);
    });
    return el("span", { class: "gen-copy" }, [button, status]);
  }

  function renderLanguages(result) {
    $$("[data-gen-language-list]").forEach(function (list) {
      var chips = result.languages.map(function (lang) { return [lang, direction(lang)]; });
      if (unchanged(list, chips)) return;
      list.textContent = "";
      result.languages.forEach(function (lang, index) {
        var dir = direction(lang);
        list.appendChild(
          el("span", { class: "gen-chip", "data-gen-language": lang }, [
            el("span", { lang: lang, dir: dir, text: languageName(lang) }),
            el("span", { class: "gen-muted", text: " " + lang + (dir === "rtl" ? " · RTL" : "") + (index === 0 ? " · fallback" : "") }),
            result.languages.length > 1
              ? el("button", { type: "button", class: "gen-chip-remove", "data-gen-remove-language": lang, "aria-label": "Remove " + languageName(lang), text: "×" })
              : null,
          ])
        );
      });
    });
  }

  function renderEditor(result) {
    $$("[data-gen-translation-editor]").forEach(function (editor) {
      var fields = editorFields(result.keys);
      var structure = { languages: result.languages, dirs: result.languages.map(direction), fields: fields.map(function (f) { return f.key; }) };
      if (unchanged(editor, structure)) return;
      var open = {};
      $$("details[data-gen-editor-language]", editor).forEach(function (details) {
        if (details.open) open[details.getAttribute("data-gen-editor-language")] = true;
      });
      editor.textContent = "";
      result.languages.forEach(function (lang) {
        var dir = direction(lang);
        var fallbackCount = 0;
        var rows = fields.map(function (field) {
          var fallback = defaultText(lang, field.key, result.context).fallback && !(state.translations[lang] && typeof state.translations[lang][field.key] === "string");
          if (fallback) fallbackCount++;
          var attrs = {
            "data-gen-t": lang + "::" + field.key,
            lang: lang,
            dir: field.key === "privacyUrl" ? "ltr" : dir,
            value: text(lang, field.key, result.context),
            class: "gen-input" + (fallback ? " gen-input-fallback" : ""),
            spellcheck: "true",
          };
          var input = field.long ? el("textarea", Object.assign({ rows: "3" }, attrs)) : el("input", Object.assign({ type: "text" }, attrs));
          return el("label", { class: "gen-field" }, [
            el("span", { class: "gen-field-label" }, [field.label, fallback ? el("span", { class: "gen-badge", text: "English – translate" }) : null]),
            input,
          ]);
        });
        var dirSelect = el("select", { class: "gen-input", "data-gen-dir": lang, "aria-label": "Text direction for " + lang }, [
          el("option", { value: "auto", text: "Detect from language (" + (D.rtl.indexOf(primary(lang)) !== -1 || (pack(lang) && pack(lang).dir === "rtl") ? "right-to-left" : "left-to-right") + ")" }),
          el("option", { value: "ltr", text: "Left-to-right" }),
          el("option", { value: "rtl", text: "Right-to-left" }),
        ]);
        dirSelect.value = state.dirs[lang] || "auto";
        var summary = el("summary", {}, [
          el("strong", { lang: lang, dir: dir, text: languageName(lang) }),
          el("span", { class: "gen-muted", text: " · " + lang + " · " + (dir === "rtl" ? "right-to-left" : "left-to-right") + (fallbackCount ? " · " + fallbackCount + (fallbackCount === 1 ? " text" : " texts") + " to translate" : " · complete") }),
        ]);
        editor.appendChild(
          el("details", { class: "gen-language", "data-gen-editor-language": lang, open: open[lang] ? "" : null }, [
            summary,
            el("div", { class: "gen-editor-grid" }, [
              el("label", { class: "gen-field" }, [el("span", { class: "gen-field-label", text: "Text direction" }), dirSelect]),
              el("span", { class: "gen-muted gen-editor-actions" }, [
                el("button", { type: "button", class: "gen-button", "data-gen-reset-language": lang, text: "Reset to built-in texts" }),
              ]),
            ].concat(rows)),
          ])
        );
      });
    });
  }

  function render() {
    if (!doc.querySelector("[data-gen-root]")) return;
    var result = build();
    setOutput("custom-code", result.customCode);
    setOutput("services", result.services);
    setOutput("translations", result.translations);

    $$("[data-gen-summary]").forEach(function (node) {
      node.textContent = result.count + " services · " + result.languages.map(languageName).join(", ");
    });

    renderLanguages(result);
    renderEditor(result);

    $$('[data-gen-output-list="embeds"]').forEach(function (list) {
      var signature = { embeds: result.embeds, languages: result.languages, gate: result.gateLanguage };
      if (unchanged(list, signature)) return;
      list.textContent = "";
      if (!result.embeds.length) {
        list.appendChild(el("p", { class: "gen-empty", text: "No gates needed for the selected services." }));
        return;
      }
      if (result.languages.length > 1) {
        var select = el("select", { class: "gen-input", "data-gen-option": "gateLanguage", "aria-label": "Gate language" },
          result.languages.map(function (lang) { return el("option", { value: lang, text: languageName(lang) }); }));
        select.value = result.gateLanguage;
        list.appendChild(el("label", { class: "gen-field gen-inline" }, [el("span", { class: "gen-field-label", text: "Gate texts in" }), select]));
      }
      result.embeds.forEach(function (item) {
        list.appendChild(
          el("div", { class: "gen-card", "data-gen-embed": item.title }, [
            el("h4", { text: item.title + (item.native ? " · native component" : "") }),
            el("p", { text: item.text }),
            el("div", { class: "gen-card-actions" }, [
              item.gate ? copyButton(item.gate, "Copy Consent Gate", "primary") : null,
              item.code ? copyButton(function () { return item.code; }, item.gate ? "Copy embed code only" : "Copy code") : null,
            ]),
            item.code ? el("details", {}, [el("summary", { text: "Show code" }), el("pre", { text: item.code })]) : null,
            item.note ? el("p", { text: item.note }) : null,
          ])
        );
      });
    });

    $$('[data-gen-output-list="notes"]').forEach(function (list) {
      if (unchanged(list, result.notes.map(function (service) { return service.id; }))) return;
      list.textContent = "";
      result.notes.forEach(function (service) {
        list.appendChild(el("p", { class: "gen-note", text: service.title + ": " + service.note }));
      });
    });

    $$("[data-gen-custom-list]").forEach(function (list) {
      if (unchanged(list, state.custom)) return;
      list.textContent = "";
      state.custom.forEach(function (custom, index) {
        var remove = el("button", { type: "button", class: "gen-button", "data-gen-remove": String(index), text: "Remove" });
        remove.setAttribute("aria-label", "Remove " + (custom.title || custom.name));
        list.appendChild(
          el("div", { class: "gen-custom-row" }, [
            el("span", {}, [
              el("strong", { text: custom.title || custom.name }),
              el("span", { class: "gen-muted", text: " · " + custom.name + " · " + (custom.purpose || "functional") + (custom.cookies && custom.cookies.length ? " · " + custom.cookies.length + " cookie patterns" : "") }),
            ]),
            remove,
          ])
        );
      });
    });

    $$("[data-gen-row]").forEach(function (row) {
      var id = row.getAttribute("data-gen-row");
      if (!!state.selected[id] === row.hasAttribute("data-gen-selected")) return;
      if (state.selected[id]) row.setAttribute("data-gen-selected", "");
      else row.removeAttribute("data-gen-selected");
    });
  }

  function hydrateInputs() {
    $$("input[data-gen-service]").forEach(function (input) {
      input.checked = !!state.selected[input.getAttribute("data-gen-service")];
    });
    $$("[data-gen-field]").forEach(function (input) {
      var value = state.fields[input.getAttribute("data-gen-field")] || "";
      if (input.value !== value) input.value = value;
    });
    $$("[data-gen-option]").forEach(function (input) {
      var key = input.getAttribute("data-gen-option");
      if (key === "gateLanguage") return;
      if (input.type === "checkbox") input.checked = !!state.options[key];
      else {
        var value = state.options[key] === undefined ? "" : String(state.options[key]);
        if (input.value !== value) input.value = value;
      }
    });
    // editors are rebuilt from state
    $$("[data-gen-translation-editor],[data-gen-language-list],[data-gen-output-list]").forEach(function (node) {
      node.__genSignature = null;
    });
  }

  function copy(value, status) {
    function done(ok) {
      if (!status) return;
      status.textContent = ok ? "Copied" : "Press ⌘/Ctrl + C";
      clearTimeout(status.__timer);
      status.__timer = setTimeout(function () { status.textContent = ""; }, 2000);
    }
    function fallback() {
      var area = el("textarea", { style: "position:fixed;opacity:0;top:0;left:0" });
      area.value = value;
      doc.body.appendChild(area);
      area.select();
      var ok = false;
      try { ok = doc.execCommand("copy"); } catch (error) {}
      area.remove();
      done(ok);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(value).then(function () { done(true); }, fallback);
    } else {
      fallback();
    }
  }

  /* ------------------------------------------------------------ loose parser */
  // Parses JSON and JavaScript object literals without executing them.

  function parseLoose(source) {
    var s = String(source);
    var i = s.search(/[\[{]/);
    if (i < 0) throw new Error("No object or array found.");

    function fail(message) {
      throw new Error(message + " (position " + i + ")");
    }

    function space() {
      for (;;) {
        while (i < s.length && /\s/.test(s[i])) i++;
        if (s.substr(i, 2) === "//") {
          while (i < s.length && s[i] !== "\n") i++;
        } else if (s.substr(i, 2) === "/*") {
          var end = s.indexOf("*/", i + 2);
          i = end < 0 ? s.length : end + 2;
        } else return;
      }
    }

    function skipString() {
      var quote = s[i++];
      while (i < s.length && s[i] !== quote) i += s[i] === "\\" ? 2 : 1;
      i++;
    }

    function skipBalanced(open, close) {
      var depth = 0;
      while (i < s.length) {
        var c = s[i];
        if (c === '"' || c === "'" || c === "`") { skipString(); continue; }
        if (s.substr(i, 2) === "//" || s.substr(i, 2) === "/*") { space(); continue; }
        if (c === open) depth++;
        else if (c === close) {
          depth--;
          if (depth === 0) { i++; return; }
        }
        i++;
      }
    }

    function skipExpression() {
      space();
      if (s[i] === "{") return skipBalanced("{", "}");
      var depth = 0;
      while (i < s.length) {
        var c = s[i];
        if (c === '"' || c === "'" || c === "`") { skipString(); continue; }
        if (c === "(" || c === "[" || c === "{") depth++;
        else if (c === ")" || c === "]" || c === "}") {
          if (depth === 0) return;
          depth--;
        } else if (c === "," && depth === 0) return;
        i++;
      }
    }

    function identifier() {
      var match = /^[A-Za-z_$][\w$]*/.exec(s.slice(i));
      if (!match) fail("Unexpected character " + JSON.stringify(s[i] || "end of input"));
      i += match[0].length;
      return match[0];
    }

    function string() {
      var quote = s[i++];
      var out = "";
      while (i < s.length && s[i] !== quote) {
        var c = s[i++];
        if (c === "\\") {
          var n = s[i++];
          if (n === "n") out += "\n";
          else if (n === "t") out += "\t";
          else if (n === "r") out += "\r";
          else if (n === "u") { out += String.fromCharCode(parseInt(s.substr(i, 4), 16)); i += 4; }
          else out += n;
        } else out += c;
      }
      i++;
      return out;
    }

    function regex() {
      i++;
      var out = "";
      var inClass = false;
      while (i < s.length) {
        var c = s[i];
        if (c === "\\") { out += c + s[i + 1]; i += 2; continue; }
        if (c === "[") inClass = true;
        else if (c === "]") inClass = false;
        else if (c === "/" && !inClass) break;
        out += c;
        i++;
      }
      i++;
      while (/[a-z]/i.test(s[i] || "")) i++;
      return { __regex: out };
    }

    function value() {
      space();
      var c = s[i];
      if (c === "{") return object();
      if (c === "[") return array();
      if (c === '"' || c === "'" || c === "`") return string();
      if (c === "/") return regex();
      if (c === "(") {
        skipBalanced("(", ")");
        space();
        if (s.substr(i, 2) === "=>") { i += 2; skipExpression(); }
        return undefined;
      }
      var number = /^-?(0x[\da-f]+|\d*\.?\d+(e[-+]?\d+)?)/i.exec(s.slice(i));
      if (number) { i += number[0].length; return Number(number[0]); }
      var word = identifier();
      if (word === "true") return true;
      if (word === "false") return false;
      if (word === "null" || word === "undefined") return null;
      if (word === "function" || word === "async") {
        while (i < s.length && s[i] !== "{") i++;
        skipBalanced("{", "}");
        return undefined;
      }
      if (word === "new") {
        space();
        var ctor = identifier();
        space();
        if (s[i] === "(") {
          i++;
          var arg = value();
          while (i < s.length && s[i] !== ")") i++;
          i++;
          return ctor === "RegExp" && typeof arg === "string" ? { __regex: arg } : undefined;
        }
        return undefined;
      }
      space();
      if (s.substr(i, 2) === "=>") { i += 2; skipExpression(); return undefined; }
      skipExpression();
      return undefined;
    }

    function object() {
      i++;
      var out = {};
      for (;;) {
        space();
        if (s[i] === "}") { i++; return out; }
        if (s.substr(i, 3) === "...") { i += 3; skipExpression(); }
        else {
          var key = s[i] === '"' || s[i] === "'" ? string() : s[i] === "[" ? (skipBalanced("[", "]"), null) : String(identifierOrNumber());
          space();
          if (s[i] === "(") {
            skipBalanced("(", ")");
            space();
            skipBalanced("{", "}");
          } else if (s[i] === ":") {
            i++;
            var v = value();
            if (key !== null && v !== undefined) out[key] = v;
          }
        }
        space();
        if (s[i] === ",") i++;
        else if (s[i] !== "}") fail("Expected , or }");
      }
    }

    function identifierOrNumber() {
      var number = /^\d+/.exec(s.slice(i));
      if (number) { i += number[0].length; return number[0]; }
      return identifier();
    }

    function array() {
      i++;
      var out = [];
      for (;;) {
        space();
        if (s[i] === "]") { i++; return out; }
        var v = value();
        if (v !== undefined) out.push(v);
        space();
        if (s[i] === ",") i++;
        else if (s[i] !== "]") fail("Expected , or ]");
      }
    }

    return value();
  }

  /* ----------------------------------------------------------------- import */

  function toPattern(cookie) {
    if (cookie == null) return null;
    if (Array.isArray(cookie)) return toPattern(cookie[0]);
    if (typeof cookie === "object" && cookie.__regex !== undefined) {
      var source = cookie.__regex;
      return source.charAt(0) === "^" ? source : "^.*(?:" + source + ")";
    }
    if (typeof cookie === "object") return toPattern(cookie.pattern);
    return String(cookie);
  }

  function importedText(lang, key, value) {
    if (typeof value !== "string" || !value.trim()) return;
    setText(lang, key, value);
  }

  function addLanguage(lang) {
    lang = normalizeLanguage(lang);
    if (!lang) return "";
    if (state.options.languages.indexOf(lang) === -1) state.options.languages.push(lang);
    return lang;
  }

  function upsertService(raw, purposeHint, services, stats) {
    if (!raw || typeof raw !== "object") return null;
    var name = slug(raw.name || raw.id);
    if (!name || name === "consent-manager") return null;
    var purposes = Array.isArray(raw.purposes) ? raw.purposes : raw.purpose ? [raw.purpose] : [];
    var purpose = slug(purposes[0] || purposeHint || "functional");
    var cookies = (raw.cookies || []).map(toPattern).filter(function (pattern, index, list) {
      return pattern && list.indexOf(pattern) === index;
    });
    var flags = {
      required: !!raw.required,
      default: !!raw.default,
      optOut: !!raw.optOut,
      onlyOnce: !!raw.onlyOnce,
      contextualOnly: !!(raw.contextualOnly || raw.contextualConsentOnly),
      dependsOn: (Array.isArray(raw.dependsOn) ? raw.dependsOn : raw.dependsOn ? [raw.dependsOn] : []).map(slug),
    };
    var known = matchCatalog(raw.name || raw.id, services);
    var target;
    var key;
    if (known) {
      state.selected[known.id] = true;
      target = state.overrides[known.id] = state.overrides[known.id] || {};
      if (cookies.length) target.cookies = cookies;
      key = known.id;
      stats.matched++;
    } else {
      target = null;
      for (var i = 0; i < state.custom.length; i++) if (state.custom[i].name === name) target = state.custom[i];
      if (!target) {
        target = { name: name };
        state.custom.push(target);
      }
      target.title = typeof raw.title === "string" ? raw.title : target.title || raw.name;
      if (typeof raw.description === "string") target.description = raw.description;
      target.purpose = purpose;
      target.cookies = cookies.length ? cookies : target.cookies || [];
      key = name;
      stats.custom++;
    }
    FLAGS.forEach(function (flag) { target[flag] = flags[flag]; });
    target.dependsOn = flags.dependsOn;
    if (raw.translations && typeof raw.translations === "object") {
      for (var lang in raw.translations) {
        var code = lang === "zz" ? "en" : addLanguage(lang);
        var entry = raw.translations[lang] || {};
        importedText(code, "service." + key + ".title", entry.title);
        importedText(code, "service." + key + ".description", entry.description);
      }
    }
    return { key: key, target: target };
  }

  function importConfig(source) {
    var value = parseLoose(source);
    var services = catalog();
    var stats = { matched: 0, custom: 0, languages: 0 };

    function importTranslations(list) {
      list.forEach(function (entry) {
        if (!entry || !entry.lang) return;
        var lang = addLanguage(entry.lang);
        if (!lang) return;
        stats.languages++;
        if (entry.dir === "rtl" || entry.dir === "ltr") state.dirs[lang] = entry.dir;
        importedText(lang, "privacyLabel", entry.privacyLabel);
        importedText(lang, "privacyUrl", entry.privacyUrl);
        ["notice", "modal"].forEach(function (group) {
          var texts = entry[group] || {};
          for (var key in texts) importedText(lang, group + "." + key, texts[key]);
        });
        (entry.purposes || []).forEach(function (purpose) {
          if (!purpose || !purpose.id) return;
          importedText(lang, "purpose." + purpose.id + ".title", purpose.title);
          importedText(lang, "purpose." + purpose.id + ".description", purpose.description);
          (purpose.services || []).forEach(function (item) {
            var result = upsertService(item, purpose.id, services, stats);
            if (!result) return;
            importedText(lang, "service." + result.key + ".title", item.title);
            importedText(lang, "service." + result.key + ".description", item.description);
          });
        });
      });
    }

    if (Array.isArray(value)) {
      if (value.some(function (item) { return item && item.lang; })) importTranslations(value);
      else value.forEach(function (item) { upsertService(item, null, services, stats); });
    } else if (value && typeof value === "object") {
      if (Array.isArray(value.consentServices)) value.consentServices.forEach(function (item) { upsertService(item, null, services, stats); });
      if (Array.isArray(value.consentTranslations)) importTranslations(value.consentTranslations);
      var list = value.services || value.apps;
      if (Array.isArray(list)) {
        // Klaro-style configuration
        var translations = value.translations && typeof value.translations === "object" ? value.translations : {};
        var codes = {};
        for (var lang in translations) codes[lang] = lang === "zz" ? "en" : addLanguage(lang);
        list.forEach(function (raw) {
          var result = upsertService(raw, null, services, stats);
          if (!result) return;
          for (var code in codes) {
            var t = translations[code] || {};
            var own = t[raw.name];
            if (own) {
              importedText(codes[code], "service." + result.key + ".title", own.title);
              importedText(codes[code], "service." + result.key + ".description", own.description);
            }
          }
        });
        var privacySet = false;
        for (var original in codes) {
          var target = codes[original];
          var texts = translations[original] || {};
          if (original !== "zz") stats.languages++;
          if (typeof texts.privacyPolicyUrl === "string" && (original === "zz" || original === "en" || !privacySet)) {
            state.options.privacyUrl = texts.privacyPolicyUrl;
            privacySet = original === "zz" || original === "en";
          }
          importedText(target, "modal.title", lookup(texts, "consentModal.title"));
          importedText(target, "modal.text", lookup(texts, "consentModal.description"));
          importedText(target, "notice.customize", lookup(texts, "consentNotice.learnMore"));
          importedText(target, "notice.accept", texts.acceptAll || texts.ok);
          importedText(target, "modal.accept", texts.acceptAll);
          importedText(target, "notice.decline", texts.decline);
          importedText(target, "modal.decline", texts.decline);
          importedText(target, "modal.save", texts.save);
          importedText(target, "modal.close", texts.close);
          importedText(target, "privacyLabel", lookup(texts, "privacyPolicy.name"));
          if (texts.purposes && typeof texts.purposes === "object") {
            for (var purpose in texts.purposes) {
              var purposeText = texts.purposes[purpose];
              var id = slug(purpose);
              if (typeof purposeText === "string") importedText(target, "purpose." + id + ".title", purposeText);
              else if (purposeText) {
                importedText(target, "purpose." + id + ".title", purposeText.title);
                importedText(target, "purpose." + id + ".description", purposeText.description);
              }
            }
          }
        }
        if (typeof value.privacyPolicy === "string") state.options.privacyUrl = value.privacyPolicy;
        if (value.storageMethod === "localStorage") state.options.storage = "localStorage";
        if (value.storageName || value.cookieName) state.options.storageName = value.storageName || value.cookieName;
        if (value.cookieExpiresAfterDays) state.options.cookieExpiresAfterDays = value.cookieExpiresAfterDays;
        if (typeof value.cookieDomain === "string") state.options.cookieDomain = value.cookieDomain;
        if (value.mustConsent) state.options.mustConsent = true;
        if (value.noNotice) {
          state.options.noNotice = true;
          state.options.mustConsent = false;
        }
      }
    }
    if (!stats.matched && !stats.custom) throw new Error("No services found. Paste a services array or a config object with a services array.");
    return stats;
  }

  /* ----------------------------------------------------------------- events */

  function message(selector, value, isError) {
    $$(selector).forEach(function (node) {
      node.textContent = value;
      if (isError) node.setAttribute("data-gen-error", "");
      else node.removeAttribute("data-gen-error");
    });
  }

  function onInput(event) {
    var target = event.target;
    if (!target.getAttribute) return;
    var service = target.getAttribute("data-gen-service");
    var field = target.getAttribute("data-gen-field");
    var option = target.getAttribute("data-gen-option");
    var translation = target.getAttribute("data-gen-t");
    var dirLanguage = target.getAttribute("data-gen-dir");
    if (service !== null) state.selected[service] = target.checked;
    else if (field !== null) state.fields[field] = target.value.trim();
    else if (translation !== null) {
      var split = translation.indexOf("::");
      setText(translation.slice(0, split), translation.slice(split + 2), target.value);
      target.classList.remove("gen-input-fallback");
    } else if (dirLanguage !== null) {
      if (target.value === "auto") delete state.dirs[dirLanguage];
      else state.dirs[dirLanguage] = target.value;
    } else if (option !== null) {
      if (target.type === "checkbox") {
        state.options[option] = target.checked;
        // contextual-only and "require a decision" exclude each other
        var other = { noNotice: "mustConsent", mustConsent: "noNotice" }[option];
        if (other && target.checked && state.options[other]) {
          state.options[other] = false;
          $$('[data-gen-option="' + other + '"]').forEach(function (input) { input.checked = false; });
        }
      } else state.options[option] = target.value.trim();
    } else return;
    save();
    render();
  }

  function onClick(event) {
    var target = event.target.closest && event.target.closest("[data-gen-action],[data-gen-copy],[data-gen-remove],[data-gen-remove-language],[data-gen-reset-language]");
    if (!target) return;
    var copyName = target.getAttribute("data-gen-copy");
    if (copyName) {
      var status = doc.querySelector('[data-gen-copy-status="' + copyName + '"]');
      if (copyName === "component") return copy(componentClipboard(), status);
      if (copyName === "link") return copy(D.fragments.link, status);
      var output = doc.querySelector('[data-gen-output="' + copyName + '"]');
      if (output) copy(output.textContent, status);
      return;
    }
    var remove = target.getAttribute("data-gen-remove");
    if (remove !== null) {
      state.custom.splice(Number(remove), 1);
      save();
      render();
      return;
    }
    var removeLanguage = target.getAttribute("data-gen-remove-language");
    if (removeLanguage !== null) {
      state.options.languages = state.options.languages.filter(function (lang) { return lang !== removeLanguage; });
      save();
      render();
      return;
    }
    var resetLanguage = target.getAttribute("data-gen-reset-language");
    if (resetLanguage !== null) {
      delete state.translations[resetLanguage];
      delete state.dirs[resetLanguage];
      $$("[data-gen-translation-editor]").forEach(function (node) { node.__genSignature = null; });
      save();
      render();
      return;
    }
    var action = target.getAttribute("data-gen-action");
    if (action === "add-language") {
      var pick = doc.querySelector("[data-gen-language-pick]");
      var codeInput = doc.querySelector("[data-gen-language-code]");
      var raw = codeInput && codeInput.value.trim() ? codeInput.value : pick ? pick.value : "";
      var lang = normalizeLanguage(raw);
      if (!lang) {
        message("[data-gen-language-message]", "Enter a language code such as fr, pt-BR or ar.", true);
        return;
      }
      if (state.options.languages.indexOf(lang) !== -1) {
        message("[data-gen-language-message]", languageName(lang) + " is already added.", true);
        return;
      }
      addLanguage(lang);
      if (codeInput) codeInput.value = "";
      message("[data-gen-language-message]", pack(lang) ? "Added " + languageName(lang) + " with built-in texts." : "Added " + languageName(lang) + ". Translate its texts below.");
      save();
      render();
    } else if (action === "add-custom") {
      var read = function (key) {
        var input = doc.querySelector('[data-gen-custom="' + key + '"]');
        if (!input) return "";
        return input.type === "checkbox" ? input.checked : input.value.trim();
      };
      var name = slug(read("name") || read("title"));
      if (!name) {
        message("[data-gen-custom-message]", "Enter at least a title or a service key.", true);
        return;
      }
      if (name === "consent-manager" || state.custom.some(function (c) { return c.name === name; })) {
        message("[data-gen-custom-message]", "A service with the key “" + name + "” already exists.", true);
        return;
      }
      state.custom.push({
        name: name,
        title: read("title") || name,
        description: read("description"),
        purpose: read("purpose") || "functional",
        cookies: words(read("cookies")),
        required: !!read("required"),
        optOut: !!read("optOut"),
      });
      $$("[data-gen-custom]").forEach(function (input) {
        if (input.type === "checkbox") input.checked = false;
        else if (input.tagName !== "SELECT") input.value = "";
      });
      message("[data-gen-custom-message]", "Added “" + name + "”.");
      save();
      render();
    } else if (action === "import") {
      var area = doc.querySelector("[data-gen-import]");
      try {
        var stats = importConfig(area ? area.value : "");
        message(
          "[data-gen-import-message]",
          "Imported " + (stats.matched + stats.custom) + " services: " + stats.matched + " matched the catalog, " + stats.custom + " added as custom services" +
            (stats.languages ? ", " + stats.languages + " languages." : ".")
        );
        save();
        hydrateInputs();
        render();
      } catch (error) {
        message("[data-gen-import-message]", "Could not import: " + error.message, true);
      }
    } else if (action === "reset") {
      var fresh = defaults();
      for (var key in fresh) state[key] = fresh[key];
      save();
      hydrateInputs();
      render();
      message("[data-gen-import-message]", "");
      message("[data-gen-custom-message]", "");
      message("[data-gen-language-message]", "");
    }
  }

  if (!window.__cmpGeneratorListeners) {
    window.__cmpGeneratorListeners = true;
    doc.addEventListener("change", onInput);
    doc.addEventListener("input", onInput);
    doc.addEventListener("click", onClick);
  }
  window.cmpGenerator = {
    parse: parseLoose,
    importConfig: importConfig,
    build: build,
    component: componentClipboard,
    state: function () { return state; },
  };

  hydrateInputs();
  render();
})();
