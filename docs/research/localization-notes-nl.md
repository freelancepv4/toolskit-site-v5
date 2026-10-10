# Localization notes: Dutch (nl), wave 1

Status: first draft, not reviewed by a native editor or a legal professional. Market: Netherlands first (understandable in Flanders). Tone: informal-neutral "je/jouw". Scope: merge-pdf, split-pdf, rotate-pdf, compress-pdf, pdf-to-images, images-to-pdf, percentage, vat, loan, compound, word-counter (categories pdf, calc, text).

## Queries chosen (volumes are OpenSEO estimates, 2026-10-10, see opportunity-matrix.csv; nothing measured)
| Tool | Primary (title/H1/lead) | Evidence |
|---|---|---|
| merge-pdf | pdf samenvoegen | 40,500, KD 0. syn: combineren, aan elkaar plakken, verbinden, mergen |
| compress-pdf | pdf verkleinen (+ pdf comprimeren in H1/title/syn) | native-terms primary "pdf verkleinen" 9,900; "pdf comprimeren" 8,100 (both KD 0) |
| split-pdf | pdf splitsen | 8,100, KD 0 |
| rotate-pdf | pdf roteren | 110, KD 0 (test). "pdf draaien" is in syn from general usage, not from a measured row |
| pdf-to-images | pdf naar afbeeldingen / pdf naar png; validated query "pdf naar jpg" (6,600, KD 0) is NOT used in title/syn | tool exports PNG only; "pdf naar jpg" is an unsupported entry with a note, and the FAQ says so honestly |
| images-to-pdf | jpg naar pdf | 5,400, KD 0 (test) |
| percentage | percentage berekenen (+ procenten berekenen, korting berekenen in syn) | 9,900, KD 0. "procenten berekenen" has no matrix row; it is a natural variant |
| vat | btw berekenen | 60,500, KD 0 (vs "btw calculator" 1,900). Labels "Exclusief btw → inclusief btw" / "Inclusief btw → exclusief btw" |
| loan | lening berekenen | 1,900, KD 26. "hypotheek berekenen" (201,000, KD 47) is only in syn, see below |
| compound | samengestelde rente (berekenen) + rente op rente | 320, KD 0. "rente op rente" not in matrix |
| word-counter | woorden tellen + tekens tellen | woorden tellen 6,600 KD 0; tekens tellen 880 KD 0 |

## URLs
/nl/pdf-tools/{pdf-samenvoegen,pdf-splitsen,pdf-roteren,pdf-verkleinen,pdf-naar-afbeeldingen,jpg-naar-pdf}.html, /nl/rekentools/{percentage-berekenen,btw-berekenen,lening-berekenen,samengestelde-rente}.html, /nl/teksttools/woorden-tellen.html. Pages: over-ons, contact, privacybeleid, gebruiksvoorwaarden; tools folder "tools". Output file names: samengevoegd.pdf, -selectie.pdf, -geroteerd.pdf, -verkleind.pdf, afbeeldingen.pdf, pagina-N.png.

## Decisions and doubts for native review
- Names: "Btw berekenen" (lowercase btw as in standard Dutch); "JPG en PNG naar PDF" as card name, because the tool accepts PNG too. Category "Rekentools" rather than "Rekenmachines".
- VAT: rate_default 21 is only a prefilled value; rate_help says a reduced rate exists without naming it, no advice. The Belastingdienst is not named as authority in the tool copy (generic "belastingdienst van je land" in the disclaimer); check wording.
- "Hypotheek berekenen" (201,000, KD 47) points at the loan tool through syn only, because the tool is a fixed-rate annuity estimate. Loan lead/FAQ/limits say clearly that it does not compute a maximum mortgage, tax deduction or linear repayment. A dedicated "maximale hypotheek" unsupported entry (related loan) catches the income-based intent. If a native reviewer finds the syn misleading, drop "hypotheek berekenen" and "hypotheek maandlasten berekenen".
- "bruto netto berekenen" (74,000) is routed to the unsupported entry "salaris- of belastingrekenmachine" (related vat, percentage, calc); the VAT syn do not contain bruto/netto.
- Compress: the title says "verkleinen of comprimeren" but the copy states plainly that images are not recompressed and no target size can be set (FAQ "tot een bepaalde grootte").
- Unsupported entries only for things that exist nowhere in ToolsKit (HEIC, background removal, crop, OCR, lorem ipsum, ...). Not added although Dutch demand exists, because the English tools exist and are simply not localized yet: "cv maken" (33,100), "qr code generator" (33,100), "webp naar jpg/png", "afbeelding verkleinen/comprimeren", "celsius naar fahrenheit". Revisit when those tools are localized. Related lists only use in-scope ids or cat:pdf / cat:calc.
- "lorem ipsum" (18,100) and "leeftijd berekenen" (8,100) appear as unsupported intents; both are candidates for new tools.
- Search words: stop/conn/filler lists are Dutch ("naar" is a connector; "omzetten, converteren, omrekenen" are fillers).
- Numbers in prose: "10%" without space (common in Dutch web copy; some style guides write "10 procent").
- Terms to confirm: "rente bijschrijven" (compounding frequency label), "annuïtair/annuïteit" (accented and ASCII both in syn), "JKP" (jaarlijks kostenpercentage), "Herstellen" for the reset button, "pdf" lowercase in running text and "PDF" in tool names.

## Needs legal review (AVG wording)
privacy.html and terms.html are faithful translations of the English drafts with the LEGAL REVIEW comment kept (plus a Dutch note). Check for NL/BE: AVG/GDPR terms (verwerkingsverantwoordelijke, Autoriteit Persoonsgegevens as toezichthouder is NOT named, as the English text names none), Telecommunicatiewet rules on storage on the device (lokale opslag), identification duty of the operator, consumer-law limits of the liability clause (Boek 6/7 BW), Belgian rules if Flanders is targeted. No jurisdiction-specific claims were added.

## Shared-code observations
- build.py only writes the default-language 404.html (`if code == DEFAULT: page_404()`), so src/content/nl/404.html is validated but never served; the 404 page stays English.
- The build prints "dist/" in its summary line even when TK_DIST is set (output goes to TK_DIST correctly).
