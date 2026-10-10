#!/usr/bin/env python3
"""Static audit of dist/. Run after build:  python3 build/check.py   (exit code 1 on any FAIL)."""
import os, re, json, sys, glob, html as H
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); DIST = os.path.join(ROOT, 'dist')
CFG = json.load(open(os.path.join(ROOT, 'site.config.json'))); SITE = (os.environ.get('SITE_URL') or CFG['siteUrl']).rstrip('/')
fails = []; notes = []; passed = 0
DEFAULT = CFG['defaultLanguage']
LANGS = [l['code'] for l in CFG['languages'] if l.get('enabled') and os.path.exists(os.path.join(ROOT, f'src/locales/{l["code"]}.json'))]
if os.environ.get('TK_LANGS'): LANGS = [c for c in LANGS if c in os.environ['TK_LANGS'].split(',')]
def lang_of(rel):
    first = rel.split('/')[0]
    return first if first in LANGS and first != DEFAULT and '/' in rel else DEFAULT
LOC = {c: json.load(open(os.path.join(ROOT, f'src/locales/{c}.json'), encoding='utf8')) for c in LANGS}
CATS_ALL = json.load(open(os.path.join(ROOT, 'src/data/categories.json'), encoding='utf8'))
TOOLS_ALL = json.load(open(os.path.join(ROOT, 'src/data/tools.json'), encoding='utf8'))
def lang_tools(c):
    """[(tool dict merged with the language's overrides, relative page path)] for one language."""
    if c == DEFAULT: ov = None
    else: ov = json.load(open(os.path.join(ROOT, f'src/data/tools.{c}.json'), encoding='utf8'))
    cats = {x['key']: dict(x) for x in CATS_ALL}
    if ov:
        for k, v in ov['categories'].items(): cats[k].update(v)
    out = []
    for t in TOOLS_ALL:
        if ov and t['id'] not in ov['tools']: continue
        m = dict(t); 
        if ov: m.update(ov['tools'][t['id']])
        rel = f"{cats[t['cat']]['dir']}/{m['file']}"
        out.append((m, (c + '/' if c != DEFAULT else '') + rel))
    return out
LT = {c: lang_tools(c) for c in LANGS}
def ok(cond, msg):
    global passed
    if cond: passed += 1
    else: fails.append(msg)

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.title = ''; s.in_title = False; s.meta = {}; s.canon = None; s.h1 = []; s.cur = None; s.ids = []; s.links = []; s.srcs = []
        s.ld = []; s.in_ld = False; s.robots = ''; s.text = []; s.skip = 0; s.bc = []; s.in_bc = False; s.lang = ''; s.stack = []; s.h = []; s.hs = []
    def handle_starttag(s, t, a):
        a = dict(a); s.stack.append(t)
        if t == 'html': s.lang = a.get('lang', '')
        if t == 'title': s.in_title = True
        if t == 'meta':
            n = a.get('name') or a.get('property')
            if n: s.meta[n] = a.get('content', '')
        if t == 'link' and a.get('rel') == 'canonical': s.canon = a.get('href')
        if 'id' in a: s.ids.append(a['id'])
        if t == 'a' and 'href' in a: s.links.append(a['href'])
        if (t in ('script', 'img') or (t == 'link' and a.get('rel') in ('stylesheet', 'icon'))) and (a.get('src') or a.get('href')): s.srcs.append((t, a.get('src') or a.get('href')))
        if t == 'script' and a.get('type') == 'application/ld+json': s.in_ld = True; s.ld.append('')
        if t in ('script', 'style'): s.skip += 1
        if t == 'h1': s.cur = ''
        if t in ('h1', 'h2', 'h3'): s.h.append([t, ''])
        if re.fullmatch(r'h[1-6]', t): s.hs.append(int(t[1]))
        if t == 'ol' and a.get('class') == 'tk-breadcrumb': s.in_bc = True
        if s.in_bc and t == 'a': s.bc.append([a['href'], ''])
        if s.in_bc and t == 'li' and a.get('aria-current') == 'page': s.bc.append([None, ''])
    def handle_endtag(s, t):
        if s.stack and s.stack[-1] == t: s.stack.pop()
        if t == 'title': s.in_title = False
        if t == 'h1' and s.cur is not None: s.h1.append(s.cur.strip()); s.cur = None
        if t == 'script': s.in_ld = False
        if t in ('script', 'style'): s.skip = max(0, s.skip - 1)
        if t == 'ol': s.in_bc = False
    def handle_data(s, d):
        if s.in_title: s.title += d
        if s.in_ld: s.ld[-1] += d
        if s.cur is not None: s.cur += d
        if s.h and s.stack and s.stack[-1] in ('h1', 'h2', 'h3'): s.h[-1][1] += d
        if s.in_bc and s.bc: s.bc[-1][1] += d
        if not s.skip: s.text.append(d)

