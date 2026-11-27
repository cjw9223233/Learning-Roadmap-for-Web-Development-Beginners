import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';

const portIndex = process.argv.indexOf('--port');
const port = portIndex < 0 ? 8080 : Number(process.argv[portIndex + 1]);
if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('連接埠須為 0–65535 的整數');
const server = createServer(async (request, response) => {
  if (request.method !== 'GET') { response.writeHead(405, { Allow: 'GET' }); response.end(); return; }
  let file;
  try { file = decodeURIComponent(new URL(request.url, 'http://127.0.0.1').pathname).slice(1) || 'index.html'; }
  catch { response.writeHead(400); response.end('Bad path'); return; }
  if (file !== 'index.html' && file !== 'THIRD_PARTY_NOTICES.txt' && !/^assets\/[A-Za-z0-9_-]+\.(?:js|css)$/.test(file)) { response.writeHead(404); response.end('Not found'); return; }
  try {
    const body = await readFile(new URL('./dist/' + file, import.meta.url));
    response.writeHead(200, { 'Content-Type': (file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : file.endsWith('.txt') ? 'text/plain' : 'text/html; charset=utf-8'), 'Content-Length': body.length, 'Cache-Control': 'no-store' });
    response.end(body);
  } catch { response.writeHead(500); response.end('Unable to read teaching file'); }
});
server.on('error', error => { console.error('無法啟動本機服務：' + error.message); process.exitCode = 1; });
server.listen(port, '127.0.0.1', () => console.log(JSON.stringify({ url: `http://127.0.0.1:${server.address().port}/` })));
