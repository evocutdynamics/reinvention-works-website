#!/usr/bin/env python3
"""
Reinvention Works - go-live switch.

Flips the site from STAGING (reinvention-works-website.netlify.app, noindex)
to PRODUCTION (reinventionworksonline.com, indexable). Run it ONCE, on cutover
day, after DNS points at Netlify. It is safe to re-run.

  python3 _migration/go_live.py --check            # report only, change nothing
  python3 _migration/go_live.py                    # switch to production
  python3 _migration/go_live.py --gtm GTM-XXXXXXX  # ...and install Google Tag Manager
  python3 _migration/go_live.py --ga4 G-XXXXXXXXXX # ...or GA4 directly (if no GTM)

What it changes:
  1. Every staging URL -> https://reinventionworksonline.com (canonicals, Open Graph,
     JSON-LD, sitemap.xml, llms.txt).
  2. Removes <meta name="robots" content="noindex, nofollow"> from every page.
  3. robots.txt -> allow all crawlers (incl. AI crawlers, a deliberate choice) + Sitemap line.
  4. netlify.toml -> removes the sitewide X-Robots-Tag: noindex header.
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
User-agent: OAI-SearchBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /

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
    a = ap.parse_args()
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
                s = s.replace("<head>", "<head>\n" + h, 1)
                s = re.sub(r"(<body[^>]*>)", r"\1\n" + b.replace("\\", "\\\\"), s, count=1); stats["tags_added"] += 1
            elif a.ga4 and "gtag/js?id=" not in s:
                s = s.replace("<head>", "<head>\n" + ga4_snippet(a.ga4), 1); stats["tags_added"] += 1
        if s != o and not a.check: p.write_text(s, encoding="utf-8")

    robots = ROOT / "robots.txt"
    robots_needs = "Disallow: /\n" in robots.read_text() or "Sitemap:" not in robots.read_text()
    toml = ROOT / "netlify.toml"; t = toml.read_text()
    toml_needs = bool(XROBOTS.search(t))
    if not a.check:
        if robots_needs: robots.write_text(ROBOTS_TXT)
        if toml_needs: toml.write_text(XROBOTS.sub("", t))

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
