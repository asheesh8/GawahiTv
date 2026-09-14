/* Minimal static file server for local preview:  node scripts/serve.mjs [port] */
import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, join, normalize, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

// Mirror production: apply the same headers vercel.json sends (CSP included), and
// its cleanUrls behaviour, so a policy that would break the live site breaks here.
const VERCEL = JSON.parse(await readFile(join(ROOT, 'vercel.json'), 'utf8'));
const toRe = src => new RegExp('^' + src.replace(/[.+^${}|[\]\\]/g, '\\$&')
  .replace(/\(([^)]*)\)/g, (m, g) => g === '.*' ? '(.*)' : `(${g})`) + '$');
const RULES = (VERCEL.headers || []).map(r => ({ re: toRe(r.source), headers: r.headers }));
const headersFor = path => Object.fromEntries(
  RULES.filter(r => r.re.test(path)).flatMap(r => r.headers.map(h => [h.key, h.value])));
const PORT = Number(process.argv[2] || 4173);
// --no-headers: serve without the production security headers. Only for the layout
// auditor, which lays pages out in same-origin iframes that frame-ancestors forbids.
const NO_HEADERS = process.argv.includes('--no-headers');
const TYPES = {
  '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8',
  '.js':'text/javascript; charset=utf-8', '.mjs':'text/javascript; charset=utf-8',
  '.json':'application/json; charset=utf-8', '.png':'image/png', '.jpg':'image/jpeg',
  '.jpeg':'image/jpeg', '.webp':'image/webp', '.svg':'image/svg+xml', '.gif':'image/gif',
  '.mp4':'video/mp4', '.mp3':'audio/mpeg', '.ico':'image/x-icon', '.pdf':'application/pdf',
};

http.createServer(async (req, res) => {
  try {
    let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    const reqPath = p;
    if (p.endsWith('/')) p += 'index.html';
    if (VERCEL.cleanUrls && !extname(p)) p += '.html';
    const file = join(ROOT, normalize(p).replace(/^(\.\.[/\\])+/, ''));
    if (!file.startsWith(ROOT)) { res.writeHead(403).end('Forbidden'); return; }
    const s = await stat(file);
    const body = await readFile(s.isDirectory() ? join(file, 'index.html') : file);
    res.writeHead(200, {
      ...(NO_HEADERS ? {} : headersFor(reqPath)),
      'Content-Type': TYPES[extname(file).toLowerCase()] || 'application/octet-stream',
      'Cache-Control': 'no-cache',
    }).end(body);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' })
       .end('<h1>404</h1><p><a href="/">Back to Gawahi</a></p>');
  }
}).listen(PORT, () => console.log(`Gawahi preview → http://localhost:${PORT}`));
