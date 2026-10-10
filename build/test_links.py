#!/usr/bin/env python3
"""Crawl the built site through build/serve.py (which mimics vercel.json: redirects, folder indexes, 404, clean URLs).

    python3 build/test_links.py [project_root]
Checks: every internal link / asset / sitemap URL / url-map URL answers 200 WITHOUT a redirect, canonical == requested URL,
legacy URLs 308 to their new URL, unknown URLs answer 404. Exit code 1 on any failure."""
import sys, os, re, csv, json, time, subprocess, urllib.request, urllib.error, urllib.parse, html
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get('PORT', 8769)); BASE = f'http://127.0.0.1:{PORT}'
srv = subprocess.Popen([sys.executable, os.path.join(ROOT, 'build', 'serve.py'), str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.0)
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedirect)
def get(path):
    try:
        r = op.open(BASE + path); return r.status, r.read().decode('utf8', 'replace'), dict(r.headers)
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf8', 'replace'), dict(e.headers)
fails = []; n = 0
def ok(c, m):
    global n; n += 1
    if not c: fails.append(m); print('FAIL', m)
cfg = json.load(open(os.path.join(ROOT, 'site.config.json'))); SITE = (os.environ.get('SITE_URL') or cfg['siteUrl']).rstrip('/')
try:
    seen = {}; queue = ['/']; assets = set()
    while queue:
        p = queue.pop(0)
        if p in seen: continue
        st, body, hd = get(p); seen[p] = st
        ok(st == 200, f'{p}: status {st}')
        if st != 200: continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', body)
        if m: ok(m.group(1) == SITE + p, f'{p}: canonical {m.group(1)} != {SITE + p}')
        for h in re.findall(r'<a [^>]*href="([^"]+)"', body):
            h = html.unescape(h)
            if h.startswith(('mailto:', 'tel:', '#', 'http')): continue
            q = h.split('#')[0].split('?')[0]
            if q and q not in seen: queue.append(q)
        for a in re.findall(r'<(?:script|link)[^>]*(?:src|href)="(/assets/[^"]+)"', body): assets.add(a)
    for a in sorted(assets):
        st, _, hd = get(a); ok(st == 200, f'asset {a}: {st}')
    sm = get('/sitemap.xml')[1]
    for loc in re.findall(r'<loc>(.*?)</loc>', sm):
        pth = loc.replace(SITE, ''); st, _, _ = get(pth); ok(st == 200, f'sitemap {pth}: {st}'); ok(pth in seen, f'sitemap URL {pth} is not linked from any page')
    ok(get('/robots.txt')[0] == 200 and get('/llms.txt')[0] == 200, 'robots.txt / llms.txt')
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'docs', 'url-map.csv'), encoding='utf8')))
    for r in rows:
        new = r['new_url']; st, _, _ = get(new); ok(st == 200 or new == '/404.html', f'url-map new_url {new}: {st}')
        leg = r['legacy_url (v3)']
        if leg.startswith('/') and leg != new:
            st, _, hd = get(leg); ok(st in (301, 308) and urllib.parse.urlparse(hd.get('Location', '')).path == new or st == 200 and leg == new, f'url-map legacy {leg}: {st} -> {hd.get("Location")} (expected {new})')
    for p in ['/does-not-exist', '/pdf-tools/nope', '/nonexistent-tool', '/random-page-123']:
        st, body, _ = get(p); ok(st == 404 and 'Page not found' in body, f'{p}: expected custom 404, got {st}')
    cs = [r['new_url'] for r in rows if r['new_url'] != '/404.html' and 'redirect' not in r['status'] and 'removed' not in r['status']]; ok(len(cs) == len(set(cs)), 'two live pages share one URL in url-map')
finally:
    srv.terminate()
print(f'link crawl: {len(seen)} pages, {len(assets)} assets, {n} checks, {len(fails)} failed (style={cfg.get("urlStyle")}, env URL_STYLE={os.environ.get("URL_STYLE")})')
sys.exit(1 if fails else 0)
