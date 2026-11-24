#!/usr/bin/env python3
"""
Builds /interviews/index.html (Shay Edmonds: Interviews and Podcast Appearances).

To add an episode or a clip, edit EPISODES below and run:
    python3 _migration/build_interviews.py

Rights rules (from Shay):
  - A full episode may be embedded from the host's own YouTube upload, with credit.
  - Clips appear ONLY when the host gave permission (clips_ok=True) AND the clip
    has a live YouTube link. Never guess a link.
Videos load only when the visitor presses Play (privacy + page speed).
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://reinvention-works-website.netlify.app"  # go_live.py swaps to the production domain
PLAYLIST_URL = None  # [NEEDS: playlist link] "Shay Edmonds: Interviews and Podcast Appearances"
CTA_URL = "/reset/#join"

# Newest first (date each host posted the episode on YouTube).
EPISODES = [
    dict(
        id="UMPWnsymiGY", show="Together We Rise", hosts="Rochelle and Alisha Schwartz",
        title="If Your Life Were a Movie, What Would This Chapter Be Called?",
        date_label="November 2026", upload="2026-11-22T20:32:31-08:00", seconds=2061,
        summary="How a major life disruption affects identity, relationships and confidence, and what you can build from where you are now. For anyone whose life has been upended and who is asking who they are now.",
        clips_ok=False, clips=[]),
    dict(
        id="il0EQZNaGII", show="Find Your Way on New Cleveland Radio", hosts="Karen Hale and Kristy Anderson",
        title="Reinvent Yourself with Shay",
        date_label="November 19, 2026", upload="2026-11-19T13:30:21-08:00", seconds=2853,
        summary="On this show about grief: rebuilding a life after disability and a major disruption, and the question all the medical care never asked: who am I going to be now? Helpful for anyone grieving a life that has changed, and for the families beside them.",
        clips_ok=True, clips=[
            dict(id="H6nCmY0Ky70", title="Nobody asked who I was going to be", seconds=48,
                 upload="2026-11-23T14:17:38-08:00"),
            dict(id="al0pHAs-TW4", title="When help takes away your confidence", seconds=60,
                 upload="2026-11-24T09:17:30-08:00"),
            # Approved, link not live yet (one a day from Nov 25): "Grieving a life I'm still living",
            # "Families grieve too, quietly", "Stacking failures", "Change where the camera is pointing".
        ]),
    dict(
        id="wNXAsrjSXhM", show="Famous Interviews", hosts="Joe Dimino",
        title="Shay Edmonds on Reinvention, Overcoming Life Challenges and Stopping Self-Sabotage",
        date_label="November 17, 2026", upload="2026-11-17T17:42:05-08:00", seconds=977,
        summary="Losing most of your vision as an adult, and the gap between treatment and building a life you want afterwards. Also covers the book Stop the Self Sabotage and the patterns that hold people back. For anyone whose life has taken an unexpected turn.",
        clips_ok=False, clips=[]),
    dict(
        id="44EM7XbWwjg", show="The Inclusive Dad Podcast", hosts="Aaron DeVries",
        title="Episode 226: Your Disability Changed Your Life. It Didn't End Your Possibilities!",
        date_label="November 10, 2026", upload="2026-11-10T01:00:08-08:00", seconds=2521,
        summary="Losing independence to vision loss, and how it touches relationships, dating, parenting and learning to ask for help. Also, how the stories we tell ourselves can keep us playing small. Helpful for people rebuilding after disability, and for families who want to understand inclusion.",
        clips_ok=True, clips=[
            # Approved, link not live yet: "Not blind, not sighted", "Asking for help made my life bigger",
            # "My son's play-by-play", "My blueprint was missing the kitchen",
            # "Where to begin when your old life is gone", "A group anyone can join".
        ]),
    dict(
        id="yYK21hwRwIk", show="Reclaim Your Energy After 50", hosts="John Curran",
        title="When the Old You No Longer Fits: Reinventing Yourself and Finding What's Next",
        date_label="November 3, 2026", upload="2026-11-03T11:11:30-08:00", seconds=1331,
        summary="Becoming legally blind and rethinking independence, career and relationships, and letting go of self-sabotaging beliefs. For people over 50 facing a life transition or wondering what comes next.",
        clips_ok=False, clips=[]),
    dict(
        id="VqomfAubyAM", show="Healthy Mind, Healthy Life", hosts="Avik",
        title="Rebuilding Identity After Life Disruption: You Are Not Broken, You Are Unfinished",
        date_label="October 30, 2026", upload="2026-10-30T17:39:46-07:00", seconds=1492,
        summary="The question that arrives when the appointments end: who am I now? Why healing the body and rebuilding a sense of self are two different journeys, and how a new blueprint and small daily steps help. For anyone whose life has been rewritten by a health change or disability.",
        clips_ok=False, clips=[]),
]

e = lambda s: html.escape(s, quote=True)


def mins(sec):
    m = round(sec / 60)
    return f"{m} minutes" if sec >= 90 else f"{sec} seconds"


def iso_dur(sec):
    return f"PT{sec // 60}M{sec % 60}S"


def player(vid, label, sec, short=False):
    cls = "yt yt-short" if short else "yt"
    return (f'<div class="{cls}" data-yt="{e(vid)}" data-title="{e(label)}">'
            f'<button type="button" class="yt-play" aria-label="Play {e(label[0].lower() + label[1:])} ({mins(sec)})">'
            f'<img src="https://i.ytimg.com/vi/{e(vid)}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy" decoding="async">'
            f'<span class="yt-icon" aria-hidden="true"></span>'
            f'<span class="yt-label" aria-hidden="true">Play &middot; {mins(sec)}</span></button></div>')


def credit(ep, link_text):
    return (f'<p class="credit">Originally recorded for {e(ep["show"])} with {e(ep["hosts"])}. '
            f'Full episode: <a href="https://youtu.be/{e(ep["id"])}" target="_blank" rel="noopener noreferrer">'
            f'{e(link_text)} on YouTube (opens in new tab)</a></p>')


sections, videos = [], []
for i, ep in enumerate(EPISODES, 1):
    hid = f"ep-{ep['id']}"
    label = f"Full episode: {ep['show']} with {ep['hosts']}"
    out = [f'<section class="episode" aria-labelledby="{hid}">',
           f'<p class="ep-meta">{e(ep["show"])} &middot; with {e(ep["hosts"])} &middot; {e(ep["date_label"])}</p>',
           f'<h2 id="{hid}">{e(ep["title"])}</h2>',
           f'<p>{e(ep["summary"])}</p>',
           player(ep["id"], label, ep["seconds"]),
           credit(ep, f'"{ep["title"]}"')]
    clips = ep["clips"] if ep["clips_ok"] else []
    if clips:
        out.append(f'<h3 id="{hid}-clips">Clips from this episode</h3><ul class="clip-list" aria-labelledby="{hid}-clips">')
        for c in clips:
            out.append(f'<li><h4>{e(c["title"])}</h4>'
                       + player(c["id"], f'Clip: {c["title"]}, from {ep["show"]}', c["seconds"], short=True)
                       + credit(ep, f'"{ep["title"]}"') + '</li>')
            videos.append(dict(id=c["id"], name=f'{c["title"]} | Shay Edmonds on {ep["show"]}',
                               desc=f'A short clip of Shay Edmonds from {ep["show"]} with {ep["hosts"]}.',
                               upload=c["upload"], sec=c["seconds"]))
        out.append('</ul>')
    out.append('</section>')
    sections.append("\n".join(out))
    videos.append(dict(id=ep["id"], name=ep["title"], desc=ep["summary"], upload=ep["upload"], sec=ep["seconds"]))

playlist = (f'<a class="text-link" href="{e(PLAYLIST_URL)}" target="_blank" rel="noopener noreferrer">Watch the full playlist on YouTube: Shay Edmonds: Interviews and Podcast Appearances (opens in new tab)</a>'
            if PLAYLIST_URL else '')

TITLE = "Podcasts and Interviews: Shay Edmonds | Reinvention Works"
DESC = ("Watch Reinvention Works founder Shay Edmonds on podcasts and shows about rebuilding "
        "identity after disability, vision loss and major life change.")

graph = [
    {"@type": "CollectionPage", "@id": f"{SITE}/interviews/#webpage", "url": f"{SITE}/interviews/",
     "name": "Interviews and Podcast Appearances with Shay Edmonds", "description": DESC, "inLanguage": "en-US",
     "isPartOf": {"@id": f"{SITE}/#website"}, "publisher": {"@id": f"{SITE}/#organization"}},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Interviews", "item": f"{SITE}/interviews/"}]},
] + [{"@type": "VideoObject", "name": v["name"], "description": v["desc"],
      "thumbnailUrl": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", "uploadDate": v["upload"],
      "duration": iso_dur(v["sec"]), "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}",
      "url": f"https://www.youtube.com/watch?v={v['id']}"} for v in videos]

head = (ROOT / "speaking/index.html").read_text().split("<main id=\"main\">")[0]
foot = (ROOT / "speaking/index.html").read_text().split("</main>", 1)[1]
head = head.replace("Speaking and Training | Shay Edmonds | Reinvention Works", TITLE)
head = head.replace("Book Shay Edmonds, a legally blind founder and author, for keynotes, workshops and podcasts on disability inclusion, resilience and reinvention.", DESC)
head = head.replace("/speaking/", "/interviews/")
head = head.replace('<a href="/interviews/">Podcasts</a>', '<a href="/interviews/" aria-current="page">Podcasts</a>', 1)
head = re.sub(r'<script type="application/ld\+json">.*?</script>',
              '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":")).replace("&", "\\u0026") + '</script>',
              head, flags=re.S)
assert head.count(TITLE) == 2 and head.count(DESC) >= 2 and "/speaking/" not in head

main = f'''<main id="main">
<section class="page-hero">
  <div class="wrap">
    <div class="eyebrow" style="color:var(--gold)">Interviews &amp; podcast</div>
    <h1>Interviews and podcast appearances.</h1>
    <p class="lede">Reinvention Works founder Shay Edmonds talks honestly about losing his sight, rebuilding who he is, and how Reinvention Works helps people start again after disability or a major health change.</p>
    {('<p class="playlist on-dark">' + playlist + '</p>') if playlist else ''}
  </div>
</section>
<section class="block">
  <div class="wrap episodes">
    <p class="note">Newest first. Each video plays only when you press its Play button, and nothing plays on its own.</p>
{chr(10).join(sections)}
  </div>
</section>
<section class="block alt" aria-labelledby="cta-title">
  <div class="wrap">
    <h2 id="cta-title" class="cta-line">Rebuilding life after disability or a major health change?</h2>
    <p class="lede">The ideas in these conversations are the foundation of the 3-Day Reinvention Reset from Reinvention Works.</p>
    <div class="btn-row"><a class="btn btn-primary" href="{CTA_URL}">Join the free 3-Day Reinvention Reset</a></div>
  </div>
</section>
'''
out = head + main + "</main>" + foot
(ROOT / "interviews").mkdir(exist_ok=True)
(ROOT / "interviews/index.html").write_text(out)
print("wrote interviews/index.html with", len(EPISODES), "episodes and",
      sum(len(x["clips"]) for x in EPISODES if x["clips_ok"]), "clips")
