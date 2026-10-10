#!/usr/bin/env python3
"""ToolsKit static site generator (Python standard library only).

    python3 build/build.py            # build ./dist
    python3 build/build.py --strict   # also fail while launch blockers remain (no contact email, unconfirmed domain, ...)
    SITE_URL=https://example.com python3 build/build.py

Single sources of truth (edit these, never the generated HTML):
    site.config.json            site name, SITE_URL, URL style, languages, contact e-mail, analytics switch
    src/data/categories.json    category names, folders, intro text, FAQ
    src/data/tools.json         every tool: name, URL file, title, description, steps, FAQ, limits, disclaimer, related tools
    src/data/search.json        search synonyms per tool id and per language, categories, unsupported intents
    src/locales/<lang>.json     interface strings
    src/content/<lang>/*.html   long-form pages (home, about, privacy, terms, contact, 404)
    src/tools/<id>/             the tool's own panel.html / script.js / extra.css
    src/templates/              shared fragments (icon sprite)
    src/assets/                 CSS, JS and self-hosted vendor libraries
"""
import json, os, re, sys, shutil, html, hashlib, csv, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src'); DIST = os.environ.get('TK_DIST') or os.path.join(ROOT, 'dist')
SCRATCH = bool(os.environ.get('TK_DIST'))  # TK_DIST=/some/dir builds there and does not touch vercel.json, docs/ or build/lastmod.json (safe for parallel test builds)
STRICT = '--strict' in sys.argv
jl = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf8'))
rd = lambda p: open(os.path.join(ROOT, p), encoding='utf8').read()

CFG = jl('site.config.json')
SITE_URL = (os.environ.get('SITE_URL') or CFG['siteUrl']).rstrip('/')
STYLE = os.environ.get('URL_STYLE') or CFG.get('urlStyle', 'html')
NAME = CFG['name']
DEFAULT = CFG['defaultLanguage']
ONLY = [x for x in os.environ.get('TK_LANGS', '').split(',') if x]  # dev/test: build just these languages, e.g. TK_LANGS=en,de
CFG_LANGS = [l for l in CFG['languages'] if l.get('enabled') and (not ONLY or l['code'] in ONLY)]
CATS_ALL = jl('src/data/categories.json'); TOOLS_ALL = jl('src/data/tools.json'); SEARCH = jl('src/data/search.json')
ANALYTICS = CFG.get('analytics', {}).get('enabled', False)
TODAY = os.environ.get('BUILD_DATE') or datetime.date.today().isoformat()
esc = lambda s: html.escape(str(s), quote=True)
errors = []; warnings = []
LOCALE_REQUIRED_TOOL = ('name', 'h1', 'title', 'description', 'card', 'lead', 'steps', 'faq', 'limits', 'good')
LOCALE_REQUIRED_CAT = ('name', 'dir', 'card', 'intro', 'title', 'description', 'faq')

# Per-language state. use_lang() points these module globals at one language; every builder below reads them.
LANG = PREFIX = ''; L = {}; TOOLS = []; TOOL = {}; CATS = []; CAT = {}; SYN = {}; PG = {}; STR = {}
LANGS = []          # languages that are actually built (enabled AND data present)
PATHS = {}          # PATHS[lang][page key] = logical path. Keys: home tools about contact privacy terms cat:<key> tool:<id>
MULTI = False

# ---------------------------------------------------------------- URLs
def logical(kind, x=None):
    """Logical path (no leading slash). '' = home, trailing '/' = folder index."""
    if kind == 'home': return ''
    if kind == 'cat': return x['dir'] + '/'
    if kind == 'tool':
        c = CAT[x['cat']]
        return c['dir'] + '/' if x['file'] == 'index.html' else f"{c['dir']}/{x['file']}"
    return x
def lang_prefix(code): return '' if code == DEFAULT else code
def route(p, lang=None):
    """Public URL path for a logical path, following urlStyle and the language directory (English lives at the root; other languages under /<code>/)."""
    pre = PREFIX if lang is None else lang_prefix(lang)
    if STYLE == 'clean':  # extensionless pages and no trailing slash (matches vercel.json cleanUrls + trailingSlash:false)
        if p.endswith('.html'): p = p[:-10] if p.endswith('index.html') else p[:-5]
        p = p.rstrip('/')
    r = '/' + p
    if pre: r = '/' + pre + (r if r != '/' else ('' if STYLE == 'clean' else '/'))
    return r
absurl = lambda p, lang=None: SITE_URL + route(p, lang)
def outfile(p):
    if p == '' or p.endswith('/'): return p + 'index.html'
    return p

def load_lang(code):
    """Localized view of the site data for one language (no global side effects)."""
    loc = jl(f'src/locales/{code}.json')
    if code == DEFAULT:
        tools = [dict(t) for t in TOOLS_ALL]; cats = [dict(c) for c in CATS_ALL]
        slugs = {'tools': 'tools', 'about': 'about.html', 'contact': 'contact.html', 'privacy': 'privacy.html', 'terms': 'terms.html'}
        return loc, tools, cats, slugs, {}
    en = jl(f'src/locales/{DEFAULT}.json')
    for k in en:
        if k not in loc: errors.append(f'locale {code}: missing UI key {k!r}')
    ov = jl(f'src/data/tools.{code}.json'); slugs = loc.get('slugs', {})
    for k in ('tools', 'about', 'contact', 'privacy', 'terms'):
        if k not in slugs: errors.append(f'locale {code}: slugs.{k} missing')
    tools = []
    for t in TOOLS_ALL:
        if t['id'] not in ov['tools']: continue
        o = ov['tools'][t['id']]; n = dict(t); n.update(o)
        for k in LOCALE_REQUIRED_TOOL:
            if k not in o: errors.append(f'{code}/{t["id"]}: missing {k}')
        tools.append(n)
    have = {t['cat'] for t in tools}; cats = []
    for c in CATS_ALL:
        if c['key'] not in have: continue
        o = ov['categories'].get(c['key'], {}); n = dict(c); n.update(o)
        for k in (LOCALE_REQUIRED_CAT if c['page'] else ('name', 'dir', 'card')):
            if k not in o: errors.append(f'{code}/category {c["key"]}: missing {k}')
        cats.append(n)
    loc['_catsyn'] = {c['key']: ov['categories'].get(c['key'], {}).get('syn', []) for c in cats}
    loc['_unsupported'] = ov.get('unsupported', [])
    return loc, tools, cats, slugs, {t['id']: ov['tools'][t['id']].get('syn', []) for t in tools}

