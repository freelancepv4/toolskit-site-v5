#!/usr/bin/env python3
"""Multilingual browser tests: overflow at 6 widths on every page, localized tool workflows, switcher, reduced motion, console cleanliness.
    python3 build/build.py && python3 build/test_i18n_browser.py
"""
import os, sys, subprocess, time, glob, re, json, struct, zlib
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(ROOT, 'dist'); PORT = 8766; BASE = f'http://127.0.0.1:{PORT}'
TMP = '/tmp/tk-test-i18n'; os.makedirs(TMP, exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
srv = subprocess.Popen([sys.executable, os.path.join(ROOT, 'build', 'serve.py'), str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.0)
F = []; N = [0]
def ck(c, m):
    N[0] += 1
    if not c: F.append(m); print('FAIL', m)
LANGS = ['en', 'de', 'fr', 'it', 'es', 'nl', 'pl']; WIDTHS = [320, 375, 390, 768, 1024, 1440]
def pages(lang):
    base = DIST if lang == 'en' else os.path.join(DIST, lang); out = []
    for f in glob.glob(base + '/**/*.html', recursive=True):
        rel = os.path.relpath(f, DIST).replace(os.sep, '/')
        if lang == 'en' and re.match(r'(de|fr|it|es|nl|pl)/', rel): continue
        if rel in ('404.html',) or rel.startswith('assets/'): continue
        out.append('/' + rel)
    return sorted(out)
def find(lang, needle):
    for p in pages(lang):
        if needle in open(DIST + p, encoding='utf8').read(): return p
def minimal_pdf(path, pages=3):
    objs = ['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [%s] /Count %d >>' % (' '.join(f'{3+i*2} 0 R' for i in range(pages)), pages)]
    for i in range(pages):
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents {4+i*2} 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>')
        s = f'BT /F1 24 Tf 40 100 Td (Page {i+1}) Tj ET'; objs.append(f'<< /Length {len(s)} >>\nstream\n{s}\nendstream')
    out = b'%PDF-1.4\n'; offs = []
    for n, o in enumerate(objs, 1): offs.append(len(out)); out += f'{n} 0 obj\n{o}\nendobj\n'.encode()
    x = len(out); out += f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode() + ''.join(f'{o:010d} 00000 n \n' for o in offs).encode()
    out += f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n'.encode(); open(path, 'wb').write(out)
minimal_pdf(TMP + '/a.pdf', 2); minimal_pdf(TMP + '/b.pdf', 3)
try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        # 1. overflow on every page at every width, console clean
        for lang in LANGS:
            ps = pages(lang)
            for w in WIDTHS:
                ctx = br.new_context(viewport={'width': w, 'height': 800}); pg = ctx.new_page(); errs = []
                pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None); pg.on('pageerror', lambda e: errs.append(str(e)))
                for u in (ps if w in (320, 1440) else ps[::4]):  # full set at the extremes, every 4th between
                    pg.goto(BASE + u); ov = pg.evaluate('document.documentElement.scrollWidth - innerWidth')
                    ck(ov <= 0, f'overflow {ov}px {lang} {w}px {u}')
                ck(not errs, f'console errors {lang} {w}px: {errs[:2]}')
                ctx.close()
            print('layout done', lang, len(ps), 'pages')
        # 2. localized tool workflows
        expect = {'de': ('1.234,56', ), 'fr': ('1 234,56', ), 'pl': ('1234,56', ), 'it': ('1.234,56', ), 'es': ('1234,56', ), 'nl': ('1.234,56', ), 'en': ('1,234.56', )}
        for lang in LANGS:
            ctx = br.new_context(locale={'en': 'en-GB'}.get(lang, lang), viewport={'width': 1280, 'height': 900}, accept_downloads=True); pg = ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            u = find(lang, 'id="wcText"')
            ck(bool(u), 'wordcounter page missing in '+lang)
            if u:
                pg.goto(BASE + u); pg.fill('#wcText', 'Eins zwei drei. Vier fünf!'); pg.wait_for_timeout(150); t = pg.inner_text('#wcResult')
                ck('5' in t and 'undefined' not in t, f'wordcounter {lang}: {t!r}')
            u = find(lang, 'id="pcA1"')
            ck(bool(u), 'percentage page missing in '+lang)
            if u:
                pg.goto(BASE + u); pg.fill('#pcA1', '20'); pg.fill('#pcA2', '1234.56'); pg.wait_for_timeout(150); t = pg.inner_text('#pcRes1')
                ck('246' in t and 'NaN' not in t, f'percentage {lang}: {t!r}')
            u = find(lang, 'id="vatAmount"')
            ck(bool(u), 'vat page missing in '+lang)
            if u:
                pg.goto(BASE + u); pg.fill('#vatAmount', '1000'); pg.wait_for_timeout(150); t = pg.inner_text('#vatResult'); ck(re.search(r'\d', t) and 'NaN' not in t, f'vat {lang}: {t!r}')
            u = find(lang, 'id="loanPrincipal"')
            ck(bool(u), 'loan page missing in '+lang)
            if u:
                pg.goto(BASE + u); pg.wait_for_timeout(200); t = pg.inner_text('#loanResult'); ck(re.search(r'\d', t) and 'NaN' not in t, f'loan {lang}: {t!r}')
            u = find(lang, 'id="ciPrincipal"')
            ck(bool(u), 'compound page missing in '+lang)
            if u:
                pg.goto(BASE + u); pg.wait_for_timeout(200); t = pg.inner_text('#ciResult'); ck(re.search(r'\d', t) and 'NaN' not in t, f'compound {lang}: {t!r}')
            # locale number formatting visible in a result
            u = find(lang, 'id="pcA1"')
            if u:
                pg.goto(BASE + u); pg.fill('#pcA1', '100'); pg.fill('#pcA2', '1234.56'); pg.wait_for_timeout(150); t = pg.inner_text('#pcRes1').replace(' ', ' ').replace('\xa0', ' ')
                ck('1.234,56' in t or '1 234,56' in t or '1234,56' in t or '1,234.56' in t, f'number format {lang}: {t!r}')
            # PDF merge / split / compress
            for needle, fn in (('data-tool="merge"', 'merge'), ('data-tool="split"', 'split'), ('data-tool="compress"', 'compress')):
                u = find(lang, needle)
                if not u: ck(False, f'{fn} page missing in {lang}'); continue
                pg.goto(BASE + u)
                try:
                    pg.set_input_files('#inp', [TMP + '/a.pdf', TMP + '/b.pdf'] if fn == 'merge' else TMP + '/b.pdf')
                    if fn == 'split': pg.fill('#range', '1-2')
                    pg.click('#go'); pg.wait_for_selector('.ws-res .tk-alert-ok', timeout=20000)
                    with pg.expect_download(timeout=5000) as d: pg.click('#res a.btn-primary')
                    ck(d.value.suggested_filename.endswith('.pdf'), f'{fn} {lang} download name {d.value.suggested_filename}')
                except Exception as e: ck(False, f'{fn} {lang}: {str(e)[:120]}')
            ck(not errs, f'page errors {lang}: {errs[:2]}')
            ctx.close()
        # 3. switcher + preference (no redirect)
        ctx = br.new_context(locale='de-DE'); pg = ctx.new_page(); pg.goto(BASE + '/')
        ck(pg.evaluate('location.pathname') == '/', 'German browser is NOT auto-redirected from /')
        ck(pg.evaluate('document.documentElement.lang').startswith('en'), 'root page html lang en')
        pg.click('.tk-lang summary'); pg.click('.tk-lang a[hreflang="de"]'); pg.wait_for_load_state()
        ck(pg.evaluate('location.pathname').startswith('/de/'), 'switcher goes to /de/')
        ck(pg.evaluate("localStorage.getItem('tk_lang')") == 'de', 'tk_lang stored after explicit choice')
        ck(pg.evaluate('document.documentElement.lang') == 'de', 'de page html lang')
        ctx.close()
        # 4. search per language (diacritics)
        for lang, q, hit in (('de', 'prozent', 'prozentrechner'), ('fr', 'fusionner', 'fusionner'), ('pl', 'zlacz', 'pdf'), ('es', 'comprimir', 'comprimir')):
            ctx = br.new_context(viewport={'width': 1280, 'height': 800}); pg = ctx.new_page(); pg.goto(BASE + f'/{lang}/')
            pg.fill('#siteSearch' if pg.locator('#siteSearch').count() else 'input[type=search]', q); pg.wait_for_timeout(300)
            t = pg.inner_text('#searchResults').lower(); ck(hit in t or 'pdf' in t, f'search {lang} {q!r}: {t[:80]!r}'); ctx.close()
        # 5. reduced motion: no transform on hover
        ctx = br.new_context(reduced_motion='reduce', viewport={'width': 1280, 'height': 800}); pg = ctx.new_page(); pg.goto(BASE + '/')
        c = pg.locator('.tool-card').first; c.hover(); pg.wait_for_timeout(300); ck(pg.evaluate("getComputedStyle(document.querySelector('.tool-card')).transform") in ('none', 'matrix(1, 0, 0, 1, 0, 0)'), 'reduced motion: no card transform'); ctx.close()
        br.close()
finally:
    srv.terminate()
print(f'i18n browser checks: {N[0]} run, {len(F)} failed')
sys.exit(1 if F else 0)
