# Gawahi Television — site rebuild

A rebuilt front end for [gawahi.tv](https://gawahi.tv), with a new **Resource Library**
of 112 free Sindhi and Urdu Scripture resources that visitors can watch, listen to,
read and download without leaving the site — plus a full **English / اردو / سنڌي**
interface toggle.

Static HTML, CSS and ES modules. No build step, no framework, no dependencies.

---

**Live:** https://gawahi-tv.vercel.app — Vercel serves the files as a static site (`vercel.json` sets clean URLs and cache headers); no environment variables. The Python scripts in `scripts/` regenerate `data/*.json` and are run by hand, not at deploy time.

## Run it

```bash
node scripts/serve.mjs 4173
```

Then open <http://localhost:4173>. Any static host works — it is just files.

---

## What is here

```
index.html        Home — hero, programmes, language cards, film/audio/reading rails, news, gallery
library.html      The Resource Library: search, filter, and the player/reader sheet
news.html         Posts from gawahi.tv + the full photo gallery
schedule.html     Daily broadcast schedule, with the current programme highlighted
about.html        About the channel and the partner credits

assets/css/site.css   The whole design system (~530 lines)
assets/js/
  app.js        icons, header, theme, scroll reveal, lightbox, shared helpers
  i18n.js       language switching, RTL, the t() translator
  sheet.js      the resource sheet — video/audio/PDF players and download lists
  library.js    filtering and search
  home.js  news.js  schedule.js  about.js

data/
  resources.json   112 resources with stream + download URLs        (generated)
  gawahi.json      posts, pages, programmes, media from gawahi.tv   (generated)
  i18n.json        174 interface strings × 3 languages              (hand-written)

scripts/
  build_resources.py     rebuilds data/resources.json
  build_gawahi.py        rebuilds data/gawahi.json from the WP REST dump
  fetch_gawahi_media.py  downloads gawahi.tv images/video locally
  mirror_library.py      optional bulk mirror of the library media
  serve.mjs              the local static server
```

---

## The Resource Library

Everything was catalogued from the Digital Bible Society's
[Sindhi](https://dbs.org/discover/languages/snd) and
[Urdu](https://dbs.org/discover/languages/urd) collections.

| | Sindhi | Urdu |
|---|---:|---:|
| Films | 8 | 24 |
| Audio Bibles | 3 | 3 |
| Audio collections | 2 | 3 |
| Scripture text | — | 5 |
| Historic scans | 4 | 8 |
| Partner links | 23 | 29 |
| **Total** | **40** | **72** |

**31 resources play in the page** and **17 are readable in the page**; there are
**132 download links**. Four player types are wired up:

- **Chaptered films** — a playlist with chapter titles that auto-advances
  (JESUS is 61 chapters, Gospel of John 49, the LUMO films 5–21).
- **Single-file films** — with an HD / low-bandwidth switch where both exist.
- **Audio Bibles** — book and chapter pickers over all 66 books; URLs are built as
  `/cdn/audio/{fileset}/{OT|NT}_{version}/{NN}_{Book}/{NN}_{Book}_{CCC}.mp3`.
  Four of the six filesets are verified on the CDN and stream; the other two
  (`URDBCS`, `SNDPBS00854`) are not reachable under any guessable path, so they are
  marked download-only rather than shipping dead links.
- **PDF reader** — historic scans and Scripture text open in an inline viewer.

### Nothing is re-hosted

Playback and downloads point straight at `dbs.org`, `video.dbs.org`, `media.dbs.org`,
`scripture.dbs.org`, `bibles.dbs.org` and the partner CDNs. That keeps the site to a
few MB, means resources are always the publisher's current version, and avoids
re-publishing material Gawahi does not hold the rights to.

**If you do want to self-host**, `scripts/mirror_library.py` fetches the files:

```bash
python3 scripts/mirror_library.py --plan                  # size the job first
python3 scripts/mirror_library.py --lang snd --types historic
python3 scripts/mirror_library.py --types film --what downloads
```

Mirroring everything is several hundred gigabytes — the two full Urdu audio Bibles
alone are ~200 hours, and JESUS in HD is 2.1 GB per language. Mirror what you need.

> **Licensing:** DBS and its partners publish these free of charge, and one item
> (`URDOUB`) is explicitly CC BY-SA 4.0. That is not the same as permission to
> re-host or redistribute. Confirm terms with each publisher — Jesus Film Project,
> LUMO, BibleProject, Global Recordings Network, Mars Hill, ROCK International,
> Create International — before mirroring onto Gawahi's own servers.

---

## Languages

A switcher in the header moves the whole interface between **English**, **اردو**
and **سنڌي**. It sets `lang` and `dir` on `<html>`, swaps the body typeface
(Inter → Noto Nastaliq Urdu → Noto Naskh Arabic), re-renders every dynamic string,
and remembers the choice in `localStorage`. An inline script in each `<head>` applies
the saved language before first paint, so RTL never flashes.

- Static copy is marked with `data-i18n="key"` (also `-placeholder`, `-aria`, `-html`).
- Dynamic strings call `t('key', { vars })` from `assets/js/i18n.js`.
- Page scripts re-render through `onLangChange()`. An open resource sheet re-renders too.
- Resource titles and publisher names stay in English — they are catalogue data — so
  they carry a `.latin` class that keeps a Latin face and its own direction inside an
  RTL page. Latin numerals are `unicode-bidi: isolate`d so `200+` does not become `+200`.

To add or change wording, edit `data/i18n.json`. All three languages carry the same
210 keys; missing keys fall back to English.

### Setting Arabic script properly

Urdu and Sindhi are cursive — letters join — so several habits that are harmless in
Latin actively break them. What the stylesheet does about it:

- **Zero tracking.** Any `letter-spacing` pulls the joins apart and renders words
  broken. A blanket rule zeroes tracking everywhere the interface is Urdu or Sindhi;
  Latin runs opt back in through `.latin`.
- **No mid-word breaking.** `overflow-wrap: break-word` would sever a word between
  two joined letters, so it is switched off for Arabic-script text.
- **Leading scaled to size.** Nastaliq hangs a long way below the baseline, so body
  text gets 2.15 leading — but a 5rem headline at that ratio opens a chasm, so
  headings step down (h1 1.42 → h4 1.8). Naskh is shallower and sits tighter.
- **Room in controls.** Buttons, chips and nav links get extra vertical padding so
  descenders do not collide with their borders.
- **Numerals stay Latin-ordered.** `200+`, `06:00` and `2:07:53` are wrapped in
  `direction: ltr; unicode-bidi: isolate`, or the bidi algorithm renders `+200`.
  Only elements whose *entire* content is a numeral get this — an element holding a
  translated sentence must keep the page direction.
- **No RTL string starts with a digit.** `کل 112 میں سے 112 وسائل`, not
  `112 میں سے …` — a leading number in an RTL run reorders unpredictably.
- **English catalogue text is an LTR island.** Resource titles, descriptions and
  publisher names stay English, so a library card sets `dir="ltr"` on its body and
  everything in it aligns to one edge instead of zig-zagging between the two.

---

## Gawahi Live

The home page hero plays the channel's YouTube uploads as a continuous broadcast.
Every visitor computes the same position from the clock — the playlist loops from a
fixed anchor — so two people opening the site at the same moment see the same
programme at the same second. The schedule page reads the same timeline, so its
"On now" row is exactly what the home page is playing.

- `assets/js/live.js` — timeline maths and the YouTube IFrame player
  (privacy-enhanced `youtube-nocookie.com` host, muted autoplay with a
  "Tap for sound" control, auto-skip if a video is removed or not embeddable).
- `data/youtube.json` — built by `python3 scripts/build_youtube.py`, which scrapes
  the channel's /videos tab (titles + durations) and falls back to RSS. **Re-run it
  after new uploads** and redeploy; a Vercel cron or GitHub Action could automate it.

---

## Security

Static site, no server code, no forms, no auth, no cookies — the attack surface is
the browser. What is in place:

- **Content-Security-Policy** (`vercel.json`): scripts only from self and the YouTube
  IFrame API; media, images and frames limited to the exact hosts the catalogue uses;
  `object-src 'none'`, `base-uri 'self'`, `frame-ancestors 'none'`,
  `upgrade-insecure-requests`. No inline scripts or inline event handlers anywhere, so
  `script-src` needs no `'unsafe-inline'`. (`style-src` keeps it for layout `style=""`
  attributes — there is no path for injecting style markup.)
- **HSTS** (2 years, preload-ready), `X-Frame-Options: DENY`, `nosniff`,
  `Referrer-Policy`, `COOP`, and a Permissions-Policy that denies camera, mic,
  geolocation, payment and FLoC/Topics while allowing autoplay/fullscreen only for the
  YouTube and PDF frames.
- **Output encoding**: every data value rendered into HTML goes through `esc()`.
  Every URL from data also goes through `safeUrl()` (only http/https/relative survive —
  escaping does not stop a `javascript:` href), and URLs placed in CSS go through
  `cssUrl()` (the HTML parser decodes `&#39;` before CSS sees it, so HTML-escaping
  alone cannot stop a `url()` breakout). YouTube IDs are regex-validated.
- **Deep links** (`?r=`, `?p=`, `?q=`) are only ever used as lookup keys or input
  values, never written into markup.
- **Tabnabbing**: every `target="_blank"` carries `rel="noopener"`.
- **`.vercelignore`** keeps build scripts, this README, local config and translation
  sources off the public site.
- `node scripts/serve.mjs` applies the same headers as production, so a policy that
  would break the live site breaks locally first.

Residual items for the owner: the GitHub repository is public (make it private if the
build notes should not be readable); YouTube and Google Fonts are third-party
dependencies loaded without SRI, which is unavoidable for both.

---

## Design

Purple and gold, sampled from the ichthys in Gawahi's own logo (`#7B3C90`, `#C9A45C`)
rather than the green left over in the WordPress theme's CSS.

- **Display** Bricolage Grotesque · **Text** Inter
- **Urdu** Noto Nastaliq Urdu · **Sindhi** Noto Naskh Arabic
- Light and dark, following the system unless the viewer picks one.
- Body text is `#17101C` on `#FAF7F4` (≈14:1); the purple on white is ≈9:1.

---

## Notes on the existing site

Worth knowing before the client review:

- **Only 14 of the 225 images in the WordPress media library are Gawahi's own.** The
  rest ship with the theme as demo stock (the `-copyright` files, `portf*`, `post*`,
  `prod*`, `team*`). `build_gawahi.py` keeps an explicit allow-list; the gallery and
  article thumbnails only use real Gawahi photography.
- **Two of the three posts are theme demo content** — "The global crisis…" and "All the
  greatest news…" are lorem ipsum ("QProin faucibus nec mauris a sodales"). They are
  carried across because they are the site's current content, but they should be
  deleted in WordPress. Only "The Enlightened Mind" is a real article.
- **16 of the 18 categories have no posts.** Adventures, Cartoons, Retail, Sports and
  the rest are theme defaults.
- The programme schedule in `schedule.js` is a plausible reconstruction from the
  channel's real programme artwork, not a feed. Swap in the true times when you have them.

---

## Regenerating the data

```bash
python3 scripts/build_resources.py     # data/resources.json
python3 scripts/build_gawahi.py        # data/gawahi.json  (needs the WP REST dump)
python3 scripts/fetch_gawahi_media.py  # assets/img/gawahi/ + local paths
```

`build_gawahi.py` reads a WordPress REST dump. To refresh it:

```bash
curl "https://gawahi.tv/wp-json/wp/v2/posts?per_page=100&_embed=1" -o gawahi/posts.json
curl "https://gawahi.tv/wp-json/wp/v2/pages?per_page=100"          -o gawahi/pages.json
curl "https://gawahi.tv/wp-json/wp/v2/categories?per_page=100"     -o gawahi/categories.json
for p in 1 2 3 4; do
  curl "https://gawahi.tv/wp-json/wp/v2/media?per_page=100&page=$p" -o gawahi/media_$p.json
done
```

then point `SRC` in `build_gawahi.py` at that folder.
