/* GAWAHI — schedule, read from the same timeline the live channel plays.
   "On now" here is exactly what is on the home page at this moment. */
import { $, $$, esc, reveal, t, onLangChange, i18nReady, latinClass } from './app.js';
import { loadLive, listing, fmtClock, thumb } from './live.js';

const DAY = i => t('day.' + i);
const ROWS = 24;

(async function init() {
  await i18nReady;
  const live = await loadLive();
  const today = new Date().getDay();
  let day = today;

  const paintChrome = () => {
    $('#tzNote').textContent = t('sch.tz',
      { tz: Intl.DateTimeFormat().resolvedOptions().timeZone.replace(/_/g, ' ') });
    $('#daySeg').innerHTML = [0,1,2,3,4,5,6].map(i =>
      `<button data-d="${i}" aria-pressed="${i === day}">${esc(DAY(i).slice(0, 3))}</button>`).join('');
  };

  // Today lists from whatever is on now; any other day, from 06:00 that day.
  const fromFor = d => {
    const now = new Date();
    if (d === today) return now.getTime();
    const target = new Date(now);
    target.setDate(now.getDate() + ((d - today + 7) % 7));
    target.setHours(6, 0, 0, 0);
    return target.getTime();
  };

  function paint() {
    $('#dayName').textContent = day === today ? t('sch.today') : DAY(day);
    const rows = listing(live, fromFor(day), ROWS);
    const nowMs = Date.now();
    $('#sched').innerHTML = rows.map(v => {
      const on = nowMs >= v.start && nowMs < v.start + v.len * 1000;
      const mins = Math.max(1, Math.round(v.len / 60));
      return `<div class="sched-row${on ? ' now' : ''}">
        <span class="sched-t">${esc(fmtClock(v.start))}</span>
        <span class="sched-prog">
          <img src="${esc(thumb(v.id))}" alt="" loading="lazy">
          <span><span class="sched-n${latinClass(v.title) ? ' latin' : ''}">${esc(v.title)}</span>
            <span class="sched-d">${esc(t('sch.dur', { m: mins }))}</span></span>
        </span>
        <span class="chip${on ? ' chip-live' : ''}">${esc(on ? t('sch.now') : fmtClock(v.start + v.len * 1000))}</span>
      </div>`;
    }).join('');
  }

  $('#daySeg').addEventListener('click', e => {
    const b = e.target.closest('button[data-d]'); if (!b) return;
    day = +b.dataset.d;
    $$('#daySeg button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    paint();
  });

  paintChrome(); paint(); reveal();
  setInterval(paint, 60000);
  onLangChange(() => { paintChrome(); paint(); });
})();
