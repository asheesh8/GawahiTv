/* GAWAHI — interface translation (English / Urdu / Sindhi) with RTL support.
   Static copy is marked up with data-i18n attributes; dynamic strings call t(). */

const KEY = 'gawahi-lang';
const FALLBACK = 'en';

let STRINGS = null, META = null, current = FALLBACK;
const listeners = new Set();

export const langs = () => META;
export const lang = () => current;

/** Translate a key, interpolating {placeholders}. */
export function t(key, vars) {
  const table = (STRINGS && STRINGS[current]) || {};
  let s = table[key];
  if (s == null) s = (STRINGS?.[FALLBACK] || {})[key];
  if (s == null) return key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.split(`{${k}}`).join(v);
  return s;
}

/** Re-run whenever the language changes (page scripts redraw dynamic content). */
export function onLangChange(fn) { listeners.add(fn); return () => listeners.delete(fn); }

function detect() {
  try { const s = localStorage.getItem(KEY); if (s && ['en', 'ur', 'sd'].includes(s)) return s; } catch {}
  const nav = (navigator.languages || [navigator.language || '']).join(',').toLowerCase();
  if (/\bur\b|urdu/.test(nav)) return 'ur';
  if (/\bsd\b|sindhi/.test(nav)) return 'sd';
  return FALLBACK;
}

/** Apply every data-i18n binding inside root. */
export function applyI18n(root = document) {
  root.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  root.querySelectorAll('[data-i18n-html]').forEach(el => {
    el.innerHTML = t(el.dataset.i18nHtml);
  });
  root.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.setAttribute('placeholder', t(el.dataset.i18nPlaceholder));
  });
  root.querySelectorAll('[data-i18n-aria]').forEach(el => {
    el.setAttribute('aria-label', t(el.dataset.i18nAria));
  });
  root.querySelectorAll('[data-i18n-title]').forEach(el => {
    el.setAttribute('title', t(el.dataset.i18nTitle));
  });
}

function paintDocument() {
  const m = META[current];
  const html = document.documentElement;
  html.lang = m.code;
  html.dir = m.dir;
  html.dataset.font = m.font;
  applyI18n();
  document.querySelectorAll('[data-lang-opt]').forEach(b =>
    b.setAttribute('aria-pressed', String(b.dataset.langOpt === current)));
}

export async function setLang(code) {
  if (!META[code] || code === current) return;
  current = code;
  try { localStorage.setItem(KEY, code); } catch {}
  paintDocument();
  listeners.forEach(fn => { try { fn(code); } catch (e) { console.error(e); } });
}

/** Build the header switcher. */
function mountSwitcher() {
  const host = document.getElementById('langSwitch');
  if (!host) return;
  host.innerHTML = Object.entries(META).map(([code, m]) =>
    `<button type="button" data-lang-opt="${code}" lang="${m.code}"
       aria-pressed="${code === current}" title="${m.name}">${m.native}</button>`).join('');
  host.addEventListener('click', e => {
    const b = e.target.closest('[data-lang-opt]');
    if (b) setLang(b.dataset.langOpt);
  });
}

export const i18nReady = (async () => {
  const res = await fetch('data/i18n.json');
  const data = await res.json();
  META = data.meta;
  STRINGS = { en: data.en, ur: data.ur, sd: data.sd };
  current = detect();
  mountSwitcher();
  paintDocument();
  return current;
})();
