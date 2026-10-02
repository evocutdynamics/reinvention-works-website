# _migration (not public: netlify.toml returns 404 for /_migration/*)

| File | What it is |
|---|---|
| `old_wordpress_urls.txt` | Every address on the old WordPress site (taken 2026-10-02 from its sitemaps): 42 posts, 12 pages, 6 categories, 65 tags, feeds, authors, sitemaps, plugin URLs. |
| `redirect_test.py` | `python3 _migration/redirect_test.py _migration/old_wordpress_urls.txt` checks each old address lands on a live page under the rules in netlify.toml. Expected: all resolve except 4 `/wpa-stats-type/` URLs (intentional 410 Gone). |
| `go_live.py` | Cutover switch. `--check` first, then run without flags (add `--gtm GTM-XXXX` or `--ga4 G-XXXX` when the IDs are known). Switches canonicals/sitemap/JSON-LD to https://reinventionworksonline.com, removes noindex (meta, header, robots.txt). Safe to re-run. |

Canonical host: **https://reinventionworksonline.com** (no www), matching the live WordPress site so existing rankings carry over.
