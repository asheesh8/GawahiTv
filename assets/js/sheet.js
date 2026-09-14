/* GAWAHI — the resource sheet: players, reader and downloads. Shared by every page. */

import { $, $$, esc, ICONS, t, onLangChange, isLatinText, safeUrl, cssUrl } from './app.js';

const CDN_AUDIO = 'https://dbs.org/cdn/audio';

/* Standard Bible book numbering — matches the DBS CDN directory layout,
   e.g. NT_URDBSI/40_Matthew/40_Matthew_001.mp3 */
const BOOKS = {
  OT: [[1,'Genesis',50],[2,'Exodus',40],[3,'Leviticus',27],[4,'Numbers',36],[5,'Deuteronomy',34],
    [6,'Joshua',24],[7,'Judges',21],[8,'Ruth',4],[9,'1Samuel',31],[10,'2Samuel',24],[11,'1Kings',22],
    [12,'2Kings',25],[13,'1Chronicles',29],[14,'2Chronicles',36],[15,'Ezra',10],[16,'Nehemiah',13],
    [17,'Esther',10],[18,'Job',42],[19,'Psalms',150],[20,'Proverbs',31],[21,'Ecclesiastes',12],
    [22,'SongofSongs',8],[23,'Isaiah',66],[24,'Jeremiah',52],[25,'Lamentations',5],[26,'Ezekiel',48],
    [27,'Daniel',12],[28,'Hosea',14],[29,'Joel',3],[30,'Amos',9],[31,'Obadiah',1],[32,'Jonah',4],
    [33,'Micah',7],[34,'Nahum',3],[35,'Habakkuk',3],[36,'Zephaniah',3],[37,'Haggai',2],
    [38,'Zechariah',14],[39,'Malachi',4]],
  NT: [[40,'Matthew',28],[41,'Mark',16],[42,'Luke',24],[43,'John',21],[44,'Acts',28],[45,'Romans',16],
    [46,'1Corinthians',16],[47,'2Corinthians',13],[48,'Galatians',6],[49,'Ephesians',6],
    [50,'Philippians',4],[51,'Colossians',4],[52,'1Thessalonians',5],[53,'2Thessalonians',3],
    [54,'1Timothy',6],[55,'2Timothy',4],[56,'Titus',3],[57,'Philemon',1],[58,'Hebrews',13],
    [59,'James',5],[60,'1Peter',5],[61,'2Peter',3],[62,'1John',5],[63,'2John',1],[64,'3John',1],
    [65,'Jude',1],[66,'Revelation',22]],
};
const pad = (n, w = 2) => String(n).padStart(w, '0');
const spaced = s => s.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/^(\d)/, '$1 ');


export { pad, spaced, BOOKS };

/* ------------------------------------------------------------------ cards */
export function card(r) {
  // Audio Bibles and text editions ship no artwork. Rather than leave a bare
  // gradient, set the native title on it — it reads as a designed cover.
  const cover = r.cover
    ? `<img src="${esc(safeUrl(r.cover))}" alt="" loading="lazy" decoding="async" data-hide-on-error>`
    : (() => {
        // Many partner records carry no native title, so this falls back to the
        // English one — set it in the Latin face, not Nastaliq.
        const label = r.native || r.title;
        const cls = isLatinText(label) ? 'latin' : (r.lang === 'urd' ? 'f-urdu' : 'f-sindhi');
        return `<span class="cover-type" aria-hidden="true">
         <span class="cover-mark">${ICONS[DATA?.types?.[r.type]?.icon] || ICONS.book}</span>
         <span class="cover-title ${cls}">${esc(label)}</span>
       </span>`;
      })();
  const playable = !!r.play, readable = !!r.read;
  // an audio Bible is not something you "Watch"
  const actKey = r.type === 'audio-bible' || r.type === 'audio' ? 'act.listen'
               : playable ? 'act.watch'
               : readable ? 'act.read' : 'act.open';
  const badge = playable ? `<span class="play-ring"><i>${ICONS.play}</i></span>` : '';
  const tags = [`<span class="tag">${esc(t('lib.' + (r.lang === 'urd' ? 'urdu' : 'sindhi')))}</span>`];
  if (r.license) tags.push(`<span class="tag tag-g">${esc(r.license)}</span>`);
  const bits = [r.org, r.year, r.stats].filter(Boolean);
  return `
  <button class="card reveal" data-r="${esc(r.id)}" type="button">
    <span class="card-media">${cover}${badge}
      <span class="card-tags">${tags.join('')}</span>
      ${r.duration ? `<span class="dur">${esc(r.duration)}</span>` : ''}
    </span>
    <span class="card-body" dir="ltr">
      <h3 class="latin">${esc(r.title)}</h3>
      ${r.native ? `<p class="native ${r.lang === 'urd' ? 'f-urdu' : 'f-sindhi'}">${esc(r.native)}</p>` : ''}
      <p class="latin">${esc(r.desc || '')}</p>
      <span class="card-foot">
        <span class="meta latin">${bits.map(esc).join('<span class="dot"></span>')}</span>
        <span class="chip">${esc(t(actKey))}</span>
      </span>
    </span>
  </button>`;
}