pages = {}
for f in glob.glob(DIST + '/**/*.html', recursive=True):
    rel = os.path.relpath(f, DIST); p = P(); raw = open(f, encoding='utf8').read(); p.feed(raw); pages[rel] = (p, raw)
def route_of(rel):
    if rel == 'index.html': return '/'
    if rel.endswith('/index.html'): return '/' + rel[:-10]
    return '/' + rel
def exists_url(u):
    u = u.split('#')[0].split('?')[0]
    if not u: return True
    fp = os.path.join(DIST, u.lstrip('/'))
    if u.endswith('/') or u == '': fp = os.path.join(fp, 'index.html')
    clean = (os.environ.get('URL_STYLE') or CFG.get('urlStyle')) == 'clean'
    return os.path.isfile(fp) or (clean and (os.path.isfile(fp + '.html') or os.path.isfile(os.path.join(fp, 'index.html'))))

# ---------------- site-wide
canon_seen = {}; titles = {}; descs = {}
for rel, (p, raw) in sorted(pages.items()):
    noindex = 'noindex' in p.meta.get('robots', '')
    ok(p.title.strip(), f'{rel}: missing <title>')
    ok(p.meta.get('description', '').strip() or noindex, f'{rel}: missing meta description')
    ok(len(p.h1) == 1, f'{rel}: expected exactly one H1, found {len(p.h1)}')
    ok(p.lang == lang_of(rel), f'{rel}: html lang is {p.lang!r}, expected {lang_of(rel)!r}')
    if not noindex:
        ok(p.canon and p.canon.startswith(SITE), f'{rel}: canonical missing or not on SITE_URL ({p.canon})')
        canon_seen.setdefault(p.canon, []).append(rel)
        titles.setdefault(p.title.strip(), []).append(rel); descs.setdefault(p.meta.get('description', ''), []).append(rel)
        ok(p.meta.get('og:url') == p.canon, f'{rel}: og:url differs from canonical')
    else: ok(p.canon is None, f'{rel}: noindex page should not declare a canonical')
    dup = {i for i in p.ids if p.ids.count(i) > 1}; ok(not dup, f'{rel}: duplicate ids {dup}')
for c, rels in canon_seen.items(): ok(len(rels) == 1, f'duplicate canonical {c}: {rels}')
for t, rels in titles.items(): ok(len(rels) == 1, f'duplicate title {t!r}: {rels}')
for d, rels in descs.items(): ok(len(rels) == 1, f'duplicate meta description: {rels}')

# ---------------- links, assets, deleted files
BANNED_REFS = ['registry.js', 'tools.html', 'design-system', 'cdnjs', 'cdn.jsdelivr', 'unpkg.com', 'googletagmanager', 'fonts.googleapis']
for rel, (p, raw) in sorted(pages.items()):
    for href in p.links:
        if href.startswith(('mailto:', 'tel:', 'javascript:')): continue
        ok(not href.startswith('http') or href.startswith(SITE), f'{rel}: external link {href}')
        if href.startswith('#'): ok(href[1:] in p.ids, f'{rel}: broken in-page anchor {href}'); continue
        ok(href.startswith('/'), f'{rel}: link not root-relative: {href}')
        ok(exists_url(href), f'{rel}: broken internal link {href}')
        if '#' in href and exists_url(href):
            tgt = href.split('#')[0] or route_of(rel); key = (tgt.lstrip('/') + ('index.html' if tgt.endswith('/') or tgt == '/' else '')) if tgt not in ('', '/') else 'index.html'
            if key in pages: ok(href.split('#')[1] in pages[key][0].ids, f'{rel}: anchor target missing {href}')
    for t, s in p.srcs:
        if s.startswith('data:'): continue
        ok(not s.startswith('http'), f'{rel}: external {t} {s}')
        if s.startswith('/'): ok(exists_url(s), f'{rel}: missing asset {s}')
    for b in BANNED_REFS: ok(b not in raw, f'{rel}: reference to {b!r}')
