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
        id="il0EQZNaGII", apple="https://podcasts.apple.com/us/podcast/reinvent-yourself-with-shay-fyw-11126-36-griefjourney/id1592360677?i=1000803005794", spotify="https://open.spotify.com/episode/4Bjp3wN5Fc8PXBkM0BCVlr", show="Find Your Way on New Cleveland Radio", hosts="Karen Hale and Kristy Anderson",
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
        id="wNXAsrjSXhM", apple="https://podcasts.apple.com/us/podcast/shay-edmonds-on-reinvention-overcoming-life-challenges/id1660256991?i=1000802707516", spotify="https://open.spotify.com/episode/1dkBUn3d0K8urg1hB2WkOw", show="Famous Interviews", hosts="Joe Dimino",
        title="Shay Edmonds on Reinvention, Overcoming Life Challenges and Stopping Self-Sabotage",
        date_label="November 17, 2026", upload="2026-11-17T17:42:05-08:00", seconds=977,
        summary="Losing most of your vision as an adult, and the gap between treatment and building a life you want afterwards. Also covers the book Stop the Self Sabotage and the patterns that hold people back. For anyone whose life has taken an unexpected turn.",
        clips_ok=False, clips=[]),
    dict(
        id=None, show="Peek Inside Podcast", hosts='Lyanne Richardson',
        title='Rebuilding Life After Loss: Self-Worth, Identity and Resilience',
        date_label="November 14, 2026", upload="2026-11-14", seconds=1740, apple="https://podcasts.apple.com/us/podcast/rebuilding-life-after-loss-self-worth-identity-and/id6805653818?i=1000801974802", spotify="https://open.spotify.com/episode/0BBQMQWzP7ZcUtvIzozcZt",
        summary='Losing eyesight, career, marriage and confidence, and the question that followed: who am I now? How self-worth, resilience and changing your personal story help you move forward after loss.',
        clips_ok=False, clips=[]),
    dict(
        id=None, show="The Elisha Show", hosts='Elisha Arowojobe',
        title='Rebuilding Your Life After Disability: Finding Purpose Again',
        date_label="November 10, 2026", upload="2026-11-10", seconds=1320, apple="https://podcasts.apple.com/us/podcast/rebuilding-your-life-after-disability-finding-purpose/id1583983723?i=1000801076750", spotify="https://open.spotify.com/episode/7hsuc1Ak63atKKlkToMN03",
        summary='What happens when the life you planned becomes impossible? Career, marriage, friendships and identity after losing most of his sight, and building a new blueprint instead of letting disability define the future.',
        clips_ok=False, clips=[]),
    dict(
        id="44EM7XbWwjg", apple="https://podcasts.apple.com/us/podcast/226-your-disability-changed-your-life-it-didnt-end/id1371390804?i=1000800961656", spotify="https://open.spotify.com/episode/3dg9T3sHE1PI06D2faTU8Q", show="The Inclusive Dad Podcast", hosts="Aaron DeVries",
        title="Episode 226: Your Disability Changed Your Life. It Didn't End Your Possibilities!",
        date_label="November 10, 2026", upload="2026-11-10T01:00:08-08:00", seconds=2521,
        summary="Losing independence to vision loss, and how it touches relationships, dating, parenting and learning to ask for help. Also, how the stories we tell ourselves can keep us playing small. Helpful for people rebuilding after disability, and for families who want to understand inclusion.",
        clips_ok=True, clips=[
            # Approved, link not live yet: "Not blind, not sighted", "Asking for help made my life bigger",
            # "My son's play-by-play", "My blueprint was missing the kitchen",
            # "Where to begin when your old life is gone", "A group anyone can join".
        ]),
    dict(
        id="yYK21hwRwIk", apple="https://podcasts.apple.com/us/podcast/when-the-old-you-no-longer-fits-reinventing-yourself/id6792543329?i=1000799655196", spotify="https://open.spotify.com/episode/3d25rxjgSQTVSAvzwq7Fsr", show="Reclaim Your Energy After 50", hosts="John Curran",
        title="When the Old You No Longer Fits: Reinventing Yourself and Finding What's Next",
        date_label="November 3, 2026", upload="2026-11-03T11:11:30-08:00", seconds=1331,
        summary="Becoming legally blind and rethinking independence, career and relationships, and letting go of self-sabotaging beliefs. For people over 50 facing a life transition or wondering what comes next.",
        clips_ok=False, clips=[]),
    dict(
        id="VqomfAubyAM", apple="https://podcasts.apple.com/us/podcast/rebuilding-identity-after-life-disruption-you-are-not/id1896807547?i=1000798976860", spotify="https://open.spotify.com/episode/03ND3XMQE1tzBN7RyVNNf6", show="Healthy Mind, Healthy Life", hosts="Avik Chakraborty",
        title="Rebuilding Identity After Life Disruption: You Are Not Broken, You Are Unfinished",
        date_label="October 30, 2026", upload="2026-10-30T17:39:46-07:00", seconds=1492,
        summary="The question that arrives when the appointments end: who am I now? Why healing the body and rebuilding a sense of self are two different journeys, and how a new blueprint and small daily steps help. For anyone whose life has been rewritten by a health change or disability.",
        clips_ok=False, clips=[]),
    dict(
        id=None, show="The Life Wisdom Lab", hosts='Asia Laurent',
        title='Rebuilding Life After Disability: Overcome Adversity, Build Resilience and Start Again',
        date_label="October 23, 2026", upload="2026-10-23", seconds=1426, apple="https://podcasts.apple.com/us/podcast/rebuilding-life-after-disability-overcome-adversity/id6818146365?i=1000797795872", spotify="https://open.spotify.com/episode/7g5ssErRxti1O0B4jQI2Yu",
        summary='When the person you used to be no longer fits your future: losing most of his vision, rebuilding a career, navigating relationships and finding a new purpose.',
        clips_ok=False, clips=[]),
    dict(
        id=None, show="Succeeding in a Troubled World", hosts=None,
        title="A Changed Life Doesn't Have to Become a Smaller Life: Navigating Identity and Reinvention",
        date_label="October 22, 2026", upload="2026-10-22", seconds=1375, apple="https://podcasts.apple.com/us/podcast/shay-edmonds-a-changed-life-doesnt-have-to-become/id6818755426?i=1000797706857", spotify="https://open.spotify.com/episode/4zzUIztIBqwhJOHPZ2XRS5",
        summary='What happens after the doctors have done their job and you still have to figure out how to live the rest of your life? A candid, practical conversation about identity and reinvention.',
        clips_ok=False, clips=[]),
]

