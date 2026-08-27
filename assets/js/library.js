/* GAWAHI — Resource Library: browse and filter; sheet.js does the playing. */

import { $, $$, esc, ICONS, reveal, loadJSON, t, onLangChange, i18nReady } from './app.js';

import { card, setData, openSheet, closeSheet, mountSheet } from './sheet.js';

let DATA = null, state = { lang: 'all', type: 'all', q: '' };

/* ------------------------------------------------------------------ filter */
function match(r) {
  if (state.lang !== 'all' && r.lang !== state.lang) return false;
  if (state.type !== 'all' && r.type !== state.type) return false;
  if (state.q) {
    const hay = [r.title, r.native, r.org, r.desc, r.typeLabel, r.langName, r.year]
      .filter(Boolean).join(' ').toLowerCase();
    if (!state.q.toLowerCase().split(/\s+/).every(term => hay.includes(term))) return false;
  }
  return true;
}

function render() {
  const rows = DATA.resources.filter(match);
  const grid = $('#grid');
  grid.innerHTML = rows.length
    ? rows.map(card).join('')
    : `<div class="empty" style="grid-column:1/-1">${ICONS.empty}
        <h3>${esc(t('lib.emptyTitle'))}</h3>
        <p>${esc(t('lib.emptyBody'))}</p>
        <button class="btn btn-o btn-sm" id="clearAll" style="margin-top:1rem">${esc(t('lib.clear'))}</button>
       </div>`;
  $('#count').textContent = t('lib.count', { n: rows.length, m: DATA.resources.length });
  $('#clearAll')?.addEventListener('click', () => {
    state = { lang: 'all', type: 'all', q: '' };
    $('#q').value = ''; syncControls(); render();
  });
  reveal(grid);
}

function counts(key, val) {
  return DATA.resources.filter(r => {
    const s = { ...state, [key]: val };
    if (s.lang !== 'all' && r.lang !== s.lang) return false;
    if (s.type !== 'all' && r.type !== s.type) return false;
    return true;
  }).length;
}

function syncControls() {
  $$('#langSeg button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.lang === state.lang)));
  $$('#typeChips .fchip').forEach(b => {
    b.setAttribute('aria-pressed', String(b.dataset.type === state.type));
    const n = b.querySelector('b'); if (n) n.textContent = counts('type', b.dataset.type);
  });
}

/* ------------------------------------------------------------------ boot */
(async function init() {
  await i18nReady;
  DATA = await loadJSON('data/resources.json');
  setData(DATA);

  const paintChips = () => {
    $('#typeChips').innerHTML = [['all', t('lib.everything')],
      ...Object.keys(DATA.types).map(k => [k, t('type.' + k)])]
      .map(([k, label]) => `<button class="fchip" data-type="${k}" aria-pressed="${k === state.type}">
          ${esc(label)} <b></b></button>`).join('');
  };
  paintChips();

  // pre-select from the URL before the first paint
  const qs = new URLSearchParams(location.search);
  const preLang = qs.get('lang'), preType = qs.get('type'), preQ = qs.get('q');
  if (preLang && DATA.languages[preLang]) state.lang = preLang;
  if (preType && DATA.types[preType])     state.type = preType;
  if (preQ) { state.q = preQ; $('#q').value = preQ; }

  $('#langSeg').addEventListener('click', e => {
    const b = e.target.closest('button[data-lang]'); if (!b) return;
    state.lang = b.dataset.lang; syncControls(); render();
  });
  $('#typeChips').addEventListener('click', e => {
    const b = e.target.closest('.fchip'); if (!b) return;
    state.type = b.dataset.type; syncControls(); render();
  });
  let searchTimer;
  $('#q').addEventListener('input', e => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { state.q = e.target.value.trim(); render(); }, 140);
  });

  mountSheet('#grid');
  syncControls(); render();

  onLangChange(() => { paintChips(); syncControls(); render(); });

  const deep = qs.get('r');
  if (deep) openSheet(deep, false);
})();
