/* GAWAHI — home page composition */
import { $, $$, esc, ICONS, reveal, loadJSON, fmtDate, t, onLangChange, i18nReady,
         latinClass, postField, safeUrl } from './app.js';
import { card, setData, mountSheet } from './sheet.js';
import { loadLive, mountLive, listing, thumb, fmtClock } from './live.js';

const pick = (rows, n) => rows.slice(0, n);

(async function init() {
  await i18nReady;
  const [res, gw] = await Promise.all([
    loadJSON('data/resources.json'),
    loadJSON('data/gawahi.json'),
  ]);
  setData(res);
  const R = res.resources;

  /* ---------------- hero stats ---------------- */
  const hours = 200; // ~91h + 107h of audio Bible alone
  const paintStats = () => {
    const stats = [
      [R.length, t('stat.resources')],
      [R.filter(r => r.type === 'film').length, t('stat.films')],
      [hours + '+', t('stat.hours')],
      ['2', t('stat.languages')],
    ];
    $('#heroStats').innerHTML = stats.map(([n, l]) =>
      `<div><b>${esc(n)}</b><span>${esc(l)}</span></div>`).join('');
  };
  paintStats();

  /* ---------------- language cards ---------------- */
  const paintLangs = () => {
  $('#langCards').innerHTML = Object.values(res.languages).map(L => {
    const mine = R.filter(r => r.lang === L.code);
    const byType = Object.keys(res.types)
      .map(k => [t('type.' + k), mine.filter(r => r.type === k).length])
      .filter(([, n]) => n);
    return `
    <a class="lang-card reveal" href="library.html?lang=${esc(L.code)}">
      <span class="scriptmark" aria-hidden="true">${esc(L.native)}</span>
      <h3>${esc(t('lib.' + (L.code === 'urd' ? 'urdu' : 'sindhi')))}</h3>
      <p class="nm ${L.code === 'urd' ? 'f-urdu' : 'f-sindhi'}">${esc(L.native)}</p>
      <p style="color:var(--ink-mute);font-size:var(--t-sm);max-width:34ch">${esc(L.blurb)}</p>
      <ul>${byType.map(([label, n]) => `<li>${n} ${esc(label)}</li>`).join('')}</ul>
      <span class="go">${esc(t('lang.browse', { name: t('lib.' + (L.code === 'urd' ? 'urdu' : 'sindhi')), n: mine.length }))} ${ICONS.arrow}</span>
    </a>`;
  }).join('');
  };
  paintLangs();

  /* ---------------- rails ---------------- */
  const films = R.filter(r => r.type === 'film' && r.play && r.cover);
  const audio = R.filter(r => r.type === 'audio-bible' || r.type === 'audio');
  const read  = R.filter(r => r.type === 'scripture' || r.type === 'historic');
  const paintRails = () => {
    $('#filmRail').innerHTML  = pick(films, 12).map(card).join('');
    $('#audioRail').innerHTML = pick(audio, 12).map(card).join('');
    $('#readRail').innerHTML  = pick(read, 12).map(card).join('');
    $$('.rail .reveal').forEach(el => el.classList.remove('reveal'));
  };
  paintRails();

  /* ---------------- news ---------------- */
  const real = gw.images.filter(im => im.local && !im.demo);
  const imgFor = (p, i) => p.featured || real[(i * 3) % real.length]?.local;
  const paintNews = () => {
  $('#newsGrid').innerHTML = gw.posts.map((p, i) => `
    <a class="article reveal" href="news.html?p=${esc(p.slug)}">
      <span class="article-img"><img src="${esc(imgFor(p, i))}" alt="" loading="lazy"></span>
      <span class="article-body">
        <span class="meta">${esc(fmtDate(p.date))}</span>
        <h3${latinClass(postField(p,'title'))}>${esc(postField(p,'title'))}</h3>
        <p${latinClass(postField(p,'excerpt') || postField(p,'body'))}>${esc(postField(p,'excerpt') || postField(p,'body'))}</p>
        <span class="chip" style="align-self:flex-start;margin-top:.4rem">${esc(t('news.read'))}</span>
      </span>
    </a>`).join('');
  };
  paintNews();

  /* ---------------- gallery strip ---------------- */
  const shots = gw.images.filter(im => im.local && !im.demo && (im.w || 0) >= 600
      && !/logo|icon|favicon/i.test(im.title));
  $('#galleryStrip').innerHTML = pick(shots, 8).map(im => `
    <figure class="reveal" data-zoom="${esc(im.local)}" data-alt="${esc(im.alt || im.title)}"
            style="margin:0;border-radius:var(--r);overflow:hidden;aspect-ratio:4/3;cursor:zoom-in">
      <img src="${esc(im.localThumb || im.local)}" alt="${esc(im.alt || im.title)}" loading="lazy"
           style="width:100%;height:100%;object-fit:cover">
    </figure>`).join('');

  /* ---------------- programmes: the channel's own stills ---------------- */
  const progs = gw.programmes.map(p => ({
    ...p,
    src: gw.images.find(i => i.id === p.mediaId)?.local || p.image,
  }));
  const pName  = p => t(`prog.${p.stub}.name`)  || p.name;
  const pBlurb = p => t(`prog.${p.stub}.blurb`) || p.blurb;

  if (progs.length) {
    // the stills now sit behind the hero as a slow, dim rotation
    $('#heroBg').innerHTML = progs.map((p, i) =>
      `<img src="${esc(p.src)}" alt="" class="${i === 0 ? 'on' : ''}">`).join('');
    const bgImgs = $$('#heroBg img');
    let bg = 0;
    if (!matchMedia('(prefers-reduced-motion:reduce)').matches) {
      setInterval(() => {
        bg = (bg + 1) % bgImgs.length;
        bgImgs.forEach((el, n) => el.classList.toggle('on', n === bg));
      }, 7000);
    }
    const paintProgGrid = () => {
      $('#progGrid').innerHTML = progs.map(p => `
        <a class="prog-card reveal" href="schedule.html">
          <img src="${esc(p.src)}" alt="${esc(pName(p))}" loading="lazy">
          <span class="veil"></span>
          <span class="cap"><b>${esc(pName(p))}</b><span>${esc(pBlurb(p))}</span></span>
        </a>`).join('');
    };
    paintProgGrid();
    onLangChange(() => { paintProgGrid(); reveal(); });
  }

  /* ---------------- Gawahi Live: the YouTube channel as a broadcast ---------------- */
  try {
    const live = await loadLive();
    if (live.list.length) {
      let nowIndex = null;
      const paintLive = () => {
        const cur = nowIndex == null ? null : live.list[nowIndex];
        const title = $('#liveTitle');
        if (cur) { title.textContent = cur.title; title.className = 'live-title' + (latinClass(cur.title) ? ' latin' : ''); }
        const upcoming = listing(live, Date.now(), 4).slice(1);
        $('#liveNext').innerHTML = upcoming.map(v => `
          <li>
            <img src="${esc(thumb(v.id))}" alt="" loading="lazy">
            <span><time>${esc(fmtClock(v.start))}</time>
              <b${latinClass(v.title)}>${esc(v.title)}</b></span>
          </li>`).join('');
      };
      // poster straight away, so there is no black box while YouTube loads
      const first = listing(live, Date.now(), 1)[0];
      $('#liveScreen').style.backgroundImage = `url('https://i.ytimg.com/vi/${first.id}/hqdefault.jpg')`;
      nowIndex = first.index; paintLive();

      const ctl = await mountLive(live, 'livePlayer', {
        onProgramme: i => { nowIndex = i; paintLive(); },
        onMuted: m => { $('#liveSound').hidden = !m; },
        onDrift: d => { $('#liveBack').hidden = !d; },
        onFail: () => {
          $('#liveScreen').insertAdjacentHTML('beforeend',
            `<a class="live-fail" href="${esc(safeUrl(live.channel.url))}" target="_blank" rel="noopener">${esc(t('live.fail'))}</a>`);
        },
      });
      $('#liveSound').addEventListener('click', () => ctl && ctl.unmute());
      $('#liveBack').addEventListener('click', () => ctl && ctl.backToLive());
      setInterval(paintLive, 60000);          // keep "up next" times honest
      onLangChange(paintLive);
    }
  } catch (e) { console.warn('live channel unavailable', e); }

  mountSheet('body');
  reveal();

  onLangChange(() => {
    paintStats(); paintLangs(); paintNews(); paintRails();
    reveal();
  });
})();
