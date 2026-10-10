#!/usr/bin/env python3
"""UX / accessibility / tool-behaviour tests (Playwright + Chromium + Pillow). Complements test_browser.py.

    python3 build/build.py && python3 build/test_ux.py
Covers: CV Edit/Preview at 5 widths + print, image tools (formats, filenames, MIME, alpha), calculator validation + aria,
live region, heading order (including JS-rendered content), accessible names, keyboard, focus, 404 status, response headers,
file-tool error states and a larger-file run. Writes build/ux-report.json.
"""
import json, os, sys, subprocess, time, io, re
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PORT = 8768; BASE = f'http://127.0.0.1:{PORT}'
TMP = os.environ.get('TK_TMP', '/tmp/tk-test-ux'); os.makedirs(TMP, exist_ok=True)
srv = subprocess.Popen([sys.executable, os.path.join(ROOT, 'build', 'serve.py'), str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.0)
R = {'checks': 0, 'failures': [], 'notes': {}}
def check(cond, msg):
    R['checks'] += 1
    if not cond: R['failures'].append(msg); print('FAIL', msg)
VIEWPORTS = [(320, 640), (375, 667), (390, 844), (414, 896), (768, 1024)]
console = []

def make_images():
    import random; random.seed(7); im = Image.new('RGB', (400, 300)); px = im.load()  # photo-like: smooth gradient plus noise
    for x in range(400):
        for y in range(300): px[x, y] = tuple(max(0, min(255, int(v + random.gauss(0, 18)))) for v in ((x * 5 // 3) % 256, (y * 3 // 2) % 256, (x + y) % 256))
    im.save(f'{TMP}/photo.jpg', quality=95); im.save(f'{TMP}/photo.png'); im.save(f'{TMP}/photo.webp', quality=90)
    t = Image.new('RGBA', (200, 100), (255, 0, 0, 0)); d = t.load()
    for x in range(100): 
        for y in range(100): d[x, y] = (0, 0, 255, 255)
    t.save(f'{TMP}/alpha.png')
    big = Image.new('RGB', (4000, 3000)); bp = big.load()
    for x in range(0, 4000, 7):
        for y in range(0, 3000, 7): bp[x, y] = ((x // 7) % 256, (y // 7) % 256, 90)
    big.save(f'{TMP}/big.jpg', quality=90)
    open(f'{TMP}/notes.txt', 'w').write('not an image'); open(f'{TMP}/fake.png', 'wb').write(b'this is not a png')
make_images()

def pdf(path, pages):
    objs = ['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [' + ' '.join(f'{3+i*2} 0 R' for i in range(pages)) + f'] /Count {pages} >>']
    for i in range(pages):
        objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents {4+i*2} 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>')
        s = f'BT /F1 24 Tf 40 100 Td (Page {i+1}) Tj ET'; objs.append(f'<< /Length {len(s)} >>\nstream\n{s}\nendstream')
    out = b'%PDF-1.4\n'; offs = []
    for n, o in enumerate(objs, 1): offs.append(len(out)); out += f'{n} 0 obj\n{o}\nendobj\n'.encode()
    x = len(out); out += f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode() + ''.join(f'{o:010d} 00000 n \n' for o in offs).encode()
    out += f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF\n'.encode(); open(path, 'wb').write(out)

def new_page(br, w=1280, h=800, mobile=None):
    ctx = br.new_context(viewport={'width': w, 'height': h}, has_touch=(w < 800) if mobile is None else mobile, accept_downloads=True); pg = ctx.new_page()
    pg.on('console', lambda m: console.append((pg.url, m.type, m.text)) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: console.append((pg.url, 'pageerror', str(e))))
    pg.on('request', lambda r: None if r.url.startswith(BASE) or r.url.startswith(('data:', 'blob:')) else console.append((pg.url, 'EXTERNAL', r.url)))
    return ctx, pg

def download(pg, selector):
    with pg.expect_download() as d: pg.click(selector)
    path = f'{TMP}/dl-' + d.value.suggested_filename; d.value.save_as(path); return d.value.suggested_filename, path

HEADINGS_JS = """()=>{const h=[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(e=>e.offsetParent!==null||getComputedStyle(e).position==='fixed').map(e=>+e.tagName[1]);const bad=[];let p=0;h.forEach(l=>{if(p&&l>p+1)bad.push([p,l]);p=l;});return {h1:h.filter(x=>x===1).length,bad}}"""
NAMES_JS = """()=>[...document.querySelectorAll('input,select,textarea')].filter(e=>e.type!=='hidden'&&!e.disabled).map(e=>{
  const nm=(e.labels&&[...e.labels].map(l=>l.textContent.trim()).join(' '))||e.getAttribute('aria-label')||(e.getAttribute('aria-labelledby')&&document.getElementById(e.getAttribute('aria-labelledby'))?.textContent)||'';
  return nm.trim()?null:(e.id||e.name||e.type)}).filter(Boolean)"""

try:
    with sync_playwright() as pw:
        br = pw.chromium.launch()

        # ===================== CV builder
        for w, h in VIEWPORTS:
            ctx, pg = new_page(br, w, h); pg.goto(BASE + '/cv-builder/'); pg.wait_for_load_state('networkidle')
            check(pg.locator('#cvTabEdit').is_visible() and pg.locator('#cvTabPrev').is_visible(), f'CV {w}: Edit/Preview switch not visible')
            check(pg.locator('#cvName').is_visible() and not pg.locator('#cvPreviewWrap').is_visible(), f'CV {w}: default view should be the form only')
            y = pg.locator('#cvName').bounding_box()['y']; check(y < h, f'CV {w}: first field below the fold (y={y})')
            pg.fill('#cvName', 'Jane Doe'); pg.fill('#cvTitle', 'Designer'); pg.fill('#cvEmail', 'jane@example.com')
            pg.fill('#cv-exp-company-0', 'Acme'); pg.fill('#cv-exp-role-0', 'Lead'); pg.fill('#cvSkills', 'Figma, Research')
            # keyboard: focus the Preview button and press Enter
            pg.focus('#cvTabPrev'); pg.keyboard.press('Enter')
            check(pg.locator('#cvPreviewWrap').is_visible() and not pg.locator('#cvEdit').is_visible(), f'CV {w}: Preview button (keyboard) did not switch view')
            check(pg.get_attribute('#cvTabPrev', 'aria-pressed') == 'true' and pg.get_attribute('#cvTabEdit', 'aria-pressed') == 'false', f'CV {w}: aria-pressed not updated')
            check('Jane Doe' in pg.inner_text('#cvPreview') and 'Acme' in pg.inner_text('#cvPreview'), f'CV {w}: preview lacks entered data')
            check(pg.evaluate('document.activeElement.id') == 'cvPrevH', f'CV {w}: focus not moved to the preview heading')
            top = pg.locator('#cvPrevH').bounding_box()['y']; hb = pg.locator('header').bounding_box(); check(hb['y'] + hb['height'] - 1 <= top < h * 0.5, f'CV {w}: preview heading hidden under the sticky header or too low (y={top}, header bottom={hb["y"]+hb["height"]})')
            dims = pg.evaluate('()=>({sw:document.documentElement.scrollWidth,iw:innerWidth})'); check(dims['sw'] <= dims['iw'], f'CV {w}: horizontal overflow in preview {dims}')
            sheet = pg.locator('#cvPreview').bounding_box(); check(sheet['width'] >= min(w - 40, 280), f'CV {w}: preview too narrow ({sheet["width"]})')
            hd = pg.evaluate(HEADINGS_JS); check(hd['h1'] == 1 and not hd['bad'], f'CV {w}: heading order in preview view {hd}')
            pg.click('#cvBackEdit'); check(pg.locator('#cvName').is_visible() and pg.input_value('#cvName') == 'Jane Doe', f'CV {w}: back to editing lost data')
            hd = pg.evaluate(HEADINGS_JS); check(hd['h1'] == 1 and not hd['bad'], f'CV {w}: heading order in edit view {hd}')
            # print: preview content only, from either view
            pg.emulate_media(media='print')
            check(pg.locator('#cvPreviewWrap').is_visible(), f'CV {w}: preview hidden in print media (edit view)')
            pdfb = pg.pdf(width='8.27in', height='11.69in'); open(f'{TMP}/cv-{w}.pdf', 'wb').write(pdfb)
            pg.emulate_media(media='screen')
            check(pdfb[:4] == b'%PDF', f'CV {w}: print to PDF failed')
            ctx.close()
        # desktop: side by side, no switch; text of the generated PDF
        ctx, pg = new_page(br, 1280, 800); pg.goto(BASE + '/cv-builder/')
        check(not pg.locator('.cv-switch').is_visible(), 'CV desktop: switch should be hidden')
        a, b = pg.locator('#cvEdit').bounding_box(), pg.locator('#cvPreviewWrap').bounding_box(); check(b['x'] > a['x'] + a['width'] - 5 and abs(a['y'] - b['y']) < 60, f'CV desktop: not side by side {a} {b}')
        pg.fill('#cvName', 'Print Test Name'); pg.fill('#cvSummary', 'Summary text here.')
        pg.emulate_media(media='print'); data = pg.pdf(format='A4'); open(f'{TMP}/cv-desktop.pdf', 'wb').write(data)
        try:
            import pypdf; txt = ' '.join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(data)).pages)
            check('Print Test Name' in txt and 'Your details' not in txt and 'Live preview' not in txt and 'Add experience' not in txt, f'CV desktop: printed PDF content wrong: {txt[:120]!r}')
            R['notes']['cv_pdf_text'] = txt[:80]
        except ImportError:
            R['notes']['cv_pdf_text'] = 'pypdf not installed: printed PDF text not inspected'
        pg.emulate_media(media='screen')
        # draft persistence
        pg.click('#cvSave'); check('saved' in pg.inner_text('#cvSaveStatus').lower(), 'CV: save draft status'); pg.reload(); check(pg.input_value('#cvName') == 'Print Test Name', 'CV: draft not restored after reload')
        pg.click('#cvClear'); pg.reload(); check(pg.input_value('#cvName') == '', 'CV: draft not cleared')
        # add/remove rows keep labels + focus
        pg.click('#cvAddExp'); check(pg.locator('#cv-exp-company-1').count() == 1, 'CV: add experience'); pg.click('[data-rmexp="1"]'); check(pg.evaluate('document.activeElement.id') == 'cvAddExp', 'CV: focus after removing a row')
        check(not pg.evaluate(NAMES_JS), f'CV: unlabeled controls {pg.evaluate(NAMES_JS)}'); ctx.close()

        # ===================== image tools
        def imgmeta(path):
            im = Image.open(path); return im.format, im.size, im.mode
        ctx, pg = new_page(br); URL = BASE + '/image-tools/image-resizer.html'
        def load(path):
            pg.goto(URL); pg.set_input_files('#imgFile', path); pg.wait_for_selector('#ctrl:not(.hidden)')
        # desktop header stays on one row (a two-row sticky header wastes 50px of every screen)
        ctxh, ph = new_page(br, 1280, 800); ph.goto(BASE + '/pdf-tools/compress-pdf.html'); check(ph.locator('header').bounding_box()['height'] < 90, f'desktop header is {ph.locator("header").bounding_box()["height"]}px tall (nav wraps)'); ctxh.close()
        # keyboard access to the file button
        pg.goto(URL); pg.keyboard.press('Tab'); focused = []
        for _ in range(25):
            pg.keyboard.press('Tab'); focused.append(pg.evaluate("document.activeElement.id||document.activeElement.tagName"))
            if focused[-1] == 'imgFile': break
        check('imgFile' in focused, f'Resizer: file input unreachable by keyboard ({focused[-5:]})')
        for name, src, fmt_expect, ext in [('jpeg', 'photo.jpg', 'JPEG', 'jpg'), ('png', 'photo.png', 'PNG', 'png'), ('webp', 'photo.webp', 'WEBP', 'webp')]:
            for tag, wd in [('smaller', 200), ('larger', 800)]:
                load(f'{TMP}/{src}'); pg.fill('#rw', str(wd)); h2 = round(wd * 300 / 400); check(pg.input_value('#rh') == str(h2), f'Resizer {name}: aspect lock {pg.input_value("#rh")} != {h2}')
                check(pg.input_value('#rfmt') == 'same', 'Resizer: default format should be same as original')
                pg.click('#go'); pg.wait_for_selector('#out a[download]'); fn, path = download(pg, '#out a[download]')
                f, size, mode = imgmeta(path)
                check(f == fmt_expect and size == (wd, h2) and fn == f'{src.rsplit(".",1)[0]}-{wd}x{h2}.{ext}', f'Resizer {name} {tag}: got {f} {size} {fn}')
                if tag == 'smaller': check(os.path.getsize(path) < os.path.getsize(f'{TMP}/{src}'), f'Resizer {name}: smaller image produced a larger file ({os.path.getsize(path)} vs {os.path.getsize(f"{TMP}/{src}")})')
        # transparent PNG: PNG keeps alpha; JPEG warns + white background; WebP keeps alpha
        load(f'{TMP}/alpha.png'); pg.fill('#rw', '100'); pg.click('#go'); pg.wait_for_selector('#out a[download]'); _, path = download(pg, '#out a[download]')
        im = Image.open(path).convert('RGBA'); check(im.getpixel((25, 25))[3] == 255 and im.getpixel((75, 25))[3] == 0, f'Resizer: transparent PNG lost alpha {im.getpixel((25,25))} {im.getpixel((75,25))}')
        check(not pg.locator('#rqWrap').is_visible(), 'Resizer: quality control should be hidden for PNG output')
        pg.select_option('#rfmt', 'image/jpeg'); check(pg.locator('#rnote').is_visible() and 'transparent' in pg.inner_text('#rnote').lower(), 'Resizer: no transparency note for JPEG'); check(pg.locator('#rqWrap').is_visible(), 'Resizer: quality hidden for JPEG')
        pg.click('#go'); pg.wait_for_selector('#out a[download]'); fn, path = download(pg, '#out a[download]'); im = Image.open(path)
        check(im.format == 'JPEG' and fn.endswith('.jpg') and im.convert('RGB').getpixel((75, 25))[0] > 240, f'Resizer: transparent->JPEG background not white: {im.convert("RGB").getpixel((75,25))}')
        pg.select_option('#rfmt', 'image/webp'); pg.click('#go'); pg.wait_for_selector('#out a[download]'); fn, path = download(pg, '#out a[download]'); im = Image.open(path)
        check(im.format == 'WEBP' and fn.endswith('.webp') and im.convert('RGBA').getpixel((75, 25))[3] == 0, f'Resizer: PNG->WebP alpha/format wrong {im.format}')
        # validation
        load(f'{TMP}/photo.jpg')
        for bad in ['', '0', '-5', '20000']:
            pg.click('#lock'); pg.fill('#rw', bad); pg.click('#go')
            check(pg.get_attribute('#rw', 'aria-invalid') == 'true', f'Resizer: width {bad!r} not aria-invalid')
            did = pg.get_attribute('#rw', 'aria-describedby') or ''; check(did and pg.inner_text('#' + did.split()[0]).strip() != '', f'Resizer: width {bad!r} has no associated error text')
            check('#out a' and pg.locator('#out a[download]').count() == 0, f'Resizer: produced output for invalid width {bad!r}')
            pg.click('#lock')
        pg.fill('#rw', '100'); check(pg.get_attribute('#rw', 'aria-invalid') is None, 'Resizer: aria-invalid not cleared after fixing')
        # huge pixel count
        pg.click('#lock'); pg.fill('#rw', '9000'); pg.fill('#rh', '9000'); pg.click('#go'); check(pg.get_attribute('#rw', 'aria-invalid') == 'true', 'Resizer: 81MP request not refused'); 
        # invalid files
        pg.goto(URL); pg.set_input_files('#imgFile', f'{TMP}/notes.txt'); pg.wait_for_selector('#tkErr:not([hidden])'); check(pg.get_attribute('#tkErr', 'role') == 'alert' and pg.locator('#ctrl.hidden').count() == 1, 'Resizer: text file not rejected')
        pg.goto(URL); pg.set_input_files('#imgFile', f'{TMP}/fake.png'); pg.wait_for_selector('#tkErr:not([hidden])'); check('could not be opened' in pg.inner_text('#tkErr'), 'Resizer: corrupt PNG not reported')
        # large-ish photo
        t0 = time.time(); load(f'{TMP}/big.jpg'); pg.fill('#rw', '1200'); pg.click('#go'); pg.wait_for_selector('#out a[download]', timeout=30000); _, path = download(pg, '#out a[download]')
        check(imgmeta(path)[1] == (1200, 900), f'Resizer: large file result {imgmeta(path)}'); R['notes']['resize_12mp_seconds'] = round(time.time() - t0, 2)
        # reset
        pg.click('#tkReset'); check(pg.locator('#ctrl.hidden').count() == 1, 'Resizer: reset did not return to empty state')
        check(not pg.evaluate(NAMES_JS), f'Resizer: unlabeled controls {pg.evaluate(NAMES_JS)}')
        # next links appear only with a result
        load(f'{TMP}/photo.jpg'); check(pg.locator('.tk-next').is_hidden(), 'Resizer: next links visible before a result'); pg.click('#go'); pg.wait_for_selector('#out a[download]'); check(pg.locator('.tk-next').is_visible() and 'Compress Image' in pg.inner_text('.tk-next'), 'Resizer: next links missing after result')
        # compress + convert
        pg.goto(BASE + '/image-tools/image-compressor.html'); pg.set_input_files('#imgFile', f'{TMP}/photo.png'); pg.wait_for_selector('#ctrl:not(.hidden)'); pg.fill('#q', '60'); pg.click('#go'); pg.wait_for_selector('#out a[download]')
        fn, path = download(pg, '#out a[download]'); check(fn == 'photo-compressed.jpg' and imgmeta(path)[0] == 'JPEG', f'Compress: {fn} {imgmeta(path)}')
        pg.fill('#q', '0'); pg.click('#go'); check(pg.get_attribute('#q', 'aria-invalid') == 'true', 'Compress: quality 0 not flagged')
        for mime, ext, fm in [('image/jpeg', 'jpg', 'JPEG'), ('image/png', 'png', 'PNG'), ('image/webp', 'webp', 'WEBP')]:
            pg.goto(BASE + '/image-tools/image-converter.html'); pg.set_input_files('#imgFile', f'{TMP}/photo.jpg'); pg.wait_for_selector('#ctrl:not(.hidden)'); pg.select_option('#fmt', mime); pg.click('#go'); pg.wait_for_selector('#out a[download]')
            fn, path = download(pg, '#out a[download]'); check(fn == f'photo.{ext}' and imgmeta(path)[0] == fm, f'Convert {mime}: {fn} {imgmeta(path)}')
        ctx.close()

        # ===================== calculators / converters: valid, invalid, edge, aria, live region
        ctx, pg = new_page(br); pg.goto(BASE + '/calculators/vat-calculator.html')
        pg.fill('#vatAmount', '100'); pg.fill('#vatRate', '20'); check('120' in pg.inner_text('#vatResult'), 'VAT: valid result')
        pg.wait_for_timeout(1100); live = pg.inner_text('#tkLive'); check('120' in live, f'VAT: result not mirrored into the live region ({live!r})')
        check(pg.get_attribute('#vatResult', 'aria-live') is None, 'VAT: result itself should not be a second live region')
        pg.fill('#vatAmount', ''); check(pg.get_attribute('#vatAmount', 'aria-invalid') == 'true' and 'Enter a number' in pg.inner_text('#vatAmount-err'), 'VAT: empty amount not flagged')
        check('Enter valid numbers' in pg.inner_text('#vatResult') and 'is-err' in (pg.get_attribute('#vatResult', 'class') or ''), 'VAT: result does not show the error state')
        check('vatAmount-err' in (pg.get_attribute('#vatAmount', 'aria-describedby') or ''), 'VAT: error not tied to the field')
        pg.fill('#vatAmount', '100'); check(pg.get_attribute('#vatAmount', 'aria-invalid') is None and pg.locator('#vatAmount-err').count() == 0, 'VAT: error not cleared')
        for amt, rate in [('0', '20'), ('-50', '20'), ('1e15', '20'), ('100', '0'), ('100', '-100'), ('100', '1000000')]:
            pg.fill('#vatAmount', amt); pg.fill('#vatRate', rate); t = pg.inner_text('#vatResult'); check('NaN' not in t and 'Infinity' not in t and 'undefined' not in t, f'VAT edge {amt}/{rate}: {t!r}')
        pg.fill('#vatAmount', '55'); pg.click('#tkReset'); check(pg.input_value('#vatAmount') == '100' and '120' in pg.inner_text('#vatResult'), 'VAT: reset')
        pg.goto(BASE + '/calculators/loan-mortgage-calculator.html'); pg.fill('#loanTerm', '0'); check(pg.get_attribute('#loanTerm', 'aria-invalid') == 'true', 'Loan: term 0 not flagged'); pg.fill('#loanTerm', '25'); pg.fill('#loanRate', '0'); check('Monthly payment' in pg.inner_text('#loanResult') and 'NaN' not in pg.inner_text('#loanResult'), 'Loan: 0% rate')
        pg.goto(BASE + '/calculators/compound-interest-calculator.html'); pg.fill('#ciYears', '0'); check(pg.get_attribute('#ciYears', 'aria-invalid') == 'true', 'Compound: years 0 not flagged')
        pg.goto(BASE + '/calculators/percentage-calculator.html'); pg.fill('#pcD1', '100'); pg.fill('#pcD2', '150'); t = pg.inner_text('#pcRes4'); check('NaN' not in t, f'Percentage: 150% -> {t!r}')
        pg.goto(BASE + '/unit-converter/temperature.html'); pg.fill('#cIn', '-273.15'); check('-459.67' in pg.inner_text('#cResult'), 'Temperature: -273.15 C'); pg.fill('#cIn', ''); pg.keyboard.type('1e'); check(pg.get_attribute('#cIn', 'aria-invalid') == 'true' and 'Enter a valid number' in pg.inner_text('#cResult'), 'Temperature: unparseable input not flagged')
        pg.goto(BASE + '/unit-converter/weight.html'); pg.fill('#cIn', '1e300'); check('NaN' not in pg.inner_text('#cResult'), 'Weight: 1e300')
        ctx.close()

        # ===================== generators + QR validation
        ctx, pg = new_page(br)
        for url, btn, field in [('/social-media-tools/hashtag-generator.html', '#hashGen', 'hashTopic'), ('/social-media-tools/instagram-caption-generator.html', '#capGen', 'capTopic'), ('/social-media-tools/youtube-title-generator.html', '#ytGen', 'ytTopic'), ('/social-media-tools/youtube-description-generator.html', '#descGen', 'descTopic'),
                                ('/qr-tools/url-qr-code.html', '#qrGenBtn', 'qrUrl'), ('/qr-tools/wifi-qr-code.html', '#qrGenBtn', 'qrSsid'), ('/qr-tools/email-qr-code.html', '#qrGenBtn', 'qrEmail'), ('/qr-tools/phone-qr-code.html', '#qrGenBtn', 'qrPhone'), ('/qr-tools/contact-qr-code.html', '#qrGenBtn', 'qrName')]:
            pg.goto(BASE + url); pg.click(btn)
            check(pg.get_attribute('#' + field, 'aria-invalid') == 'true' and pg.locator(f'#{field}-err').count() == 1 and pg.evaluate('document.activeElement.id') == field, f'{url}: empty required field not flagged/focused')
            pg.fill('#' + field, 'abc'); check(pg.get_attribute('#' + field, 'aria-invalid') is None, f'{url}: error not cleared on typing')
        pg.goto(BASE + '/social-media-tools/hashtag-generator.html'); pg.fill('#hashTopic', 'coffee'); pg.click('#hashGen'); check(pg.locator('[data-copy]').count() == 1 and pg.locator('.tk-next').is_visible(), 'Hashtag: result/copy/next missing')
        pg.goto(BASE + '/qr-tools/url-qr-code.html'); check(pg.locator('.tk-next').is_hidden(), 'QR: next visible before result'); pg.fill('#qrUrl', 'example.com'); pg.wait_for_selector('#qrDownloads a[download]'); fn, path = download(pg, '#qrDownloads a[download]')
        check(fn == 'qr-code.png' and imgmeta(path)[0] == 'PNG', f'QR download {fn} {imgmeta(path)}'); check(pg.locator('.tk-next').is_visible(), 'QR: next links missing after result')
        pg.wait_for_timeout(1100); check('QR code generated' in pg.inner_text('#tkLive'), f'QR: live region {pg.inner_text("#tkLive")!r}')
        pg.fill('#qrSize', '5000'); check(pg.get_attribute('#qrSize', 'aria-invalid') == 'true', 'QR: size 5000 not flagged'); ctx.close()

        # ===================== PDF workspace: empty, invalid, valid, large-ish
        ctx, pg = new_page(br); pdf(f'{TMP}/a.pdf', 2); pdf(f'{TMP}/many.pdf', 300)
        pg.goto(BASE + '/pdf-tools/merge-pdf.html'); check(pg.locator('#act').is_hidden() and pg.locator('#go').is_hidden(), 'Merge: actions visible in empty state')
        pg.set_input_files('#inp', f'{TMP}/notes.txt'); pg.wait_for_selector('#err:not([hidden])'); check('supported file type' in pg.inner_text('#err') and pg.get_attribute('#err', 'role') == 'alert', 'Merge: text file not rejected')
        pg.set_input_files('#inp', f'{TMP}/fake.png'); check(pg.locator('#act').is_hidden(), 'Merge: png accepted as pdf')
        open(f'{TMP}/broken.pdf', 'wb').write(b'%PDF-1.4 broken'); pg.set_input_files('#inp', f'{TMP}/broken.pdf'); pg.wait_for_timeout(600); check(pg.locator('.err-text').count() >= 1 or pg.locator('#err:not([hidden])').count() >= 1, 'Merge: corrupt PDF not reported')
        pg.goto(BASE + '/pdf-tools/compress-pdf.html'); t0 = time.time(); pg.set_input_files('#inp', f'{TMP}/many.pdf'); pg.click('#go'); pg.wait_for_selector('.ws-res .tk-alert-ok', timeout=60000); R['notes']['compress_300_pages_seconds'] = round(time.time() - t0, 2)
        check(pg.evaluate('document.activeElement.tagName') == 'H2', 'PDF result: focus not moved to the result heading')
        fn, path = download(pg, '#res a.btn-primary'); check(fn == 'many-compressed.pdf' and open(path, 'rb').read(4) == b'%PDF', f'Compress download {fn}')
        hd = pg.evaluate(HEADINGS_JS); check(not hd['bad'] and hd['h1'] == 1, f'PDF result: heading order {hd}')
        check(not pg.evaluate(NAMES_JS), f'PDF workspace: unlabeled controls {pg.evaluate(NAMES_JS)}')
        ctx.close()

        # ===================== static pages: headings, names (all pages), keyboard + focus
        ctx, pg = new_page(br)
        pages = ['/', '/tools/', '/pdf-tools/', '/image-tools/', '/qr-tools/', '/unit-converter/', '/calculators/', '/social-media-tools/', '/about.html', '/privacy.html', '/terms.html', '/contact.html', '/404.html'] + \
                [f'/{d}/{f}' for d, f in [('pdf-tools', 'merge-pdf.html'), ('image-tools', 'image-resizer.html'), ('qr-tools', 'wifi-qr-code.html'), ('calculators', 'vat-calculator.html'), ('unit-converter', 'weight.html'), ('social-media-tools', 'hashtag-generator.html')]]
        for path in pages:
            pg.goto(BASE + path); hd = pg.evaluate(HEADINGS_JS); check(hd['h1'] == 1 and not hd['bad'], f'{path}: heading order {hd}'); nm = pg.evaluate(NAMES_JS); check(not nm, f'{path}: unlabeled controls {nm}')
        # skip link is the first tab stop and works
        pg.goto(BASE + '/about.html'); pg.keyboard.press('Tab'); check(pg.evaluate('document.activeElement.className') == 'tk-skip' and pg.locator('.tk-skip').is_visible(), 'skip link not first/visible on focus')
        # focus visible on header search + tool links
        pg.focus('#toolSearch'); ol = pg.evaluate("getComputedStyle(document.activeElement).boxShadow+getComputedStyle(document.activeElement).outlineStyle"); check(ol.strip() not in ('', 'none##'), 'search focus not visible')
        # search combobox keyboard
        pg.fill('#toolSearch', 'qr'); pg.wait_for_selector('#searchResults:not(.hidden)'); pg.keyboard.press('ArrowDown'); check(pg.get_attribute('#toolSearch', 'aria-activedescendant') == 'sr-0', 'combobox: ArrowDown did not set activedescendant')
        pg.keyboard.press('Escape'); check(pg.locator('#searchResults').is_hidden() and pg.get_attribute('#toolSearch', 'aria-expanded') == 'false', 'combobox: Escape did not close')
        # mobile menu: open, Escape returns focus
        ctx2, p2 = new_page(br, 390, 844); p2.goto(BASE + '/about.html'); p2.click('#menuBtn'); check(p2.get_attribute('#menuBtn', 'aria-expanded') == 'true' and p2.locator('#catnav').is_visible(), 'menu: not open')
        p2.keyboard.press('Escape'); check(p2.get_attribute('#menuBtn', 'aria-expanded') == 'false' and p2.evaluate('document.activeElement.id') == 'menuBtn', 'menu: Escape should close and restore focus')
        p2.click('#menuBtn'); p2.keyboard.press('Tab'); check(p2.evaluate("document.activeElement.closest('#catnav')!==null||document.activeElement.id!=='menuBtn'"), 'menu: Tab from the button does not enter the menu'); ctx2.close()
        # touch targets: primary controls >= 44px on mobile (documented exceptions: inline text links)
        for w, h in [(320, 640), (390, 844), (768, 1024)]:
            c3, p3 = new_page(br, w, h)
            for path in ['/', '/pdf-tools/compress-pdf.html', '/image-tools/image-resizer.html', '/calculators/vat-calculator.html', '/unit-converter/weight.html', '/qr-tools/url-qr-code.html', '/cv-builder/', '/contact.html']:
                p3.goto(BASE + path); p3.wait_for_load_state('networkidle')
                if path == '/image-tools/image-resizer.html': p3.set_input_files('#imgFile', f'{TMP}/photo.jpg'); p3.wait_for_selector('#ctrl:not(.hidden)')
                small = p3.evaluate('''()=>{const o=[];document.querySelectorAll('button,.btn,input:not([type=hidden]):not([type=file]):not([type=checkbox]),select,textarea,summary,.tk-chip,.chips a,.catnav a,.ft-list a').forEach(e=>{const r=e.getBoundingClientRect(),cs=getComputedStyle(e);
                    if(!r.width||!r.height||cs.visibility==='hidden'||e.closest('[hidden],.hidden,.tk-vh'))return;if(e.closest('.catnav')&&getComputedStyle(e.closest('.catnav')).display==='none')return;
                    if(r.height<43.5)o.push([e.tagName,(e.id||e.textContent||'').trim().slice(0,24),Math.round(r.width),Math.round(r.height)])});return o}''')
                check(not small, f'{w}px {path}: controls under 44px high: {small[:4]}')
            c3.close()
        ctx.close()

        # ===================== CSP actually blocks injected inline script
        ctx = br.new_context(); pg = ctx.new_page(); pg.goto(BASE + '/')  # no console capture: the violations below are deliberate
        res = pg.evaluate("() => new Promise(r => { document.addEventListener('securitypolicyviolation', e => r('blocked:' + e.violatedDirective)); const s = document.createElement('script'); s.textContent = 'window.__x=1'; document.body.append(s); setTimeout(() => r(window.__x ? 'ran' : 'no-event'), 400); })")
        check(res.startswith('blocked:script-src'), f'CSP did not block an injected inline script: {res}')
        res = pg.evaluate("() => new Promise(r => { document.addEventListener('securitypolicyviolation', e => r('blocked:' + e.violatedDirective)); const s = document.createElement('script'); s.src = 'https://example.com/x.js'; document.body.append(s); setTimeout(() => r('no-event'), 600); })")
        check(res.startswith('blocked:'), f'CSP did not block an external script: {res}'); ctx.close()
        # ===================== 404 + headers (local server mirrors vercel.json; real Vercel behaviour is verified after deployment)
        ctx, pg = new_page(br)
        for path in ['/does-not-exist', '/nonexistent-tool', '/random-page-123', '/pdf-tools/nope.html', '/calculators/vat/', '/assets/missing.js']:
            r = pg.goto(BASE + path); check(r.status == 404, f'{path}: status {r.status}')
            if path.endswith('.js'): continue
            check('Page not found' in pg.title(), f'{path}: not the custom 404 ({pg.title()!r})'); check(pg.locator('link[rel=canonical]').count() == 0 and 'noindex' in (pg.get_attribute('meta[name=robots]', 'content') or ''), f'{path}: 404 has canonical or lacks noindex')
            check(pg.locator('#toolSearch').is_visible() and pg.locator('a[href="/"]').count() >= 1, f'{path}: 404 lacks search/home link')
        for path in ['/', '/pdf-tools/compress-pdf.html', '/assets/main.js']:
            r = pg.request.get(BASE + path); h = r.headers
            for k in ('x-content-type-options', 'referrer-policy', 'permissions-policy', 'content-security-policy'): check(k in h, f'{path}: header {k} missing')
            if path == '/': check('frame-ancestors' in h.get('content-security-policy', '') and h.get('x-frame-options') == 'DENY', 'frame protection headers missing')
        r = pg.request.get(BASE + '/index.html', max_redirects=0); check(r.status in (301, 308) and r.headers.get('location') == '/', f'/index.html redirect {r.status}')
        r = pg.request.get(BASE + '/tools.html', max_redirects=0); check(r.status in (301, 308) and '/tools/' in r.headers.get('location', ''), f'/tools.html redirect {r.status}')
        r = pg.request.get(BASE + '/pdf-tools/index.html', max_redirects=0); check(r.status in (301, 308) and r.headers.get('location') == '/pdf-tools/', f'/pdf-tools/index.html redirect {r.status}')
        ctx.close(); br.close()
finally:
    srv.terminate()
noise = [c for c in console if not (c[2].startswith('Failed to load resource') and any(x in c[0] for x in ('does-not-exist', 'nonexistent', 'random-page', 'nope.html', 'vat/', 'missing.js')))]
for c in noise[:20]: check(False, f'console: {c}')
R['console_issues'] = noise; R['pass'] = not R['failures']
json.dump(R, open(os.path.join(ROOT, 'build', 'ux-report.json'), 'w'), indent=1, default=str)
print(f"UX checks: {R['checks']} run, {len(R['failures'])} failed | notes: {R['notes']}")
sys.exit(0 if R['pass'] else 1)