def tool_strings(tid, code):
    """Strings for a tool's panel placeholders [[key]] and its script (TKD.str[tid]). strings.json holds the English base; strings.<lang>.json must cover every key."""
    f = os.path.join(SRC, 'tools', tid, 'strings.json')
    if not os.path.exists(f): return {}
    base = json.load(open(f, encoding='utf8'))[DEFAULT]; out = dict(base)
    if code != DEFAULT:
        fl = os.path.join(SRC, 'tools', tid, f'strings.{code}.json')
        o = json.load(open(fl, encoding='utf8')) if os.path.exists(fl) else {}
        for k in base:
            if k not in o: errors.append(f'strings {tid}/{code}: missing {k!r}')
        for k in o:
            if k not in base: errors.append(f'strings {tid}/{code}: unknown key {k!r}')
        out.update(o)
    return out

def pdf_strings(code):
    base = jl('src/strings/pdf.json')[DEFAULT]; out = dict(base)
    if code != DEFAULT:
        fl = os.path.join(ROOT, 'src', 'strings', f'pdf.{code}.json')
        o = json.load(open(fl, encoding='utf8')) if os.path.exists(fl) else {}
        for k in base:
            if k not in o: errors.append(f'strings pdf/{code}: missing {k!r}')
        for k in o:
            if k not in base: errors.append(f'strings pdf/{code}: unknown key {k!r}')
        out.update(o)
    return out

def use_lang(code):
    global LANG, PREFIX, L, TOOLS, TOOL, CATS, CAT, SYN, PG, STR
    LANG = code; PREFIX = lang_prefix(code)
    L, TOOLS, CATS, slugs, syn_over = load_lang(code)
    CAT = {c['key']: c for c in CATS}; TOOL = {t['id']: t for t in TOOLS}
    PG = {'home': '', 'tools': slugs['tools'] + '/', 'about': slugs['about'], 'contact': slugs['contact'], 'privacy': slugs['privacy'], 'terms': slugs['terms']}
    for t in TOOLS:
        t['path'] = logical('tool', t); t['url'] = route(t['path'])
        t['related'] = [i for i in t.get('related', []) if i in TOOL]; t['next'] = [i for i in t.get('next', []) if i in TOOL]
    for c in CATS:
        if c['page']: c['path'] = logical('cat', c)
        else:  # single-tool category: its page is the tool page
            only = [t for t in TOOLS if t['cat'] == c['key']]; assert len(only) == 1; c['path'] = only[0]['path']
        c['url'] = route(c['path']); c['tools'] = [t for t in TOOLS if t['cat'] == c['key']]
    SYN = {t['id']: (SEARCH['synonyms'].get(t['id'], {}).get(code, []) if code == DEFAULT else syn_over.get(t['id'], [])) for t in TOOLS}
    STR = {t['id']: tool_strings(t['id'], code) for t in TOOLS}
    if any(t['kind'] == 'workspace' for t in TOOLS): STR['pdf'] = pdf_strings(code)

def collect_paths():
    """First pass over all languages: page paths per language, so hreflang and the language switcher can point at the other languages."""
    global MULTI
    for l in CFG_LANGS:
        c = l['code']
        if not os.path.exists(os.path.join(ROOT, f'src/locales/{c}.json')) or (c != DEFAULT and not os.path.exists(os.path.join(ROOT, f'src/data/tools.{c}.json'))):
            errors.append(f'language {c} is enabled in site.config.json but its data files are missing'); continue
        use_lang(c); LANGS.append(l)
        P = dict(PG)
        for ct in CATS:
            if ct['page']: P['cat:' + ct['key']] = ct['path']
        for t in TOOLS: P['tool:' + t['id']] = t['path']
        PATHS[c] = P
    MULTI = len(LANGS) > 1

# ---------------------------------------------------------------- tiny template engine
def fill(text, ctx):
    def get(k):
        v = ctx
        for part in k.split('.'): v = v[part]
        return v
    text = re.sub(r'\{\{\{\s*([\w.]+)\s*\}\}\}', lambda m: str(get(m.group(1))), text)
    return re.sub(r'\{\{\s*([\w.]+)\s*\}\}', lambda m: esc(get(m.group(1))), text)

# ---------------------------------------------------------------- components
SPRITE = rd('src/templates/sprite.html')
def libs_of(ts):
    names = []
    for t in ts:
        for l in t.get('libs', []):
            if l not in names: names.append(l)
    return names
def plural_cat(n):
    """CLDR cardinal category for the languages ToolsKit builds (en, de, fr, it, es, nl, pl)."""
    if LANG == 'pl':
        if n == 1: return 'one'
        if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14: return 'few'
        return 'many'
    if LANG == 'fr': return 'one' if n in (0, 1) else 'other'
    return 'one' if n == 1 else 'other'
def n_tools(n): return (L.get('n_tools_' + plural_cat(n)) or L['n_tools_other']).replace('{n}', str(n))

def badge(t): return L['badge_file'] if t['proc'] == 'file' else L['badge_input']
def card(t):
    c = CAT[t['cat']]
    return (f'<article class="tool-card tk-tool" data-id="{esc(t["id"])}"><span class="ico"><svg width="22" height="22" aria-hidden="true"><use href="#{c["icon"]}"/></svg></span>'
            f'<h3>{esc(t["name"])}</h3><p>{esc(t["card"])}</p><p class="tk-meta"><span>{esc(c["name"])}</span><span class="tk-local">{esc(badge(t))}</span></p>'
            f'<a class="btn btn-secondary btn-sm" href="{t["url"]}">{esc(L["open"])}<span class="tk-vh">: {esc(t["name"])}</span></a></article>')
grid = lambda ts: '<div class="tool-grid tk-grid">' + ''.join(card(t) for t in ts) + '</div>'
def cat_card(c, desc=False):
    return (f'<a class="cat-card" href="{c["url"]}"><span class="ico"><svg width="22" height="22" aria-hidden="true"><use href="#{c["icon"]}"/></svg></span><h3>{esc(c["name"])}</h3>'
            + (f'<p>{esc(c["card"])} {n_tools(len(c["tools"]))}.</p>' if desc else '') + '</a>')

