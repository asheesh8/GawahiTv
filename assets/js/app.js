/* GAWAHI — shared behaviour: icons, header, theme, reveal, small helpers */
import { i18nReady, t, onLangChange, lang } from './i18n.js';
export { t, onLangChange, lang, i18nReady };
export const $  = (s, r = document) => r.querySelector(s);
export const $$ = (s, r = document) => [...r.querySelectorAll(s)];
/** Only http(s) and same-site relative URLs survive; anything else (javascript:,
 *  data:, vbscript:) becomes "#". Escaping alone does not stop a javascript:
 *  href from running, so every URL that comes from data goes through this. */
export function safeUrl(u) {
  if (u == null || u === '') return '#';
  try {
    const x = new URL(String(u), location.href);
    return x.protocol === 'https:' || x.protocol === 'http:' ? x.href : '#';
  } catch { return '#'; }
}
/** For CSS url(): the HTML parser decodes &#39; back to a quote before CSS sees
 *  it, so HTML-escaping is not enough — percent-encode the breakout characters. */
export const cssUrl = u => safeUrl(u).replace(/["'()\\\s<>]/g,
  c => '%' + c.charCodeAt(0).toString(16).toUpperCase().padStart(2, '0'));

export const esc = s => String(s ?? '').replace(/[&<>"']/g, c =>
  ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));

export const ICONS = {
  play:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.14v13.72a1 1 0 0 0 1.54.84l10.3-6.86a1 1 0 0 0 0-1.68L9.54 4.3A1 1 0 0 0 8 5.14Z"/></svg>',
  search:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
  download:'<svg viewBox="0 0 24 24"><path d="M12 3v12m0 0 4.5-4.5M12 15l-4.5-4.5M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>',
  external:'<svg viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
  arrow:'<svg viewBox="0 0 24 24"><path d="M5 12h14m0 0-6-6m6 6-6 6"/></svg>',
  close:'<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg>',
  menu:'<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  sun:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>',
  moon:'<svg viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>',
  film:'<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 12h18M3 8h4m10 0h4M3 16h4m10 0h4"/></svg>',
  audio:'<svg viewBox="0 0 24 24"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="M16 9a4 4 0 0 1 0 6m2.5-8.5a7 7 0 0 1 0 11"/></svg>',
  wave:'<svg viewBox="0 0 24 24"><path d="M3 12h2m3-5v10m4-14v18m4-13v8m4-5v2m3-2v2"/></svg>',
  book:'<svg viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5Z"/><path d="M8 7h7M8 11h7"/></svg>',
  scan:'<svg viewBox="0 0 24 24"><path d="M4 8V5a1 1 0 0 1 1-1h3M4 16v3a1 1 0 0 0 1 1h3m8-16h3a1 1 0 0 1 1 1v3m0 8v3a1 1 0 0 1-1 1h-3"/><path d="M8 8h8v8H8z"/></svg>',
  link:'<svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
  empty:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5M8 11h6"/></svg>',
};

/* ---------- theme: system → light → dark, persisted ---------- */
function initTheme() {
  const KEY = 'gawahi-theme';
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch {}
  if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved;

  const btn = $('#themeBtn');
  if (!btn) return;
  const paint = () => {
    const dark = document.documentElement.dataset.theme === 'dark' ||
      (!document.documentElement.dataset.theme &&
        matchMedia('(prefers-color-scheme:dark)').matches);
    btn.innerHTML = dark ? ICONS.sun : ICONS.moon;
  };
  paint();
  btn.addEventListener('click', () => {
    const dark = document.documentElement.dataset.theme === 'dark' ||
      (!document.documentElement.dataset.theme &&
        matchMedia('(prefers-color-scheme:dark)').matches);
    const next = dark ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem(KEY, next); } catch {}
    paint();
  });
}

