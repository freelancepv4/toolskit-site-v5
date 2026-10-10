# Localization guide (ToolsKit)

English is the base. A language is built when it is enabled in `site.config.json` AND has all the files below. A language lists only the tools it has localized; other tools stay English-only and are not linked from that language.

## Files per language `<lang>` (all required)
| File | Content |
|---|---|
| `src/locales/<lang>.json` | every key of `en.json`, translated. `slugs` = URL names (ASCII, lowercase, hyphens, `.html` for pages, no `.html` for the `tools` folder). `search_words` = stop/connector/filler words for search. `months` = month names. |
| `src/data/tools.<lang>.json` | `categories`, `tools`, `unsupported` (see below) |
| `src/strings/pdf.<lang>.json` | every key of `src/strings/pdf.json` (flat object) |
| `src/tools/<id>/strings.<lang>.json` | every key of that tool's `strings.json` `en` object (flat object) |
| `src/content/<lang>/{home,about,privacy,terms,404}.html` | long pages; keep the `{{ … }}` / `{{{ … }}}` placeholders |

### `tools.<lang>.json`
```
{"categories": {"pdf": {"name","dir","card","intro","title","description","faq":[[q,a],…],"syn":[…]},
                "calc": {…same…}, "text": {"name","dir","card","syn"}},
 "tools": {"<id>": {"file","name","h1","title","description","card","lead","steps":[[h,p]×3],"formula","faq","good","limits":[…],
                    "disclaimer" (only if the English tool has one),"ws":{"title","choose","hint"} (only PDF tools),"syn":[native search phrases]}},
 "unsupported": [{"label","patterns":[…],"related":[ids or "cat:pdf"],"note"?}]}
```
`dir` and `file` become the URL: `/<lang>/<dir>/<file>`. ASCII only, no diacritics.

## Rules
1. Write for how people in that market search; do not translate word for word. The primary query comes from `docs/research/native-terms.json` and `docs/research/opportunity-matrix.csv`; use it naturally in title, H1 and lead, never stuffed.
2. Describe only what the tool really does (compare with the English entry, `limits`, and the script). Keep every limit: 150 MB file limit, no password-protected PDFs, Compress PDF does not recompress images, PDF→images produces PNG, etc.
3. Privacy wording: processing happens in the browser; files are not uploaded to ToolsKit. Do not write "100% secure", "completely private", "best", "fastest", or any claim about guarantees.
4. No invented statistics, reviews, tax advice, legal identities, addresses or company data.
5. Numbers/dates follow the language automatically in the tools (`toLocaleString`); write prose with the local conventions (decimal comma, thin-space percent where customary).
6. VAT tool: `rate_default` is only a prefilled starting value. Use the well-known standard rate of the market and say in `rate_help` that the user must check the rate that applies. Never state it as legal advice.
7. Titles ≤ 60 characters and descriptions ≤ 155 characters where the language allows. Brand "ToolsKit" is never translated; it ends titles after " | ".
8. Interface strings must fit on a 320 px screen: keep buttons short.
9. Legal pages (`privacy`, `terms`): faithful translation of the English draft, same structure and placeholders, keep the LEGAL REVIEW comment. Do not add jurisdiction-specific legal claims that are not in the English text.
10. Everything is a first draft until a native editor has reviewed it. Record doubts in `docs/research/localization-notes-<lang>.md` (queries chosen, terms you were unsure about, anything needing native or legal review).

## Verify
`TK_DIST=/tmp/dist-<lang> TK_LANGS=en,<lang> python3 build/build.py` must end without `ERROR:` lines. `TK_DIST` keeps the build out of the shared `dist/`.
