# ToolsKit European search-demand research

Research date: 2026-10-10. Single working data source: **OpenSEO `get_keyword_metrics`** (DataForSEO / Google Ads-derived volumes, KD, CPC). All figures below come from those tool results and are tool estimates, not measurements of ToolsKit traffic. Every row in `opportunity-matrix.csv` is therefore labeled `estimated-by-tool`. No row is `measured` (no first-party Search Console data was queried) and the SERP checks were qualitative only.

Volumes are Google monthly search estimates for the country/language of the query. Near-synonym queries share Google Ads grouping, so do not sum across rows. "KD" is the tool's difficulty score; 0 often means "not enough SERP data", not "free to rank".

## Top ~20 opportunities (ranked by volume x feasibility x fit with existing in-browser tools)

| # | Opportunity | Market / query (monthly volume, KD) | Action | Confidence |
|---|---|---|---|---|
| 1 | Merge PDF localized | es "unir pdf" 450,000 (KD 20); de "pdf zusammenfügen" 368,000 (21); fr "fusionner pdf" 201,000 (16); it "unire pdf" 165,000 (0); pt "juntar pdf" 74,000 (13); nl "pdf samenvoegen" 40,500 (0); pl "połącz pdf" 27,100 (14) | improve/localize merge-pdf | High on demand; medium on ranking (incumbents like Smallpdf in DE SERP) |
| 2 | Compress PDF localized | fr "compresser pdf" 301,000 (15); it "comprimere pdf" 201,000 (27); es "comprimir pdf" 165,000 (15); de "pdf komprimieren" 135,000 (20); de "pdf verkleinern" 60,500; fr "réduire taille pdf" 49,500; es "reducir tamaño pdf" 40,500; en-GB "compress pdf" 60,500 (50) | improve compress-pdf | High on demand. Caveat: in-browser compression quality may be weaker than server-side; test before promising size targets |
| 3 | Percentage calculator localized | de "prozentrechner" 246,000 (KD 6); en-GB 246,000 (33); fr "calcul pourcentage" 90,500 (18); it "calcolo percentuale" 90,500 (0); es "calcular porcentaje" 40,500; pl "kalkulator procentowy" 33,100 (0); fi "prosenttilaskuri" 90,500 (11) | improve percentage | High |
| 4 | Split PDF localized | it "dividere pdf" 135,000 (0); es "dividir pdf" 90,500 (33); fr "diviser pdf" 49,500 (1); pl "podziel pdf" 18,100; de "pdf teilen" 9,900 | improve split-pdf | High |
| 5 | VAT calculator localized | en-GB "vat calculator" 165,000 (25), "vat calculator uk" 27,100; fr "calcul tva" 74,000 (18); nl "btw berekenen" 60,500 (0); de "mehrwertsteuer rechner" 49,500 (9); es "calculadora iva" 49,500 (19); it "calcolo iva" 40,500 (0), "scorporo iva" 33,100 (0); pl "kalkulator vat" 33,100 (26); fi "alv laskuri" 49,500; ro "calculator tva" 18,100 | improve vat; add per-country rate presets and "scorporo / HT-TTC / netto-brutto" modes | High on demand; rates are country-specific (see caveats) |
| 6 | Compound interest calculator | en-GB 201,000 (56); de "zinseszinsrechner" 135,000 (7); es 12,100; it 12,100; fr 5,400; pl 4,400 | improve compound (de is the standout: high volume, KD 7) | High for de/en-GB |
| 7 | Loan calculator | de "kreditrechner" 110,000 (24, CPC 3.77 est., high ad competition); en-GB 60,500 (22); fr "simulateur prêt" 22,200; pl 33,100 (KD 51) | improve loan | Medium (YMYL, strong incumbents, bank sites) |
| 8 | Images to PDF (JPG to PDF) | es "jpg a pdf" 90,500 (28); en-GB 60,500 (54); fr 33,100 (10); pl 22,200 (1); de 14,800; it 14,800; el "jpg to pdf" 60,500 (KD 43, English-language query in GR) | improve images-to-pdf | High |
| 9 | Word counter / character counter (MISSING) | en-GB "word counter" 301,000 (57), "character counter" 60,500; es "contador de palabras" 90,500, "contador de caracteres" 22,200; it "conta caratteri" 33,100, "conta parole" 18,100; pl "licznik słów" 27,100 (KD 6); de "zeichenzähler" 22,200 (5); fr "compteur de mots" 18,100 | **add** (trivial client-side, one tool, multiple locales) | High on demand; low build cost |
| 10 | Convert image: WebP/HEIC to JPG/PNG | en-GB "heic to jpg" 33,100, "webp to jpg" 27,100, "webp to png" 27,100; de "webp in jpg" 22,200, "webp in png" 18,100, "heic in jpg" 8,100; it "webp in jpg" 18,100, "webp in png" 12,100; es "heic a jpg" 14,800, "webp a jpg" 12,100; fr "heic en jpg" 14,800 | localize convert-image with dedicated landing pages per format pair | High; verify HEIC decoding works in-browser (needs a WASM decoder) |
| 11 | Password generator (MISSING) | en-GB 60,500 (37); fr "générateur mot de passe" 40,500 (36); pl "generator haseł" 27,100 (6); de 33,100 (13); es 12,100; it 12,100 | add | High demand; commodity tool |
| 12 | Lorem ipsum (MISSING) | en-GB 40,500; de 49,500 (KD 6); fr 40,500; pl 27,100; es 27,100; it 27,100; nl 18,100 | add | High demand; same string in all locales so one tool serves all |
| 13 | Age calculator / days between dates (MISSING) | en-GB "age calculator" 110,000; de "tagerechner" 49,500 (KD 2), "alter berechnen" 9,900; it "calcolo giorni tra due date" 27,100; nl "leeftijd berekenen" 8,100; pl "kalkulator wieku" 5,400; es "calcular edad" no data | add | Medium-high |
| 14 | PDF to images | de "pdf in jpg" 18,100; fr "pdf en jpg" 18,100; it 12,100; es "pdf a jpg" 40,500; en-GB "pdf to jpg" 49,500; pl 22,200 | improve pdf-to-images | High |
| 15 | Italian scorporo IVA mode | it "scorporo iva" 33,100 (0), "calcolo iva scorporo" 4,400; SERP is editorial/fiscal sites plus a Qonto tool | improve vat (add scorporo/ventilazione mode and landing page) | High demand, medium ranking feasibility |
| 16 | Resize image | fr "redimensionner image" 18,100 (11); en-GB 18,100 (57); es 12,100 (21); it "ridimensionare immagine" 9,900 (4); de "bildgröße ändern" 4,400 | improve resize-image (fr/en/es/it first) | High |
| 17 | Compress image | es "comprimir imagen" 14,800 (51); en-GB 12,100 (75); fr "compresser image" 33,100 (10); fr "compresser photo" 14,800; de "bild verkleinern" 12,100 (35); it 6,600 | improve compress-image | High |
| 18 | QR code generator | de 135,000 (KD 80); en-GB 135,000 (76); fr 60,500 (86); nl 33,100 (0); pl "generator kodów qr" 9,900 (6); es 18,100 (33); it 6,600 (18) | improve url-qr-code and wifi pages; de "wlan qr code" 3,600 (KD 0) is an easy niche | Medium: head terms very competitive, niche variants are realistic |
| 19 | JSON formatter / Base64 (MISSING) | en-GB "json formatter" 18,100 (31); de 18,100 (KD 0); fr 14,800; es 12,100; base64 decode 6,600-18,100 across markets | add (developer audience) | Medium: KD varies widely (63-76 in fr/it/es/nl/pl), de KD 0 looks suspicious |
| 20 | CV builder | de "lebenslauf erstellen" 49,500 (44); nl "cv maken" 33,100 (41); en-GB "cv maker" 33,100; pl "kreator cv" 27,100 (53); es 2,400; it 1,900 | improve cv in de/nl/pl/en-GB; CPC 3.7-7.8 shows ad value but also very strong incumbents | Medium |

