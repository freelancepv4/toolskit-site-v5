#!/usr/bin/env python3
"""Browser tests (Playwright + Chromium): honest search, 5 viewport widths, tool smoke tests, CSP/console cleanliness.

    python3 build/build.py && python3 build/test_browser.py
Starts build/serve.py itself (same headers/CSP/404 behaviour as vercel.json). Writes build/test-report.json.
"""
import json, os, sys, subprocess, time, struct, zlib, re
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PORT = 8765; BASE = f'http://127.0.0.1:{PORT}'
TMP = os.environ.get('TK_TMP', '/tmp/tk-test'); os.makedirs(TMP, exist_ok=True)
srv = subprocess.Popen([sys.executable, os.path.join(ROOT, 'build', 'serve.py'), str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.0)
R = {'search': [], 'viewports': {}, 'smoke': [], 'console': [], 'failures': []}
def fail(m): R['failures'].append(m); print('FAIL', m)

def minimal_pdf(path, pages=2):
    objs = []; kids = ' '.join(f'{3+i*2} 0 R' for i in range(pages))
    objs.append('<< /Type /Catalog /Pages 2 0 R >>'); objs.append(f'<< /Type /Pages /Kids [{kids}] /Count {pages} >>')
    for i in range(pages):
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents {4+i*2} 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>')
        s = f'BT /F1 24 Tf 40 100 Td (Page {i+1} ToolsKit test) Tj ET'; objs.append(f'<< /Length {len(s)} >>\nstream\n{s}\nendstream')
    out = b'%PDF-1.4\n'; offs = []
    for n, o in enumerate(objs, 1): offs.append(len(out)); out += f'{n} 0 obj\n{o}\nendobj\n'.encode()
    x = len(out); out += f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode() + ''.join(f'{o:010d} 00000 n \n' for o in offs).encode()
    out += f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n'.encode(); open(path, 'wb').write(out)
def png(path, w=64, h=48):
    raw = b''.join(b'\x00' + b''.join(bytes([(x*4) % 256, (y*5) % 256, 128]) for x in range(w)) for y in range(h))
    def ch(t, d): c = struct.pack('>I', len(d)) + t + d; return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b''))

SEARCH_CASES = [  # query, expected kind of outcome, first tool id (if any)
 ('compress pdf', 'tools', 'compress-pdf'), ('pdf compressor', 'tools', 'compress-pdf'), ('reduce pdf size', 'tools', 'compress-pdf'),
 ('resize image', 'tools', 'resize-image'), ('kg to lb', 'tools', 'weight'), ('kilograms to pounds', 'tools', 'weight'), ('kilos to pounds', 'tools', 'weight'), ('convert kg', 'tools', 'weight'),
 ('create qr code', 'tools', 'url-qr-code'), ('qr generator', 'tools', 'url-qr-code'), ('vat calculator', 'tools', 'vat'), ('cv builder', 'tools', 'cv'),
 ('pdf to images', 'tools', 'pdf-to-images'), ('images to pdf', 'tools', 'images-to-pdf'), ('jpg to pdf', 'tools', 'images-to-pdf'), ('jpg to png', 'tools', 'convert-image'),
 ('celsius to fahrenheit', 'tools', 'temperature'), ('mortgage calculator', 'tools', 'loan'), ('resume maker', 'tools', 'cv'), ('wifi qr code', 'tools', 'wifi-qr-code'),
 ('qr code generator', 'tools', 'url-qr-code'), ('make qr code', 'tools', 'url-qr-code'), ('shrink pdf', 'tools', 'compress-pdf'), ('resume builder', 'tools', 'cv'), ('lb to kg', 'tools', 'weight'), ('pounds to kilograms', 'tools', 'weight'),
 ('compress image', 'tools', 'compress-image'), ('image to pdf', 'tools', 'images-to-pdf'), ('merge pdfs', 'tools', 'merge-pdf'), ('calculate vat', 'tools', 'vat'), ('mortgage', 'tools', 'loan'), ('convert png to jpg', 'tools', 'convert-image'),
 ('youtube title', 'tools', 'yt-title'), ('hashtags', 'tools', 'hashtag'), ('wifi qr', 'tools', 'wifi-qr-code'), ('rotate pdf', 'tools', 'rotate-pdf'), ('split pdf', 'tools', 'split-pdf'),
 ('video to pdf', 'none', None), ('instagram downloader', 'none', None), ('download youtube video', 'none', None), ('tiktok downloader', 'none', None), ('pdf editor', 'none', None), ('ocr', 'none', None), ('sign pdf', 'none', None), ('unlock pdf', 'none', None),
 ('xyzabc123', 'none', None), ('something random that matches nothing', 'none', None),
 ('pdf to word', 'none', None), ('word to pdf', 'none', None), ('pdf to excel', 'none', None), ('pdf to jpg', 'none', None), ('edit pdf', 'none', None), ('remove background', 'none', None),
 ('currency converter', 'none', None), ('json formatter', 'none', None), ('image to word', 'none', None), ('completely nonsensical query', 'none', None), ('asdfghjk', 'none', None), ('xyz to abc', 'none', None),
]
VIEWPORTS = [(320, 640), (375, 667), (390, 844), (414, 896), (768, 1024)]
PAGES = ['/', '/tools/', '/pdf-tools/', '/pdf-tools/compress-pdf.html', '/pdf-tools/merge-pdf.html', '/image-tools/image-resizer.html', '/qr-tools/url-qr-code.html', '/qr-tools/wifi-qr-code.html',
         '/unit-converter/weight.html', '/calculators/vat-calculator.html', '/calculators/loan-mortgage-calculator.html', '/cv-builder/', '/social-media-tools/hashtag-generator.html',
         '/about.html', '/privacy.html', '/terms.html', '/contact.html', '/this-page-does-not-exist']