/* ------------------------------------------------------------------ sheet */
function chapterPlayer(r) {
  const p = r.play, items = p.items;
  const src = i => p.base + items[i].file;
  return {
    html: `
      <div class="player" id="pl">
        ${r.cover ? `<div class="player-poster" id="poster" style="background-image:url('${esc(cssUrl(r.cover))}')">
            <i>${ICONS.play}</i></div>` : ''}
        <video id="vid" controls preload="metadata" playsinline
               ${r.cover ? `poster="${esc(safeUrl(r.cover))}"` : ''} src="${esc(safeUrl(src(0)))}"></video>
      </div>
      <div class="chapters">
        <div class="chapters-hd"><span>${items.length} ${esc(t(items.length > 20 ? 'sheet.chapters' : 'sheet.parts'))}</span>
          <span class="meta" id="nowPlaying">${esc(items[0].title)}</span></div>
        <div class="chapters-list" id="chapList">
          ${items.map((c, i) => `<button type="button" data-i="${i}"${i === 0 ? ' aria-current="true"' : ''}>
              <span class="n">${c.n === 0 ? '—' : pad(c.n)}</span><span class="latin">${esc(c.title)}</span></button>`).join('')}
        </div>
      </div>`,
    wire(root) {
      const vid = $('#vid', root), poster = $('#poster', root);
      let cur = 0;
      const go = (i, autoplay = true) => {
        cur = i; vid.src = safeUrl(src(i)); vid.load();
        if (autoplay) vid.play().catch(() => {});
        poster?.remove();
        $$('#chapList button', root).forEach(b =>
          b.toggleAttribute('aria-current', +b.dataset.i === i));
        $('#nowPlaying', root).textContent = items[i].title;
        $$('#chapList button', root)[i]?.scrollIntoView({ block: 'nearest' });
      };
      poster?.addEventListener('click', () => { poster.remove(); vid.play().catch(() => {}); });
      $('#chapList', root).addEventListener('click', e => {
        const b = e.target.closest('button[data-i]'); if (b) go(+b.dataset.i);
      });
      vid.addEventListener('ended', () => { if (cur + 1 < items.length) go(cur + 1); });
    }
  };
}

function filePlayer(r) {
  const p = r.play, primary = p.hd || p.sd;
  return {
    html: `
      <div class="player">
        ${r.cover ? `<div class="player-poster" id="poster" style="background-image:url('${esc(cssUrl(r.cover))}')">
            <i>${ICONS.play}</i></div>` : ''}
        <video id="vid" controls preload="metadata" playsinline
               ${r.cover ? `poster="${esc(safeUrl(r.cover))}"` : ''}>
          <source src="${esc(safeUrl(primary))}" type="video/mp4">
        </video>
      </div>
      ${p.hd && p.sd ? `<div class="seg" style="margin-bottom:1.2rem" id="qual">
          <button data-q="hd" aria-pressed="true">${esc(t('sheet.hq'))}</button>
          <button data-q="sd" aria-pressed="false">${esc(t('sheet.sd'))}</button></div>` : ''}`,
    wire(root) {
      const vid = $('#vid', root), poster = $('#poster', root);
      poster?.addEventListener('click', () => { poster.remove(); vid.play().catch(() => {}); });
      $('#qual', root)?.addEventListener('click', e => {
        const b = e.target.closest('button[data-q]'); if (!b) return;
        const at = vid.currentTime, playing = !vid.paused;
        vid.src = safeUrl(p[b.dataset.q]); vid.load(); vid.currentTime = at;
        if (playing) vid.play().catch(() => {});
        $$('#qual button', root).forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      });
    }
  };
}