Country-specific high-volume tools not currently in ToolsKit (need maintained data; see section below): de/fr/it/es/nl/pl/en-GB gross-net salary (de "brutto netto rechner" 1,830,000; pl "kalkulator wynagrodzeń" 368,000; fr "salaire brut net" 368,000; en-GB "take home pay calculator" 301,000; en-GB "stamp duty calculator" 246,000), it "calcolo codice fiscale" 1,220,000, nl "hypotheek berekenen" 201,000.

## Per-country notes

### Germany (de)
Top validated queries: "brutto netto rechner" 1,830,000 (KD 48); "pdf zusammenfügen" 368,000 (21); "prozentrechner" 246,000 (6); "pdf komprimieren" 135,000 (20); "zinseszinsrechner" 135,000 (7); "kreditrechner" 110,000 (24); "pdf verkleinern" 60,500; "mehrwertsteuer rechner" 49,500 (9); "tagerechner" 49,500; "lebenslauf erstellen" 49,500; "bild verkleinern" 12,100 (35); "pdf teilen" 9,900. Terminology: use "Mehrwertsteuer" (not only "Umsatzsteuer", 4,400), "zusammenfügen" as primary (the SERP also showed "zusammenführen"), "pdf teilen" (not "splitten"), "WLAN QR-Code". Conventions: decimal comma and period thousands separator (1.234,56 EUR), standard VAT 19% and reduced 7% (verify current rates before shipping), A4 paper. Note "pdf komprimieren" and "pdf verkleinern" are different queries; one page should target both.

