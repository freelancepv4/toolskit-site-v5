# Localization notes: Italian (it), wave 1

Status: first draft, not reviewed by a native editor or a legal professional. Scope: merge-pdf, split-pdf, rotate-pdf, compress-pdf, pdf-to-images, images-to-pdf, percentage, vat, loan, compound, word-counter (categories pdf, calc, text). Register: Lei-form / impersonal.

## Queries chosen (volumes are OpenSEO estimates, 2026-10-10, see opportunity-matrix.csv; nothing measured)
| Tool | Primary (title/H1/lead) | Evidence |
|---|---|---|
| merge-pdf | unire pdf | 165,000, KD 0 (KD 0 is probably missing SERP data) |
| compress-pdf | comprimere pdf (+ ridurre dimensione pdf in lead/syn) | 201,000 KD 27; ridurre dimensione pdf 18,100 |
| split-pdf | dividere pdf | 135,000 KD 0 |
| rotate-pdf | ruotare pdf | 2,400 KD 0 |
| images-to-pdf | jpg in pdf | 14,800 KD 0 |
| pdf-to-images | pdf in immagini (PNG). Validated query "pdf in jpg" (12,100 KD 15) is NOT a title/syn: the tool exports PNG only. It is an unsupported entry with a note pointing to the tool; the lead and FAQ say plainly that the output is PNG | tool limit |
| percentage | calcolo percentuale | 90,500 KD 0 |
| vat | calcolo iva (40,500) + scorporo iva (33,100) both in title/H1/lead/FAQ and syn | matrix; SERP note: editorial/fiscal sites, one Qonto tool |
| loan | calcolo prestito (3,600, KD 37) + "mutuo" in name/H1/syn | "calcolo mutuo" has no matrix row: included on the brief's request, volume unverified |
| compound | interesse composto | 12,100 KD 0 |
| word-counter | conta parole (18,100, KD 7) and conta caratteri (33,100, KD 0) | matrix rows (tool not in native-terms.json) |

## URLs
/it/strumenti-pdf/{unire-pdf,dividere-pdf,ruotare-pdf,comprimere-pdf,pdf-in-immagini,jpg-in-pdf}.html, /it/calcolatori/{calcolo-percentuale,calcolo-iva,calcolo-prestito-mutuo,interesse-composto}.html, /it/strumenti-testo/conta-parole-caratteri.html. Pages: chi-siamo, contatti, privacy, termini-di-utilizzo; tools folder "strumenti". Output file names are Italian ASCII (unito.pdf, -estratto.pdf, -ruotato.pdf, -compresso.pdf, pagina-N.png, immagini.pdf).

## Decisions and doubts for native review
- VAT: rate_default 22 is only a prefilled value; rate_help says reduced rates exist and the user must enter the applicable one. Option labels "Aggiungi IVA (netto → lordo)" / "Scorpora IVA (lordo → netto)" are long for 320 px: please check the select width. Generic phrases such as "netto lordo" are deliberately NOT in vat syn (they belong to the salary unsupported entry).
- Percentage results use "{p}% di {y} = {r}" and "{x} su {y} = {r}%" to avoid the il/l'/all' article problem before numbers like 8, 11, 80.
- Loan: rate label is "Tasso annuo nominale (%)"; FAQ states it is not the TAEG. Rate is described as constant instalments; no claim of "ammortamento alla francese" in the UI.
- Compound: "versamento per periodo", "montante finale". Contribution frequency equals compounding frequency (as in the English tool).
- Unsupported entries added because research shows demand and the tools do not exist: "calcolo codice fiscale" (1,220,000), salary/busta paga/netto-lordo (14,800), TFR/IMU/ritenuta d'acconto (12,100 / 33,100 / 1,300). Related is only cat:calc. WebP/HEIC to JPG/PNG (18,100 / 12,100 / 1,000) and remove background (90,500) are unsupported with empty related, since the image tools are not in the Italian scope yet. "lorem ipsum", password generator, age/date calculator and QR reader were added as unsupported too (matrix rows, no tool).
- Search words: "in" is a connector (pdf in jpg), not a stop word; articles/prepositions are stop words. "modificare", "convertitore" are fillers.
- Word counter FAQ explains that apostrophe words ("l'anno") count as one word, because counting is by whitespace.
- Number format in prose: percent written "10%" (no space), as is customary in Italian everyday usage; some style guides use a space.

## Needs legal review
privacy.html and terms.html are faithful translations of the English drafts with the LEGAL REVIEW comment kept (plus an Italian note). Points to check for IT: GDPR/Codice Privacy information duties (artt. 13-14), titolare del trattamento identity placeholders, cookie / local-storage guidance of the Garante, consumer-law limits of the liability clause (Codice del Consumo), whether a governing-law or ODR note is needed. None were added. Wording "note legali" (footer_legal) is a generic heading, please confirm.

## Shared-code observations
- build.py emits only the default-language 404 (`if code == DEFAULT: page_404()`), so src/content/it/404.html and the it 404_title/404_desc are not used in the output yet. The file is complete and ready if per-language 404s are added.