function audioBiblePlayer(r) {
  const { fileset, version, testaments } = r.play;
  const list = testaments.flatMap(tt => BOOKS[tt].map(b => [tt, ...b]));
  const url = (test, num, name, ch) =>
    `${CDN_AUDIO}/${fileset}/${test}_${version}/${pad(num)}_${name}/${pad(num)}_${name}_${pad(ch, 3)}.mp3`;
  return {
    html: `
      <div class="audio-player">
        <h4 class="latin" id="abNow">${esc(spaced(list[0][2]))} 1</h4>
        <p class="latin">${esc(r.title)} — ${esc(r.org)}</p>
        <audio id="aud" controls preload="none" src="${esc(safeUrl(url(list[0][0], list[0][1], list[0][2], 1)))}"></audio>
      </div>
      <div class="chapters">
        <div class="chapters-hd">
          <select id="bookSel" class="book-sel" aria-label="${esc(t('sheet.book'))}">
            ${list.map((b, i) => `<option value="${i}">${esc(spaced(b[2]))}</option>`).join('')}
          </select>
          <span class="meta" id="chCount">${list[0][3]} ${esc(t('sheet.chapters'))}</span>
        </div>
        <div class="ch-grid" id="chGrid"></div>
      </div>`,
    wire(root) {
      const aud = $('#aud', root), sel = $('#bookSel', root), grid = $('#chGrid', root);
      let bi = 0, ci = 1;
      const paintChapters = () => {
        const [, , , n] = list[bi];
        $('#chCount', root).textContent = `${n} ${t('sheet.chapters')}`;
        grid.innerHTML = Array.from({ length: n }, (_, i) =>
          `<button type="button" data-c="${i + 1}"${i + 1 === ci ? ' aria-pressed="true"' : ''}>${i + 1}</button>`).join('');
      };
      const go = (chapter) => {
        ci = chapter;
        const [test, num, name] = list[bi];
        aud.src = safeUrl(url(test, num, name, ci)); aud.play().catch(() => {});
        $('#abNow', root).textContent = `${spaced(name)} ${ci}`;
        $$('#chGrid button', root).forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.c === ci)));
      };
      sel.addEventListener('change', () => { bi = +sel.value; ci = 1; paintChapters(); go(1); });
      grid.addEventListener('click', e => {
        const b = e.target.closest('button[data-c]'); if (b) go(+b.dataset.c);
      });
      aud.addEventListener('ended', () => { if (ci < list[bi][3]) go(ci + 1); });
      paintChapters();
    }
  };
}

function audioCollectionPlayer(r) {
  return {
    html: `<div class="audio-player">
        <h4 class="latin">${esc(r.title)}</h4>
        <p class="latin">${esc(r.org)}${r.stats ? ' — ' + esc(r.stats) : ''}</p>
        <audio controls preload="none" src="${esc(safeUrl(r.play.sample))}"></audio>
      </div>
      <p class="note">${esc(t('sheet.collNote'))}</p>`,
    wire() {}
  };
}

function readerBlock(r) {
  return `<div class="reader">
      <iframe src="${esc(safeUrl(r.read.url))}#view=FitH" referrerpolicy="strict-origin-when-cross-origin" title="${esc(r.title)} — reader" loading="lazy"></iframe>
    </div>`;
}

