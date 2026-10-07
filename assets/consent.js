/* Reinvention Works - cookie consent banner (Google Consent Mode v2).
   Defaults (set inline in <head> before any Google tag): analytics + ads DENIED until the visitor chooses.
   Choice stored in localStorage "rw_consent_v1" as {a:bool, m:bool, t:timestamp}. Storage wrapped in try/catch. */
(function () {
  var KEY = "rw_consent_v1";
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }

  function read() { try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; } }
  function apply(c) {
    gtag("consent", "update", {
      analytics_storage: c.a ? "granted" : "denied",
      ad_storage: c.m ? "granted" : "denied",
      ad_user_data: c.m ? "granted" : "denied",
      ad_personalization: c.m ? "granted" : "denied"
    });
    window.dataLayer.push({ event: "rw_consent_update", rw_analytics: c.a, rw_marketing: c.m });
  }
  function save(a, m) {
    var c = { a: !!a, m: !!m, t: Date.now() };
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {}
    apply(c); hide();
    try { document.dispatchEvent(new CustomEvent("rw:consent", { detail: c })); } catch (e) {}
  }

  var el = document.createElement("section");
  el.className = "cc";
  el.setAttribute("aria-label", "Cookie choices");
  el.innerHTML =
    '<div class="cc-in">' +
      '<div class="cc-text"><h2 class="cc-title">Your privacy, your choice</h2>' +
      '<p>We use essential cookies to run this site. With your permission, we also use analytics cookies to learn which pages help people, and marketing cookies to measure our outreach. ' +
      'See our <a href="/privacy-policy/">Privacy Policy</a>.</p>' +
      '<fieldset class="cc-opts" hidden><legend>Choose which cookies to allow</legend>' +
        '<label><input type="checkbox" checked disabled> Essential (always on)</label>' +
        '<label><input type="checkbox" id="cc-a"> Analytics</label>' +
        '<label><input type="checkbox" id="cc-m"> Marketing</label>' +
      '</fieldset></div>' +
      '<div class="cc-btns">' +
        '<button type="button" class="btn btn-primary" data-cc="all">Accept all</button>' +
        '<button type="button" class="btn btn-ghost" data-cc="none">Reject non-essential</button>' +
        '<button type="button" class="cc-link" data-cc="choose" aria-expanded="false">Choose cookies</button>' +
        '<button type="button" class="btn btn-ghost" data-cc="save" hidden>Save my choices</button>' +
      '</div>' +
    '</div>';

  function show() {
    if (!el.parentNode) document.body.appendChild(el);
    var c = read();
    el.querySelector("#cc-a").checked = !!(c && c.a);
    el.querySelector("#cc-m").checked = !!(c && c.m);
    el.classList.add("show");
  }
  function hide() { el.classList.remove("show"); }

  el.addEventListener("click", function (e) {
    var b = e.target.closest("[data-cc]"); if (!b) return;
    var k = b.getAttribute("data-cc");
    if (k === "all") save(true, true);
    else if (k === "none") save(false, false);
    else if (k === "save") save(el.querySelector("#cc-a").checked, el.querySelector("#cc-m").checked);
    else if (k === "choose") {
      var f = el.querySelector(".cc-opts"), s = el.querySelector('[data-cc="save"]');
      var open = f.hasAttribute("hidden");
      if (open) { f.removeAttribute("hidden"); s.removeAttribute("hidden"); } else { f.setAttribute("hidden", ""); s.setAttribute("hidden", ""); }
      b.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) el.querySelector("#cc-a").focus();
    }
  });

  // Footer "Cookie preferences" links reopen the banner.
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-cookie-prefs]"); if (!a) return;
    e.preventDefault(); show();
    var f = el.querySelector(".cc-opts"); f.removeAttribute("hidden");
    el.querySelector('[data-cc="save"]').removeAttribute("hidden");
    el.querySelector('[data-cc="choose"]').setAttribute("aria-expanded", "true");
    el.querySelector("#cc-a").focus();
  });

  window.rwConsentDecided = function () { return !!read(); };
  if (!read()) {
    if (document.body) show(); else document.addEventListener("DOMContentLoaded", show);
  }
})();
