#!/usr/bin/env python3
"""
Mirror the library's media to local disk, so Gawahi can self-host instead of
streaming from the Digital Bible Society CDN.

The site works fine without this — it streams straight from the source. Run this
only if you need the files on your own server (or on an offline drive).

    python3 scripts/mirror_library.py --plan               # show what would be fetched
    python3 scripts/mirror_library.py --types film,historic
    python3 scripts/mirror_library.py --lang urd --what downloads
    python3 scripts/mirror_library.py --all --out /Volumes/Drive/gawahi-media

  --what  stream    the chapter/film files the site plays  (default)
          downloads the ZIP/PDF/EPUB bundles on each resource
          both
  --lang  snd | urd | all           --types film,audio-bible,audio,scripture,historic
  --workers N (default 4)           --limit N   stop after N files
  --skip-external   ignore files hosted outside dbs.org

Be aware: "everything" is several hundred gigabytes. Mirror what you actually need.
Nothing here is re-licensed — check each publisher's terms before redistributing.
"""
import argparse, json, pathlib, sys, time, urllib.request, urllib.parse, concurrent.futures

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "resources.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

def urls_for(r, what, skip_external):
    """Every media URL a resource exposes, as (url, suggested relative path)."""
    out, p = [], r.get("play") or {}
    if what in ("stream", "both"):
        if p.get("kind") == "chapters":
            for it in p["items"]:
                out.append((p["base"] + it["file"], f'{r["id"]}/{it["file"]}'))
        elif p.get("kind") == "file":
            for q in ("hd", "sd"):
                if p.get(q):
                    out.append((p[q], f'{r["id"]}/{q}-' + p[q].rsplit("/", 1)[-1]))
        elif p.get("kind") == "audio-collection" and p.get("sample"):
            out.append((p["sample"], f'{r["id"]}/' + p["sample"].rsplit("/", 1)[-1]))
        elif p.get("kind") == "audio-bible":
            # 1,189 chapters per full Bible — use --what downloads for the ZIP instead
            pass
        if r.get("read", {}).get("url"):
            out.append((r["read"]["url"], f'{r["id"]}/' + r["read"]["url"].rsplit("/", 1)[-1]))
    if what in ("downloads", "both"):
        for d in r.get("downloads", []):
            if d.get("external") and skip_external:
                continue
            if not d["url"].lower().split("?")[0].endswith(
                    (".zip", ".pdf", ".epub", ".mp3", ".mp4")):
                continue                      # a landing page, not a file
            out.append((d["url"], f'{r["id"]}/' + urllib.parse.unquote(d["url"].rsplit("/", 1)[-1])))
    return out

def human(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024: return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"

def head_size(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=25) as r:
            return int(r.headers.get("content-length") or 0)
    except Exception:
        return 0

def fetch(job, out_root, retries=2):
    url, rel = job
    dest = out_root / rel
    if dest.exists() and dest.stat().st_size > 0:
        return ("skip", rel, dest.stat().st_size)
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            tmp = dest.with_suffix(dest.suffix + ".part")
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as fh:
                while chunk := r.read(1 << 20):
                    fh.write(chunk)
            tmp.rename(dest)
            return ("ok", rel, dest.stat().st_size)
        except Exception as e:
            if attempt == retries:
                return ("fail", rel, str(e)[:90])
            time.sleep(1.5 * (attempt + 1))

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "media"))
    ap.add_argument("--lang", default="all")
    ap.add_argument("--types", default="film,audio,scripture,historic")
    ap.add_argument("--what", default="stream", choices=["stream", "downloads", "both"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--plan", action="store_true", help="list and size the job, download nothing")
    ap.add_argument("--all", action="store_true", help="every type, both stream and downloads")
    ap.add_argument("--skip-external", action="store_true")
    a = ap.parse_args()

    if a.all:
        a.types = "film,audio-bible,audio,scripture,historic,link"
        a.what = "both"

    res = json.loads(DATA.read_text(encoding="utf-8"))["resources"]
    types = {t.strip() for t in a.types.split(",") if t.strip()}
    rows = [r for r in res if (a.lang == "all" or r["lang"] == a.lang) and r["type"] in types]

    jobs, seen = [], set()
    for r in rows:
        for u, rel in urls_for(r, a.what, a.skip_external):
            if u not in seen:
                seen.add(u); jobs.append((u, rel))
    if a.limit: jobs = jobs[:a.limit]

    out_root = pathlib.Path(a.out).expanduser().resolve()
    print(f"{len(rows)} resources → {len(jobs)} files → {out_root}\n")
    if not jobs:
        print("Nothing matched. Try --types film or --what downloads."); return

    if a.plan:
        print("Sizing (HEAD requests)…")
        total = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            sizes = list(ex.map(head_size, [j[0] for j in jobs]))
        for (u, rel), sz in zip(jobs, sizes):
            total += sz
            print(f"  {human(sz):>10}  {rel}")
        print(f"\n  TOTAL {human(total)} across {len(jobs)} files")
        print("  (0 B means the server did not report a size; it will still download.)")
        return

    ok = skipped = failed = 0; total = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for i, (status, rel, info) in enumerate(
                ex.map(lambda j: fetch(j, out_root), jobs), 1):
            if status == "ok":
                ok += 1; total += info
                print(f"  [{i}/{len(jobs)}] {human(info):>10}  {rel}")
            elif status == "skip":
                skipped += 1; total += info
            else:
                failed += 1
                print(f"  [{i}/{len(jobs)}] FAILED    {rel}  — {info}", file=sys.stderr)

    print(f"\nDone. {ok} downloaded, {skipped} already present, {failed} failed — {human(total)} on disk.")
    if failed:
        print("Re-run to retry the failures; completed files are skipped.")

if __name__ == "__main__":
    main()