### France (fr)
"salaire brut net" 368,000; "compresser pdf" 301,000 (15); "fusionner pdf" 201,000 (16); "calcul pourcentage" 90,500; "calcul tva" 74,000; "diviser pdf" 49,500 (KD 1); "réduire taille pdf" 49,500; "compresser image" 33,100; "jpg en pdf" 33,100; "redimensionner image" 18,100; "convertir ttc en ht" 8,100; "calcul tva ht ttc" 2,900. Terminology: "compresser" is the dominant verb; French uses prepositions "en" (jpg en pdf), "diviser" outranks "séparer" (12,100). VAT: HT/TTC modes matter; rates 20/10/5.5/2.1 (verify). Decimal comma, narrow/space thousands separator, A4.

### Italy (it)
"calcolo codice fiscale" 1,220,000 (KD 10); "comprimere pdf" 201,000 (27); "unire pdf" 165,000 (0); "dividere pdf" 135,000 (0); "calcolo percentuale" 90,500 (0); "calcolo iva" 40,500; "scorporo iva" 33,100; "calcolo imu" 33,100; "calcolo giorni tra due date" 27,100; "calcolo tfr" 12,100; "ritenuta d'acconto calcolo" 1,300 (smaller than the seeds implied). Terminology: "scorporo IVA" (extract VAT from gross) is a distinct high-volume intent versus "calcolo iva"; "ridurre dimensione pdf" 18,100 is an additional compress phrasing; "comprimere pdf online" 14,800. IVA standard 22% (verify). Decimal comma, A4.

### Spain (es)
"unir pdf" 450,000 (20); "quitar fondo" 201,000 (13); "comprimir pdf" 165,000 (15); "pdf a word" 110,000; "contador de palabras" 90,500; "dividir pdf" 90,500 (33); "jpg a pdf" 90,500 (28); "calculadora irpf" 49,500; "calculadora iva" 49,500 and "calcular iva" 49,500 (separate queries); "calcular porcentaje" 40,500; "reducir tamaño pdf" 40,500. Terminology: "a" preposition for conversions; "comprimir" for PDF, "reducir tamaño" for both. IVA 21/10/4 (verify); IRPF depends on regional rules, so avoid a generic tool. Decimal comma, A4.

### Netherlands (nl)
"hypotheek berekenen" 201,000 (47); "bruto netto berekenen" 74,000 (0); "btw berekenen" 60,500 (0); "pdf samenvoegen" 40,500 (0); "cv maken" 33,100 (41); "qr code generator" 33,100; "pdf naar word" 18,100; "achtergrond verwijderen" 14,800. Note "btw berekenen" (60,500) far outweighs "btw calculator" (1,900), and "pdf verkleinen" 9,900 > "pdf comprimeren" 8,100. Small image volumes: "foto verkleinen" 3,600 > "afbeelding verkleinen" 2,400. BTW 21% / 9% (verify). Decimal comma, A4. Low KD numbers (0) in NL are common data-sparsity artifacts, so treat feasibility cautiously.

