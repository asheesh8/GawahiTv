#!/usr/bin/env python3
"""Builds data/gawahi.json from the live gawahi.tv WordPress REST API dump."""
import json, glob, re, html, pathlib
SRC = pathlib.Path("/private/tmp/claude-501/-Users-ashishsubedi-Desktop-ARKITECH-SOLUTIONS-01-Active-Client-Work-GawahiiTV/cbf54c0d-9bc9-4997-b55d-090a77257c23/scratchpad/gawahi")
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "gawahi.json"

def strip(h):
    h = re.sub(r"<[^>]+>", " ", h or "")
    return re.sub(r"\s+", " ", html.unescape(h)).strip()

media = []
for f in sorted(glob.glob(str(SRC / "media_*.json"))):
    media += json.load(open(f, encoding="utf-8"))
posts = json.load(open(SRC / "posts.json", encoding="utf-8"))
pages = json.load(open(SRC / "pages.json", encoding="utf-8"))
cats  = json.load(open(SRC / "categories.json", encoding="utf-8"))

def sizes(m):
    d = (m.get("media_details") or {}).get("sizes") or {}
    out = {}
    for k in ("thumbnail", "medium", "medium_large", "large", "full"):
        if k in d: out[k] = {"url": d[k]["source_url"], "w": d[k].get("width"), "h": d[k].get("height")}
    return out

images, videos, audio = [], [], []
for m in media:
    mime = m.get("mime_type", "")
    rec = {"id": m["id"], "title": strip(m["title"]["rendered"]), "url": m["source_url"],
           "alt": m.get("alt_text") or "", "date": m["date"][:10], "mime": mime,
           "w": (m.get("media_details") or {}).get("width"),
           "h": (m.get("media_details") or {}).get("height")}
    if mime.startswith("image/"):
        if mime == "image/svg+xml": continue
        rec["sizes"] = sizes(m); images.append(rec)
    elif mime.startswith("video/"): videos.append(rec)
    elif mime.startswith("audio/"): audio.append(rec)

# --------------------------------------------------------------- programmes
# Gawahi's own programme artwork, hand-picked from the media library.
# Everything else in the WordPress library ships with the theme as demo stock
# (the "-copyright" suffixed files), so it is kept out of the gallery.
PROGRAMMES = [
    ("AJJ-KI-Gawahi",              "Ajj Ki Gawahi",        "Today's witness — the flagship daily programme.", "Urdu"),
    ("App-Ka-Sawal-2",             "App Ka Sawal",         "Your questions answered on air.",                 "Urdu"),
    ("LIVE-MESSAGE",               "Live Message",         "Live worship and preaching.",                     "Urdu"),
    ("Andrew-Wommack-Ministries-2","Living Commentary",    "Verse-by-verse teaching with Andrew Wommack.",    "Urdu"),
    ("The-Enlightened-Mind-1",     "The Enlightened Mind", "Faith, culture and public life in conversation.", "Urdu"),
    ("jeevan-ka-faisla",           "Jeevan Ka Faisla",     "Drama: the decision that changes a life.",        "Urdu"),
    ("jawed-260526",               "The Gawahi Podcast",   "Long-form conversation from the podcast studio.", "Urdu"),
    ("studio-252626",              "Inside the Studio",    "How Gawahi is made, day to day.",                 "Both"),
]

# Gawahi's WordPress library is mostly the theme's demo stock. These are the files
# that are genuinely the channel's own photography and programme artwork — everything
# else (logos, decorative vectors, the "-copyright" demo posts) stays out of the gallery.
OWN = [
    "AJJ-KI-Gawahi", "App-Ka-Sawal", "LIVE-MESSAGE", "Andrew-Wommack-Ministries",
    "The-Enlightened-Mind", "jeevan-ka-faisla", "jawed-260526", "studio-252626",
    "podcast-studio-260526", "front-page-250526", "Sarfaraz-Wiliam",
    "home-banner-1", "home-banner-2",
]

def is_own(im):
    hay = (im["title"] + " " + im["url"]).lower().replace(" ", "-")
    return any(k.lower() in hay for k in OWN)

def find_img(stub):
    for im in images:
        if stub.lower() in im["title"].lower().replace(" ", "-") or stub.lower() in im["url"].lower():
            return im
    return None

programmes = []
for stub, name, blurb, lang in PROGRAMMES:
    im = find_img(stub)
    if im:
        programmes.append({"name": name, "blurb": blurb, "lang": lang,
                           "image": im["url"], "mediaId": im["id"], "stub": stub})

for im in images:
    im["own"] = is_own(im)
    im["demo"] = not im["own"]

# Hand-written Urdu/Sindhi versions of the post content, merged in by slug.
I18N_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "posts_i18n.json"
POST_I18N = json.load(open(I18N_PATH, encoding="utf-8")) if I18N_PATH.exists() else {}

def post(p):
    return {"id": p["id"], "slug": p["slug"], "title": strip(p["title"]["rendered"]),
            "date": p["date"][:10], "link": p["link"],
            "excerpt": strip(p.get("excerpt", {}).get("rendered", ""))[:280],
            "body": strip(p.get("content", {}).get("rendered", "")),
            "categories": p.get("categories", []),
            "featured": (p.get("_embedded", {}).get("wp:featuredmedia") or [{}])[0].get("source_url"),
            "i18n": {k: v for k, v in POST_I18N.get(p["slug"], {}).items() if not k.startswith("_")}}

payload = {
    "site": {"name": "GAWAHI Television", "tagline": "A Voice of Hope to the Nations.",
             "promise": "Bringing God's Word to Every Home.", "origin": "https://gawahi.tv"},
    "categories": [{"id": c["id"], "name": c["name"], "slug": c["slug"], "count": c["count"]} for c in cats],
    "posts": [post(p) for p in posts],
    "pages": [{"id": p["id"], "slug": p["slug"], "title": strip(p["title"]["rendered"]), "link": p["link"]} for p in pages],
    "programmes": programmes,
    "images": images, "videos": videos, "audio": audio,
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Wrote {OUT} — {len(payload['posts'])} posts, {len(programmes)} programmes, "
      f"{sum(1 for i in images if i['own'])} own / {sum(1 for i in images if i['demo'])} theme-stock images, "
      f"{sum(1 for p in payload['posts'] if p['i18n'])} translated posts, "
      f"{len(videos)} videos, {len(audio)} audio, {OUT.stat().st_size//1024} KB")
