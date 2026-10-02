#!/usr/bin/env python3
"""
Reinvention Works - go-live switch.

Flips the site from STAGING (reinvention-works-website.netlify.app, noindex)
to PRODUCTION (reinventionworksonline.com, indexable). Safe to re-run.

Normally you do NOT run this by hand: netlify.toml runs `go_live.py --ci` on every
build. It only switches when BOTH are true:
  - the build is Netlify's production context (CONTEXT=production), and
  - the Netlify environment variable GO_LIVE is set to 1.
Deploy previews / branch deploys always stay noindex. Optional env vars: GTM_ID or GA4_ID.
Set GO_LIVE=1 and deploy BEFORE switching DNS, so Google never sees a noindex
version of the real domain.

  python3 _migration/go_live.py --check            # report only, change nothing
  python3 _migration/go_live.py                    # switch to production
  python3 _migration/go_live.py --gtm GTM-XXXXXXX  # ...and install Google Tag Manager
  python3 _migration/go_live.py --ga4 G-XXXXXXXXXX # ...or GA4 directly (if no GTM)

What it changes:
  1. Every staging URL -> https://reinventionworksonline.com (canonicals, Open Graph,
     JSON-LD, sitemap.xml, llms.txt).
  2. Removes <meta name="robots" content="noindex, nofollow"> from every page.
  3. robots.txt -> allow all crawlers (incl. AI crawlers, a deliberate choice) + Sitemap line.
  4. _headers -> removes the sitewide X-Robots-Tag: noindex header (Netlify reads _headers after the build).
  5. Optional: inserts GTM or GA4 on every page.
"""
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STAGING = "https://reinvention-works-website.netlify.app"
PROD = "https://reinventionworksonline.com"
ROBOTS_META = re.compile(r'\s*<meta name="robots" content="noindex, nofollow">')
XROBOTS = re.compile(r'\n\s*X-Robots-Tag = "noindex, nofollow"')

ROBOTS_TXT = f"""# Reinvention Works - production robots.txt
# Search engines and AI assistants are welcome (deliberate choice: we want
# Shay's work found and cited accurately).
User-agent: *
Allow: /
Disallow: /_migration/

User-agent: GPTBot
Allow: /
Disallow: /_migration/
User-agent: OAI-SearchBot
Allow: /
Disallow: /_migration/
User-agent: ClaudeBot
Allow: /
Disallow: /_migration/
User-agent: PerplexityBot
Allow: /
Disallow: /_migration/
User-agent: Google-Extended
Allow: /
Disallow: /_migration/
User-agent: Applebot-Extended
Allow: /
Disallow: /_migration/

Sitemap: {PROD}/sitemap.xml
"""

def gtm_snippets(gid):
    head = ("<!-- Google Tag Manager -->\n<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),"
            "dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
            f"f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{gid}');</script>\n<!-- End Google Tag Manager -->")
    body = (f'<!-- Google Tag Manager (noscript) --><noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gid}" '
            'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript><!-- End Google Tag Manager (noscript) -->')
    return head, body