### Poland (pl)
"kalkulator wynagrodzeń" 368,000 (44); "kalkulator brutto netto" 135,000 (KD 86); "kalkulator vat" 33,100 (26); "kalkulator procentowy" 33,100 (0); "generator haseł" 27,100; "licznik słów" 27,100 (6); "połącz pdf" 27,100 (14); "jpg na pdf" 22,200; "pdf na jpg" 22,200; "kompresja pdf" 18,100 (30); "podziel pdf" 18,100; "zmniejsz pdf" 14,800. Terminology: "kompresja pdf" is the compress seed, but "zmniejsz pdf" is also big. Images: "zmniejsz zdjęcie" only 390 whereas "zmiana rozmiaru zdjęcia" 3,600 and "kompresja zdjęć" 1,300, so the Polish image seeds are weak. VAT 23/8/5 (verify). Decimal comma, space thousands separator, A4.

### United Kingdom (en-GB)
"take home pay calculator" 301,000; "word counter" 301,000 (57); "percentage calculator" 246,000 (33); "stamp duty calculator" 246,000; "compound interest calculator" 201,000 (56); "vat calculator" 165,000 (25); "remove background" 165,000 (64); "age calculator" 110,000; "mortgage calculator uk" 90,500; "merge pdf" 60,500 (KD 64); "compress pdf" 60,500 (50). The suggested seeds "compress pdf to 100kb" (210) and "compress image to 100kb" (210) are tiny, but "reduce pdf size" 18,100 is meaningful. UK VAT is 20%/5%/0% (verify), decimal point, A4, GBP, "colour" spelling for any colour tool (only "color picker" 22,200 measured; "colour picker" not tested).

### Secondary markets (light sample, one batch each)
Portugal (pt-PT): "juntar pdf" 74,000 (13); "remover fundo" 49,500; "comprimir pdf" 33,100; "calculadora iva" 6,600. Sweden: "jpg till pdf" 6,600; "procenträknare" 6,600; "komprimera pdf" 2,400; "slå ihop pdf" 1,600. Denmark: "momsberegner" 3,600; "komprimer pdf" 1,900. Norway (queried as nb): "prosentkalkulator" 6,600; "mva kalkulator" 2,900; "slå sammen pdf" 1,000. Finland: "prosenttilaskuri" 90,500 (KD 11); "alv laskuri" 49,500; "yhdistä pdf" 1,600 (note: PDF volumes are tiny, calculators big). Romania: "calculator tva" 18,100; "calculator procente" 12,100; "unire pdf" 3,600. Czechia: "kalkulačka dph" 6,600; "odstranění pozadí" 2,900; "rozdělit pdf" 2,400. Greece: only "jpg to pdf" 60,500 (English query), Greek PDF queries 720-1,600. Nordics/CEE: percentage and VAT calculators dominate, PDF tools are small; Portugal behaves like a smaller Spain. Finland's calculators (90,500 and 49,500) are notable given the small population but not verified further.

## Highest-priority existing pages to improve
1. merge-pdf in es, de, fr, it, pt, nl, pl.
2. compress-pdf in fr, it, es, de (also target "pdf verkleinern/reducir tamaño/réduire taille/ridurre dimensione" phrasing).
3. percentage (de, fr, it, en-GB, fi).
4. vat (en-GB, fr, nl, de, es, it incl. scorporo, pl, ro, fi) with country presets and HT/TTC/netto-brutto modes.
5. split-pdf (it, es, fr).
6. compound (de, en-GB) and loan (de, en-GB).
7. images-to-pdf (es, en-GB, fr, pl) and pdf-to-images (es, en-GB, de, fr, pl).
8. convert-image: dedicated WebP/HEIC pages for en-GB, de, it, es, fr.
9. resize-image / compress-image (fr, es, it, en-GB).
Low value: length, area, temperature converters and the Instagram bio/hashtag/YouTube title generators. Measured volumes are tiny (de "längenumrechner" 210, fr "générateur hashtag instagram" 40, en-GB "instagram bio generator" 210, "youtube title generator" 390). The temperature converter has modest demand only in en-GB (60,500 "celsius to fahrenheit"), pl 1,900, it 1,000. en-GB "square meters to square feet" 22,200 is the one worthwhile area query.

