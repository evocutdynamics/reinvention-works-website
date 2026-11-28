#!/usr/bin/env python3
"""
Builds approved articles from Markdown into the site's article template.

Each article lives in _migration/articles/ as two files, copied exactly as approved:
    <slug>.md       the article text (published word for word)
    <slug>.seo.md   the SEO fields file (SEO title, meta description, tags, JSON-LD)

To publish a new article, add both files, add an entry to ARTICLES below, and run:
    python3 _migration/build_articles.py
Then add it to sitemap.xml, llms.txt and the resources listing (see README).

The page chrome (head, header, footer) is copied from the existing pillar article,
so new articles always match the site's current template and accessibility features.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_migration" / "articles"
PROD = "https://reinventionworksonline.com"
TEMPLATE = ROOT / "who-am-i-now-identity-after-disability" / "index.html"

ARTICLES = [
    dict(slug="adjusting-to-a-new-disability", date="2026-12-01", date_label="December 1, 2026",
         section="Adjusting to Disability", image="adjusting-to-a-new-disability",
         alt="Illustration of a house blueprint. A dashed outline shows where the kitchen used to be, "
             "and a gold arrow points to the kitchen's new spot in a different room."),
    dict(slug="disability-grief-grieving-a-life-youre-still-living", date="2026-12-01", date_label="December 1, 2026",
         section="Adjusting to Disability", image="disability-grief",
         alt="Illustration of a dining table with two place settings. A solid chair sits at one end, "
             "and a dashed outline of a matching chair sits at the other."),
    dict(slug="how-to-accept-a-disability-without-pretending-youre-fine", date="2026-12-01", date_label="December 1, 2026",
         section="Adjusting to Disability", image="accept-a-disability",
         alt="Illustration of a camera on a tripod, with a dashed arrow showing it turning toward "
             "a sunrise over green hills and a winding path."),
]

e = lambda s: html.escape(s, quote=True)


def inline(text):
    """Markdown inline -> HTML. Text is escaped, never reworded."""
    out, i = [], 0
    pat = re.compile(r"\[([^\]]+)\]\(([^)]+)\)|\*\*(.+?)\*\*|\*(.+?)\*")
    for m in pat.finditer(text):
        out.append(e(text[i:m.start()]))
        if m.group(1) is not None:
            out.append(f'<a class="text-link" href="{e(m.group(2))}">{inline(m.group(1))}</a>')
        elif m.group(3) is not None:
            out.append(f"<strong>{inline(m.group(3))}</strong>")
        else:
            out.append(f"<em>{inline(m.group(4))}</em>")
        i = m.end()
    out.append(e(text[i:]))
    return "".join(out)


def md_to_html(md):
    lines = md.strip("\n").split("\n")
    assert lines[0].startswith("# "), "first line must be the # title"
    title = lines[0][2:].strip()
    blocks = [b.strip() for b in "\n".join(lines[1:]).split("\n\n") if b.strip()]
    body, dek = [], None
    for n, b in enumerate(blocks):
        assert "\n" not in b, f"unexpected multi-line block: {b[:60]}"
        if b == "---":
            body.append('<hr class="article-rule">')
        elif b.startswith("## "):
            body.append(f"<h2>{inline(b[3:])}</h2>")
        elif b.startswith("### "):
            body.append(f"<h3>{inline(b[4:])}</h3>")
        elif n == 0 and b.startswith("*") and b.endswith("*"):
            dek = b.strip("*")
            body.append(f'<p class="lede">{inline(b)}</p>')
        else:
            body.append(f"<p>{inline(b)}</p>")
    return title, dek, "\n\n".join(body)


def seo_fields(text):
    def field(label):
        m = re.search(r"^" + re.escape(label) + r"[^:]*:\s*(.+)$", text, re.M)
        assert m, f"missing SEO field: {label}"
        return m.group(1).strip()
    ld = json.loads(re.search(r"```json\n(.*?)\n```", text, re.S).group(1))
    return dict(title=field("SEO title"), description=field("Meta description"), slug=field("URL slug"),
                tags=[t.strip() for t in field("Tags").split("·")], jsonld=ld)


tpl = TEMPLATE.read_text()
head_tpl = tpl.split("<main id=\"main\">")[0]
foot_tpl = tpl.split("</main>", 1)[1]

for a in ARTICLES:
    md = (SRC / f"{a['slug']}.md").read_text()
    seo = seo_fields((SRC / f"{a['slug']}.seo.md").read_text())
    assert seo["slug"] == a["slug"], (seo["slug"], a["slug"])
    title, dek, body = md_to_html(md)
    url = f"{PROD}/{a['slug']}/"
    img = f"{PROD}/assets/resources/{a['image']}.jpg"

    # JSON-LD exactly as approved, plus the featured image so the article is eligible for rich results.
    ld = json.loads(json.dumps(seo["jsonld"]))
    post = next(x for x in ld if x["@type"] == "BlogPosting")
    assert post["datePublished"] == a["date"] and post["url"] == url
    post["image"] = img
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{PROD}/"},
        {"@type": "ListItem", "position": 2, "name": "Resources", "item": f"{PROD}/resources/"},
        {"@type": "ListItem", "position": 3, "name": title, "item": url}]}
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    head = head_tpl
    head = re.sub(r"<title>.*?</title>", f"<title>{e(seo['title'])}</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(seo["description"])}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    head = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', head)
    head = head.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
    head = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(title)}">', head)
    head = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(seo["description"])}">', head)
    head = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{img}">', head)
    head = re.sub(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{e(a["alt"])}">', head)
    head = re.sub(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{img}">', head)
    tags = "".join(f'<meta property="article:tag" content="{e(t)}">' for t in seo["tags"])
    head = head.replace('<meta name="twitter:card"',
                        f'<meta property="article:published_time" content="{a["date"]}">{tags}\n<meta name="twitter:card"', 1)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  f'<script type="application/ld+json">{js(ld)}</script>\n<script type="application/ld+json">{js(crumbs)}</script>',
                  head, flags=re.S)
    for check in (e(seo["title"]), url, img):
        assert check in head, check

    main = f'''<main id="main">
<article aria-labelledby="article-title">
<section class="block" style="padding-bottom:0">
  <div class="wrap">
    <div class="eyebrow"><a href="/resources/" class="text-link">Resources</a> &middot; {e(a["section"])}</div>
    <h1 id="article-title" style="max-width:20ch">{inline(title)}</h1>
    <p class="article-meta"><span><time datetime="{a["date"]}">{a["date_label"]}</time></span> <span aria-hidden="true">&middot;</span> <span>Shay Edmonds</span></p>
  </div>
</section>
<section class="block" style="padding-top:24px">
  <div class="wrap">
    <div class="article-hero-img"><picture><source type="image/webp" srcset="/assets/resources/{a["image"]}-600.webp 600w, /assets/resources/{a["image"]}.webp 1200w" sizes="(max-width: 760px) 100vw, 760px"><img fetchpriority="high" width="1200" height="630" src="/assets/resources/{a["image"]}.jpg" alt="{e(a["alt"])}" loading="eager" decoding="async"></picture></div>
    <div class="article-body">
{body}
    </div>
    <p class="article-disclaimer">Peer-led education written by Shay Edmonds. It is not therapy, medical care, or crisis support. If you are in crisis, call or text <a href="tel:988">988</a>, or call <a href="tel:911">911</a>. <a href="/resources/">See more resources</a> or <a href="/first-move/">start with Your First Move</a>.</p>
  </div>
</section>
</article>
'''
    out_dir = ROOT / a["slug"]
    out_dir.mkdir(exist_ok=True)
    (out_dir / "index.html").write_text(head + main + "</main>" + foot_tpl)
    a["title"], a["dek"] = title, dek
    print("wrote", a["slug"])
