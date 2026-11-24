/* Reinvention Works — nav toggle + newsletter pop-up (First Move GHL form). Storage wrapped in try/catch. */
(function () {
  var FORM = "https://api.reinventionworksonline.com/widget/form/5P9QEHNjigDUcJymygdV";
  var KEY = "rw_nl_dismissed_v1", DAYS = 14, DELAY_MS = 3500;

  // mobile nav
  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("site-nav");
  if (btn && nav) btn.addEventListener("click", function () {
    var o = nav.classList.toggle("open"); btn.setAttribute("aria-expanded", o ? "true" : "false");
  });

  // pop-up
  var bd = document.getElementById("nl-backdrop");
  if (!bd) return;
  var dlg = bd.querySelector(".nl"), closeBtn = bd.querySelector(".nl-close"), lastFocus = null, loaded = false;

  function dismissedRecently() {
    try { var t = parseInt(localStorage.getItem(KEY), 10); return t && (Date.now() - t) < DAYS * 864e5; } catch (e) { return false; }
  }
  function remember() { try { localStorage.setItem(KEY, String(Date.now())); } catch (e) {} }
  function focusables() { return dlg.querySelectorAll('a[href],button,iframe,input,select,textarea,[tabindex]:not([tabindex="-1"])'); }

  function open() {
    if (bd.classList.contains("show")) return;
    lastFocus = document.activeElement;
    if (!loaded) {
      var f = document.getElementById("nl-frame"), st = document.getElementById("nl-status");
      f.addEventListener("load", function () { st.textContent = ""; });
      f.src = FORM; loaded = true;
      setTimeout(function () { if (st.textContent) st.textContent = "The form is taking a moment. If it does not appear, use the link below to open it in a new tab."; }, 6000);
    }
    bd.classList.add("show"); document.body.style.overflow = "hidden";
    closeBtn.focus();
  }
  function close() {
    bd.classList.remove("show"); document.body.style.overflow = ""; remember();
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  closeBtn.addEventListener("click", close);
  var skip = document.getElementById("nl-skip"); if (skip) skip.addEventListener("click", close);
  bd.addEventListener("click", function (e) { if (e.target === bd) close(); });
  document.addEventListener("keydown", function (e) {
    if (!bd.classList.contains("show")) return;
    if (e.key === "Escape") { close(); return; }
    if (e.key === "Tab") {
      var f = focusables(); if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  // "Join the newsletter" links anywhere can reopen it
  document.querySelectorAll("[data-open-newsletter]").forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); open(); });
  });

  // Don't stack the sign-up pop-up on top of the cookie banner: wait until a cookie choice is made.
  // Pages that carry their own sign-up offer (e.g. /reset/) opt out of the automatic pop-up with
  // <body data-no-auto-popup>. "Join the newsletter" links still open it on request.
  function schedule() {
    if (document.body.hasAttribute("data-no-auto-popup")) return;
    if (!dismissedRecently()) setTimeout(open, DELAY_MS);
  }
  if (!window.rwConsentDecided || window.rwConsentDecided()) schedule();
  else document.addEventListener("rw:consent", schedule, { once: true });
})();

/* 2026-11-18 Conversion events for Google Analytics 4 (G-R2H9HJ5858).
   GTM's GA4 tag does not forward custom events, so key events are sent with a separate,
   page-view-free gtag instance on its own data layer ("rwGaLayer").
   Respects the cookie banner: nothing loads or sends unless the visitor allowed analytics.
   Events: generate_lead (GHL form submitted) and booking_click (booking calendar link clicked).
   Add ?rwdebug=1 to a page URL to log form-iframe messages in the browser console. */
(function () {
  var GA = "G-R2H9HJ5858", L = "rwGaLayer", started = false;
  var DEBUG = /[?&]rwdebug=1/.test(location.search);
  var FORMS = {
    "5P9QEHNjigDUcJymygdV": "first_move_signup",
    "yCD3hqVo8IlTAfF0vOmH": "reset_founding_application",
    "LbVI2dF2Nsz8x8XBtkYm": "referral_partnership"
  };
  var CALENDARS = { "rws-discovery-call": "individual_discovery", "shay-b2b-discovery": "organization_discovery" };
  window[L] = window[L] || [];
  function g() { window[L].push(arguments); }
  function granted() {
    try { var c = JSON.parse(localStorage.getItem("rw_consent_v1")); return !!(c && c.a); } catch (e) { return false; }
  }
  g("consent", "default", { analytics_storage: "denied", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });
  g("js", new Date());
  g("config", GA, { send_page_view: false });
  function start() {
    if (started || !granted()) return;
    started = true;
    g("consent", "update", { analytics_storage: "granted" });
    var s = document.createElement("script");
    s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA + "&l=" + L;
    document.head.appendChild(s);
  }
  function send(name, params) {
    if (!granted()) return;
    start();
    params = params || {};
    params.page_path = location.pathname;
    params.transport_type = "beacon";
    g("event", name, params);
    if (DEBUG) console.log("[rw-analytics]", name, params);
  }
  start();
  document.addEventListener("rw:consent", start);

  // Form submissions from the GoHighLevel form iframes
  var sent = [];
  function formNameFor(win) {
    var frames = document.querySelectorAll("iframe");
    for (var i = 0; i < frames.length; i++) {
      if (frames[i].contentWindow === win) {
        var m = (frames[i].src || "").match(/widget\/form\/([A-Za-z0-9]+)/);
        return { el: frames[i], name: m ? (FORMS[m[1]] || "form_" + m[1]) : "form_unknown" };
      }
    }
    return null;
  }
  window.addEventListener("message", function (e) {
    if (!/reinventionworksonline\.com|leadconnectorhq\.com|msgsndr\.com/.test(e.origin || "")) return;
    var raw; try { raw = typeof e.data === "string" ? e.data : JSON.stringify(e.data); } catch (x) { return; }
    if (DEBUG) console.log("[rw-analytics] message", e.origin, raw && raw.slice(0, 300));
    if (!/set-sticky-contacts|form-?submit|formSubmitted|form_submitted/i.test(raw || "")) return;
    var f = formNameFor(e.source); if (!f || sent.indexOf(f.el) > -1) return;
    sent.push(f.el);
    send("generate_lead", { form_name: f.name });
  });

  // Clicks on booking-calendar links
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href*="/widget/bookings/"]') : null;
    if (!a) return;
    var m = a.href.match(/widget\/bookings\/([a-z0-9-]+)/i);
    send("booking_click", { calendar: m ? (CALENDARS[m[1]] || m[1]) : "unknown", link_text: (a.textContent || "").trim().slice(0, 80) });
  });
})();

/* Click-to-play YouTube (interviews page). Nothing loads from YouTube until the visitor presses Play. */
(function () {
  document.addEventListener("click", function (e) {
    var btn = e.target && e.target.closest ? e.target.closest(".yt-play") : null;
    if (!btn) return;
    var box = btn.parentNode, id = box.getAttribute("data-yt"), title = box.getAttribute("data-title");
    if (!/^[\w-]{11}$/.test(id || "")) return;
    var f = document.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
    f.title = title;
    f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    f.allowFullscreen = true;
    f.setAttribute("tabindex", "0");
    box.innerHTML = "";
    box.appendChild(f);
    box.classList.add("yt-on");
    f.focus();
    if (window.gtag) window.gtag("event", "video_play", { video_title: title });
  });
})();