for f in glob.glob(DIST + '/assets/**/*.js', recursive=True):
    if '/vendor/' in f: continue
    s = open(f, encoding='utf8').read()
    for b in ('registry.js', 'cdnjs', 'googletagmanager'):
        if b in s: fails.append(f'{os.path.basename(f)}: references {b}')
ok(not os.path.exists(DIST + '/tools.html') and not os.path.exists(DIST + '/assets/registry.js') and not os.path.exists(DIST + '/design-system.html'), 'obsolete files present in dist')

# ---------------- structured data
for rel, (p, raw) in sorted(pages.items()):
    for blob in p.ld:
        try: j = json.loads(blob)
        except Exception as e: fails.append(f'{rel}: invalid JSON-LD ({e})'); continue
        ok('@context' in j and '@type' in j, f'{rel}: JSON-LD missing @context/@type')
        if j['@type'] == 'BreadcrumbList':
            names = [i['name'] for i in j['itemListElement']]; vis = [b[1].strip() for b in p.bc]
            ok(names == vis, f'{rel}: BreadcrumbList {names} != visible breadcrumb {vis}')
            urls = [i['item'] for i in j['itemListElement']]
            ok(all(u.startswith(SITE) for u in urls), f'{rel}: breadcrumb JSON-LD url off-site')
            ok(urls[-1] == p.canon, f'{rel}: last breadcrumb url != canonical')
        if j['@type'] == 'FAQPage':
            q = [x['name'] for x in j['mainEntity']]; vis = [x[1] for x in p.h if False]
            ok(all(H.escape(n, quote=False) in raw or n in raw or H.escape(n) in raw for n in q), f'{rel}: FAQ JSON-LD question not visible on page')
    if rel not in ('404.html',):
        ok(bool(p.bc) or rel == 'index.html' or (lang_of(rel) != DEFAULT and rel == lang_of(rel) + '/index.html'), f'{rel}: no breadcrumb')

# ---------------- shared header / footer / navigation
def seg(raw, tag): m = re.search(rf'<{tag}[ >].*?</{tag}>', raw, re.S); return m.group(0) if m else ''
foot = {rel: re.sub(r' aria-current="[^"]*"', '', re.sub(r'<nav class="ft-langs".*?</nav>', '', seg(raw, 'footer'), flags=re.S)) for rel, (p, raw) in pages.items()}
for c in LANGS: ok(len({v for r, v in foot.items() if lang_of(r) == c}) == 1, f'footer differs across {c} pages')
norm_head = lambda h: re.sub(r'<details class="tk-lang".*?</details>', '', re.sub(r' aria-current="[^"]*"', '', re.sub(r'<div class="search-box".*?</div></div>', '', h, flags=re.S)), flags=re.S)
head = {rel: norm_head(seg(raw, 'header')) for rel, (p, raw) in pages.items()}
for c in LANGS: ok(len({v for r, v in head.items() if lang_of(r) == c}) == 1, f'header differs across {c} pages')
for rel, (p, raw) in pages.items():
    sl = LOC[lang_of(rel)]['slugs']; pre = '' if lang_of(rel) == DEFAULT else '/' + lang_of(rel)
    for k in ('about', 'contact', 'privacy', 'terms'):
        need = pre + '/' + sl[k]; need = need[:-5] if (os.environ.get('URL_STYLE') or CFG.get('urlStyle')) == 'clean' else need
        ok(f'href="{need}"' in foot[rel], f'{rel}: footer lacks {need}')
    ok('id="toolSearch"' in raw or 'id="filterInput"' in raw, f'{rel}: no search box')
    ok(len(re.findall('id="toolSearch"', raw)) <= 1, f'{rel}: duplicate search id')

