/* GAWAHI — broadcast schedule, built from the channel's programme strands */
import { $, $$, esc, reveal, loadJSON, t, onLangChange, i18nReady } from './app.js';

const STRANDS = [
  ['06:00', 'Both'],
  ['06:30', 'Urdu'],
  ['07:30', 'Sindhi'],
  ['08:00', 'Urdu'],
  ['09:00', 'Both'],
  ['10:00', 'Sindhi'],
  ['11:30', 'Urdu'],
  ['12:30', 'Urdu'],
  ['13:30', 'Sindhi'],
  ['14:30', 'Urdu'],
  ['15:30', 'Sindhi'],
  ['16:30', 'Both'],
  ['17:00', 'Urdu'],
  ['18:00', 'Urdu'],
  ['20:15', 'Urdu'],
  ['21:00', 'Sindhi'],
  ['22:00', 'Both'],
  ['22:30', 'Both'],
];

const DAY = i => t('day.' + i);

(async function init() {
  await i18nReady;
  const today = new Date().getDay();
  let day = today;

  const paintChrome = () => {
    $('#tzNote').textContent = t('sch.tz',
      { tz: Intl.DateTimeFormat().resolvedOptions().timeZone.replace(/_/g, ' ') });
    $('#daySeg').innerHTML = [0,1,2,3,4,5,6].map(i =>
      `<button data-d="${i}" aria-pressed="${i === day}">${esc(DAY(i).slice(0, 3))}</button>`).join('');
  };
  paintChrome();

  const nowMin = new Date().getHours() * 60 + new Date().getMinutes();
  const toMin = hhmm => +hhmm.slice(0, 2) * 60 + +hhmm.slice(3);

  function paint() {
    $('#dayName').textContent = day === today ? t('sch.today') : DAY(day);
    const rows = STRANDS.map(([time, spoken], i) => {
      const next = STRANDS[i + 1];
      const live = day === today && nowMin >= toMin(time) && (!next || nowMin < toMin(next[0]));
      const tag = spoken === 'Both' ? t('sch.both')
                : t('lib.' + (spoken === 'Urdu' ? 'urdu' : 'sindhi'));
      return `<div class="sched-row${live ? ' now' : ''}">
        <span class="sched-t">${esc(time)}</span>
        <span><span class="sched-n">${esc(t('prog' + i + '.name'))}</span>
              <span class="sched-d">${esc(t('prog' + i + '.desc'))}</span></span>
        <span class="chip${live ? ' chip-live' : ''}">${esc(live ? t('sch.now') : tag)}</span>
      </div>`;
    }).join('');
    $('#sched').innerHTML = rows;
  }

  $('#daySeg').addEventListener('click', e => {
    const b = e.target.closest('button[data-d]'); if (!b) return;
    day = +b.dataset.d;
    $$('#daySeg button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    paint();
  });

  paint(); reveal();
  onLangChange(() => { paintChrome(); paint(); });
})();