function sheetHTML(r) {
  let media = { html: '', wire() {} };
  if (r.play?.kind === 'chapters')          media = chapterPlayer(r);
  else if (r.play?.kind === 'file')         media = filePlayer(r);
  else if (r.play?.kind === 'audio-bible')  media = audioBiblePlayer(r);
  else if (r.play?.kind === 'audio-collection') media = audioCollectionPlayer(r);

  const facts = [
    ['Language', t('lib.' + (r.lang === 'urd' ? 'urdu' : 'sindhi'))],
    ['Category', t('type.' + r.type)], ['Publisher', r.org],
    ['Year', r.year], ['Runtime', r.duration], ['Scope', r.scope],
    ['Contents', r.stats], ['Licence', r.license],
  ].filter(([, v]) => v);

  const dls = (r.downloads || []).map(d => `
    <a class="dl" href="${esc(safeUrl(d.url))}"${d.external ? ' target="_blank" rel="noopener"' : ' download'}>
      ${d.external ? ICONS.external : ICONS.download}
      <span class="dl-t latin">${esc(d.label)}</span>
      ${d.size ? `<span class="dl-s">${esc(d.size)}</span>` : ''}
    </a>`).join('');

  return {
    html: `
      <div class="sheet-close">
        <span class="meta"><span class="chip">${esc(t('lib.' + (r.lang === 'urd' ? 'urdu' : 'sindhi')))}</span>
          <span class="chip chip-g">${esc(t('type.' + r.type))}</span></span>
        <button class="icon-btn" id="sheetX" aria-label="${esc(t('sheet.close'))}">${ICONS.close}</button>
      </div>
      <div class="sheet-body">
        <h2 class="latin" style="margin:.6rem 0 .3rem">${esc(r.title)}</h2>
        ${r.native ? `<p class="${r.lang === 'urd' ? 'f-urdu' : 'f-sindhi'}"
            style="color:var(--purple-500);font-size:1.5rem;margin:0 0 .8rem">${esc(r.native)}</p>` : ''}
        <p class="latin" style="color:var(--ink-mute);max-width:62ch">${esc(r.desc || '')}</p>
        ${media.html}
        ${r.read ? readerBlock(r) : ''}
        ${facts.length ? `<dl class="facts">${facts.map(([k, v]) =>
            `<div><dt>${esc(t('fact.' + k))}</dt><dd class="latin">${esc(v)}</dd></div>`).join('')}</dl>` : ''}
        ${dls ? `<h4 style="margin-top:1.6rem">${esc(t('sheet.download'))}</h4>
          <p class="meta" style="margin:.3rem 0 0">${esc(t('sheet.dlNote'))}</p>
          <div class="dl-list">${dls}</div>` : ''}
        <p style="margin-top:1.8rem">
          <a class="btn btn-o btn-sm" href="${esc(safeUrl(r.source))}" target="_blank" rel="noopener">
            ${ICONS.external} ${esc(t('sheet.source'))}</a>
        </p>
      </div>`,
    wire: media.wire,
  };
}

let DATA = null, lastFocus = null, openId = null;
export function setData(d) { DATA = d; }
export function openSheet(id, push = true) {
  const r = DATA.resources.find(x => x.id === id); if (!r) return;
  openId = id;
  const sheet = $('#sheet'), panel = $('#sheetPanel');
  const built = sheetHTML(r);
  panel.innerHTML = built.html;
  built.wire(panel);
  sheet.setAttribute('data-open', '');
  document.body.style.overflow = 'hidden';
  lastFocus = document.activeElement;
  panel.scrollTop = 0;
  $('#sheetX', panel).focus();
  $('#sheetX', panel).addEventListener('click', () => closeSheet());
  if (push) history.pushState({ r: id }, '', `?r=${encodeURIComponent(id)}`);
  document.title = `${r.title} — Gawahi`;
}

export function closeSheet(pop = true) {
  const sheet = $('#sheet');
  if (!sheet.hasAttribute('data-open')) return;
  openId = null;
  $$('video,audio', sheet).forEach(m => { try { m.pause(); m.src = ''; } catch {} });
  sheet.removeAttribute('data-open');
  $('#sheetPanel').innerHTML = '';
  document.body.style.overflow = '';
  lastFocus?.focus?.();
  document.title = t('lib.title') + ' — Gawahi Television';
  if (pop && location.search) history.pushState({}, '', location.pathname);
}

/* An open sheet is fully re-rendered when the interface language changes,
   so its labels, facts and chips follow the switch. Playback restarts. */
onLangChange(() => { if (openId) openSheet(openId, false); });

/** Wire a container of .card[data-r] buttons plus the #sheet dialog. */
export function mountSheet(gridSel) {
  $(gridSel)?.addEventListener('click', e => {
    const c = e.target.closest('[data-r]'); if (c) openSheet(c.dataset.r);
  });
  $('#sheet')?.addEventListener('click', e => { if (e.target.id === 'sheetBg') closeSheet(); });
  addEventListener('keydown', e => { if (e.key === 'Escape') closeSheet(); });
  addEventListener('popstate', () => {
    const id = new URLSearchParams(location.search).get('r');
    if (id) openSheet(id, false); else closeSheet(false);
  });
}