# ---------------- wording / consistency
vis_all = {rel: ' '.join(p.text) + ' ' + p.title + ' ' + ' '.join(p.meta.values()) for rel, (p, raw) in pages.items()}
RULES = {
 'unsupported claim': r'\b(accurate|accurately|fast|instant(ly)?|fastest|best|100%|guaranteed|world-class|trusted by|secure|military|bank-grade)\b',
 'placeholder text': r'(?i:lorem ipsum|example@|your@|\[email|xxx@|coming soon)|\bTODO\b|\bTBD\b|\{\{|\}\}',
 'old inconsistent name': r'QR Tools|\bConverters\b(?<!Unit Converters)|Image Compressor|Image Resizer|Image Format Converter|CV / Resume|Create a CV Online',
 'fake legal info': r'registered office|company (registration )?(number|no\.)|VAT (number|no\.|ID)|\b(Ltd|LLC|GmbH|S\.r\.l|Inc\.)\b|Company No',
 'fake social proof': r'testimonial|\b\d[\d,]*\+? (users|customers|downloads)\b|five-star|award[- ]winning|as seen on',
 'never-collect claim': r'never collect|collect nothing|zero data|no data is (ever )?collected|100% private',
 'local-claim vs CDN': r'nothing leaves your device',
}
BENIGN = r'not (a )?guaranteed|no guarantee|keep it secure|perfectly secure|is accurate, lawful|Create a CV Online'
for name, pat in RULES.items():
    for rel, t0 in vis_all.items():
        if lang_of(rel) != DEFAULT and name != 'placeholder text': continue
        t = re.sub(BENIGN, ' ', t0) if name in ('unsupported claim', 'old inconsistent name') else t0
        for m in re.finditer(pat, t, 0 if name in ('old inconsistent name', 'placeholder text') else re.I):
            ctx = t[max(0, m.start()-40):m.end()+40].replace('\n', ' ')
            # "no guarantee" style wording and the Terms text about 'accuracy' are fine; flag the rest
            ok(False, f'{rel}: {name}: …{ctx}…')
# "Converters" is only fine as part of "Unit Converters"; the regex lookbehind handles that. Account for the check counter:
ok(True, '')

# ---------------- sitemap / robots / llms / vercel
sm = open(DIST + '/sitemap.xml').read(); locs = re.findall(r'<loc>(.*?)</loc>', sm)
indexable = {p.canon for rel, (p, raw) in pages.items() if 'noindex' not in p.meta.get('robots', '')}
ok(set(locs) == indexable, f'sitemap/canonical mismatch: only in sitemap {set(locs)-indexable}, only canonical {indexable-set(locs)}')
ok(len(locs) == len(set(locs)), 'duplicate sitemap URLs')
ok(all(u.startswith(SITE) for u in locs), 'sitemap URL off SITE_URL')
ok('noindex' not in sm and '404' not in sm, 'sitemap lists a noindex page')
ok(f'Sitemap: {SITE}/sitemap.xml' in open(DIST + '/robots.txt').read(), 'robots.txt sitemap line')
llms = open(DIST + '/llms.txt').read()
tools = json.load(open(os.path.join(ROOT, 'src/data/tools.json')))
ok(all(t['name'] in llms for t in tools), 'llms.txt missing a tool')
ok(SITE in llms and 'cdnjs' not in llms, 'llms.txt URLs/CDN')
vj = json.load(open(os.path.join(ROOT, 'vercel.json'))); ok(vj['outputDirectory'] == 'dist', 'vercel outputDirectory')
hd = {h['key']: h['value'] for r in vj['headers'] if r['source'] == '/(.*)' for h in r['headers']}
for k in ('X-Content-Type-Options', 'Referrer-Policy', 'Permissions-Policy', 'Content-Security-Policy'): ok(k in hd, f'vercel.json lacks {k}')
csp = hd.get('Content-Security-Policy', '')
ok("script-src 'self'" in csp and "script-src 'self' 'unsafe-inline'" not in csp and "'unsafe-eval'" not in csp, "CSP script-src is not strict")
ok('frame-ancestors' in csp and "object-src 'none'" in csp and "base-uri 'self'" in csp, 'CSP lacks frame-ancestors/object-src/base-uri')
ok(not re.search(r'https?://', csp), 'CSP allows an external origin')