def ga4_snippet(gid):
    return (f'<!-- Google tag (gtag.js) -->\n<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>\n'
            f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{gid}');</script>")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--gtm")
    ap.add_argument("--ga4")
    ap.add_argument("--ci", action="store_true", help="Netlify build mode: switch only if CONTEXT=production and GO_LIVE=1")
    a = ap.parse_args()
    if a.ci:
        import os
        ctx, live = os.environ.get("CONTEXT", ""), os.environ.get("GO_LIVE", "")
        if not (ctx == "production" and live == "1"):
            print(f"go_live.py --ci: staying in STAGING mode (CONTEXT={ctx or 'unset'}, GO_LIVE={live or 'unset'})")
            return
        a.gtm = a.gtm or os.environ.get("GTM_ID") or None
        a.ga4 = a.ga4 or os.environ.get("GA4_ID") or None
    if a.gtm and a.ga4: sys.exit("Use GTM or GA4, not both (put GA4 inside GTM).")
    if a.gtm and not re.fullmatch(r"GTM-[A-Z0-9]+", a.gtm): sys.exit("GTM ID looks wrong (expected GTM-XXXXXXX)")
    if a.ga4 and not re.fullmatch(r"G-[A-Z0-9]+", a.ga4): sys.exit("GA4 ID looks wrong (expected G-XXXXXXXXXX)")

    files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in (".html", ".xml", ".txt", ".webmanifest")
             and "_migration" not in p.parts and ".git" not in p.parts]
    stats = {"files_with_staging_urls": 0, "staging_urls": 0, "noindex_meta": 0, "tags_added": 0}
    for p in files:
        s = p.read_text(encoding="utf-8"); o = s
        n = s.count(STAGING)
        if n: stats["files_with_staging_urls"] += 1; stats["staging_urls"] += n
        s = s.replace(STAGING, PROD)
        if p.suffix == ".html":
            s, k = ROBOTS_META.subn("", s); stats["noindex_meta"] += k
            if a.gtm and "googletagmanager.com/gtm.js" not in s:
                h, b = gtm_snippets(a.gtm)
                s = re.sub(r'(<meta name="viewport"[^>]*>)', lambda m: m.group(1) + "\n" + h, s, count=1)
                s = re.sub(r"(<body[^>]*>)", r"\1\n" + b.replace("\\", "\\\\"), s, count=1); stats["tags_added"] += 1
            elif a.ga4 and "gtag/js?id=" not in s:
                s = re.sub(r'(<meta name="viewport"[^>]*>)', lambda m: m.group(1) + "\n" + ga4_snippet(a.ga4), s, count=1); stats["tags_added"] += 1
        if s != o and not a.check: p.write_text(s, encoding="utf-8")

    robots = ROOT / "robots.txt"
    robots_needs = "Disallow: /\n" in robots.read_text() or "Sitemap:" not in robots.read_text()
    hdr = ROOT / "_headers"
    toml_needs = hdr.exists() and "X-Robots-Tag" in hdr.read_text()
    if not a.check:
        if robots_needs: robots.write_text(ROBOTS_TXT)
        if toml_needs: hdr.write_text("# Production: no noindex header.\n")
        # Send the old staging address to the real domain (Netlify reads _redirects after the build,
        # and it takes precedence over netlify.toml rules).
        rd = ROOT / "_redirects"
        line = f"{STAGING}/*  {PROD}/:splat  301!\n"
        if not rd.exists() or line not in rd.read_text():
            rd.write_text((rd.read_text() if rd.exists() else "") + line)

    if not a.check:
        left = [str(p.relative_to(ROOT)) for p in files if STAGING in p.read_text(encoding="utf-8") or ROBOTS_META.search(p.read_text(encoding="utf-8"))]
        if left or "Disallow: /\n" in robots.read_text() or (hdr.exists() and "X-Robots-Tag" in hdr.read_text()):
            sys.exit(f"go_live.py FAILED: staging URL or noindex still present in {left[:5]}")
    mode = "CHECK (nothing changed)" if a.check else "APPLIED"
    print(f"go_live.py - {mode}")
    print(f"  staging URLs -> production : {stats['staging_urls']} in {stats['files_with_staging_urls']} files")
    print(f"  noindex meta tags removed  : {stats['noindex_meta']}")
    verb = "will change" if a.check else "changed"
    print(f"  robots.txt -> production   : {verb if robots_needs else 'already done'}")
    print(f"  X-Robots-Tag noindex header: {('will be removed' if a.check else 'removed') if toml_needs else 'already gone'}")
    print(f"  analytics tags added       : {stats['tags_added']}" + ("" if (a.gtm or a.ga4) else "  (no --gtm/--ga4 given)"))

if __name__ == "__main__":
    main()