def breadcrumb(crumbs):
    """crumbs: [(label, logical path or None for the current page)] -> (html, json-ld)."""
    items = ''; ld = []
    for i, (label, p) in enumerate(crumbs, 1):
        cur = p is None
        items += f'<li aria-current="page">{esc(label)}</li>' if cur else f'<li><a href="{route(p)}">{esc(label)}</a></li>'
        ld.append({'@type': 'ListItem', 'position': i, 'name': label, 'item': absurl(crumbs[i-1][1] if not cur else CURRENT[0])})
    return (f'<nav aria-label="{esc(L["breadcrumb"])}"><ol class="tk-breadcrumb">{items}</ol></nav>',
            {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': ld})
CURRENT = ['']  # logical path of the page being rendered (used for the last breadcrumb item)

def header(cur_path, cur_cat=None, search=True):
    links = [(L['nav_all'], PG['tools'], 'page' if cur_path == PG['tools'] else None)]
    for c in CATS:
        state = 'page' if cur_path == c['path'] else ('true' if cur_cat == c['key'] else None)
        links.append((c['name'], c['path'], state))
    nav = ''.join(f'<a href="{route(p)}"' + (f' aria-current="{s}"' if s else '') + f'>{esc(n)}</a>' for n, p, s in links)
    sbox = (f'<div class="search-box" role="search"><input id="toolSearch" type="search" placeholder="{esc(L["search_ph_short"])}" aria-label="{esc(L["search_label"])}" autocomplete="off" spellcheck="false">'
            '<div id="searchResults" class="hidden"></div></div>') if search else ''
    return (f'<header><div class="wrap hdr-row"><button class="menu-btn" id="menuBtn" type="button" aria-label="{esc(L["menu"])}">☰</button>'
            f'<a href="{route("")}" class="logo">{esc(NAME)}</a><nav class="catnav" id="catnav" aria-label="{esc(L["nav_main"])}">{nav}</nav>{lang_switch(cur_path)}{sbox}</div></header>')

def page_key(path):
    """Page key (home, tools, tool:<id>, ...) of a logical path in the current language, or None."""
    for k, v in PATHS.get(LANG, {}).items():
        if v == path: return k
    return None

def lang_switch(cur_path):
    """Visible language selector with native names. Links go to the equivalent page when it exists, otherwise to that language's home page. No automatic redirects."""
    if not MULTI: return ''
    key = page_key(cur_path); items = ''
    for l in LANGS:
        c = l['code']; target = PATHS[c].get(key) if key else None
        href = route(target if target is not None else '', c)
        cur = ' aria-current="true"' if c == LANG else ''
        items += f'<li><a href="{href}" lang="{c}" hreflang="{c}" data-lang="{c}"{cur}>{esc(l["label"])}</a></li>'
    return (f'<details class="tk-lang"><summary aria-label="{esc(L["lang_label"])}"><svg width="18" height="18" aria-hidden="true" focusable="false"><use href="#i-globe"/></svg>'
            f'<span>{esc(LABEL_OF(LANG))}</span></summary><ul>{items}</ul></details>')
LABEL_OF = lambda c: next(l['label'] for l in CFG['languages'] if l['code'] == c)

def footer():
    col = lambda h, links: (f'<nav aria-labelledby="ft-{h[0]}"><p class="ft-h" id="ft-{h[0]}">{esc(h[1])}</p><ul class="ft-list">' + ''.join(f'<li><a href="{route(p)}">{esc(n)}</a></li>' for n, p in links) + '</ul></nav>')
    tools = [(c['name'], c['path']) for c in CATS] + [(L['nav_all'], PG['tools'])]
    info = [(L['about'], PG['about']), (L['contact'], PG['contact'])]
    legal = [(L['privacy'], PG['privacy']), (L['terms'], PG['terms'])]
    return (f'<footer><div class="wrap"><div class="footer-grid"><div><p class="ft-h">{esc(NAME)}</p><p class="ft-about">{esc(L["tagline"])}</p></div>'
            + col(('tools', L['footer_tools']), tools) + col(('info', L['footer_info']), info) + col(('legal', L['footer_legal']), legal)
            + '</div>' + footer_langs() + f'<p class="ft-bottom">© {TODAY[:4]} {esc(NAME)}. {esc(L["footer_asis"])}</p></div></footer>')

def footer_langs():
    if not MULTI: return ''
    key = page_key(CURRENT[0]); items = ''
    for l in LANGS:
        c = l['code']; target = PATHS[c].get(key) if key else None
        items += f'<li><a href="{route(target if target is not None else "", c)}" lang="{c}" hreflang="{c}" data-lang="{c}"' + (' aria-current="true"' if c == LANG else '') + f'>{esc(l["label"])}</a></li>'
    return f'<nav class="ft-langs" aria-label="{esc(L["lang_label"])}"><ul>{items}</ul></nav>'

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%2322252b'/%3E%3Cpath d='M9 10h14M16 10v13' stroke='white' stroke-width='3' stroke-linecap='round' fill='none'/%3E%3C/svg%3E"
PAGES = []  # (logical path, indexable?) for sitemap + checks
VER = {}
def asset(name):
    """Versioned URL for a file in dist/assets (content hash in the query string, so long-lived caching is safe)."""
    return f'/assets/{name}?v={VER[name]}'

def layout(path, title, desc, content, *, jsonld=(), cur_cat=None, search=True, extra_css='', scripts='', index=True, canonical_path=None, write=True, out=None):
    canon = absurl(path if canonical_path is None else canonical_path)
    ld = ''.join('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False) + '</script>' for j in jsonld)
    alt = ''
    alts = alternates(path) if index else []
    if len(alts) > 1:  # reciprocal hreflang: only between pages that really exist in each language; x-default = the English page (language chooser in header and footer)
        alt = ''.join(f'<link rel="alternate" hreflang="{c}" href="{u}">' for c, u in alts) + f'<link rel="alternate" hreflang="x-default" href="{dict(alts)[DEFAULT]}">'
    page = (f'<!DOCTYPE html>\n<html lang="{LANG}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">'
            + ('' if index else '<meta name="robots" content="noindex,follow">')
            + (f'<link rel="canonical" href="{canon}">' if index else '') + alt
            + '<noscript><style>.ws .tk-drop,#tkReset{display:none}</style></noscript><link rel="stylesheet" href="' + asset('style.css') + '">' + (f'<style>{extra_css}</style>' if extra_css else '')
            + f'<meta property="og:type" content="website"><meta property="og:site_name" content="{esc(NAME)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">'
            + (f'<meta property="og:url" content="{canon}">' if index else '') + '<meta name="twitter:card" content="summary">'
            + f'<link rel="icon" href="{FAVICON}">{ld}</head><body><a class="tk-skip" href="#main">{esc(L["skip"])}</a>{SPRITE}'
            + header(path, cur_cat, search) + f'<main id="main">{content}</main>' + footer()
            + ''.join(f'<script src="{asset(n)}"></script>' for n in (f'tk-data-{LANG}.js', 'i18n.js', 'search.js', 'main.js')) + scripts
            + (f'<script src="{asset("analytics.js")}" defer></script>' if ANALYTICS else '') + '</body></html>\n')
    if write:
        f = os.path.join(DIST, PREFIX, out or outfile(path)); os.makedirs(os.path.dirname(f), exist_ok=True); open(f, 'w', encoding='utf8').write(page)
        PAGES.append((LANG, path, index, page))
    return page

def alternates(path):
    """[(lang, absolute url)] for this page in every language where an equivalent page exists (including this one)."""
    key = page_key(path)
    if not key: return []
    return [(l['code'], absurl(PATHS[l['code']][key], l['code'])) for l in LANGS if key in PATHS[l['code']]]

faq_html = lambda items, hid='fq': (f'<section class="pg-sec faq" aria-labelledby="{hid}"><h2 id="{hid}">{esc(L["faq"])}</h2>' + ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in items) + '</section>') if items else ''
faq_ld = lambda items: {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]} if items else None

def privacy_text(t):
    libs = [L['lib_names'][l] for l in t.get('libs', [])]
    key = ('priv_file' if t['proc'] == 'file' else 'priv_input') + ('_lib' if libs else '')
    s = L[key].replace('{libs}', ' + '.join(libs))
    if not ANALYTICS and not libs and t['proc'] == 'file': s += ' ' + L['priv_no3p']
    return s
def privacy_cat_text(ts):
    libs = [L['lib_names'][l] for l in libs_of(ts)]
    base = L['pcat_file'] if any(t['proc'] == 'file' for t in ts) else L['pcat_input']
    return base + (' ' + L['pcat_libs'].replace('{libs}', ', '.join(libs)) if libs else '')

# ---------------------------------------------------------------- page builders
def tool_page(t):
    c = CAT[t['cat']]; CURRENT[0] = t['path']
    crumbs = [(L['home'], '')] + ([(c['name'], c['path'])] if c['page'] else []) + [(t['name'], None)]
    bc, bcld = breadcrumb(crumbs)
    related = [TOOL[i] for i in t['related']]
    ws_next = json.dumps([[r['name'], r['url']] for r in related])
    body = bc + f'<h1>{esc(t["h1"])}</h1><p class="lead">{esc(t["lead"])}</p>'
    scripts = ''; extra_css = ''
    if t['kind'] == 'workspace':
        w = t['ws']  # static first paint of the drop zone: same markup the script renders, so nothing moves when it starts (no layout shift)
        body += (f'<div class="panel ws" id="tk-ws" data-tool="{esc(t["workspace"])}" data-next="{esc(ws_next)}" data-next-label="{esc(L["next"])}"><div class="tk-drop" id="drop"><p class="tk-drop-title" id="title">{esc(w["title"])}</p><p class="tk-drop-msg">{esc(L["or"])}</p>'
                 f'<label class="btn btn-primary" id="choose">{esc(w["choose"])}<input class="tk-vh" type="file" id="inp" disabled></label><p class="tk-drop-msg" id="hint">{esc(w["hint"])}</p></div>'
                 f'<noscript><p class="tk-alert tk-alert-warn">{esc(L["needs_js"])}</p></noscript></div>')
        scripts = f'<script src="{asset("pdf-workspace.js")}"></script>'
    else:
        d = os.path.join(SRC, 'tools', t['id'])
        panel = open(os.path.join(d, 'panel.html'), encoding='utf8').read().strip()
        S = STR.get(t['id'], {})
        def sub(m):
            if m.group(1) not in S: errors.append(f'{LANG}/{t["id"]}: panel uses [[{m.group(1)}]] but strings.json has no such key'); return ''
            return esc(S[m.group(1)])
        panel = re.sub(r'\[\[(\w+)\]\]', sub, panel)
        if t.get('disclaimer'):
            ms = list(re.finditer(r'<div class="result"[^>]*>[^<]*</div>', panel))  # disclaimer goes under the LAST result block
            if not ms: errors.append(f'{t["id"]}: could not place disclaimer next to the result element')
            else:
                m = ms[-1]; panel = panel[:m.end()] + f'<p class="tk-disclaimer" role="note"><strong>{esc(L["estimate_label"])}</strong> {esc(t["disclaimer"])}</p>' + panel[m.end():]
        if t['id'] != 'cv':  # Reset button and next-step links are rendered here (not injected by script) so nothing shifts
            nx = ''
            if t.get('next'):
                after = t['cat'] in ('image', 'qr', 'soc')  # tools with a Generate/Download step: next links appear once there is a result
                nx = (f'<p class="ws-next tk-next"{" data-after hidden" if after else ""}>{esc(L["next"])} ' + ' '.join(f'<a href="{TOOL[i]["url"]}">{esc(TOOL[i]["name"])}</a>' for i in t['next']) + '</p>')
            i = panel.rindex('</div>'); panel = panel[:i] + nx + f'<button type="button" id="tkReset" class="btn btn-secondary" style="margin-top:var(--s3)">{esc(L["reset"])}</button>' + panel[i:]
        body += f'<noscript><p class="tk-alert tk-alert-warn">{esc(L["needs_js"])}</p></noscript>' + panel
        if os.path.exists(os.path.join(d, 'extra.css')): extra_css = open(os.path.join(d, 'extra.css'), encoding='utf8').read().strip()
        scripts = f'<script src="{asset("tool-ui.js")}"></script>'
        if 'qrcodejs' in t.get('libs', []): scripts += f'<script src="{asset("vendor/qrcode.min.js")}"></script>'
        scripts += f'<script src="{asset("tools/" + t["id"] + ".js")}"></script>'
    if t.get('steps'):
        body += f'<section class="pg-sec" aria-labelledby="hw"><h2 id="hw">{esc(L["how"])}</h2><ol class="pts">' + ''.join(f'<li><span class="step-n">{i:02d}</span><h3>{esc(a)}</h3><p>{esc(b)}</p></li>' for i, (a, b) in enumerate(t['steps'], 1)) + '</ol></section>'
    if t.get('formula'): body += f'<section class="pg-sec" aria-labelledby="fm"><h2 id="fm">{esc(L["calc_h"])}</h2><p class="formula">{esc(t["formula"])}</p></section>'
    if t.get('limits'): body += f'<section class="pg-sec" aria-labelledby="lm"><h2 id="lm">{esc(L["limits"])}</h2><ul class="tk-list">' + ''.join(f'<li>{esc(x)}</li>' for x in t['limits']) + '</ul></section>'
    body += f'<section class="pg-sec" aria-labelledby="pv"><h2 id="pv">{esc(L["privacy_h"])}</h2><p>{esc(privacy_text(t))} <a href="{route(PG["privacy"])}">{esc(L["privacy_link"])}</a></p></section>'
    body += faq_html(t['faq'])
    if t.get('good'): body += f'<section class="pg-sec" aria-labelledby="gn"><h2 id="gn">{esc(L["good"])}</h2><p>{esc(t["good"])}</p></section>'
    content = (f'<div class="wrap" style="padding-block:var(--s5)">{body}</div>'
               f'<section class="related" aria-labelledby="relh"><div class="wrap"><h2 id="relh">{esc(L["related"])}</h2>{grid(related)}</div></section>')
    app = {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': t['name'], 'url': absurl(t['path']), 'description': t['card'],
           'applicationCategory': 'UtilitiesApplication', 'operatingSystem': 'Any (web browser)', 'browserRequirements': 'Requires JavaScript',
           'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}, 'inLanguage': LANG}
    jl_ = [bcld, app] + ([faq_ld(t['faq'])] if t['faq'] else [])
    layout(t['path'], t['title'], t['description'], content, jsonld=jl_, cur_cat=t['cat'], scripts=scripts, extra_css=extra_css)

def cat_page(c):
    CURRENT[0] = c['path']
    bc, bcld = breadcrumb([(L['home'], ''), (c['name'], None)])
    others = ''.join(cat_card(o) for o in CATS if o['key'] != c['key'])
    body = (bc + f'<div class="page-head"><h1>{esc(c["name"])}</h1><p>{esc(c["intro"])}</p></div><h2 class="tk-vh">{esc(L["tools_in"].replace("{name}", c["name"]))}</h2>' + grid(c['tools'])
            + f'<section class="pg-sec" aria-labelledby="pp"><h2 id="pp">{esc(L["privacy_h"])}</h2><p>{esc(privacy_cat_text(c["tools"]))} <a href="{route(PG["privacy"])}">{esc(L["privacy_link"])}</a></p></section>'
            + faq_html(c.get('faq', []), 'pf') + f'<section class="pg-sec"><h2>{esc(L["other_cats"])}</h2><div class="cat-grid">{others}</div></section>')
    jl_ = [bcld] + ([faq_ld(c['faq'])] if c.get('faq') else [])
    layout(c['path'], c['title'], c['description'], f'<div class="wrap">{body}</div>', jsonld=jl_, cur_cat=c['key'])

def tools_index():
    CURRENT[0] = PG['tools']
    bc, bcld = breadcrumb([(L['home'], ''), (L['nav_all'], None)])
    chips = f'<button class="tk-chip" data-chip="" aria-pressed="true" type="button">{esc(L["all"])}</button>' + ''.join(f'<button class="tk-chip" data-chip="{c["key"]}" aria-pressed="false" type="button">{esc(c["name"])}</button>' for c in CATS)
    cats = ''.join(f'<section data-sec="cat" data-cat="{c["key"]}" id="{c["key"]}"><h2>{esc(c["name"])}</h2>{grid(c["tools"])}</section>' for c in CATS)
    body = (bc + f'<div class="page-head"><h1>{esc(L["nav_all"])}</h1><p>{esc(L["all_intro"])}</p></div>'
            f'<div class="search-lg" role="search"><label class="tk-vh" for="filterInput">{esc(L["search_label"])}</label><input id="filterInput" type="search" placeholder="{esc(L["search_ph_long"])}" autocomplete="off" spellcheck="false"></div>'
            f'<div class="tk-chips" role="group" aria-label="{esc(L["filter_cat"])}">{chips}</div><p class="note" id="resultCount" aria-live="polite"></p>'
            '<div id="matchList" class="tool-grid tk-grid" hidden></div>'
            f'<div id="noResults" hidden><div class="tk-alert tk-alert-warn" role="status"><div><p id="nrMsg" style="margin:0"></p><p id="nrNote" style="margin:.25rem 0 0" hidden></p></div></div>'
            f'<div id="nrRelWrap" hidden><h2>{esc(L["related"])}</h2><div id="nrRelated" class="tool-grid tk-grid"></div></div>'
            f'<p><a class="btn btn-secondary" href="{route(PG["tools"])}">{esc(L["browse_all_plain"])}</a></p></div>'
            f'<div id="directory"><section id="recent" data-sec="extra" data-empty="1" hidden><h2>{esc(L["recent"])}</h2><p class="note" style="margin-top:0">{esc(L["recent_note"])} <button type="button" class="btn btn-secondary btn-sm" id="clearRecent">{esc(L["clear"])}</button></p><div class="tool-grid tk-grid" id="recentGrid"></div></section>'
            f'<section data-sec="extra"><h2>{esc(L["popular"])}</h2>{grid([t for t in TOOLS if t["popular"]])}</section>{cats}</div>')
    layout(PG['tools'], L['all_title'], L['all_desc'], f'<div class="wrap">{body}</div>', jsonld=[bcld], search=False)

def popular_tasks():
    return ''.join(f'<li><a href="{TOOL[tid]["url"]}">{esc(label)}</a></li>' for label, tid in L['home_tasks'])
def static_ctx():
    n = len(TOOLS)
    return {'site': {'name': NAME}, 'u': {'tools': route(PG['tools']), 'about': route(PG['about']), 'contact': route(PG['contact']), 'privacy': route(PG['privacy']), 'terms': route(PG['terms']), 'home': route('')}, 'tool_count': n, 'cat_count': len(CATS),
            'popular_grid': grid([t for t in TOOLS if t['popular']]),
            'category_cards': ''.join(cat_card(c, True) for c in CATS),
            'category_list': '<ul class="tk-list">' + ''.join(f'<li><a href="{c["url"]}">{esc(c["name"])}</a> — {n_tools(len(c["tools"]))}</li>' for c in CATS) + '</ul>',
            'task_chips': popular_tasks(), 'updated': pretty_date(CFG['lastUpdated']),
            'tool_list': '<ul class="tk-list">' + ''.join(f'<li><a href="{t["url"]}">{esc(t["name"])}</a> — {esc(t["card"])}</li>' for t in TOOLS) + '</ul>',
            'contact': contact_block(), 'operator': operator_block(),
            'libs_list': '<ul class="tk-list">' + ''.join(f'<li>{esc(v)}</li>' for v in L['lib_full'].values()) + '</ul>'}
def pretty_date(s): d = datetime.date.fromisoformat(s); return f'{d.day} {L["months"][d.month - 1]} {d.year}'
def operator_block():
    return (L['operator_known'].replace('{name}', esc(CFG['operatorName'])) if CFG.get('operatorName') else L['operator_unknown'])
def contact_block():
    e = CFG.get('contactEmail')
    return (L['contact_known'].replace('{email}', f'<a href="mailto:{esc(e)}">{esc(e)}</a>') if e else L['contact_unknown'])

def content_page(slug, path, title, desc, crumb_name, *, faq=None, extra_ld=()):
    CURRENT[0] = path
    bc, bcld = breadcrumb([(L['home'], ''), (crumb_name, None)])
    ctx = static_ctx()
    frag = open(os.path.join(SRC, 'content', LANG, slug + '.html'), encoding='utf8').read()
    body = bc + fill(frag, ctx)
    layout(path, title, desc, f'<div class="wrap prose">{body}</div>', jsonld=[bcld, *extra_ld, *([faq_ld(faq)] if faq else [])])

def contact_page():
    path = PG['contact']; CURRENT[0] = path
    bc, bcld = breadcrumb([(L['home'], ''), (L['contact'], None)])
    e = CFG.get('contactEmail')
    cards = ''
    for k in ('general', 'bug', 'suggest', 'privacy', 'business'):
        c = L['contact_topics'][k]
        subj = f'{NAME}: {c["subject"]}'
        action = (f'<a class="btn btn-secondary" href="mailto:{esc(e)}?subject={html.escape(subj.replace(" ", "%20"), quote=True)}">{esc(L["contact_email_btn"])}</a>' if e else f'<p class="note" style="margin:0">{esc(L["contact_unavailable"])}</p>')
        cards += f'<article class="tk-card contact-card"><h2>{esc(c["title"])}</h2><p>{esc(c["body"])}</p>' + ('<ul class="tk-list">' + ''.join(f'<li>{esc(x)}</li>' for x in c['include']) + '</ul>' if c.get('include') else '') + action + '</article>'
    status = (f'<div class="tk-alert tk-alert-ok" role="status"><div>{L["contact_known"].replace("{email}", f"<a href=mailto:{esc(e)}>{esc(e)}</a>")}</div></div>' if e
              else f'<div class="tk-alert tk-alert-warn" role="status"><div>{L["contact_unknown"]}</div></div>')
    body = (bc + f'<h1>{esc(L["contact"])}</h1><p class="lead">{esc(L["contact_lead"])}</p>' + status
            + f'<div class="contact-grid">{cards}</div><section class="pg-sec"><h2>{esc(L["contact_safe_h"])}</h2><p>{esc(L["contact_safe"])}</p></section>')
    layout(path, L['contact_title'], L['contact_desc'], f'<div class="wrap">{body}</div>', jsonld=[bcld])

def page_404():
    CURRENT[0] = '404.html'
    ctx = static_ctx(); ctx['popular_tools'] = grid([t for t in TOOLS if t['popular']][:6])
    frag = open(os.path.join(SRC, 'content', LANG, '404.html'), encoding='utf8').read()
    search = (f'<div class="hero-search" role="search" style="margin-inline:0"><svg width="24" height="24" aria-hidden="true" focusable="false"><use href="#i-search"/></svg>'
              f'<input id="toolSearch" type="search" placeholder="{esc(L["search_ph_long"])}" aria-label="{esc(L["search_label"])}" autocomplete="off" spellcheck="false"><div id="searchResults" class="hidden"></div></div>')
    ctx['search_box'] = search
    layout('404.html', L['404_title'], L['404_desc'], f'<div class="wrap prose">{fill(frag, ctx)}</div>', search=False, index=False, out='404.html')

def home_page():
    CURRENT[0] = ''
    ctx = static_ctx(); ctx['faq'] = faq_html(L['home_faq'], 'fh'); ctx['language_chooser'] = language_chooser()
    ctx['search_box'] = (f'<div class="hero-search" role="search"><svg width="24" height="24" aria-hidden="true" focusable="false"><use href="#i-search"/></svg>'
                         f'<input id="toolSearch" type="search" placeholder="{esc(L["search_ph_long"])}" aria-label="{esc(L["search_label"])}" autocomplete="off" spellcheck="false"><div id="searchResults" class="hidden"></div></div>')
    frag = open(os.path.join(SRC, 'content', LANG, 'home.html'), encoding='utf8').read()
    ld = [{'@context': 'https://schema.org', '@type': 'WebSite', 'name': NAME, 'url': SITE_URL + '/', 'description': L['home_desc'], 'inLanguage': LANG}, faq_ld(L['home_faq'])]
    layout('', L['home_title'], L['home_desc'], fill(frag, ctx), jsonld=ld, search=False)

def language_chooser():
    """Visible, crawlable language list for the home page (also the x-default destination). Native names, plain links, no redirects."""
    if not MULTI: return ''
    items = ''.join(f'<li><a href="{route("", l["code"])}" lang="{l["code"]}" hreflang="{l["code"]}" data-lang="{l["code"]}"' + (' aria-current="true"' if l['code'] == LANG else '') + f'>{esc(l["label"])}</a></li>' for l in LANGS)
    return f'<section class="lang-sec" aria-labelledby="lgh"><div class="wrap"><h2 id="lgh">{esc(L["lang_label"])}</h2><ul class="lang-list">{items}</ul><p class="note">{esc(L["lang_note"])}</p></div></section>'

# ---------------------------------------------------------------- generated files
UI_JS_KEYS = ('open', 'results', 'related', 'browse_all', 'see_all', 'found', 'no_tool_for', 'no_tool_generic', 'no_in_cat', 'n_tools_one', 'n_tools_few', 'n_tools_many', 'n_tools_other', 'n_related', 'copied_sr', 'none_tools',
              'enter_number', 'min_msg', 'max_msg', 'copied', 'copy_fail', 'qr_ok', 'qr_lowcontrast', 'img_type', 'img_open', 'err_prefixes')
def data_js():
    tools = [{'id': t['id'], 'name': t['name'], 'cat': CAT[t['cat']]['name'], 'catKey': t['cat'], 'url': t['url'], 'desc': t['card'], 'icon': CAT[t['cat']]['icon'],
              'badge': badge(t), 'pop': t['popular'], 'phrases': SYN[t['id']]} for t in TOOLS]
    csyn = (lambda k: SEARCH['categories'].get(k, {}).get(LANG, [])) if LANG == DEFAULT else (lambda k: L['_catsyn'].get(k, []))
    cats = [{'key': c['key'], 'name': c['name'], 'url': c['url'], 'icon': c['icon'], 'syn': csyn(c['key'])} for c in CATS]
    ui = {k: L[k] for k in UI_JS_KEYS if k in L}
    unsup = SEARCH['unsupported'].get(LANG, []) if LANG == DEFAULT else L['_unsupported']
    data = {'lang': LANG, 'allUrl': route(PG['tools']), 'tools': tools, 'cats': cats, 'unsupported': unsup, 'ui': ui, 'sw': L['search_words'], 'str': STR}
    return '// GENERATED by build/build.py from src/data/*.json. Do not edit.\nwindow.TKD=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'

def llms_txt():
    lines = [f'# {NAME}', '', f'> {L["llms_summary"]}', '', f'## {L["llms_pages"]}']
    lines += [f'- [{L["about"]}]({absurl(PG["about"])}): {L["llms_about"]}', f'- [{L["nav_all"]}]({absurl(PG["tools"])}): {L["llms_all"]}', f'- [{L["privacy"]}]({absurl(PG["privacy"])})', f'- [{L["terms"]}]({absurl(PG["terms"])})', f'- [{L["contact"]}]({absurl(PG["contact"])})']
    lines += ['', f'## {L["llms_tools"]}']
    for c in CATS:
        lines.append(f'### {c["name"]}' + ('' if not c['page'] else f' ({absurl(c["path"])})'))
        for t in c['tools']:
            lim = ' Limits: ' + ' '.join(t['limits']) if t.get('limits') else ''
            lines.append(f'- [{t["name"]}]({absurl(t["path"])}): {t["card"]}{lim}')
    lines += ['', f'## {L["llms_privacy_h"]}'] + [f'- {x}' for x in L['llms_privacy']]
    lines += ['', f'## {L["llms_audience_h"]}', L['llms_audience'], '', f'## {L["llms_not_h"]}'] + [f'- {x}' for x in L['llms_not']]
    if len(LANGS) > 1:  # other languages: only the tools that are actually localized into them
        lines += ['', '## Other languages (each language lists only the tools translated into it)']
        for l in LANGS:
            if l['code'] == DEFAULT: continue
            use_lang(l['code'])
            lines.append(f'### {l["label"]} ({absurl("")})')
            lines += [f'- [{t["name"]}]({absurl(t["path"])}): {t["card"]}' for t in TOOLS]
        use_lang(DEFAULT)
    return '\n'.join(lines) + '\n'

def vercel_json():
    csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self' blob: data:; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors " + CFG.get('frameAncestors', "'none'")
    headers = [{'key': 'X-Content-Type-Options', 'value': 'nosniff'}, {'key': 'Referrer-Policy', 'value': 'strict-origin-when-cross-origin'},
               {'key': 'Permissions-Policy', 'value': 'camera=(), microphone=(), geolocation=(), payment=()'}, {'key': 'Content-Security-Policy', 'value': csp}] + ([{'key': 'X-Frame-Options', 'value': 'DENY'}] if CFG.get('frameAncestors', "'none'") == "'none'" else [])
    use_lang(DEFAULT)
    redirects = [{'source': '/index.html', 'destination': '/', 'permanent': True}, {'source': '/tools.html', 'destination': route(PG['tools']), 'permanent': True}]
    for l in LANGS:  # folder-index twins and renamed pages, per language
        use_lang(l['code'])
        pre = ('/' + PREFIX) if PREFIX else ''
        if PREFIX: redirects.append({'source': f'{pre}/index.html', 'destination': route(''), 'permanent': True})
        redirects.append({'source': pre + '/' + PG['tools'] + 'index.html', 'destination': route(PG['tools']), 'permanent': True})
        for c in CATS:
            if c['page'] or c['path'].endswith('/'): redirects.append({'source': pre + f'/{c["dir"]}/index.html', 'destination': route(c['dir'] + '/'), 'permanent': True})
        for t in TOOLS:
            for old in t.get('legacy_files', []):
                redirects.append({'source': pre + f'/{CAT[t["cat"]]["dir"]}/{old}', 'destination': t['url'], 'permanent': True})
    use_lang(DEFAULT)
    cfg = {'$schema': 'https://openapi.vercel.sh/vercel.json', 'outputDirectory': 'dist', 'cleanUrls': STYLE == 'clean', 'trailingSlash': False if STYLE == 'clean' else None,
           'redirects': redirects,
           'headers': [{'source': '/(.*)', 'headers': headers},
                       {'source': '/assets/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=31536000, immutable'}]}]}
    cfg = {k: v for k, v in cfg.items() if v is not None}
    if STYLE == 'clean':  # extensionless URLs only: send the .html twins to them
        cfg['redirects'] += [{'source': '/:path*.html', 'destination': '/:path*', 'permanent': True}]
    return json.dumps(cfg, indent=2) + '\n'