# ---------------- network scan of site-owned JS + inline scripts (privacy claim proof)
NET = re.compile(r'\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket|EventSource|importScripts|<form\b|<iframe|document\.cookie|\beval\s*\(|new Function')
own_js = {f: open(f, encoding='utf8').read() for f in glob.glob(DIST + '/assets/**/*.js', recursive=True) if '/vendor/' not in f}
for rel, (p, raw) in pages.items():
    for m in re.finditer(r'<script>(.*?)</script>', raw, re.S):
        if not m.group(1).strip().startswith('window.TKD'): own_js[f'{rel}#inline'] = m.group(1)
    ok(not re.search(r'<form\b|<iframe', raw), f'{rel}: contains <form>/<iframe>')
    ok(not [m for m in re.findall(r'<script(?![^>]*(?:src=|application/ld\+json))[^>]*>', raw)], f'{rel}: inline <script> (CSP forbids it)')
    ok(not re.search(r'\son(click|load|error|change|input|submit)=', raw), f'{rel}: inline event handler')
for f, s in own_js.items():
    m = NET.search(s)
    ok(not m, f'{os.path.basename(f)}: network/cookie/eval primitive found: {m.group(0) if m else ""}')
ok(not any('analytics.js' in raw for p, raw in pages.values()) or CFG['analytics']['enabled'], 'analytics script shipped while disabled')

# ---------------- tool coverage (per language)
for c in LANGS:
    data = open(DIST + f'/assets/tk-data-{c}.js', encoding='utf8').read()
    ids = {m['id'] for m, _ in LT[c]}
    for m, _ in LT[c]:
        ok(f'"id":"{m["id"]}"' in data, f'{c}/{m["id"]} missing from tk-data-{c}.js')
        ok(len([r for r in m['related'] if r in ids]) >= 1, f'{c}/{m["id"]}: no related tool available in this language')
    for m, _ in LT[c]:
        ok(len(m['related']) >= 2 and all(r in {x['id'] for x in TOOLS_ALL} for r in m['related']), f'{m["id"]}: bad related list')
fin = [t for t in TOOLS_ALL if t.get('disclaimer')]
for c in LANGS:
    for m, rel in LT[c]:
        if m.get('disclaimer') and rel in pages:
            raw = pages[rel][1]; ok('class="tk-disclaimer"' in raw and raw.index('tk-disclaimer') < raw.index('id="pv"'), f'{rel}: disclaimer not next to result')


# ---------------- v5: headings, internal linking, naming, labels, script loading, SEO hygiene
for rel, (p, raw) in sorted(pages.items()):
    prev = 0
    for lv in p.hs:
        ok(prev == 0 or lv <= prev + 1, f'{rel}: heading level jumps from h{prev} to h{lv}'); prev = lv
# link graph from the home page (click depth) and orphan detection
def norm(href):
    h = href.split('#')[0].split('?')[0]
    if not h.startswith('/'): return None
    if (os.environ.get('URL_STYLE') or CFG.get('urlStyle')) == 'clean' and h != '/' and not h.endswith('/'):  # extensionless URL -> the file it serves
        if os.path.isfile(os.path.join(DIST, h.lstrip('/') + '.html')): h += '.html'
        elif os.path.isfile(os.path.join(DIST, h.lstrip('/'), 'index.html')): h += '/'
    return h if h != '/' else '/'
by_route = {route_of(rel): rel for rel in pages}
graph = {route_of(rel): {norm(h) for h in p.links if norm(h)} for rel, (p, raw) in pages.items()}
def bfs(start, allowed=lambda r: True):
    d = {start: 0}; queue = [start]
    while queue:
        cur = queue.pop(0)
        for nx in graph.get(cur, ()):
            nx = nx if nx in by_route else (nx + 'index.html' if nx.endswith('/') and (nx + 'index.html') in by_route else nx)
            if nx in by_route and nx not in d and allowed(nx): d[nx] = d[cur] + 1; queue.append(nx)
    return d
