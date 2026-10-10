#!/usr/bin/env python3
"""Local preview server that behaves like the Vercel deployment: folder index pages, custom 404.html,
the redirects and the security headers (including the Content-Security-Policy) from vercel.json.

    python3 build/build.py && python3 build/serve.py [port]
"""
import http.server, json, os, sys, re, functools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
CFG = json.load(open(os.path.join(ROOT, 'vercel.json')))
HEADERS = [(h['key'], h['value']) for r in CFG['headers'] if r['source'] == '/(.*)' for h in r['headers']]
REDIRECTS = {r['source']: r['destination'] for r in CFG.get('redirects', []) if ':' not in r['source']}
FOLDER_REDIR = [r for r in CFG.get('redirects', []) if ':' in r['source']]

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=DIST, **k)
    def log_message(self, *a): pass
    def end_headers(self):
        for k, v in HEADERS: self.send_header(k, v)
        super().end_headers()
    def do_GET(self):
        path = self.path.split('?')[0]; qs = self.path[len(path):]
        dest = REDIRECTS.get(path)
        if dest:
            self.send_response(308); self.send_header('Location', dest + qs); self.end_headers(); return
        for r in FOLDER_REDIR:  # e.g. /:dir/index.html -> /:dir/
            pat = '^' + re.escape(r['source']).replace('\\:dir', '([^/]+)').replace('\\:path\\*', '(.*)') + '$'
            m = re.match(pat, path)
            if m: self.send_response(308); self.send_header('Location', r['destination'].replace(':dir', m.group(1)).replace(':path*', m.group(1)) + qs); self.end_headers(); return
        if CFG.get('cleanUrls') and path != '/':  # Vercel cleanUrls + trailingSlash:false
            if path.endswith('.html'): self.send_response(308); self.send_header('Location', (path[:-10] if path.endswith('/index.html') else path[:-5]) + qs); self.end_headers(); return
            if path.endswith('/') and CFG.get('trailingSlash') is False: self.send_response(308); self.send_header('Location', path.rstrip('/') + qs); self.end_headers(); return
        fs = self.translate_path(path)
        if os.path.isdir(fs) and not path.endswith('/') and os.path.isfile(os.path.join(fs, 'index.html')) and CFG.get('cleanUrls'):
            self.path = path + '/index.html' + qs; return super().do_GET()
        if os.path.isdir(fs) and not path.endswith('/'):
            self.send_response(308); self.send_header('Location', path + '/' + qs); self.end_headers(); return
        if not os.path.exists(fs) and not os.path.exists(fs + '.html' if CFG.get('cleanUrls') else fs):
            body = open(os.path.join(DIST, '404.html'), 'rb').read()
            self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body); return
        if CFG.get('cleanUrls') and not os.path.exists(fs) and os.path.exists(fs + '.html'): self.path = path + '.html' + qs
        return super().do_GET()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f'Serving dist/ at http://localhost:{port}/'); http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