## Strongest missing tools (simple, client-side)
Word counter + character counter (largest, everywhere), password generator, lorem ipsum, age / days-between-dates calculators, color picker/converter (en-GB 22,200; fr 22,200; it 18,100; de 9,900), JSON formatter and Base64 (developer audience), text compare (en-GB 8,100, es 2,400, de 1,300), crop image (es 9,900, fr 3,600, de 3,600). CSV to JSON and case converter have near-zero demand outside en-GB (720 and 6,600).

## Demand real but not recommended / needs more research
- PDF to Word: large volume (es 110,000; en-GB 110,000; fr 74,000; it 22,200; nl 18,100; pl 18,100, de 14,800) but accurate conversion is not feasible client-side. Do not build it as a quality product.
- Remove background: big volume (es 201,000; en-GB 165,000; it 90,500; de 60,500; pt 49,500) but needs an ML segmentation model; feasible only with a WASM/ONNX model, with download-size and quality risk. Treat as a separate experiment.
- Country-specific finance tools (gross/net salary, stamp duty, income tax, codice fiscale, IMU, IRPF, TFR, mortgage): enormous volume but require maintained legislative tables and legal accuracy. Run a scoped pilot in one market (candidate: it codice fiscale/scorporo IVA or de brutto-netto) before committing. KD 41-86 for salary terms indicates hard SERPs.
- Dutch, Polish, Portuguese, Nordic, Romanian, Czech, Greek: only lightly sampled; no SERP checks.

## Caveats on conventions
Decimal comma and thousands separators vary (de/fr/it/es/nl/pl use comma decimals; en-GB uses a point); implement locale-aware number formatting. A4 is the default paper size everywhere in this set (no US Letter). VAT rates change by country and over time and have reduced rates; use presets sourced from the official tax authority at build time and display "rate as of" text. Percentage and unit converters must not hard-code `.` as the decimal separator.

## Limitations
- **Only OpenSEO returned data.** Ahrefs returned "Insufficient plan". Semrush: report names were unknown and the single schema lookup I tried failed ("unknown report"); I did not retry. Ubersuggest and OpenRush were loaded but not used because OpenSEO supplied batch data.
- No first-party data (Search Console/Analytics) was queried, so nothing is `measured`; all volumes are `estimated-by-tool` and come from Google Ads-style grouping, so close variants share volume and different phrasing should not be summed.
- KD of 0 appears often and probably reflects missing SERP data rather than zero difficulty. KD for the head terms (qr code generator 76-86, json formatter 63-76, brutto netto kalkulator 86 in pl) is high.
- No monthly trends, seasonality, intent mix or SERP-feature data were retrieved (trends were disabled to save credits). The "informational" intent labels are the tool's.
- Competition notes are limited to the tool's KD and two qualitative WebSearch checks (de "pdf zusammenfügen online kostenlos": Smallpdf, WPS, karrierebibel, clickup; it "calcolo scorporo iva online": informazionefiscale, pmi.it, fiscomania, Qonto). No other SERPs were inspected; no domain strength was measured.
- Missing/failed queries: es "calcular edad" returned no volume; nl "csv naar json" no data; several queries returned no row at all (for example fr "csv en json", pl "wifi qr" variants not requested, some Portuguese, Swedish, Danish, Czech and Greek terms). Norwegian failed with language code "no" and was rerun as "nb". Finland "jpg pdf:ksi" is a poor phrasing, and Greek/Portuguese were checked with only a handful of queries.
- CPC values were not used as revenue indicators; they are advertiser-bid estimates and ToolsKit has no ad-revenue or conversion data. Business-potential notes in the CSV are intentionally generic.
- The matrix maps existing tool ids using folder names under `src/tools` (e.g. `cv`, `vat`, `loan`, `compound`, `hashtag`, `bio`, `yt-title`). The "Instagram caption" tool (`instagram` folder) and "yt-desc" were not queried (no validated phrasing). Secondary-market rows are unmapped samples with action "defer".