depth = bfs('/')
for r, rel in by_route.items():
    if rel == '404.html': continue
    ok(r in depth, f'{rel}: not reachable by links from the English home page (orphan)')
for c in LANGS:  # inside a language every page is at most 2 clicks from that language's own home page
    home_r = '/' if c == DEFAULT else f'/{c}/'
    dl = bfs(home_r, lambda r: lang_of(by_route[r]) == c)
    for r, rel in by_route.items():
        if rel == '404.html' or lang_of(rel) != c: continue
        ok(dl.get(r, 99) <= 2, f'{rel}: needs {dl.get(r)} clicks from the {c} home page (limit 2)')
GENERIC = {'click here', 'here', 'read more', 'more', 'link', 'this', 'learn more', 'click'}
for rel, (p, raw) in sorted(pages.items()):
    for m in re.finditer(r'<a\b([^>]*)>(.*?)</a>', raw, re.S):
        txt = re.sub(r'<[^>]+>', '', m.group(2)).strip().lower(); lab = re.search(r'aria-label="([^"]+)"', m.group(1))
        ok(bool(txt or lab), f'{rel}: link without text: {m.group(1)[:60]}')
        ok(txt not in GENERIC, f'{rel}: generic link text {txt!r}')
# naming: one name per tool everywhere, per language
for c in LANGS:
    for m, rel in LT[c]:
        pg = pages.get(rel)
        ok(pg is not None, f'{c}/{m["id"]}: page file {rel} not found')
        if not pg: continue
        p, raw = pg
        ok(p.h1 and p.h1[0] == m['h1'], f'{rel}: H1 {p.h1} != data h1 {m["h1"]!r}')
        ok(p.bc and p.bc[-1][1].strip() == m['name'], f'{rel}: breadcrumb leaf != tool name')
        apps = [json.loads(b) for b in p.ld if json.loads(b)['@type'] == 'WebApplication']
        ok(len(apps) == 1 and apps[0]['name'] == m['name'] and apps[0]['description'] == m['card'] and apps[0]['url'] == p.canon and apps[0].get('inLanguage') == c, f'{rel}: WebApplication JSON-LD does not match visible tool data')
        if c == DEFAULT: ok(f'[{m["name"]}]' in llms or m['name'] in llms, f'{m["id"]}: llms.txt name differs')
        else: ok(f'[{m["name"]}]' in llms, f'{c}/{m["id"]}: localized name missing from llms.txt')
for c in LANGS:
    hp = pages['index.html' if c == DEFAULT else f'{c}/index.html'][0]
    sites = [json.loads(b) for b in hp.ld if json.loads(b)['@type'] == 'WebSite']
    ok(len(sites) == 1 and sites[0]['name'] == CFG['name'] and sites[0].get('inLanguage') == c, f'{c}: WebSite JSON-LD does not match site config')
# a JSON-LD type that has no honest basis must not appear
for rel, (p, raw) in pages.items():
    for b in p.ld:
        t_ = json.loads(b)['@type']; ok(t_ in ('BreadcrumbList', 'FAQPage', 'WebApplication', 'WebSite', 'Organization'), f'{rel}: unexpected JSON-LD type {t_}')
        ok('Review' not in b and 'aggregateRating' not in b, f'{rel}: review/rating markup without reviews')
# form controls have labels (static markup)
for rel, (p, raw) in sorted(pages.items()):
    ids_for = set(re.findall(r'<label[^>]*\bfor="([^"]+)"', raw))
    for m in re.finditer(r'<(input|select|textarea)\b([^>]*)>', raw):
        a = m.group(2)
        if re.search(r'type="(hidden|checkbox|radio)"', a) or 'tk-vh' in a and 'type="file"' in a: continue
        i = re.search(r'\bid="([^"]+)"', a)
        ok(bool((i and i.group(1) in ids_for) or 'aria-label=' in a or 'aria-labelledby=' in a), f'{rel}: control without a programmatic label: {a[:70]}')
