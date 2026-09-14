/* GAWAHI — news list, single story, and the full gallery */
import { $, $$, esc, ICONS, reveal, loadJSON, fmtDate, t, onLangChange, i18nReady,
         latinClass, postField, safeUrl } from './app.js';

(async function init() {
  await i18nReady;
  const gw = await loadJSON('data/gawahi.json');
  // translate category names by slug, falling back to the WordPress name
  const cats = Object.fromEntries(gw.categories.map(c => [c.id, c]));
  const catName = id => cats[id] ? (t('cat.' + cats[id].slug) === 'cat.' + cats[id].slug
    ? cats[id].name : t('cat.' + cats[id].slug)) : null;

  const shots = gw.images.filter(im => im.local && !im.demo && (im.w || 0) >= 500
    && !/logo|icon|favicon/i.test(im.title));
  const imgFor = (p, i) => p.featured || shots[(i * 5) % shots.length]?.local;

  /* ---- single story view (?p=slug) ---- */
  const slug = new URLSearchParams(location.search).get('p');
  const post = slug && gw.posts.find(p => p.slug === slug);
  const paintSingle = () => {
    if (!post) return;
    const single = $('#single');
    single.hidden = false;
    single.innerHTML = `
      <a class="btn btn-ghost btn-sm" href="news.html" style="margin-bottom:1.2rem">${esc(t('news.back'))}</a>
      <article style="max-width:720px">
        <p class="meta">${esc(fmtDate(post.date))}
          ${(post.categories || []).map(catName).filter(Boolean)
            .map(n => `<span class="chip">${esc(n)}</span>`).join('')}</p>
        <h1${latinClass(postField(post,'title'))} style="font-size:var(--t-2xl);margin:.5rem 0 1rem">${esc(postField(post,'title'))}</h1>
        ${imgFor(post, 0) ? `<img src="${esc(imgFor(post, 0))}" alt=""
            style="border-radius:var(--r);margin-bottom:1.5rem;width:100%">` : ''}
        <div${latinClass(postField(post,'body'))} style="font-size:var(--t-md);color:var(--ink-soft)">
          ${postField(post,'body').split(/\n{2,}|(?<=\.)\s+(?=[A-Z])/).filter(Boolean).reduce((acc, s, i) => {
            const p = Math.floor(i / 3); (acc[p] ||= []).push(s); return acc;
          }, []).map(par => `<p>${esc(par.join(' '))}</p>`).join('')}
        </div>
        <p style="margin-top:2rem"><a class="btn btn-o btn-sm" href="${esc(safeUrl(post.link))}"
           target="_blank" rel="noopener">${ICONS.external} ${esc(t('news.onsite'))}</a></p>
      </article>
      <hr style="margin:3rem 0;border:0;border-top:1px solid var(--line)">
      <h2 style="font-size:var(--t-xl);margin-bottom:1.2rem">${esc(t('news.more'))}</h2>`;
  };
  paintSingle();

  /* ---- list ---- */
  const list = post ? gw.posts.filter(p => p.slug !== slug) : gw.posts;
  const paintList = () => {
  $('#posts').innerHTML = list.map((p, i) => `
    <a class="article reveal" href="news.html?p=${esc(p.slug)}">
      <span class="article-img"><img src="${esc(imgFor(p, i + 1))}" alt="" loading="lazy"></span>
      <span class="article-body">
        <span class="meta">${esc(fmtDate(p.date))}
          ${(p.categories || []).map(catName).filter(Boolean)
            .map(n => `<span class="chip">${esc(n)}</span>`).join('')}</span>
        <h3${latinClass(postField(p,'title'))}>${esc(postField(p,'title'))}</h3>
        <p${latinClass(postField(p,'excerpt') || postField(p,'body'))}>${esc(postField(p,'excerpt') || postField(p,'body'))}</p>
      </span>
    </a>`).join('');
  };
  paintList();

  /* ---- gallery ---- */
  const paintCount = () => { $('#galCount').textContent = t('gal.count', { n: shots.length }); };
  paintCount();
  $('#gallery-grid').innerHTML = shots.map(im => `
    <figure data-zoom="${esc(im.local)}" data-alt="${esc(im.alt || im.title)}">
      <img src="${esc(im.localThumb || im.local)}" alt="${esc(im.alt || im.title)}" loading="lazy">
    </figure>`).join('');

  reveal();
  onLangChange(() => { paintSingle(); paintList(); paintCount(); reveal(); });
})();
