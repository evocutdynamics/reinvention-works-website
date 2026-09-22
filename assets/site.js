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

  if (!dismissedRecently()) setTimeout(open, DELAY_MS);
})();
