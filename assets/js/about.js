/* GAWAHI — about page: library totals and partner credits */
import { $, esc, reveal, loadJSON, t, onLangChange, i18nReady } from './app.js';

(async function init() {
  await i18nReady;
  const res = await loadJSON('data/resources.json');
  const R = res.resources;

  const orgs = [...new Set(R.map(r => r.org).filter(Boolean))]
    .map(o => [o, R.filter(r => r.org === o).length])
    .sort((a, b) => b[1] - a[1]);

  const paint = () => {
    $('#aboutCount').textContent = t('about.count', { n: R.length });
    $('#partners').innerHTML = orgs.map(([name, n]) => `
      <div class="card reveal" style="padding:1.2rem 1.1rem;display:block">
        <h4 class="latin" style="font-size:var(--t-base);margin-bottom:.3rem">${esc(name)}</h4>
        <p class="meta">${n} ${esc(t(n === 1 ? 'about.res' : 'about.resPl'))}</p>
      </div>`).join('');
    reveal();
  };
  paint();
  onLangChange(paint);
})();
