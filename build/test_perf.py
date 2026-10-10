#!/usr/bin/env python3
"""Performance checks (Playwright + Chromium): layout shift (CLS), requests and transfer size per page, which scripts load where.
Uses 4x CPU throttling and a slow-network profile for the CLS runs. Lighthouse is not run (not available here)."""
import json, os, sys, subprocess, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PORT = 8767; BASE = f'http://127.0.0.1:{PORT}'
srv = subprocess.Popen([sys.executable, os.path.join(ROOT, 'build', 'serve.py'), str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.0)
CLS_JS = """() => new Promise(r => { let v = 0; new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) v += e.value; }).observe({type:'layout-shift', buffered:true});
  setTimeout(() => r(v), 1500); })"""
PAGES = ['/', '/tools/', '/pdf-tools/compress-pdf.html', '/pdf-tools/merge-pdf.html', '/pdf-tools/pdf-to-images.html', '/image-tools/image-resizer.html', '/qr-tools/url-qr-code.html',
         '/unit-converter/weight.html', '/calculators/vat-calculator.html', '/cv-builder/', '/social-media-tools/hashtag-generator.html', '/about.html', '/privacy.html', '/pdf-tools/']
R = {'cls': {}, 'weight': {}, 'failures': []}
def fail(m): R['failures'].append(m); print('FAIL', m)
try:
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for (w, h, mobile) in [(390, 844, True), (1280, 800, False)]:
            for path in PAGES:
                ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=mobile); pg = ctx.new_page()
                cdp = ctx.new_cdp_session(pg); cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
                cdp.send('Network.enable'); cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 150, 'downloadThroughput': 1.6e6 / 8, 'uploadThroughput': 750e3 / 8})
                pg.add_init_script("window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});")
                pg.goto(BASE + path, wait_until='load'); pg.wait_for_timeout(1500)
                cls = pg.evaluate('window.__cls'); R['cls'][f'{path}@{w}'] = round(cls, 4)
                if cls > 0.02: fail(f'CLS {cls:.3f} on {path} at {w}px (limit 0.02)')
                ctx.close()
        for path in PAGES:
            ctx = br.new_context(viewport={'width': 1280, 'height': 800}); pg = ctx.new_page(); sizes = {}
            pg.on('response', lambda r: sizes.__setitem__(r.url, len(r.body()) if r.ok else 0) if r.url.startswith(BASE) else None)
            pg.goto(BASE + path, wait_until='load'); pg.wait_for_timeout(500)
            tot = {'js': 0, 'css': 0, 'html': 0, 'other': 0}; files = {}
            for u, n in sizes.items():
                u = u.split('?')[0]
                k = 'js' if u.endswith('.js') else 'css' if u.endswith('.css') else 'html' if not os.path.splitext(u)[1] or u.endswith('.html') else 'other'; tot[k] += n; files[u.replace(BASE, '')] = n
            R['weight'][path] = {'total': sum(tot.values()), **tot, 'requests': len(sizes), 'files': files}; ctx.close()
        # libraries must load only where needed (before any file is added)
        for path, forbidden in [('/', ['vendor']), ('/unit-converter/weight.html', ['vendor']), ('/pdf-tools/compress-pdf.html', ['qrcode', 'pdf.min', 'jszip']), ('/qr-tools/url-qr-code.html', ['pdf-lib', 'pdf.min', 'jszip', 'pdf-workspace']),
                                ('/image-tools/image-resizer.html', ['vendor', 'pdf-workspace'])]:
            f = ' '.join(R['weight'][path]['files']) if path in R['weight'] else ''
            if not f:
                ctx = br.new_context(); pg = ctx.new_page(); seen = []; pg.on('request', lambda r: seen.append(r.url)); pg.goto(BASE + path); pg.wait_for_timeout(500); f = ' '.join(seen); ctx.close()
            for x in forbidden:
                if x in f: fail(f'{path} loads {x}')
        br.close()
finally:
    srv.terminate()
json.dump(R, open(os.path.join(ROOT, 'build', 'perf-report.json'), 'w'), indent=1)
print('CLS (max):', max(R['cls'].values()), '| failures:', len(R['failures']))
for p, v in R['weight'].items(): print(f"{p:50s} {v['total']/1024:7.1f} KB  js {v['js']/1024:6.1f}  css {v['css']/1024:5.1f}  html {v['html']/1024:5.1f}  req {v['requests']}")
sys.exit(1 if R['failures'] else 0)
