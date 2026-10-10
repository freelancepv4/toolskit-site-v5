# Localization notes: German (de), wave 1

Status: first draft, not reviewed by a native editor or a legal professional. Scope: merge-pdf, split-pdf, rotate-pdf, compress-pdf, pdf-to-images, images-to-pdf, percentage, vat, loan, compound, word-counter (categories pdf, calc, text).

## Queries chosen (all volumes are OpenSEO estimates, 2026-10-10, see opportunity-matrix.csv; nothing measured)
| Tool | Primary (title/H1/lead) | Evidence |
|---|---|---|
| merge-pdf | pdf zusammenfügen | 368,000, KD 21. Also in syn: zusammenführen, verbinden, kombinieren (SERP also shows "zusammenführen") |
| compress-pdf | pdf komprimieren (+ pdf verkleinern in H1/syn) | 135,000 KD 20; pdf verkleinern 60,500 KD 23 |
| split-pdf | pdf teilen | 9,900 KD 11 |
| rotate-pdf | pdf drehen | 5,400 KD 0 |
| images-to-pdf | jpg in pdf | 14,800 KD 20 |
| pdf-to-images | pdf in bilder (PNG); validated query "pdf in jpg" (18,100, KD 26) is NOT used as title/syn | tool exports PNG only; "pdf in jpg" is an unsupported intent with a note, and is mentioned honestly in lead/FAQ |
| percentage | prozentrechner | 246,000 KD 6 |
| vat | mehrwertsteuer rechner | 49,500 KD 9 (not "umsatzsteuer", 4,400; in syn only) |
| loan | kreditrechner | 110,000 KD 24 |
| compound | zinseszinsrechner | 135,000 KD 7 |
| word-counter | zeichenzähler & wortzähler | zeichenzähler 22,200 KD 5; wortzähler 8,100 KD 16 (no word-counter row in native-terms.json; taken from the matrix) |

## URLs
/de/pdf-werkzeuge/{pdf-zusammenfuegen,pdf-teilen,pdf-drehen,pdf-komprimieren,pdf-in-bilder,jpg-in-pdf}.html, /de/rechner/{prozentrechner,mehrwertsteuer-rechner,kreditrechner,zinseszinsrechner}.html, /de/text-werkzeuge/zeichenzaehler.html. Pages: ueber-uns, kontakt, datenschutz, nutzungsbedingungen; tools folder "werkzeuge".

## Decisions and doubts for native review
- Sie-form throughout. "Zu- oder Abnahme", "Von/Auf" labels in the percentage change block; "Grundwert/Teilwert" for the what-percent block.
- VAT: rate_default 19 is only a prefilled value; rate_help mentions that a reduced rate exists, no rates beyond 19 are named, no advice. Please confirm the wording "Mehrwertsteuer herausrechnen" vs. "Brutto → Netto (herausrechnen)" fits the select width on 320 px.
- Search: "brutto netto rechner" (1.83M, salary intent) is routed to an unsupported entry "Gehalts- oder Steuerrechner" (related: vat, percentage, calc). The VAT tool has syn "netto in brutto", "brutto in netto", "mehrwertsteuer netto brutto"; if the search ranking ever lets VAT outrank the unsupported entry for salary queries, drop those syn.
- Loan: label "Jahreszins" is the nominal rate typed by the user; FAQ states it is not the effektiver Jahreszins. Compound: "Zinsperiode" wording and the note that contributions are per compounding period.
- Search words: both umlaut and ae/oe/ue forms are listed because the search folds ü to u, not to ue; syn and unsupported patterns get ASCII variants automatically.
- Unsupported entries for image/dev/QR scanner etc. keep English parity but have empty "related" because those tools are not in the German scope yet. Revisit when image/QR tools are localized.
- Output file names are German ASCII (zusammengefuegt.pdf, -auszug.pdf, -gedreht.pdf, -komprimiert.pdf, bilder.pdf, seite-N.png).
- Numbers in prose use a non-breaking space before % ("10 %").

## Needs legal review
privacy.html and terms.html are faithful translations of the English drafts with the LEGAL REVIEW comment kept (plus a German note). Points to check for DE/AT/CH: DSGVO wording, Impressum duty (operator identity placeholders), TTDSG/TDDDG on local storage, consumer-law limits of the liability clause, and whether a German-law governing clause or Widerrufs/Streitbeilegung notes are needed. None were added.

## Shared-code observations
- build/check.py reads DIST + '/assets/tk-data.js' (not tk-data-<lang>.js) and ignores TK_DIST in my run; I did not use it for verification.
- build/test_links.py reports "url-map legacy /cv-builder/index.html: 200 -> None" on the English-only part of the build; unrelated to de.
