/*!
 * SPDX-License-Identifier: AGPL-3.0-or-later
 *
 * Native CMP — consent engine
 *
 * Runs once from Project Settings → Custom Code (<head>). The visible UI is
 * built from native Webstudio instances and wired via data-cmp-* attributes,
 * so it survives client-side (SPA) navigation where pages remount.
 *
 * Optional configuration: define `window.cmpConfig = {...}` before this script.
 */
(function () {
  "use strict";

  if (window.cmp && window.cmp.__engine) return;

  var VERSION = "1.3.0";

  var doc = document;
  var html = doc.documentElement;

  var cfg = assign(
    {
      storage: "cookie", // "cookie" | "localStorage"
      storageName: "cmp_consent",
      cookieDomain: "", // e.g. ".example.com" to share consent across subdomains
      cookiePath: "/",
      cookieExpiresAfterDays: 365,
      default: false, // default consent for services without an explicit `default`
      mustConsent: false, // open the modal instead of the notice until the visitor decides
      noNotice: false, // never open the notice automatically (API / links only)
      confirmDelay: 800, // ms the switches stay visible after "accept/decline all" in the modal
      consentMode: null, // Google Consent Mode v2: { analytics_storage: ["google-analytics"], ... }
      consentModeDefaults: null, // extra `gtag("consent","default",…)` fields, e.g. { security_storage: "granted" }
      dataLayer: false, // push { event: "cmp_consent" } into window.dataLayer on decisions
      consentLog: "", // URL of your own consent log, e.g. "https://consentlog.example.com". No IP address is sent.
      fallbackLanguage: "", // language shown when no translation matches <html lang> (default: first one)
      debug: false,
    },
    window.cmpConfig || {}
  );

  /* ------------------------------------------------------------------ utils */

  function assign(target) {
    for (var i = 1; i < arguments.length; i++) {
      var src = arguments[i];
      if (src) for (var k in src) if (Object.prototype.hasOwnProperty.call(src, k)) target[k] = src[k];
    }
    return target;
  }

  function log() {
    if (cfg.debug && window.console) console.debug.apply(console, ["[cmp]"].concat([].slice.call(arguments)));
  }

  function words(value) {
    return (value || "").split(/\s+/).filter(Boolean);
  }

  function bool(el, name) {
    var v = el.getAttribute(name);
    if (v === null || v === "") return undefined;
    return v === "true";
  }

  function each(selector, fn, scope) {
    var list = (scope || doc).querySelectorAll(selector);
    for (var i = 0; i < list.length; i++) fn(list[i]);
  }

  function escapeRegex(str) {
    return str.replace(/[-[\]/{}()*+?.\\^$|]/g, "\\$&");
  }

  function isInternal(node) {
    return node.nodeType === 1 && node.hasAttribute("data-cmp-internal");
  }

  /* ---------------------------------------------------------------- storage */

  // document.cookie throws where cookies are blocked (e.g. sandboxed iframes)
  function cookieString() {
    try {
      return doc.cookie || "";
    } catch (error) {
      return "";
    }
  }

  function writeCookie(value) {
    try {
      doc.cookie = value;
    } catch (error) {}
  }

  function readCookie(name) {
    var parts = cookieString() ? cookieString().split(";") : [];
    for (var i = 0; i < parts.length; i++) {
      var idx = parts[i].indexOf("=");
      if (idx < 0) continue;
      if (parts[i].slice(0, idx).trim() === name) return parts[i].slice(idx + 1).trim();
    }
    return null;
  }

  function cookieNames() {
    return (cookieString() ? cookieString().split(";") : [])
      .map(function (part) {
        return part.split("=")[0].trim();
      })
      .filter(Boolean);
  }

  var store = {
    get: function () {
      try {
        var raw = cfg.storage === "localStorage" ? localStorage.getItem(cfg.storageName) : readCookie(cfg.storageName);
        if (!raw) return null;
        var data = JSON.parse(decodeURIComponent(raw));
        return data && typeof data === "object" ? data : null;
      } catch (error) {
        return null;
      }
    },
    set: function (data) {
      var value = encodeURIComponent(JSON.stringify(data));
      if (cfg.storage === "localStorage") {
        try {
          localStorage.setItem(cfg.storageName, value);
        } catch (error) {}
        return;
      }
      var expires = new Date(Date.now() + cfg.cookieExpiresAfterDays * 864e5).toUTCString();
      writeCookie(
        cfg.storageName +
        "=" +
        value +
        "; expires=" +
        expires +
        "; path=" +
        (cfg.cookiePath || "/") +
        (cfg.cookieDomain ? "; domain=" + cfg.cookieDomain : "") +
        "; SameSite=Lax" +
        (location.protocol === "https:" ? "; Secure" : "")
      );
    },
    remove: function () {
      if (cfg.storage === "localStorage") {
        try {
          localStorage.removeItem(cfg.storageName);
        } catch (error) {}
        return;
      }
      deleteCookie(cfg.storageName, cfg.cookieDomain ? [cfg.cookieDomain] : undefined);
    },
  };

  function cookieDomains() {
    var host = location.hostname;
    var list = ["", host, "." + host];
    var labels = host.split(".");
    for (var i = 1; i < labels.length - 1; i++) list.push("." + labels.slice(i).join("."));
    return list;
  }

  function deleteCookie(name, domains) {
    var paths = ["/", location.pathname];
    (domains || cookieDomains()).forEach(function (domain) {
      paths.forEach(function (path) {
        writeCookie(name + "=; Max-Age=-99999999; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=" + path + (domain ? "; domain=" + domain : ""));
      });
    });
  }

  /* ----------------------------------------------------------------- events */

  var listeners = {};

  function on(type, fn) {
    (listeners[type] = listeners[type] || []).push(fn);
    return function () {
      off(type, fn);
    };
  }

  function off(type, fn) {
    listeners[type] = (listeners[type] || []).filter(function (item) {
      return item !== fn;
    });
  }

  function emit(type, detail) {
    (listeners[type] || []).slice().forEach(function (fn) {
      try {
        fn(detail);
      } catch (error) {
        console.error(error);
      }
    });
    try {
      doc.dispatchEvent(new CustomEvent("cmp:" + type, { detail: detail }));
    } catch (error) {}
  }

  /* ------------------------------------------------------------------ state */

  var services = {}; // name -> service definition (read from the Webstudio UI)
  var serviceOrder = [];
  var configSignature = "";
  var configReady = false;
  var hasDefinitions = false;

  var stored = store.get();
  var consents = stored && stored.consents ? assign({}, stored.consents) : {};
  var savedConsents = assign({}, consents);
  var confirmed = !!stored; // re-validated once service definitions are known
  var changed = false;
  var temporary = {}; // "accept once" consents, not persisted
  var serviceStates = {}; // name -> last applied effective consent
  var initialized = {};
  var executedOnce = {};
  var loadedSources = {};
  var ui = { notice: false, modal: false, confirming: false, opener: null };
  var uid = 0;

  function getDefaultConsent(service) {
    if (service.required) return true;
    if (service.default !== undefined) return service.default;
    return !!cfg.default;
  }

  function effectiveConsent(name) {
    var service = services[name];
    if (service && service.required) return true;
    if (temporary[name]) return true;
    if (!consents[name]) return false;
    var optOut = service ? service.optOut : false;
    return confirmed || !!optOut;
  }

  function dependsOn(service) {
    return service && service.dependsOn ? service.dependsOn : [];
  }

  function updateConsent(name, value) {
    var service = services[name];
    if (service && service.required) value = true;
    var didChange = !!consents[name] !== value;
    consents[name] = value;
    if (value) {
      dependsOn(service).forEach(function (dep) {
        if (!consents[dep]) updateConsent(dep, true);
      });
    } else {
      serviceOrder.forEach(function (other) {
        if (dependsOn(services[other]).indexOf(name) !== -1 && consents[other]) updateConsent(other, false);
      });
    }
    return didChange;
  }

  function changeAll(value) {
    var count = 0;
    serviceOrder.forEach(function (name) {
      var service = services[name];
      if (service.contextualOnly) return;
      if (updateConsent(name, service.required || value)) count++;
    });
    return count;
  }

  function checkConsents() {
    if (!stored) return;
    var complete = true;
    Object.keys(consents).forEach(function (name) {
      if (!services[name]) delete consents[name];
    });
    serviceOrder.forEach(function (name) {
      if (!(name in consents)) {
        consents[name] = getDefaultConsent(services[name]);
        complete = false;
      }
    });
    confirmed = complete;
    changed = !complete;
    savedConsents = assign({}, consents);
  }

  /* ---------------------------------------------------------- consent log */

  function randomId() {
    try {
      if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
      var bytes = new Uint8Array(16);
      window.crypto.getRandomValues(bytes);
      return [].map
        .call(bytes, function (byte) {
          return (byte + 256).toString(16).slice(1);
        })
        .join("");
    } catch (error) {
      return String(Date.now()) + Math.random().toString(36).slice(2, 10);
    }
  }

  // short fingerprint of the service list, so a log entry says which setup the visitor saw
  function configHash() {
    var text = configSignature || "";
    var hash = 5381;
    for (var i = 0; i < text.length; i++) hash = ((hash << 5) + hash + text.charCodeAt(i)) | 0;
    return (hash >>> 0).toString(36);
  }

  function consentId() {
    if (!stored) return "";
    if (!stored.id) {
      stored.id = randomId();
      store.set(stored);
    }
    return stored.id;
  }

  // Sent from the browser when a decision is made. No IP address, no page URL:
  // the log server only stores what is in this payload plus the origin it came from.
  function sendLog(type, id) {
    if (!cfg.consentLog || !id) return;
    var payload = {
      id: id,
      time: new Date().toISOString(),
      type: type,
      consents: assign({}, consents),
      config: configHash(),
      language: html.getAttribute("data-cmp-language") || "",
      engine: VERSION,
    };
    var body = JSON.stringify(payload);
    log("consent log", payload);
    try {
      // text/plain keeps it a simple request, so no preflight and no blocked decision
      if (navigator.sendBeacon && navigator.sendBeacon(cfg.consentLog, new Blob([body], { type: "text/plain" }))) return;
    } catch (error) {}
    try {
      fetch(cfg.consentLog, { method: "POST", body: body, headers: { "Content-Type": "text/plain" }, keepalive: true, mode: "cors" }).catch(function () {});
    } catch (error) {}
  }

  // The consent ID is the only text the engine writes into the page, so it waits
  // for the first interaction or the dialog opening. A framework hydrates the
  // markup it rendered on the server, and text changed while that runs breaks it.
  var interacted = false;

  function renderConsentId() {
    if (!interacted && !ui.modal) return;
    var id = stored && stored.id ? stored.id : "";
    each("[data-cmp-consent-id]", function (el) {
      if (el.textContent !== id) el.textContent = id;
    });
  }

  ["pointerdown", "keydown", "touchstart"].forEach(function (type) {
    doc.addEventListener(
      type,
      function () {
        if (interacted) return;
        interacted = true;
        renderConsentId();
      },
      { capture: true, passive: true }
    );
  });

  function saveConsents(type) {
    var changes = {};
    Object.keys(consents).forEach(function (name) {
      if (savedConsents[name] !== consents[name]) changes[name] = consents[name];
    });
    stored = { id: (stored && stored.id) || randomId(), consents: assign({}, consents), timestamp: new Date().toISOString(), version: 1 };
    store.set(stored);
    sendLog(type, stored.id);
    renderConsentId();
    confirmed = true;
    changed = false;
    temporary = {};
    savedConsents = assign({}, consents);
    if (cfg.dataLayer) {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: "cmp_consent", cmp_type: type, cmp_consents: assign({}, consents) });
    }
    emit("save", { type: type, consents: assign({}, consents), changes: changes });
  }

  /* ------------------------------------------------------ service registry */

  function readServices() {
    var rows = doc.querySelectorAll("[data-cmp-service-def]");
    var items = doc.querySelectorAll("[data-cmp-service-item]");
    if (!rows.length && !items.length) return false;
    var next = {};
    var order = [];

    function define(name, row) {
      if (!name) return null;
      if (!next[name]) {
        order.push(name);
        next[name] = {
          name: name,
          purposes: [],
          required: false,
          default: undefined,
          optOut: false,
          onlyOnce: false,
          contextualOnly: false,
          cookies: [],
          dependsOn: [],
        };
      }
      var service = next[name];
      if (row && !service.defined) {
        service.defined = true;
        service.required = bool(row, "data-cmp-required") || false;
        service.default = bool(row, "data-cmp-default");
        service.optOut = bool(row, "data-cmp-opt-out") || false;
        service.onlyOnce = bool(row, "data-cmp-only-once") || false;
        service.contextualOnly = bool(row, "data-cmp-contextual-only") || false;
        service.cookies = words(row.getAttribute("data-cmp-cookies"));
        service.dependsOn = words(row.getAttribute("data-cmp-depends-on"));
      }
      return service;
    }

    function addPurposes(service, list) {
      list.forEach(function (purpose) {
        if (purpose && service.purposes.indexOf(purpose) === -1) service.purposes.push(purpose);
      });
    }

    // technical definitions (service registry)
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      var service = define(row.getAttribute("data-cmp-service-def"), row);
      if (!service) continue;
      var purposeEl = row.closest("[data-cmp-purpose]");
      addPurposes(service, words(row.getAttribute("data-cmp-purposes")).concat(purposeEl ? [purposeEl.getAttribute("data-cmp-purpose")] : []));
    }
    // purpose membership from the (translated) preferences UI
    for (var j = 0; j < items.length; j++) {
      var item = define(items[j].getAttribute("data-cmp-service-item"));
      var group = items[j].closest("[data-cmp-purpose]");
      if (item && group) addPurposes(item, [group.getAttribute("data-cmp-purpose")]);
    }
    order.forEach(function (name) {
      delete next[name].defined;
    });

    var signature = JSON.stringify(next);
    if (signature === configSignature) return false;
    configSignature = signature;
    services = next;
    serviceOrder = order;
    hasDefinitions = true;
    if (stored) {
      checkConsents();
    } else {
      serviceOrder.forEach(function (name) {
        if (!(name in consents)) consents[name] = getDefaultConsent(services[name]);
      });
      savedConsents = assign({}, consents);
    }
    log("services", services);
    return true;
  }

  /* ---------------------------------------------------- element activation */

  var SWAP_ATTRS = ["src", "srcset", "href", "poster", "data"];

  function runScript(original) {
    var src = original.getAttribute("data-src") || original.getAttribute("src");
    if (src) {
      if (loadedSources[src]) return null;
      loadedSources[src] = true;
    }
    var script = doc.createElement("script");
    for (var i = 0; i < original.attributes.length; i++) {
      var attr = original.attributes[i];
      if (/^(type|src|data-src|data-type|data-cmp-state|data-cmp-service|data-cmp-on|data-cmp-id)$/.test(attr.name)) continue;
      script.setAttribute(attr.name, attr.value);
    }
    var type = original.getAttribute("data-type");
    if (type) script.type = type;
    if (original.nonce) script.nonce = original.nonce;
    if (src) script.src = src;
    else script.text = original.text || original.textContent || "";
    script.setAttribute("data-cmp-internal", "");
    script.setAttribute("data-cmp-for", original.getAttribute("data-cmp-service") || "");
    doc.head.appendChild(script);
    return script;
  }

  function elementId(el) {
    var id = el.getAttribute("data-cmp-id");
    if (!id) {
      id = "cmp" + ++uid;
      el.setAttribute("data-cmp-id", id);
    }
    return id;
  }

  function removeGenerated(el) {
    each('[data-cmp-generated="' + elementId(el) + '"]', function (node) {
      node.parentNode && node.parentNode.removeChild(node);
    });
  }

  function markGenerated(node, el) {
    if (node.nodeType === 1) {
      node.setAttribute("data-cmp-generated", elementId(el));
      node.setAttribute("data-cmp-internal", "");
    }
    return node;
  }

  function stampTemplate(template) {
    var fragment = template.content.cloneNode(true);
    var scripts = [];
    each(
      "script",
      function (script) {
        scripts.push(script);
        script.parentNode.removeChild(script);
      },
      fragment
    );
    var nodes = [].slice.call(fragment.childNodes);
    var anchor = template;
    nodes.forEach(function (node) {
      if (node.nodeType === 3 && !node.textContent.trim()) return;
      if (node.nodeType !== 1) return;
      markGenerated(node, template);
      anchor.parentNode.insertBefore(node, anchor.nextSibling);
      anchor = node;
    });
    scripts.forEach(function (script) {
      var copy = runScript(script);
      if (copy) markGenerated(copy, template);
    });
  }

  // React may re-create the children of an HTML Embed (e.g. right after
  // hydration) without remounting the embed itself. Remember what was applied
  // per container + element signature so re-created nodes are not re-executed.
  var containerMemo = typeof WeakMap === "function" ? new WeakMap() : null;

  function elementMemo(el) {
    var parent = el.parentNode;
    if (!containerMemo || !parent) return null;
    var memo = containerMemo.get(parent);
    if (!memo) containerMemo.set(parent, (memo = {}));
    var index = 0;
    var node = el;
    var name = el.getAttribute("data-cmp-service");
    while ((node = node.previousElementSibling)) {
      if (node.tagName === el.tagName && node.getAttribute("data-cmp-service") === name) index++;
    }
    var key = [el.tagName, name, el.getAttribute("data-cmp-on") || "", index].join("|");
    return memo[key] || (memo[key] = {});
  }

  function setElementState(el, granted) {
    var name = el.getAttribute("data-cmp-service");
    var service = services[name];
    var state = granted ? "granted" : "denied";
    var tag = el.tagName;
    var memo = elementMemo(el) || {};
    if (memo.id && !el.hasAttribute("data-cmp-id")) el.setAttribute("data-cmp-id", memo.id);
    var previous = el.getAttribute("data-cmp-state") || memo.state;
    if (el.getAttribute("data-cmp-state") !== state) el.setAttribute("data-cmp-state", state);
    memo.state = state;
    memo.id = elementId(el);

    if (previous === state) {
      // same logical element re-rendered: restore side effects that lived inside it
      if (tag === "TEMPLATE" && granted && !doc.querySelector('[data-cmp-generated="' + memo.id + '"]')) stampTemplate(el);
      if (tag !== "SCRIPT" && tag !== "TEMPLATE" && tag !== "LINK") swapAttributes(el, granted);
      return;
    }
    if (tag === "SCRIPT") {
      var trigger = el.getAttribute("data-cmp-on") || "accept";
      var shouldRun = trigger === "decline" ? !granted : granted;
      if (!shouldRun) {
        if (!granted) removeGenerated(el);
        return;
      }
      if (trigger === "accept" && service && service.onlyOnce) {
        if (executedOnce[name]) return;
        executedOnce[name] = true;
      }
      var copy = runScript(el);
      if (copy && trigger === "accept") markGenerated(copy, el);
      return;
    }

    if (tag === "TEMPLATE") {
      removeGenerated(el);
      if (granted) {
        if (service && service.onlyOnce && executedOnce[name + ":" + elementId(el)]) return;
        executedOnce[name + ":" + elementId(el)] = true;
        stampTemplate(el);
      }
      return;
    }

    if (tag === "LINK") {
      removeGenerated(el);
      if (granted && el.getAttribute("data-href")) {
        var link = doc.createElement("link");
        for (var i = 0; i < el.attributes.length; i++) {
          var attr = el.attributes[i];
          if (/^(href|data-href|data-cmp-state|data-cmp-service|data-cmp-id)$/.test(attr.name)) continue;
          link.setAttribute(attr.name, attr.value);
        }
        link.href = el.getAttribute("data-href");
        doc.head.appendChild(markGenerated(link, el));
      }
      return;
    }

    swapAttributes(el, granted);
  }

  // iframes, images, media and any other element with data-src / data-href / …
  function swapAttributes(el, granted) {
    var tag = el.tagName;
    var changed = false;
    SWAP_ATTRS.forEach(function (attr) {
      var value = el.getAttribute("data-" + attr);
      if (value === null) return;
      if (granted) {
        if (el.getAttribute(attr) !== value) {
          el.setAttribute(attr, value);
          changed = true;
        }
      } else if (tag === "IFRAME" && attr === "src") {
        if (el.hasAttribute("src") && el.getAttribute("src") !== "about:blank") {
          el.setAttribute("src", "about:blank");
          changed = true;
        }
      } else if (el.hasAttribute(attr)) {
        el.removeAttribute(attr);
        changed = true;
      }
    });
    if (changed && (tag === "SOURCE" || tag === "TRACK")) {
      var media = el.parentElement;
      if (media && typeof media.load === "function") media.load();
    }
  }

  function updateServiceStorage(name) {
    var service = services[name];
    if (!service || !service.cookies.length) return;
    var names = cookieNames();
    service.cookies.forEach(function (pattern) {
      var regex = pattern.charAt(0) === "^" ? new RegExp(pattern) : new RegExp("^" + escapeRegex(pattern) + "$");
      names.forEach(function (cookie) {
        if (cookie !== cfg.storageName && regex.test(cookie)) {
          log("deleting cookie", cookie);
          deleteCookie(cookie);
        }
      });
    });
  }

  function applyConsents() {
    serviceOrder.forEach(function (name) {
      if (!initialized[name]) {
        initialized[name] = true;
        emit("init", { service: services[name] });
      }
      var consent = effectiveConsent(name);
      if (serviceStates[name] !== consent) {
        serviceStates[name] = consent;
        if (!consent) updateServiceStorage(name);
        emit("service", { name: name, consent: consent, service: services[name] });
      }
    });
    each("[data-cmp-service]", function (el) {
      if (isInternal(el)) return;
      setElementState(el, effectiveConsent(el.getAttribute("data-cmp-service")));
    });
    updateConsentMode();
  }

  /* ------------------------------------------------- Google Consent Mode v2 */

  var lastConsentMode = "";

  function gtag() {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(arguments);
  }

  function consentModeState(useEffective) {
    var state = {};
    Object.keys(cfg.consentMode).forEach(function (key) {
      var names = [].concat(cfg.consentMode[key]);
      var granted = names.some(function (name) {
        return useEffective ? effectiveConsent(name) : false;
      });
      state[key] = granted ? "granted" : "denied";
    });
    return state;
  }

  function initConsentMode() {
    if (!cfg.consentMode) return;
    var defaults = assign(consentModeState(false), { wait_for_update: 500 }, cfg.consentModeDefaults || {});
    gtag("consent", "default", defaults);
    if (stored) updateConsentMode();
  }

  function updateConsentMode() {
    if (!cfg.consentMode) return;
    var state = consentModeState(true);
    var signature = JSON.stringify(state);
    if (signature === lastConsentMode) return;
    lastConsentMode = signature;
    gtag("consent", "update", state);
  }

  /* --------------------------------------------------------------------- UI */

  function setRootAttr(name, value) {
    if (value === null || value === false) {
      if (html.hasAttribute(name)) html.removeAttribute(name);
    } else if (html.getAttribute(name) !== String(value)) {
      html.setAttribute(name, String(value));
    }
  }

  // noNotice without mustConsent: consent is only asked in context (gates, settings link)
  function contextualOnly() {
    return !!cfg.noNotice && !cfg.mustConsent;
  }

  function renderRoot() {
    setRootAttr("data-cmp", configReady ? "ready" : "loading");
    setRootAttr("data-cmp-mode", contextualOnly() ? "contextual" : null);
    setRootAttr("data-cmp-open", ui.modal ? "modal" : ui.notice ? "notice" : null);
    setRootAttr("data-cmp-confirmed", confirmed ? "true" : "false");
    setRootAttr("data-cmp-changed", changed ? "true" : null);
    setRootAttr("data-cmp-confirming", ui.confirming ? "true" : null);
  }

  function purposeServices(purpose) {
    return serviceOrder.filter(function (name) {
      return services[name].purposes.indexOf(purpose) !== -1;
    });
  }

  function setToggle(input, names) {
    var togglable = names.filter(function (name) {
      return !services[name].required;
    });
    var on = togglable.filter(function (name) {
      return consents[name];
    }).length;
    var checked = togglable.length === 0 || on === togglable.length;
    var mixed = on > 0 && on < togglable.length;
    if (input.checked !== checked) input.checked = checked;
    if (input.indeterminate !== mixed) input.indeterminate = mixed;
    if (input.disabled !== (togglable.length === 0)) input.disabled = togglable.length === 0;
    if (mixed) input.setAttribute("aria-checked", "mixed");
    else if (input.getAttribute("aria-checked") === "mixed") input.removeAttribute("aria-checked");
  }

  function renderToggles() {
    each("input[data-cmp-toggle]", function (input) {
      var parts = input.getAttribute("data-cmp-toggle").split(":");
      var kind = parts[0];
      var key = parts.slice(1).join(":");
      if (kind === "service" && services[key]) setToggle(input, [key]);
      else if (kind === "purpose") setToggle(input, purposeServices(key));
      else if (kind === "all") setToggle(input, serviceOrder);
    });
    each("[data-cmp-purpose]", function (el) {
      var names = purposeServices(el.getAttribute("data-cmp-purpose"));
      var required = names.length > 0 && names.every(function (name) {
        return services[name].required;
      });
      el.setAttribute("data-cmp-required", required ? "true" : "false");
    });
  }

  function renderGates() {
    each("[data-cmp-gate],[data-cmp-status]", function (el) {
      var name = el.getAttribute("data-cmp-gate") || el.getAttribute("data-cmp-status");
      var state = effectiveConsent(name) ? "granted" : "denied";
      var previous = el.getAttribute("data-cmp-state");
      if (previous === state) return;
      el.setAttribute("data-cmp-state", state);
      // revoked while a native player (React-managed iframe) is loaded: stop it
      if (previous === "granted" && el.getAttribute("data-cmp-gate-mode") === "interaction") {
        each(
          "[data-cmp-gate-content] iframe",
          function (frame) {
            if (frame.getAttribute("src") !== "about:blank") frame.setAttribute("src", "about:blank");
          },
          el
        );
      }
    });
  }

  var ROW_CONDITIONS = { required: 1, "not-required": 1, "opt-out": 1, granted: 1, denied: 1 };

  function rowFlags(el) {
    var row = el.closest("[data-cmp-service-item],[data-cmp-purpose],[data-cmp-status],[data-cmp-gate]");
    if (!row) return null;
    var names;
    if (row.hasAttribute("data-cmp-service-item")) names = [row.getAttribute("data-cmp-service-item")];
    else if (row.hasAttribute("data-cmp-purpose")) names = purposeServices(row.getAttribute("data-cmp-purpose"));
    else names = [row.getAttribute("data-cmp-status") || row.getAttribute("data-cmp-gate")];
    var known = names.filter(function (name) {
      return services[name];
    });
    return {
      required: known.length > 0 && known.every(function (name) {
        return services[name].required;
      }),
      "opt-out": known.some(function (name) {
        return services[name].optOut && !services[name].required;
      }),
      granted: names.length > 0 && names.every(effectiveConsent),
    };
  }

  function renderConditions() {
    renderConsentId();
    each("[data-cmp-if]", function (el) {
      var conditions = words(el.getAttribute("data-cmp-if")).filter(function (c) {
        return ROW_CONDITIONS[c];
      });
      if (!conditions.length) return;
      var flags = rowFlags(el);
      var show =
        !!flags &&
        conditions.every(function (c) {
          if (c === "not-required") return !flags.required;
          if (c === "denied") return !flags.granted;
          return flags[c];
        });
      if (show === el.hasAttribute("data-cmp-hidden")) {
        if (show) el.removeAttribute("data-cmp-hidden");
        else el.setAttribute("data-cmp-hidden", "");
      }
    });
  }

  /* ------------------------------------------------------------- language */

  var languageStyle = doc.createElement("style");
  languageStyle.setAttribute("data-cmp-language", "");
  (doc.head || html).appendChild(languageStyle);

  function cleanLanguage(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/_/g, "-")
      .replace(/[^a-z0-9-]/g, "");
  }

  function resolveLanguages() {
    var lang = cleanLanguage(html.getAttribute("lang"));
    var primary = lang.split("-")[0];
    var wanted = lang && lang !== primary ? [lang, primary] : [primary];
    if (doc.readyState === "loading") return wanted; // translations may still be streaming in
    var available = [];
    each("[data-cmp-lang]", function (el) {
      var code = cleanLanguage(el.getAttribute("data-cmp-lang"));
      if (code && available.indexOf(code) === -1) available.push(code);
    });
    if (!available.length) return wanted;
    for (var i = 0; i < wanted.length; i++) if (available.indexOf(wanted[i]) !== -1) return [wanted[i]];
    for (var j = 0; j < available.length; j++) if (available[j].split("-")[0] === primary) return [available[j]];
    var fallback = cleanLanguage(cfg.fallbackLanguage);
    return [available.indexOf(fallback) !== -1 ? fallback : available[0]];
  }

  function renderLanguage() {
    var languages = resolveLanguages().filter(Boolean);
    var css =
      "[data-cmp-lang]" +
      languages
        .map(function (code) {
          return ':not([data-cmp-lang="' + code + '" i])';
        })
        .join("") +
      "{display:none!important}";
    if (languageStyle.textContent !== css) languageStyle.textContent = css;
    setRootAttr("data-cmp-language", languages[0] || null);
  }

  var FOCUSABLE =
    'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),summary,[tabindex]:not([tabindex="-1"])';

  function visible(el) {
    return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  }

  function modalDialog() {
    var modals = doc.querySelectorAll("[data-cmp-modal]:not([data-cmp-preview] *)");
    var first = null;
    for (var i = 0; i < modals.length; i++) {
      var dialog = modals[i].querySelector("[data-cmp-dialog]") || modals[i];
      if (visible(dialog)) return dialog;
      first = first || dialog;
    }
    return first;
  }

  function focusModal() {
    var dialog = modalDialog();
    if (!dialog || dialog.contains(doc.activeElement)) return;
    if (!dialog.hasAttribute("tabindex")) dialog.setAttribute("tabindex", "-1");
    try {
      dialog.focus({ preventScroll: true });
    } catch (error) {
      dialog.focus();
    }
  }

  var syncQueued = false;

  function sync() {
    syncQueued = false;
    if (doc.readyState === "loading") {
      // service rows may still be streaming in: only paint what storage already tells us
      renderRoot();
      renderLanguage();
      renderGates();
      return;
    }
    var definitionsChanged = readServices();
    if (!configReady) {
      configReady = true;
      if (!hasDefinitions) {
        // no consent UI on this page: fall back to the stored decisions
        Object.keys(consents).forEach(function (name) {
          if (!services[name]) {
            services[name] = { name: name, purposes: [], cookies: [], dependsOn: [] };
            serviceOrder.push(name);
          }
        });
      }
      openInitial();
      applyConsents();
      emit("ready", api.getConsents());
    } else {
      if (definitionsChanged) openInitial();
      applyConsents();
    }
    renderRoot();
    renderLanguage();
    renderGates();
    renderToggles();
    renderConditions();
    renderConditions();
    if (ui.modal) focusModal();
  }

  function queueSync() {
    if (syncQueued) return;
    syncQueued = true;
    Promise.resolve().then(sync);
  }

  function openInitial() {
    if (confirmed) return;
    if (cfg.mustConsent) ui.modal = true;
    else if (!cfg.noNotice) ui.notice = true;
  }

  function openModal(opener) {
    ui.opener = opener || doc.activeElement;
    ui.modal = true;
    renderRoot();
    renderToggles();
    renderConsentId();
    focusModal();
    emit("modal", { open: true });
  }

  function closeModal() {
    if (!ui.modal) return;
    if (cfg.mustConsent && !confirmed) return;
    if (confirmed) {
      consents = assign({}, savedConsents);
      ui.notice = false;
    }
    ui.modal = false;
    renderRoot();
    renderToggles();
    var opener = ui.opener;
    ui.opener = null;
    if (opener && opener.isConnected && typeof opener.focus === "function") opener.focus();
    emit("modal", { open: false });
  }

  function closeAll() {
    var wasModal = ui.modal;
    var opener = ui.opener;
    ui.notice = false;
    ui.modal = false;
    ui.confirming = false;
    ui.opener = null;
    renderRoot();
    if (wasModal) {
      if (opener && opener.isConnected && typeof opener.focus === "function") opener.focus();
      emit("modal", { open: false });
    }
  }

  function decide(value, type, source) {
    var inModal = ui.modal && source && source.closest && source.closest("[data-cmp-modal]");
    var wasConfirmed = confirmed;
    var count = value === null ? 0 : changeAll(value);
    saveConsents(type);
    applyConsents();
    renderGates();
    renderToggles();
    renderConditions();
    if (value !== null && !wasConfirmed && (inModal || cfg.mustConsent) && count > 0 && cfg.confirmDelay > 0) {
      ui.confirming = true;
      renderRoot();
      setTimeout(closeAll, cfg.confirmDelay);
    } else {
      closeAll();
    }
  }

  /* ------------------------------------------ interaction-mode Consent Gates */
  // The gate content (e.g. Webstudio's native YouTube or Vimeo component) stays
  // visible. The first interaction is held back until the visitor allows the
  // service, then replayed.

  var pendingInteraction = typeof WeakMap === "function" ? new WeakMap() : null;

  function interactionGate(node) {
    var gate = node && node.closest && node.closest('[data-cmp-gate][data-cmp-gate-mode="interaction"]');
    if (!gate || effectiveConsent(gate.getAttribute("data-cmp-gate"))) return null;
    if (node.closest("[data-cmp-gate-notice]")) return null;
    return node.closest("[data-cmp-gate-content]") ? gate : null;
  }

  function requestGate(gate, target) {
    if (pendingInteraction) pendingInteraction.set(gate, target);
    gate.setAttribute("data-cmp-requested", "");
    var notice = gate.querySelector("[data-cmp-gate-notice]");
    var focusable = notice && notice.querySelector("button, a[href]");
    if (focusable) {
      try {
        focusable.focus({ preventScroll: true });
      } catch (error) {
        focusable.focus();
      }
    }
    emit("gate", { name: gate.getAttribute("data-cmp-gate"), requested: true });
  }

  function releaseGate(gate, replay) {
    if (!gate || !gate.hasAttribute("data-cmp-requested")) return;
    gate.removeAttribute("data-cmp-requested");
    var target = pendingInteraction && pendingInteraction.get(gate);
    if (pendingInteraction) pendingInteraction.delete(gate);
    if (!target || !target.isConnected) return;
    if (replay) {
      // let React commit consent-dependent state first, then continue the original action
      setTimeout(function () {
        target.click();
      }, 0);
    } else if (typeof target.focus === "function") {
      target.focus();
    }
  }

  ["click", "auxclick"].forEach(function (type) {
    doc.addEventListener(
      type,
      function (event) {
        var gate = interactionGate(event.target);
        if (!gate) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        requestGate(gate, event.target.closest("button, a, [role='button']") || event.target);
      },
      true
    );
  });

  function acceptContextual(name, always, source) {
    if (!name) return;
    updateConsent(name, true);
    // without a notice there is no first decision to wait for: "always" saves right away
    if (always && (confirmed || contextualOnly())) {
      var keep = assign({}, temporary);
      saveConsents("contextual-accept");
      temporary = keep;
      delete temporary[name];
    } else {
      temporary[name] = true;
      dependsOn(services[name]).forEach(function (dep) {
        temporary[dep] = true;
      });
    }
    applyConsents();
    renderRoot();
    renderGates();
    renderToggles();
    renderConditions();
    var gate = source && source.closest && source.closest("[data-cmp-gate]");
    if (gate) releaseGate(gate, true);
  }

  function resetConsents() {
    if (stored && stored.id) sendLog("reset", stored.id);
    store.remove();
    stored = null;
    consents = {};
    serviceOrder.forEach(function (name) {
      consents[name] = getDefaultConsent(services[name]);
    });
    savedConsents = assign({}, consents);
    confirmed = false;
    changed = false;
    temporary = {};
    applyConsents();
    renderConsentId();
    ui.modal = false;
    openInitial();
    renderRoot();
    renderGates();
    renderToggles();
    renderConditions();
  }

  /* ------------------------------------------------------ DOM interactions */

  function gateName(el) {
    var explicit = el.getAttribute("data-cmp-name");
    if (explicit) return explicit;
    var gate = el.closest("[data-cmp-gate]");
    return gate ? gate.getAttribute("data-cmp-gate") : null;
  }

  doc.addEventListener("click", function (event) {
    var target = event.target.closest && event.target.closest("[data-cmp-action]");
    if (!target) return;
    var action = target.getAttribute("data-cmp-action");
    if (target.tagName === "A" || target.tagName === "BUTTON") event.preventDefault();
    switch (action) {
      case "accept-all":
        return decide(true, "accept", target);
      case "decline-all":
        return decide(false, "decline", target);
      case "save":
        return decide(null, "save", target);
      case "open-modal":
      case "show":
        return openModal(target);
      case "close":
        return closeModal();
      case "accept-once":
        return acceptContextual(gateName(target), false, target);
      case "accept-always":
        return acceptContextual(gateName(target), true, target);
      case "dismiss":
        return releaseGate(target.closest("[data-cmp-gate]"), false);
      case "reset":
        return resetConsents();
    }
  });

  doc.addEventListener("change", function (event) {
    var input = event.target;
    if (!input.matches || !input.matches("input[data-cmp-toggle]")) return;
    var parts = input.getAttribute("data-cmp-toggle").split(":");
    var key = parts.slice(1).join(":");
    var names = parts[0] === "service" ? [key] : parts[0] === "purpose" ? purposeServices(key) : serviceOrder;
    names.forEach(function (name) {
      if (services[name] && !services[name].required) updateConsent(name, input.checked);
    });
    renderToggles();
    emit("change", assign({}, consents));
  });

  doc.addEventListener("keydown", function (event) {
    if (!ui.modal && event.key === "Escape") {
      var requested = event.target.closest && event.target.closest("[data-cmp-gate][data-cmp-requested]");
      if (requested) releaseGate(requested, false);
      return;
    }
    if (!ui.modal) return;
    if (event.key === "Escape") {
      closeModal();
      return;
    }
    if (event.key !== "Tab") return;
    var dialog = modalDialog();
    if (!dialog) return;
    var items = [].filter.call(dialog.querySelectorAll(FOCUSABLE), visible);
    if (!items.length) return;
    var first = items[0];
    var last = items[items.length - 1];
    if (!dialog.contains(doc.activeElement)) {
      event.preventDefault();
      first.focus();
    } else if (event.shiftKey && (doc.activeElement === first || doc.activeElement === dialog)) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && doc.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  // Keep focus inside the open modal. Other dialogs (for example a Radix Sheet
  // whose close button opened the modal) restore focus to their trigger after
  // closing; that element becomes the fallback opener for when the modal closes.
  // Refocusing is deferred (the other dialog may still hold its own focus trap
  // while it closes) and capped, so two traps never bounce focus forever.
  var refocus = { count: 0, since: 0, queued: false };
  doc.addEventListener("focusin", function (event) {
    if (!ui.modal) return;
    var dialog = modalDialog();
    if (!dialog || dialog.contains(event.target)) return;
    if (!(ui.opener && ui.opener.isConnected) && event.target !== doc.body) ui.opener = event.target;
    var now = Date.now();
    if (now - refocus.since > 1000) {
      refocus.since = now;
      refocus.count = 0;
    }
    if (refocus.queued || ++refocus.count > 10) return;
    refocus.queued = true;
    setTimeout(function () {
      refocus.queued = false;
      if (ui.modal) focusModal();
    }, 0);
  });

  // Webstudio remounts page content on client-side navigation. Watch the whole
  // document and re-sync whenever consent-related nodes appear.
  var RELEVANT =
    "[data-cmp-service],[data-cmp-service-def],[data-cmp-service-item],[data-cmp-gate],[data-cmp-status],[data-cmp-toggle],[data-cmp-if],[data-cmp-lang],[data-cmp-modal],[data-cmp-notice],[data-cmp-consent-id]";

  new MutationObserver(function (mutations) {
    for (var i = 0; i < mutations.length; i++) {
      var added = mutations[i].addedNodes;
      for (var j = 0; j < added.length; j++) {
        var node = added[j];
        if (node.nodeType !== 1 || isInternal(node)) continue;
        if ((node.matches && node.matches(RELEVANT)) || (node.querySelector && node.querySelector(RELEVANT))) {
          queueSync();
          return;
        }
      }
    }
  }).observe(html, { childList: true, subtree: true });

  // client-side navigation between pages of different languages updates <html lang>
  new MutationObserver(function () {
    renderLanguage();
    if (ui.modal) focusModal();
  }).observe(html, { attributes: true, attributeFilter: ["lang"] });

  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", sync);

  /* -------------------------------------------------------------------- API */

  var api = {
    __engine: true,
    version: VERSION,
    config: cfg,
    show: function () {
      if (!configReady) sync();
      openModal();
    },
    showNotice: function () {
      ui.notice = true;
      renderRoot();
    },
    hide: closeAll,
    getConsent: effectiveConsent,
    getLanguage: function () {
      return html.getAttribute("data-cmp-language");
    },
    getConsents: function () {
      var result = {};
      serviceOrder.forEach(function (name) {
        result[name] = effectiveConsent(name);
      });
      return result;
    },
    isConfirmed: function () {
      return confirmed;
    },
    getConsentId: function () {
      return consentId();
    },
    getServices: function () {
      return serviceOrder.map(function (name) {
        return assign({}, services[name]);
      });
    },
    setConsent: function (name, value, save) {
      updateConsent(name, !!value);
      if (save !== false) saveConsents("api");
      applyConsents();
      renderRoot();
      renderGates();
      renderToggles();
    },
    acceptAll: function () {
      decide(true, "accept");
    },
    declineAll: function () {
      decide(false, "decline");
    },
    save: function () {
      decide(null, "save");
    },
    reset: resetConsents,
    refresh: sync,
    on: on,
    off: off,
  };

  window.cmp = api;

  // Early, flash-free first paint: decide the open state from storage before
  // the body is parsed; the service list is validated on DOMContentLoaded.
  initConsentMode();
  openInitial();
  renderRoot();
  renderLanguage();
  if (doc.readyState !== "loading") sync();
})();
