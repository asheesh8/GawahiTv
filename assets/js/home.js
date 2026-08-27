/* GAWAHI — home page composition */
import { $, $$, esc, ICONS, reveal, loadJSON, fmtDate, t, onLangChange, i18nReady,
         latinClass, postField } from './app.js';
import { card, setData, mountSheet } from './sheet.js';

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
    // rotating hero backdrop
    $('#heroBg').innerHTML = progs.map((p, i) =>
      `<img src="${esc(p.src)}" alt="" class="${i === 0 ? 'on' : ''}">`).join('');
    // featured panel
    const panel = $('#progPanel');
    panel.insertAdjacentHTML('afterbegin', progs.map((p, i) =>
      `<img src="${esc(p.src)}" alt="${esc(p.name)}" class="${i === 0 ? 'on' : ''}">`).join(''));
    $('#progDots').innerHTML = progs.map((p, i) =>
      `<button role="tab" data-i="${i}" aria-pressed="${i === 0}"
        aria-label="${esc(p.name)}"></button>`).join('');

    const bgImgs = $$('#heroBg img'), panelImgs = $$('#progPanel > img');
    let cur = 0, timer;
    const show = i => {
      cur = i;
      bgImgs.forEach((el, n) => el.classList.toggle('on', n === i));
      panelImgs.forEach((el, n) => el.classList.toggle('on', n === i));
      $$('#progDots button').forEach((b, n) => b.setAttribute('aria-pressed', String(n === i)));
      $('#progName').textContent = pName(progs[i]);
      $('#progBlurb').textContent = pBlurb(progs[i]);
    };
    const start = () => {
      if (matchMedia('(prefers-reduced-motion:reduce)').matches) return;
      timer = setInterval(() => show((cur + 1) % progs.length), 5200);
    };
    $('#progDots').addEventListener('click', e => {
      const b = e.target.closest('button[data-i]'); if (!b) return;
      clearInterval(timer); show(+b.dataset.i); start();
    });
    panel.addEventListener('mouseenter', () => clearInterval(timer));
    panel.addEventListener('mouseleave', start);
    show(0); start();

    // grid of every programme
    const paintProgGrid = () => {
      $('#progGrid').innerHTML = progs.map(p => `
        <a class="prog-card reveal" href="schedule.html">
          <img src="${esc(p.src)}" alt="${esc(pName(p))}" loading="lazy">
          <span class="veil"></span>
          <span class="cap"><b>${esc(pName(p))}</b><span>${esc(pBlurb(p))}</span></span>
        </a>`).join('');
    };
    paintProgGrid();
    onLangChange(() => { show(cur); paintProgGrid(); reveal(); });
  }

  mountSheet('body');
  reveal();

  onLangChange(() => {
    paintStats(); paintLangs(); paintNews(); paintRails();
    reveal();
  });
})();