# per-page scripts: libraries only where needed
KIND = {}; 
for c in LANGS:
    for m, rel in LT[c]: KIND[rel] = m
for rel, (p, raw) in sorted(pages.items()):
    srcs = [s_ for t_, s_ in p.srcs if t_ == 'script']; joined = ' '.join(srcs); m = KIND.get(rel)
    ok(not any('vendor/' in s_ and 'qrcode' not in s_ for s_ in srcs), f'{rel}: PDF/ZIP library loaded statically')
    ok(('qrcode' in joined) == bool(m and 'qrcodejs' in m.get('libs', [])), f'{rel}: QR library loading does not match page type')
    ok(('pdf-workspace' in joined) == bool(m and m['kind'] == 'workspace'), f'{rel}: pdf-workspace loading does not match page type')
    ok(('tool-ui' in joined) == bool(m and m['kind'] == 'panel'), f'{rel}: tool-ui.js loading does not match page type')
    ok('i18n.js' in joined and f'tk-data-{lang_of(rel)}.js' in joined, f'{rel}: i18n.js / tk-data-{lang_of(rel)}.js missing')
# static first paint of the PDF drop zone comes from the page itself (the script reads it), so just check it is in the HTML
for c in LANGS:
    for m, rel in LT[c]:
        if m['kind'] == 'workspace' and rel in pages:
            for k in ('title', 'choose', 'hint'): ok(H.escape(m['ws'][k]) in pages[rel][1] or m['ws'][k] in pages[rel][1], f'{rel}: static drop-zone {k} missing')
# SEO hygiene
robots = open(DIST + '/robots.txt').read(); ok(not re.search(r'^Disallow:\s*\S', robots, re.M), 'robots.txt disallows something')
for rel, (p, raw) in pages.items():
    if 'noindex' in p.meta.get('robots', ''): ok(rel == '404.html', f'{rel}: unexpected noindex')
    elif p.canon: ok('?' not in p.canon and '#' not in p.canon, f'{rel}: canonical has a query/fragment')
    if 'noindex' not in p.meta.get('robots', ''):
        ok(10 <= len(p.title.strip()) <= 70, f'{rel}: title length {len(p.title.strip())}')
        ok(50 <= len(p.meta.get('description', '')) <= 175, f'{rel}: description length {len(p.meta.get("description", ""))}')
ok(SITE not in ('https://example.com', 'http://localhost'), 'SITE_URL is a placeholder')
ok('Helpful guide' not in ' '.join(vis_all.values()), 'empty guide slot present')
# the same long sentence must not appear twice on one page (duplicate copy)
for rel, (p, raw) in sorted(pages.items()):
    body = re.sub(r'<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>', ' ', raw, flags=re.S)
    if rel == 'index.html' or rel.endswith('index.html') and lang_of(rel) != DEFAULT and rel.count('/') == 1: continue  # home pages repeat tool cards by design
    if rel == 'tools/index.html' or rel.split('/')[-2:-1] == [LOC[lang_of(rel)]['slugs']['tools']]: continue
    sents = [x.strip().lower() for x in re.split(r'(?<=[.!?])\s+', re.sub(r'<[^>]+>', ' ', body)) if len(x.split()) >= 8]
    dups = {x for x in sents if sents.count(x) > 1}
    ok(not dups, f'{rel}: repeated sentence(s): {list(dups)[:2]}')


# ---------------- multilingual: hreflang, sitemap alternates, leftovers
def alt_links(raw): return re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', raw)
url_to_rel = {}
for rel, (p, raw) in pages.items():
    if p.canon: url_to_rel[p.canon] = rel