def sitemap(lastmod):
    """One sitemap for every language. Pages that exist in several languages carry xhtml:link alternates (same reciprocal set as the HTML hreflang tags)."""
    out = []
    for lang, p, idx, _ in PAGES:
        if not idx: continue
        use_lang(lang)
        alts = alternates(p); extra = ''
        if len(alts) > 1:
            extra = ''.join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{u}"/>' for c, u in alts) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{dict(alts)[DEFAULT]}"/>'
        out.append((absurl(p), f'<url><loc>{absurl(p)}</loc><lastmod>{lastmod[(lang, p)]}</lastmod>{extra}</url>\n'))
    use_lang(DEFAULT)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + ''.join(x for _, x in sorted(out)) + '</urlset>\n')

def url_map():
    """English URL map (v3 -> current)."""
    use_lang(DEFAULT)
    rows = [['legacy_url (v3)', 'legacy_canonical (v3)', 'tool_id', 'category', 'new_url', 'canonical', 'status']]
    pub = lambda p: route(p)
    rows.append(['/index.html', '/index.html', '', '', '/', absurl(''), 'canonicalised: / is canonical; /index.html 308-redirects'])
    rows.append(['/tools/index.html', '/tools/index.html', '', '', pub(PG['tools']), absurl(PG['tools']), 'canonicalised: folder URL is canonical; /tools/index.html 308-redirects' if STYLE == 'html' else 'changed (clean URLs)'])
    rows.append(['/tools.html', '(noindex leftover)', '', '', pub(PG['tools']), absurl(PG['tools']), 'removed file; 308-redirects to /tools/'])
    rows.append(['/about.html', '/about.html', '', '', pub(PG['about']), absurl(PG['about']), 'unchanged'])
    for n in ('privacy', 'terms', 'contact'): rows.append(['—', '—', '', '', pub(PG[n]), absurl(PG[n]), 'new'])
    rows.append(['—', '—', '', '', '/404.html', '(noindex)', 'new (served for unknown URLs)'])
    for c in CATS:
        if c['page']: rows.append([f'/{c["dir"]}/index.html', f'/{c["dir"]}/index.html', '', c['key'], c['url'], absurl(c['path']), 'canonicalised: folder URL is canonical; /index.html 308-redirects'])
    for t in TOOLS:
        legacy = f'/{CAT[t["cat"]]["dir"]}/{t["file"]}'
        same = legacy == t['url']
        rows.append([legacy, SITE_URL + legacy, t['id'], t['cat'], t['url'], absurl(t['path']), 'unchanged' if same else ('canonicalised: folder URL is canonical; /index.html 308-redirects' if t['file'] == 'index.html' else 'changed')])
        for old in t.get('legacy_files', []):
            lo = f'/{CAT[t["cat"]]["dir"]}/{old}'
            rows.append([lo, SITE_URL + lo, t['id'], t['cat'], t['url'], absurl(t['path']), 'renamed: the old URL 308-redirects to the new one'])
    return rows

