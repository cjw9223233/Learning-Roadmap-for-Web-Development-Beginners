"""Loopback-only teaching server for observable Fetch success and failure."""
import argparse
import json
import mimetypes
import socket
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((Path(__file__).parent / 'data.json').read_text(encoding='utf-8'))


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *_args):
        pass

    def reply(self, status, body, content_type='application/json; charset=utf-8', delay_body=False):
        try:
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.flush()
            if delay_body:
                time.sleep(2.5)
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # A browser can stop receiving while the server is still working.
            pass

    def do_GET(self):
        request = urlsplit(self.path)
        if request.path == '/api/inspections':
            case = parse_qs(request.query).get('case', ['success'])[0]
            if case == 'disconnect':
                self.close_connection = True
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.connection.close()
                return
            if case == 'slow':
                time.sleep(2.5)
            status, value = 200, DATA
            if case == 'empty':
                value = {'version': 1, 'rows': []}
            elif case == 'not-found':
                status, value = 404, {'error': '教學用：找不到資源'}
            elif case == 'server-error':
                status, value = 500, {'error': '教學用：伺服器錯誤'}
            elif case == 'invalid-data':
                value = {'version': 1, 'rows': [{'id': 'x', 'equipment': '  ', 'result': '未知'}]}
            elif case == 'invalid-json':
                self.reply(200, b'{')
                return
            elif case not in {'success', 'slow', 'slow-body'}:
                status, value = 400, {'error': '未知練習情境'}
            body = json.dumps(value, ensure_ascii=False).encode('utf-8')
            self.reply(status, body, delay_body=case == 'slow-body')
            return
        if request.path == '/':
            self.send_response(302)
            self.send_header('Location', '/examples/fetch-lab/index.html')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        target = (ROOT / unquote(request.path).lstrip('/')).resolve()
        try:
            relative = target.relative_to(ROOT)
        except ValueError:
            self.reply(404, b'{"error":"not found"}')
            return
        allowed = relative.parts and (relative.parts[0] in {'assets', 'lessons', 'examples'} or str(relative) in {'index.html', 'README.md', '教材.md'})
        if not allowed or any(p.startswith('.') for p in relative.parts) or target.suffix not in {'.html', '.css', '.js', '.json', '.md', '.png'} or not target.is_file():
            self.reply(404, b'{"error":"not found"}')
            return
        types = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.md': 'text/plain; charset=utf-8'}
        self.reply(200, target.read_bytes(), types.get(target.suffix, mimetypes.guess_type(str(target))[0] or 'application/octet-stream'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}/examples/fetch-lab/index.html'}), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
