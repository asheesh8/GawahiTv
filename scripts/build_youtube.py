#!/usr/bin/env python3
"""
Builds data/youtube.json — the playlist behind the "Gawahi Live" channel on the
home page. Scrapes the channel's /videos tab (latest ~30 uploads, with titles and
durations), falling back to the public RSS feed (latest 15, no durations).

Re-run whenever the channel posts new videos:
    python3 scripts/build_youtube.py
"""
import json, pathlib, re, urllib.request, xml.etree.ElementTree as ET

CHANNEL_ID = "UC8ZNIVXuurOa57dMWDD94LA"          # @gawahitelevision
HANDLE     = "gawahitelevision"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "youtube.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")        # never let anything else into the page

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read().decode("utf-8", "replace")

def secs(t):
    if not t or not re.fullmatch(r"\d+(:\d{2}){1,2}", t): return None
    n = 0
    for part in t.split(":"): n = n * 60 + int(part)
    return n

def from_channel_page():
    html = get(f"https://www.youtube.com/@{HANDLE}/videos")
    data = json.loads(re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S).group(1))
    found = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("contentId") and "contentImage" in o and "metadata" in o:
                s = json.dumps(o, ensure_ascii=False)
                title = (o.get("metadata", {}).get("lockupMetadataViewModel", {})
                           .get("title", {}).get("content"))
                badge = re.search(r'"thumbnailBadgeViewModel": \{"text": "([^"]+)"', s)
                found.append({"id": o["contentId"], "title": title,
                              "duration": secs(badge.group(1)) if badge else None})
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(data)
    return found

def from_rss():
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    root = ET.fromstring(get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"))
    return [{"id": e.find("yt:videoId", ns).text, "title": e.find("a:title", ns).text,
             "published": e.find("a:published", ns).text[:10], "duration": None}
            for e in root.findall("a:entry", ns)]

videos, source = [], ""
try:
    videos, source = from_channel_page(), "channel page"
except Exception as e:
    print("channel page failed:", e)
if len(videos) < 5:
    videos, source = from_rss(), "rss"

# publish dates from RSS where we have them
try:
    pub = {v["id"]: v["published"] for v in from_rss()}
except Exception:
    pub = {}

seen, clean = set(), []
for v in videos:
    vid = v.get("id") or ""
    if not ID_RE.match(vid) or vid in seen: continue
    seen.add(vid)
    d = v.get("duration")
    if d is not None and d < 45: continue          # skip Shorts-length clips
    clean.append({"id": vid, "title": (v.get("title") or "").strip()[:160],
                  "duration": d, "published": pub.get(vid) or v.get("published")})

payload = {"channel": {"id": CHANNEL_ID, "handle": "@" + HANDLE,
                       "url": f"https://www.youtube.com/@{HANDLE}",
                       "uploads": "UU" + CHANNEL_ID[2:]},
           "source": source, "videos": clean}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
known = [v["duration"] for v in clean if v["duration"]]
print(f"Wrote {OUT.name}: {len(clean)} videos from {source}; "
      f"{len(known)} with durations, {sum(known)//3600}h {sum(known)%3600//60}m total")
for v in clean[:8]: print(f"  {v['id']}  {str(v['duration']):>5}s  {v['title'][:70]}")