def locale_map():
    rows = [['language', 'page_key', 'url', 'canonical', 'hreflang_alternates']]
    for l in LANGS:
        if l['code'] == DEFAULT: continue
        use_lang(l['code'])
        for k, p in PATHS[l['code']].items(): rows.append([l['code'], k, route(p), absurl(p), ' '.join(c for c, _ in alternates(p))])
    use_lang(DEFAULT)
    return rows

def copy_assets():
    dst = os.path.join(DIST, 'assets')
    shutil.copytree(os.path.join(SRC, 'assets'), dst)
    for l in LANGS:
        use_lang(l['code']); open(os.path.join(dst, f'tk-data-{l["code"]}.js'), 'w', encoding='utf8').write(data_js())
    if not ANALYTICS: os.remove(os.path.join(dst, 'analytics.js'))  # only ship what is used
    os.makedirs(os.path.join(dst, 'tools'))  # per-tool scripts are external files (lets the CSP drop 'unsafe-inline' for scripts, and lets browsers cache them)
    for t in TOOLS_ALL:
        if t['kind'] == 'panel': shutil.copy(os.path.join(SRC, 'tools', t['id'], 'script.js'), os.path.join(dst, 'tools', t['id'] + '.js'))
    for r, _, fs in os.walk(dst):
        for f in fs:
            full = os.path.join(r, f); VER[os.path.relpath(full, dst).replace(os.sep, '/')] = hashlib.md5(open(full, 'rb').read()).hexdigest()[:8]