/* ---------- header ---------- */
function initHeader() {
  const nav = $('#nav'), burger = $('#burger');
  if (burger && nav) {
    burger.innerHTML = ICONS.menu;
    burger.addEventListener('click', () => {
      const open = nav.hasAttribute('data-open');
      nav.toggleAttribute('data-open', !open);
      burger.setAttribute('aria-expanded', String(!open));
      burger.innerHTML = open ? ICONS.menu : ICONS.close;
    });
    nav.addEventListener('click', e => {
      if (e.target.closest('#langSwitch')) return;
      if (e.target.closest('a')) {
        nav.removeAttribute('data-open');
        burger.setAttribute('aria-expanded', 'false');
        burger.innerHTML = ICONS.menu;
      }
    });
  }
  /* Below ~600px the bar cannot hold the wordmark, three languages, the theme
     toggle and the menu button at once. Move the switcher into the drawer, where
     each language can keep its full native label. */
  const narrow = matchMedia('(max-width:600px)');
  const placeSwitcher = () => {
    const sw = document.getElementById('langSwitch');
    if (!sw || !nav) return;
    const inNav = sw.parentElement === nav;
    if (narrow.matches && !inNav) { nav.appendChild(sw); sw.dataset.inNav = ''; }
    else if (!narrow.matches && inNav) {
      document.querySelector('.hdr-act')?.prepend(sw); delete sw.dataset.inNav;
    }
  };
  placeSwitcher();
  narrow.addEventListener?.('change', placeSwitcher);
  addEventListener('resize', placeSwitcher, { passive: true });

  // Vercel's cleanUrls serves /library for library.html, so compare without the
  // extension and treat an empty path as the home page.
  const page = p => (p.split('/').pop() || 'index').replace(/\.html$/, '') || 'index';
  const here = page(location.pathname);
  $$('#nav a').forEach(a => {
    if (page(a.getAttribute('href') || '') === here) a.setAttribute('aria-current', 'page');
  });
}

/* ---------- reveal on scroll ---------- */
export function reveal(root = document) {
  const els = $$('.reveal:not(.in)', root);
  if (!els.length) return;
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion:reduce)').matches) {
    els.forEach(e => e.classList.add('in')); return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en, i) => {
      if (!en.isIntersecting) return;
      setTimeout(() => en.target.classList.add('in'), Math.min(i * 55, 260));
      io.unobserve(en.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: .06 });
  els.forEach(e => io.observe(e));
}

/* ---------- lightbox ---------- */
export function initLightbox() {
  let box = $('#lightbox');
  if (!box) {
    box = document.createElement('div');
    box.id = 'lightbox'; box.className = 'lightbox';
    box.innerHTML = `<button class="icon-btn x" aria-label="Close">${ICONS.close}</button><img alt="">`;
    document.body.appendChild(box);
  }
  const img = $('img', box);
  const close = () => { box.removeAttribute('data-open'); document.body.style.overflow = ''; };
  box.addEventListener('click', e => { if (e.target === box || e.target.closest('.x')) close(); });
  addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  document.addEventListener('click', e => {
    const fig = e.target.closest('[data-zoom]');
    if (!fig) return;
    img.src = fig.dataset.zoom; img.alt = fig.dataset.alt || '';
    box.setAttribute('data-open', ''); document.body.style.overflow = 'hidden';
  });
}

export async function loadJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  return r.json();
}

/** True when a string is predominantly Latin script — used to decide whether a
 *  piece of CONTENT (article title, body, resource name) should be set in the
 *  Latin face and read left-to-right, regardless of the interface language.
 *  Article text comes from WordPress and may be English or Urdu; this keeps
 *  either one set correctly instead of forcing the UI font onto it. */
export function isLatinText(str) {
  const s = String(str || '');
  const latin  = (s.match(/[A-Za-z]/g) || []).length;
  const arabic = (s.match(/[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/g) || []).length;
  return latin > arabic;
}

/** Returns ' class="latin"' when the text should be set as Latin, else ''. */
export function latinClass(str, extra = '') {
  const base = isLatinText(str) ? 'latin' : '';
  const cls = [base, extra].filter(Boolean).join(' ');
  return cls ? ` class="${cls}"` : '';
}

/** Content field for a post in the current interface language, falling back to
 *  the original English when no translation exists for that field. */
export function postField(post, field) {
  const tr = post?.i18n?.[lang()];
  return (tr && tr[field]) || post?.[field] || '';
}

export function fmtDate(iso) {
  const locale = { en: 'en-GB', ur: 'ur-PK', sd: 'sd-PK' }[lang()] || 'en-GB';
  try {
    return new Date(iso + 'T00:00:00')
      .toLocaleDateString(locale, { day: 'numeric', month: 'short', year: 'numeric' });
  } catch { return iso; }
}

function paintFooter() {
  const el = document.getElementById('ftrRights');
  if (el) el.textContent = t('ftr.rights', { y: new Date().getFullYear() });
  const yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
}

/* Broken artwork hides itself. Replaces the old inline onerror="" handler, which a
   strict script CSP would block. Error events don't bubble, so listen in capture. */
document.addEventListener('error', e => {
  const el = e.target;
  if (el && el.tagName === 'IMG' && el.hasAttribute('data-hide-on-error')) el.remove();
}, true);

initTheme(); initHeader();
i18nReady.then(() => { paintFooter(); onLangChange(paintFooter); });
document.addEventListener('DOMContentLoaded', () => { reveal(); initLightbox(); });
if (document.readyState !== 'loading') { reveal(); initLightbox(); }
