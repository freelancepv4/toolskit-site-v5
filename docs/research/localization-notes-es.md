# Localization notes: Spanish (es), wave 1

Status: first draft, not reviewed by a native editor or a legal professional. Spain-first, tuteo, neutral where it costs nothing. Scope: merge-pdf, split-pdf, rotate-pdf, compress-pdf, pdf-to-images, images-to-pdf, percentage, vat, loan, compound, word-counter (categories pdf, calc, text).

## Queries chosen (volumes are OpenSEO estimates, 2026-10-10, see opportunity-matrix.csv; nothing measured)
| Tool | Primary (title/H1/lead) | Evidence |
|---|---|---|
| merge-pdf | unir pdf | 450,000, KD 20. syn: juntar, combinar, fusionar |
| compress-pdf | comprimir pdf (+ reducir tamaño pdf in H1/syn) | 165,000 KD 15; reducir tamaño pdf 40,500 KD 16 |
| split-pdf | dividir pdf | 90,500 KD 33 |
| rotate-pdf | rotar pdf | 4,400 KD 2 (syn: girar pdf) |
| images-to-pdf | jpg a pdf | 90,500 KD 28 |
| pdf-to-images | pdf a imágenes / pdf a png. Validated query "pdf a jpg" (40,500 KD 20) NOT used in title/syn | tool exports PNG only; "pdf a jpg" is an unsupported entry with a note, and the lead/FAQ say plainly there is no JPG |
| percentage | calculadora de porcentajes + calcular porcentaje | calcular porcentaje 40,500 KD 13 |
| vat | calculadora de IVA + calcular IVA, quitar IVA, base imponible | calculadora iva 49,500 KD 19; calcular iva 49,500 (separate query, report) |
| loan | calculadora de préstamos e hipotecas | calculadora de préstamos 1,900 KD 27 (small); calculadora de hipoteca 6,600 KD 38 is in the title/H1/syn because the tool also serves fixed-rate mortgage estimates |
| compound | interés compuesto | 12,100 KD 31 |
| word-counter | contador de palabras y caracteres | contador de palabras 90,500 KD 23; contador de caracteres 22,200 KD 26 |

## URLs
/es/herramientas-pdf/{unir-pdf,dividir-pdf,rotar-pdf,comprimir-pdf,pdf-a-imagenes,jpg-a-pdf}.html, /es/calculadoras/{calculadora-de-porcentajes,calculadora-iva,calculadora-de-prestamos,calculadora-interes-compuesto}.html, /es/herramientas-de-texto/contador-de-palabras.html. Pages: acerca-de, contacto, privacidad, condiciones-de-uso; tools folder "herramientas".

## Decisions and doubts for native review
- Register: tuteo, imperative forms (elige, añade, descarga). "PDF" treated as masculine ("este PDF").
- Dates: `months` holds "de enero de" … because the shared builder formats `{day} {month} {year}`; this yields "10 de octubre de 2026". If the builder ever uses months elsewhere (headings, lists) this will look odd.
- Percent sign: non-breaking space before % in prose and result strings ("15 % de 200"), as per RAE/Fundéu.
- VAT: rate_default 21 (peninsular general rate) is only a start value. rate_help and FAQ mention that reduced rates exist and that Canarias, Ceuta and Melilla have a different regime (no further rates named, no advice). Labels: "base imponible", "Sumar IVA (base → total)", "Quitar IVA (total → base)". Check width of the select on 320 px.
- Salary/IRPF/finiquito queries (calculadora irpf 49,500; sueldo bruto neto 14,800; indemnización despido 14,800) route to one unsupported entry with related vat, percentage, cat:calc. VAT syn avoids "bruto/neto" to keep that routing clean.
- Loan: label "Tipo de interés anual" is the nominal rate typed by the user; FAQ says it is not the TAE and that variable-rate (euríbor) mortgages are not covered.
- Compound: "capitalización" for the frequency select; contributions are per compounding period.
- Search words: accents are folded by search.js (NFD), so stop/conn/filler are listed without worrying about accents. "a" and "en" are connectors ("jpg a pdf", "pdf en jpg"). "calcular" is deliberately NOT a filler word.
- Unsupported entries: "pdf a word" (110,000) and "quitar fondo" (201,000) added honestly with no related tool (PDF cat for pdf a word). Image/dev/QR-scanner entries keep English parity with empty related because those tools are not in the Spanish scope yet; revisit when image/QR tools are localized.
- Output file names are Spanish ASCII (unido.pdf, -extraido.pdf, -rotado.pdf, -comprimido.pdf, imagenes.pdf, pagina-N.png).
- Not localized on purpose: nothing claims JPG output, nothing says "100% seguro", no statistics.

## Needs legal review
privacy.html and terms.html are faithful translations of the English drafts with the LEGAL REVIEW comment kept (plus a Spanish note). Points to check for Spain: RGPD / LOPDGDD wording and data-subject rights text (including right to complain to the AEPD, not added), LSSI-CE art. 22.2 on local storage/cookies, operator identification duty under LSSI-CE art. 10 (placeholders for operator and contact), consumer-law limits of the liability clause (TRLGDCU, unfair terms), and whether a Spanish governing-law clause is needed. None were added.

## Shared-code observations
- Build prints "LAUNCH BLOCKER: SITE_URL ... staging" (siteUrlConfirmed false): unrelated to es.
- The es 404 page is not emitted as dist/es/404.html (only the root 404.html is); presumably by design.