# Recorded but not yet published. No links until the host posts the episode;
# when one goes live, move it into EPISODES above (with its YouTube id) and delete it here.
RECORDED = [
    dict(show="The MISOGI Method", hosts="Jody B. Miller", date_label="November 19, 2026"),
    dict(show="Lethal Venom", hosts="Noah May", date_label="November 18, 2026"),
]
# Booked recordings. When recorded, move to RECORDED.
UPCOMING = [
    dict(show="The Blind Spot", hosts="Sarah Larose and Keila Alequin", date_label="December 2026"),
    dict(show="Sunday Edition", hosts="ACB Media Network", date_label="December 2026", by=True),
    dict(show="Positive Talk Radio", hosts="Bleav Network", date_label="December 2026", by=True),
    dict(show="The Blind Chick", hosts="Aftersight", date_label="January 2027", by=True),
    dict(show="It Happened To Me", hosts=None, date_label="January 2027"),
]

e = lambda s: html.escape(s, quote=True)


def show_line(x):
    who = ""
    if x.get("hosts"):
        who = f' from {e(x["hosts"])}' if x.get("by") else f' with {e(x["hosts"])}'
    return f'<li><strong>{e(x["show"])}</strong>{who} &middot; {e(x["date_label"])}</li>'



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


def listen_links(ep):
    items = []
    for key, name in (("apple", "Apple Podcasts"), ("spotify", "Spotify")):
        if ep.get(key):
            items.append(f'<li><a href="{e(ep[key])}" target="_blank" rel="noopener noreferrer"><span class="sr-only">Listen to {e(ep["show"])} on </span>{name}<span class="sr-only"> (opens in new tab)</span><span aria-hidden="true"> &#8599;</span></a></li>')
    if ep.get("id"):
        items.append(f'<li><a href="https://youtu.be/{e(ep["id"])}" target="_blank" rel="noopener noreferrer"><span class="sr-only">Watch {e(ep["show"])} on </span>YouTube<span class="sr-only"> (opens in new tab)</span><span aria-hidden="true"> &#8599;</span></a></li>')
    return ('<div class="listen"><span class="listen-label" aria-hidden="true">Listen or watch:</span><ul class="listen-links" aria-label="Listen or watch this episode">' + "".join(items) + '</ul></div>') if items else ''


def with_hosts(ep):
    return f' with {e(ep["hosts"])}' if ep.get("hosts") else ''


sections, videos = [], []
for i, ep in enumerate(EPISODES, 1):
    hid = f"ep-{ep['id'] or re.sub(r'[^a-z0-9]+', '-', ep['show'].lower()).strip('-')}"
    label = f"Full episode: {ep['show']}{' with ' + ep['hosts'] if ep.get('hosts') else ''}"
    meta_host = f' &middot; with {e(ep["hosts"])}' if ep.get("hosts") else ''
    out = [f'<section class="episode" aria-labelledby="{hid}">',
           f'<p class="ep-meta">{e(ep["show"])}{meta_host} &middot; {e(ep["date_label"])}{"" if ep.get("id") else " &middot; audio"}</p>',
           f'<h2 id="{hid}">{e(ep["title"])}</h2>',
           f'<p>{e(ep["summary"])}</p>']
    if ep.get("id"):
        out.append(player(ep["id"], label, ep["seconds"]))
    out.append(listen_links(ep))
    out.append(f'<p class="credit">Originally recorded for {e(ep["show"])}{with_hosts(ep)}. Length about {mins(ep["seconds"])}.</p>')
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
    if ep.get("id"):
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
    <p class="note">Newest first. Each video plays only when you press its Play button, and nothing plays on its own. Listen links open Apple Podcasts or Spotify in a new tab.</p>
{chr(10).join(sections)}
  </div>
</section>
<section class="block" aria-labelledby="soon-title">
  <div class="wrap episodes">
    <h2 id="soon-title">Recorded and coming soon</h2>
    <p>These conversations are recorded and waiting for each show to publish. We add the episode here as soon as it goes live.</p>
    <ul class="list-plain soon-list">
{chr(10).join(show_line(x) for x in RECORDED)}
    </ul>
    <h3>Booked</h3>
    <ul class="list-plain soon-list">
{chr(10).join(show_line(x) for x in UPCOMING)}
    </ul>
    <p class="note">Producers and hosts: <a href="/speaking/">see topics and booking details</a>.</p>
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