try:
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        def new(w=1280, h=800):
            ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=w < 800, accept_downloads=True)
            pg = ctx.new_page(); pg.on('console', lambda m: R['console'].append((pg.url, m.type, m.text)) if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: R['console'].append((pg.url, 'pageerror', str(e)))); pg.on('requestfailed', lambda r: R['console'].append((pg.url, 'requestfailed', r.url)))
            pg.on('request', lambda r: None if r.url.startswith(BASE) or r.url.startswith(('data:', 'blob:')) else R['console'].append((pg.url, 'EXTERNAL REQUEST', r.url)))
            return ctx, pg
        # ---------------------------------------------------------------- search (engine + real UI)
        ctx, pg = new(); pg.goto(BASE + '/'); pg.wait_for_function('window.TKS')
        for q, kind, first in SEARCH_CASES:
            r = pg.evaluate('q=>{const r=TKS.search(q);return {kind:r.kind,ids:r.results.map(t=>t.id),related:r.related.map(t=>t.id),message:r.message||"",note:r.note||""}}', q)
            good = (r['kind'] == 'none' and not r['ids']) if kind == 'none' else (r['kind'] != 'none' and r['ids'] and r['ids'][0] == first)
            R['search'].append({'query': q, **r, 'pass': bool(good)})
            if not good: fail(f'search {q!r}: {r}')
        # every synonym returns its own tool first; no unsupported pattern matches a real tool; direction matters
        bad = pg.evaluate('''()=>{const out=[];for(const t of TKD.tools){for(const p of [t.name,...t.phrases]){const r=TKS.search(p);if(!r.results.some(x=>x.id===t.id))out.push(['own phrase misses its tool',p,t.id]);}}
          for(const u of TKD.unsupported){for(const p of u.patterns){const r=TKS.search(p);if(r.kind!=='none')out.push(['unsupported pattern returns tools',p,r.results.map(x=>x.id)]);}}
          const a=TKS.search('pdf to images').results.map(t=>t.id)[0],b=TKS.search('images to pdf').results.map(t=>t.id)[0];if(a!=='pdf-to-images'||b!=='images-to-pdf')out.push(['direction',a,b]);return out}''')
        R['search_consistency'] = bad
        for b in bad: fail(f'search consistency: {b}')
        # real UI: home hero search dropdown
        def dropdown(q):
            pg.goto(BASE + '/'); pg.fill('#toolSearch', q); pg.wait_for_selector('#searchResults:not(.hidden)'); return pg.inner_text('#searchResults')
        t = dropdown('pdf to word'); R['ui_pdf_to_word'] = t
        if 'No PDF to Word converter is currently available' not in t or 'Merge PDF' in t.split('Related tools')[0]: fail(f'UI pdf to word dropdown wrong: {t!r}')
        if not all(x in t for x in ('Compress PDF', 'Merge PDF', 'Split PDF', 'PDF to Images')): fail(f'UI related PDF tools missing: {t!r}')
        t = dropdown('kg to lb'); R['ui_kg_to_lb'] = t
        if 'Weight Converter' not in t or 'No tool' in t: fail(f'UI kg to lb wrong: {t!r}')
        t = dropdown('completely nonsensical query'); R['ui_nonsense'] = t
        if 'No tool currently matches this request.' not in t or 'Merge' in t: fail(f'UI nonsense wrong: {t!r}')
        pg.goto(BASE + '/'); pg.fill('#toolSearch', 'compress pdf'); pg.keyboard.press('Enter'); pg.wait_for_url('**/pdf-tools/compress-pdf.html')
        pg.goto(BASE + '/'); pg.fill('#toolSearch', 'pdf to word'); pg.keyboard.press('Enter'); pg.wait_for_url(re.compile(r'/tools/\?q=pdf(%20|\+)to(%20|\+)word'));
        txt = pg.inner_text('#noResults'); R['ui_tools_page_pdf_to_word'] = txt
        if 'No PDF to Word converter is currently available on ToolsKit.' not in txt: fail(f'tools page no-result message wrong: {txt!r}')
        pg.goto(BASE + '/tools/?q=qr'); pg.wait_for_selector('#matchList article'); n = pg.locator('#matchList article').count(); R['ui_tools_qr_count'] = n
        if n != 5: fail(f'tools page ?q=qr expected 5 results, got {n}')
        pg.goto(BASE + '/tools/'); pg.fill('#filterInput', 'asdfghjk');
        if pg.locator('#noResults').is_hidden(): fail('tools page: nonsense query shows no message')
        ctx.close()
        # ---------------------------------------------------------------- viewports
        for w, h in VIEWPORTS:
            ctx, pg = new(w, h); rep = {'overflow': [], 'small_targets': [], 'menu': None, 'checked': 0}
            for path in PAGES:
                resp = pg.goto(BASE + path); pg.wait_for_load_state('networkidle'); rep['checked'] += 1
                if path.endswith('does-not-exist') and resp.status != 404: fail(f'{path} should return 404, got {resp.status}')
                dims = pg.evaluate('()=>({sw:document.documentElement.scrollWidth,iw:window.innerWidth,bw:document.body.scrollWidth})')
                if dims['sw'] > dims['iw'] or dims['bw'] > dims['iw']: rep['overflow'].append((path, dims)); fail(f'{w}px {path}: horizontal overflow {dims}')
                small = pg.evaluate('''()=>{const out=[];document.querySelectorAll('a[href],button,input:not([type=hidden]):not(.tk-vh),select,textarea,summary').forEach(e=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);
                    if(r.width===0||r.height===0||cs.visibility==='hidden'||e.closest('[hidden],.hidden')||e.closest('.tk-vh')||e.classList.contains('tk-vh')||e.closest('.catnav')&&getComputedStyle(e.closest('.catnav')).display==='none')return;
                    if(e.tagName==='A'&&e.closest('p,li,.faq,.prose,.tk-list,.note,.tk-alert')&&!e.closest('.ft-list')&&!e.closest('.chips'))return; /* inline text links are exempt (WCAG 2.5.8) */
                    if(r.height<24||r.width<24)out.push([e.tagName,(e.id||e.textContent||'').trim().slice(0,30),Math.round(r.width),Math.round(r.height)])});return out}''')
                if small: rep['small_targets'].append((path, small)); fail(f'{w}px {path}: targets under 24px: {small[:4]}')
            # navigation + search + footer on this width
            pg.goto(BASE + '/pdf-tools/compress-pdf.html'); mb = pg.locator('#menuBtn')
            if w <= 960:
                vis = mb.is_visible(); nav_hidden = pg.locator('#catnav').is_hidden(); mb.click(); nav_open = pg.locator('#catnav').is_visible() and mb.get_attribute('aria-expanded') == 'true'
                rep['menu'] = {'button_visible': vis, 'closed_by_default': nav_hidden, 'opens': nav_open}
                if not (vis and nav_hidden and nav_open): fail(f'{w}px: mobile menu broken {rep["menu"]}')
                links = pg.locator('#catnav a').count(); rep['menu']['links'] = links
                for a in pg.locator('#catnav a').all():
                    bb = a.bounding_box()
                    if bb and bb['height'] < 44: fail(f'{w}px: nav link under 44px {bb}')
            fh = pg.evaluate('()=>[...document.querySelectorAll(".ft-list a")].map(a=>a.getBoundingClientRect().height)'); rep['footer_min_link_height'] = round(min(fh), 1)
            if min(fh) < 44: fail(f'{w}px: footer link height {min(fh)}')
            pg.fill('#toolSearch', 'vat'); pg.wait_for_selector('#searchResults:not(.hidden)'); box = pg.locator('#searchResults').bounding_box()
            if box and (box['x'] < -1 or box['x'] + box['width'] > w + 1): fail(f'{w}px: search dropdown outside viewport {box}')
            rep['breadcrumb_visible'] = pg.locator('.tk-breadcrumb').is_visible()
            if not rep['breadcrumb_visible']: fail(f'{w}px: breadcrumb not visible')
            R['viewports'][f'{w}px'] = rep; ctx.close()
        # ---------------------------------------------------------------- tool smoke tests (self-hosted libs under the CSP)
        ctx, pg = new(); minimal_pdf(f'{TMP}/a.pdf', 2); minimal_pdf(f'{TMP}/b.pdf', 3); png(f'{TMP}/i.png')
        def smoke(name, fn):
            try: fn(); R['smoke'].append({'tool': name, 'pass': True})
            except Exception as e: R['smoke'].append({'tool': name, 'pass': False, 'error': str(e)[:300]}); fail(f'smoke {name}: {str(e)[:200]}')
        def compress():
            pg.goto(BASE + '/pdf-tools/compress-pdf.html'); pg.set_input_files('#inp', f'{TMP}/a.pdf'); pg.click('#go'); pg.wait_for_selector('.ws-res .tk-alert-ok', timeout=15000)
            assert 'Original:' in pg.inner_text('#res')
            with pg.expect_download() as d: pg.click('#res a.btn-primary')
            assert d.value.suggested_filename.endswith('-compressed.pdf')
        def merge():
            pg.goto(BASE + '/pdf-tools/merge-pdf.html'); pg.set_input_files('#inp', [f'{TMP}/a.pdf', f'{TMP}/b.pdf']); pg.click('#go'); pg.wait_for_selector('.ws-res .tk-alert-ok', timeout=15000)
            assert 'Total pages: 5' in pg.inner_text('#res')
        def split():
            pg.goto(BASE + '/pdf-tools/split-pdf.html'); pg.set_input_files('#inp', f'{TMP}/b.pdf'); pg.fill('#range', '1-2'); pg.click('#go'); pg.wait_for_selector('.ws-res .tk-alert-ok', timeout=15000); assert 'Pages extracted: 2 of 3' in pg.inner_text('#res')
        def rotate():
            pg.goto(BASE + '/pdf-tools/rotate-pdf.html'); pg.set_input_files('#inp', f'{TMP}/a.pdf'); pg.click('#go'); pg.wait_for_selector('.ws-res .tk-alert-ok', timeout=15000)
        def p2i():  # pdf.js + worker + JSZip, all from /assets/vendor
            pg.goto(BASE + '/pdf-tools/pdf-to-images.html'); pg.set_input_files('#inp', f'{TMP}/b.pdf'); pg.click('#go'); pg.wait_for_selector('.ws-res .tk-alert-ok', timeout=30000); assert 'PNG images in one ZIP file: 3' in pg.inner_text('#res')
        def i2p():
            pg.goto(BASE + '/pdf-tools/images-to-pdf.html'); pg.set_input_files('#inp', f'{TMP}/i.png'); pg.click('#go'); pg.wait_for_selector('.ws-res .tk-alert-ok', timeout=15000)
        def qr():
            pg.goto(BASE + '/qr-tools/url-qr-code.html'); pg.fill('#qrUrl', 'example.com'); pg.wait_for_selector('#qrDownloads a', timeout=5000); assert pg.locator('#qrCanvasWrap canvas').count() == 1
        def resize():
            pg.goto(BASE + '/image-tools/image-resizer.html'); pg.set_input_files('#imgFile', f'{TMP}/i.png'); pg.wait_for_selector('#ctrl:not(.hidden)', timeout=5000)
        def weight():
            pg.goto(BASE + '/unit-converter/weight.html'); pg.fill('#cIn', '10'); assert '22.046226' in pg.inner_text('#cResult')
        def vat():
            pg.goto(BASE + '/calculators/vat-calculator.html'); pg.fill('#vatAmount', '100'); pg.fill('#vatRate', '20'); assert '120' in pg.inner_text('#vatResult')
            d = pg.locator('.tk-disclaimer'); assert d.is_visible() and 'Estimate only.' in d.inner_text()
            ry = pg.locator('#vatResult').bounding_box()['y']; dy = d.bounding_box()['y']; assert 0 <= dy - ry < 120, f'disclaimer {dy-ry}px below result'
        def loan():
            pg.goto(BASE + '/calculators/loan-mortgage-calculator.html'); assert 'Monthly payment' in pg.inner_text('#loanResult'); assert 'Estimate only.' in pg.inner_text('.tk-disclaimer')
        def compound():
            pg.goto(BASE + '/calculators/compound-interest-calculator.html'); assert 'Estimate only.' in pg.inner_text('.tk-disclaimer')
        def cv():
            pg.goto(BASE + '/cv-builder/'); pg.fill('#cvName', 'Jane Doe'); assert 'Jane Doe' in pg.inner_text('#cvPreview')
        for n, f in [('compress-pdf', compress), ('merge-pdf', merge), ('split-pdf', split), ('rotate-pdf', rotate), ('pdf-to-images', p2i), ('images-to-pdf', i2p), ('url-qr-code', qr), ('resize-image', resize), ('weight', weight), ('vat', vat), ('loan', loan), ('compound', compound), ('cv', cv)]: smoke(n, f)
        # recently used + 404 search
        pg.goto(BASE + '/tools/');
        if pg.locator('#recent').is_hidden(): fail('recently used list empty after visiting tools')
        pg.goto(BASE + '/no-such-tool.html'); pg.fill('#toolSearch', 'pdf to word'); pg.wait_for_selector('#searchResults:not(.hidden)')
        if 'No PDF to Word converter' not in pg.inner_text('#searchResults'): fail('404 page search is not honest')
        ctx.close(); br.close()
finally:
    srv.terminate()
# console / CSP / external requests: nothing expected on any page
noise = [c for c in R['console'] if not (c[2].startswith('Failed to load resource') and ('this-page-does-not-exist' in c[0] or 'no-such-tool' in c[0] or '404' in c[2]))]
R['console_issues'] = noise
for c in noise[:20]: fail(f'console: {c}')
R['pass'] = not R['failures']
json.dump(R, open(os.path.join(ROOT, 'build', 'test-report.json'), 'w'), indent=1, default=str)
print('search cases:', sum(1 for s in R['search'] if s['pass']), '/', len(R['search']), '| smoke:', sum(1 for s in R['smoke'] if s['pass']), '/', len(R['smoke']), '| viewports:', ', '.join(R['viewports']), '| failures:', len(R['failures']))
sys.exit(0 if R['pass'] else 1)
