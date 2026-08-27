#!/usr/bin/env python3
"""
Downloads the gawahi.tv media the site actually renders into assets/img/gawahi/,
and rewrites data/gawahi.json to point at those local copies.

Only Gawahi's own photography and programme artwork is fetched (see OWN in
build_gawahi.py) plus each post's featured image and the one programme video.
The ~200 WordPress theme demo images are left as remote URLs — nothing renders
them, and carrying 30 MB of stock into the repo helps no one.
"""
import json, pathlib, urllib.request, urllib.parse, concurrent.futures

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "assets" / "img" / "gawahi"
DATA = ROOT / "data" / "gawahi.json"
DEST.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

# the one programme video the home page plays; the theme's background loop is not used
KEEP_VIDEO = "The-Enlighted-Minds-with-GAWAHI-TELEVISION.mp4"

d = json.loads(DATA.read_text(encoding="utf-8"))
local_name = lambda url: urllib.parse.unquote(url.rsplit("/", 1)[-1])

def grab(url):
    dest = DEST / local_name(url)
    if dest.exists() and dest.stat().st_size:
        return dest.stat().st_size, None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
            dest.write_bytes(r.read())
        return dest.stat().st_size, None
    except Exception as e:
        return 0, f"{url} -> {e}"

jobs = []
featured = {p.get("featured") for p in d["posts"] if p.get("featured")}

for img in d["images"]:
    sizes = img.get("sizes") or {}
    if not (img.get("own") or img["url"] in featured):
        img.pop("local", None); img.pop("localThumb", None)
        continue
    pick = (sizes.get("large") or sizes.get("medium_large")
            or sizes.get("full") or {"url": img["url"]})
    img["local"] = "assets/img/gawahi/" + local_name(pick["url"])
    jobs.append(pick["url"])
    thumb = sizes.get("medium") or sizes.get("thumbnail")
    if thumb:
        img["localThumb"] = "assets/img/gawahi/" + local_name(thumb["url"])
        jobs.append(thumb["url"])

# posts point at their local featured image where we have one
by_url = {i["url"]: i for i in d["images"]}
for p in d["posts"]:
    f = p.get("featured")
    if f and f in by_url and by_url[f].get("local"):
        p["featured"] = by_url[f]["local"]

for v in d["videos"]:
    if local_name(v["url"]) == KEEP_VIDEO:
        v["local"] = "assets/img/gawahi/" + KEEP_VIDEO
        jobs.append(v["url"])
    else:
        v.pop("local", None)
for a in d["audio"]:
    a.pop("local", None)

jobs = list(dict.fromkeys(jobs))
total, errs = 0, []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    for size, err in ex.map(grab, jobs):
        total += size
        if err: errs.append(err)

# remove anything left in the folder that is no longer referenced
keep = {local_name(u) for u in jobs}
removed = 0
for f in DEST.iterdir():
    if f.is_file() and f.name not in keep:
        f.unlink(); removed += 1

DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Kept {len(jobs)-len(errs)}/{len(jobs)} files ({total/1048576:.1f} MB); "
      f"removed {removed} unreferenced.")
for e in errs[:8]: print("  FAIL", e)
