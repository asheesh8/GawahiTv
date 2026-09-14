/* GAWAHI Live — the channel's YouTube uploads played as a continuous broadcast.
 *
 * Every visitor computes the same position from the clock: the playlist loops
 * forever from a fixed anchor, so two people opening the site at the same moment
 * see the same programme at the same second, exactly like a TV channel. The
 * schedule page reads the same timeline, so "On now" there is what is actually
 * on here. Playlist data comes from scripts/build_youtube.py.
 */
import { loadJSON } from './app.js';

const ANCHOR = Date.UTC(2026, 0, 1);   // the moment the loop began
const UNKNOWN_LEN = 240;               // short clips the channel page lists without a length
const ID_RE = /^[A-Za-z0-9_-]{11}$/;

export async function loadLive() {
  const d = await loadJSON('data/youtube.json');
  const list = (d.videos || [])
    .filter(v => ID_RE.test(v.id))
    .map(v => ({ ...v, len: v.duration || UNKNOWN_LEN }));
  return { channel: d.channel, list, total: list.reduce((a, v) => a + v.len, 0) };
}

/** Which programme is on at a given moment, and how far into it. */
export function at(live, ms = Date.now()) {
  let t = Math.floor((ms - ANCHOR) / 1000) % live.total;
  if (t < 0) t += live.total;
  for (let i = 0; i < live.list.length; i++) {
    if (t < live.list[i].len) return { index: i, offset: t, startsAt: ms - t * 1000 };
    t -= live.list[i].len;
  }
  return { index: 0, offset: 0, startsAt: ms };
}

/** The running order from whatever is on at `fromMs`, with start times. */
export function listing(live, fromMs, count) {
  const cur = at(live, fromMs);
  const out = [];
  let start = cur.startsAt, i = cur.index;
  for (let n = 0; n < count; n++) {
    out.push({ ...live.list[i], start, index: i });
    start += live.list[i].len * 1000;
    i = (i + 1) % live.list.length;
  }
  return out;
}

export const thumb = id => `https://i.ytimg.com/vi/${id}/mqdefault.jpg`;
export const fmtClock = ms => new Date(ms).toLocaleTimeString('en-GB',
  { hour: '2-digit', minute: '2-digit', hour12: false });
export const fmtLen = s => s >= 3600
  ? `${Math.floor(s / 3600)}:${String(Math.floor(s % 3600 / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
  : `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

/* ---------------------------------------------------------------- player */
let apiPromise = null;
function loadYouTubeAPI() {
  if (window.YT && window.YT.Player) return Promise.resolve(window.YT);
  if (apiPromise) return apiPromise;
  apiPromise = new Promise((resolve, reject) => {
    const prev = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => { prev && prev(); resolve(window.YT); };
    const s = document.createElement('script');
    s.src = 'https://www.youtube.com/iframe_api';
    s.async = true;
    s.onerror = () => reject(new Error('YouTube API blocked'));
    document.head.appendChild(s);
  });
  return apiPromise;
}

/**
 * Mount the live channel into `mountId`. Callbacks let the page paint the
 * "now playing / up next" chrome in the current interface language.
 */
export async function mountLive(live, mountId, { onProgramme, onMuted, onDrift, onFail } = {}) {
  let cur = at(live);
  let player, current = cur.index, failures = 0, driftTimer;

  const play = (index, offset) => {
    current = index;
    onProgramme && onProgramme(index);
    player.loadVideoById({ videoId: live.list[index].id, startSeconds: offset });
  };
  // At the end of a programme, rejoin the clock. If our length estimate for
  // the one that just ended was too long the clock still points at it, so
  // step forward instead of replaying it.
  const next = () => {
    const now = at(live);
    if (now.index === current) play((current + 1) % live.list.length, 0);
    else play(now.index, now.offset);
  };

  let YT;
  try { YT = await loadYouTubeAPI(); }
  catch (e) { onFail && onFail(e); return null; }

  player = new YT.Player(mountId, {
    host: 'https://www.youtube-nocookie.com',
    videoId: live.list[cur.index].id,
    playerVars: {
      autoplay: 1, mute: 1, start: cur.offset, playsinline: 1,
      rel: 0, modestbranding: 1, iv_load_policy: 3, controls: 1,
      origin: location.origin,
    },
    events: {
      onReady: e => { e.target.mute(); e.target.playVideo(); onProgramme && onProgramme(cur.index); onMuted && onMuted(true); },
      onStateChange: e => {
        clearTimeout(driftTimer);
        if (e.data === YT.PlayerState.ENDED) next();
        if (e.data === YT.PlayerState.PLAYING) { failures = 0; onDrift && onDrift(false); }
        // YouTube pauses for a beat while it loads; only a pause that sticks is the viewer's
        if (e.data === YT.PlayerState.PAUSED) driftTimer = setTimeout(() => onDrift && onDrift(true), 1500);
      },
      // 100/101/150: removed, private or embedding disabled — skip it
      onError: () => { if (++failures > live.list.length) { onFail && onFail(); return; } play((current + 1) % live.list.length, 0); },
    },
  });

  return {
    // also starts playback, for phones that refused muted autoplay
    unmute() { player.unMute(); player.setVolume(100); player.playVideo(); onMuted && onMuted(false); },
    backToLive() { const n = at(live); play(n.index, n.offset); player.playVideo(); onDrift && onDrift(false); },
    get index() { return current; },
  };
}