def build_language(code):
    use_lang(code)
    for t in TOOLS: tool_page(t)
    for c in CATS:
        if c['page']: cat_page(c)
    tools_index(); home_page()
    content_page('about', PG['about'], L['about_title'], L['about_desc'], L['about'])
    content_page('privacy', PG['privacy'], L['privacy_title'], L['privacy_desc'], L['privacy'])
    content_page('terms', PG['terms'], L['terms_title'], L['terms_desc'], L['terms'])
    contact_page()
    if code == DEFAULT: page_404()

def main():
    if os.path.isdir(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    collect_paths()
    if errors:
        for e_ in errors: print('ERROR:', e_)
        sys.exit(1)
    copy_assets()
    for l in LANGS: build_language(l['code'])
    use_lang(DEFAULT)
    # lastmod: only moves when a page's generated HTML actually changes
    lm_file = os.path.join(ROOT, 'build', 'lastmod.json'); lm = json.load(open(lm_file)) if os.path.exists(lm_file) else {}
    lastmod = {}
    for lang, p, idx, page in PAGES:
        k = p if lang == DEFAULT else f'{lang}:{p}'  # English keys are unchanged from earlier builds
        h = hashlib.sha1(re.sub(r'\?v=[0-9a-f]{8}', '', page).encode()).hexdigest(); e = lm.get(k)
        if not e or e['hash'] != h: e = {'hash': h, 'date': TODAY}
        lm[k] = e; lastmod[(lang, p)] = e['date']
    if not SCRATCH: json.dump(lm, open(lm_file, 'w'), indent=1, sort_keys=True)
    w = lambda name, s: open(os.path.join(DIST, name), 'w', encoding='utf8').write(s)
    w('sitemap.xml', sitemap(lastmod)); w('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n'); w('llms.txt', llms_txt())
    if not SCRATCH:
        open(os.path.join(ROOT, 'vercel.json'), 'w').write(vercel_json())
        os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
        with open(os.path.join(ROOT, 'docs', 'url-map.csv'), 'w', newline='', encoding='utf8') as f: csv.writer(f).writerows(url_map())
        with open(os.path.join(ROOT, 'docs', 'locale-map.csv'), 'w', newline='', encoding='utf8') as f: csv.writer(f).writerows(locale_map())
    # launch blockers (reported, and fatal with --strict)
    if not CFG.get('siteUrlConfirmed') and not os.environ.get('SITE_URL'): warnings.append(f'SITE_URL {SITE_URL} is a staging address, not a confirmed production domain (site.config.json: siteUrlConfirmed).')
    if not CFG.get('contactEmail'): warnings.append('No contactEmail set: the Contact page says contact details are not yet published.')
    if not CFG.get('operatorName'): warnings.append('No operatorName set: Privacy/Terms say the operator is not yet named.')
    print(f'built {len(PAGES)} pages -> dist/  (SITE_URL={SITE_URL}, urlStyle={STYLE}, languages={",".join(l["code"] for l in LANGS)})')
    for w_ in warnings: print('LAUNCH BLOCKER:', w_)
    for e_ in errors: print('ERROR:', e_)
    if errors or (STRICT and warnings): sys.exit(1)

if __name__ == '__main__': main()