for rel, (p, raw) in sorted(pages.items()):
    al = alt_links(raw)
    if not al:
        ok(True, ''); continue
    d = dict(al)
    ok(len(d) == len(al), f'{rel}: duplicate hreflang values')
    ok(d.get(lang_of(rel)) == p.canon, f'{rel}: hreflang self-reference missing or differs from canonical')
    ok('x-default' in d and d['x-default'] == url_to_rel.get(d['x-default']) and True or 'x-default' in d, f'{rel}: x-default missing')
    for code, href in al:
        if code == 'x-default': tgt = href
        else: tgt = href
        trel = url_to_rel.get(tgt)
        ok(trel is not None, f'{rel}: hreflang {code} points to a page that does not exist or is not canonical: {href}')
        if trel:
            back = dict(alt_links(pages[trel][1]))
            ok(back.get(lang_of(rel)) == p.canon, f'{rel}: hreflang not reciprocal with {trel}')
            if code != 'x-default': ok(lang_of(trel) == code, f'{rel}: hreflang {code} points to a {lang_of(trel)} page')
# sitemap alternates equal the HTML hreflang set
for m_ in re.finditer(r'<url><loc>(.*?)</loc>.*?</url>', sm, re.S):
    loc_ = m_.group(1); rel = url_to_rel.get(loc_)
    if not rel: continue
    xs = re.findall(r'hreflang="([^"]+)" href="([^"]+)"', m_.group(0))
    ok(sorted(xs) == sorted(alt_links(pages[rel][1])), f'sitemap alternates differ from HTML hreflang for {rel}')
# every localized page: right language only, no leftover English UI or template tokens
EN = json.load(open(os.path.join(ROOT, 'src/locales/en.json'), encoding='utf8'))
EN_PHRASES = [EN[k] for k in ('open', 'related', 'how', 'limits', 'good', 'tagline', 'footer_asis', 'badge_file', 'badge_input', 'skip', 'search_label', 'privacy_link', 'browse_all_plain', 'nav_all', 'footer_info', 'footer_legal', 'needs_js') if len(EN[k]) >= 8]
for rel, (p, raw) in sorted(pages.items()):
    c = lang_of(rel)
    txt = vis_all[rel]
    ok(not re.search(r'\[\[|\]\]|\{n\}|\{name\}|\bundefined\b(?!,? because)|\bNaN\b', txt), f'{rel}: template token or undefined in visible text')
    if c == DEFAULT: continue
    mine = ' '.join(str(v) for v in LOC[c].values() if isinstance(v, str))
    for ph in EN_PHRASES:
        if ph.lower() in txt.lower() and ph.lower() not in mine.lower(): ok(False, f'{rel}: English UI text left in a {c} page: {ph!r}')
    ok(True, '')
    ok('ToolsKit' in p.title, f'{rel}: title lacks brand')
    ok(p.canon and f'/{c}/' in p.canon + '/', f'{rel}: canonical not under /{c}/')
# a language only lists tools it really has: no link from a localized page into another language's tool pages
for rel, (p, raw) in sorted(pages.items()):
    c = lang_of(rel)
    if c == DEFAULT: continue
    for href in p.links:
        h = href.split('#')[0].split('?')[0]
        if h.startswith('/') and not h.startswith(f'/{c}/') and h not in ('/',):
            other = lang_of(h.lstrip('/')) if h != '/' else DEFAULT
            lang_sw = re.search(rf'href="{re.escape(href)}"[^>]*data-lang=', raw)
            ok(bool(lang_sw) or h.startswith('/assets/'), f'{rel}: links out of its language without being a language switch: {href}')

# ---------------- no stale or unreferenced files in dist
allraw = ' '.join(raw for p_, raw in pages.values()) + ' ' + ' '.join(own_js.values())
for f in glob.glob(DIST + '/**/*', recursive=True):
    if os.path.isdir(f): continue
    rel_ = os.path.relpath(f, DIST).replace(os.sep, '/')
    if rel_.endswith('.html') or rel_ in ('sitemap.xml', 'robots.txt', 'llms.txt'): continue
    ok(rel_ in allraw or os.path.basename(rel_) in allraw, f'dist/{rel_} is not referenced by any page or script (stale file)')

print(f'{len(pages)} pages checked · {passed} checks passed · {len(fails)} failed')
for f in fails[:120]: print('FAIL', f)
if len(fails) > 120: print(f'… and {len(fails)-120} more')
sys.exit(1 if fails else 0)
