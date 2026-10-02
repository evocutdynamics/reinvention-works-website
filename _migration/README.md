# _migration (not public: netlify.toml returns 404 for /_migration/*)

| File | What it is |
|---|---|
| `old_wordpress_urls.txt` | Every address on the old WordPress site (taken 2026-10-02 from its sitemaps): 42 posts, 12 pages, 6 categories, 65 tags, feeds, authors, sitemaps, plugin URLs. |
| `redirect_test.py` | `python3 _migration/redirect_test.py _migration/old_wordpress_urls.txt` checks each old address lands on a live page under the rules in netlify.toml. Expected: all resolve except 4 `/wpa-stats-type/` URLs (intentional 410 Gone). |
| `go_live.py` | Cutover switch, run automatically by Netlify on every build (`--ci`). It flips to production ONLY when the build is the production context AND the Netlify env var `GO_LIVE=1` (optional `GTM_ID` or `GA4_ID`). Switches canonicals/sitemap/JSON-LD to https://reinventionworksonline.com and removes noindex (meta, header, robots.txt); fails the build if anything is left. Previews stay noindex. Set GO_LIVE=1 and deploy BEFORE changing DNS. |

Canonical host: **https://reinventionworksonline.com** (no www), matching the live WordPress site so existing rankings carry over.
