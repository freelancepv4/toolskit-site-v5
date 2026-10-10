# Localization notes: Polish (pl), wave 1

Status: first draft, not reviewed by a native editor or a legal professional. Scope: merge-pdf, split-pdf, rotate-pdf, compress-pdf, pdf-to-images, images-to-pdf, percentage, vat, loan, compound, word-counter (categories pdf, calc, text).

## Queries chosen (volumes are OpenSEO estimates, 2026-10-10, see opportunity-matrix.csv; nothing measured)
| Tool | Primary (title/H1/lead) | Evidence |
|---|---|---|
| merge-pdf | połącz pdf (+ scal pdf in lead/syn) | 27,100, KD 14 |
| compress-pdf | kompresja pdf (H1 "Kompresja PDF – zmniejsz rozmiar pliku") | kompresja pdf 18,100 KD 30; zmniejsz pdf 14,800 KD 3 (in lead and syn) |
| split-pdf | podziel pdf | 18,100, KD 0 |
| rotate-pdf | obróć pdf | 2,900, KD 0 |
| images-to-pdf | jpg na pdf | 22,200, KD 1 |
| pdf-to-images | pdf na png / pdf na obrazy | validated query "pdf na jpg" (22,200, KD 0) is NOT used in title or syn: the tool exports PNG only. "pdf na jpg" is an unsupported intent with a note, and the FAQ answers it honestly. |
| percentage | kalkulator procentowy | 33,100, KD 0 |
| vat | kalkulator vat | 33,100, KD 26; "kalkulator netto brutto vat" 2,900 KD 19 in syn |
| loan | kalkulator kredytowy (+ kalkulator kredytu in lead/syn) | matrix primary "kalkulator kredytowy" 33,100 KD 51 |
| compound | procent składany kalkulator (title "Procent składany – kalkulator z wpłatami", name "Kalkulator procentu składanego") | 4,400, KD 0 |
| word-counter | licznik słów i znaków | licznik słów 27,100 KD 6; licznik znaków 14,800 KD 3 (matrix rows with action "add"; no native-terms row) |

## URLs
/pl/narzedzia-pdf/{polacz-pdf,podziel-pdf,obroc-pdf,kompresja-pdf,pdf-na-obrazy,jpg-na-pdf}.html, /pl/kalkulatory/{kalkulator-procentowy,kalkulator-vat,kalkulator-kredytowy,kalkulator-procentu-skladanego}.html, /pl/narzedzia-tekstowe/licznik-slow.html. Pages: o-nas, kontakt, polityka-prywatnosci, regulamin; tools folder "narzedzia".

## Unsupported intents with demand
- "kalkulator wynagrodzeń" (368,000, KD 44), "kalkulator brutto netto" (135,000, KD 86): listed as unsupported (related only cat:calc, with a note that the VAT calculator is not a salary calculator). The VAT FAQ also says so. Salary maths depends on Polish contribution and tax rules and is not in scope.
- "pdf na jpg" (22,200): unsupported with note (PNG only), related pdf-to-images.
- "pdf na word" (18,100), "heic na jpg" (5,400), "usuwanie tła" (5,400), "kalkulator wieku" (5,400), "generator haseł" (27,100), "lorem ipsum" (27,100), json/base64 (9,900 each): unsupported entries.
- "kreator cv" and "generator kodów qr" exist in the English product but are not localized in wave 1; they are neither listed as unsupported nor linked.

## Decisions and doubts for native review
- Register: impersonal imperative ("Wybierz", "Dodaj"), no "Ty"/"Państwo". A few phrases such as "Prosimy nie wysyłać…" and "Użytkownik zobowiązuje się…" (terms) use impersonal/third-person forms.
- Percent sign written without a space ("23%"), the common convention in Polish web UIs; check house style.
- VAT: rate_default = 23 (standard rate in Poland) as a start value only; rate_help and FAQ say reduced rates exist and the user must enter the applicable one. Labels "netto → brutto" / "brutto → netto".
- "Kompresja PDF" vs "Zmniejsz PDF": name uses the validated seed; "zmniejsz pdf" is in lead, syn and the home chip ("Zmniejsz plik PDF").
- "Podziel PDF" actually extracts one page range into one new PDF; the lead and limits say so, to avoid over-promising.
- Loan: the page says "równe raty miesięczne (stałe, annuitetowe)"; declining installments are not supported. Not stating RRSO, WIBOR or Polish consumer-credit rules.
- Compound: label "Suma wpłat (wraz z kwotą początkową)" because the script adds the initial amount to the contributions.
- Word counter: label "Znaki bez spacji", "Czas czytania" (200 wpm); sentence count note uses "np." and "tzn." as examples.
- Months in the genitive (stycznia … grudnia). Plurals: n_tools_one/few/many/other defined.
- Search: diacritics are folded by search.js, but syn lists keep both spellings as required. stop words include "to", "co", "jest", "o", "po", "za" (harmless because they are also removed from the synonym phrases). conn words: na, do, w, z, jako, 2.
- Unsupported labels are lower-case nominative phrases because they are inserted after "Obecnie w ToolsKit nie ma narzędzia: …". Check the grammar of the long labels.

## Needs legal review (RODO wording)
privacy.html "Prawa użytkownika" translates the English GDPR/UK GDPR/California sentence faithfully (RODO, "organ ochrony danych"). No controller identity, no Polish-law specifics (UODO, legal bases, retention periods) were added; a Polish lawyer should review the whole page, the terms (governing law, consumer rights wording "ustawowe prawa konsumentów") and the cookie/consent paragraph (ustawa Prawo telekomunikacyjne / ePrivacy not discussed).

## Shared-code observations (not fixed)
1. build.py line ~190: category cards append a hard-coded English "N tool(s)" ("6 tools.") to the card text on the home page for every language; it should use n_tools_* plural keys of the locale.
2. page_404() runs only for the default language; src/content/pl/404.html is validated by nobody and no /pl/404.html is generated, so Polish visitors get the English 404 page.
