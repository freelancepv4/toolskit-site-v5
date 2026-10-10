# Localization notes: French (fr), wave 1

Status: first draft, not reviewed by a native editor or a legal professional. Scope: merge-pdf, split-pdf, rotate-pdf, compress-pdf, pdf-to-images, images-to-pdf, percentage, vat, loan, compound, word-counter (categories pdf, calc, text). Vouvoiement, neutral standard French (FR/BE/CH).

## Queries chosen (volumes are OpenSEO estimates, 2026-10-10, see opportunity-matrix.csv; nothing measured)
| Tool | Primary (title/H1/lead) | Evidence |
|---|---|---|
| merge-pdf | fusionner pdf | 201,000, KD 16. syn: assembler, joindre, combiner, regrouper |
| compress-pdf | compresser pdf (+ réduire taille pdf in lead/syn) | 301,000 KD 15; réduire taille pdf 49,500 KD 20 |
| split-pdf | diviser pdf | 49,500 KD 1. séparer/découper/extraire in syn (séparer pdf 12,100 per research report) |
| rotate-pdf | rotation pdf | 2,900 KD 0. pivoter / tourner pdf in syn |
| images-to-pdf | jpg en pdf | 33,100 KD 10 |
| pdf-to-images | pdf en images (PNG). Validated query "pdf en jpg" (18,100, KD 18) is NOT used in title or syn | tool exports PNG only; "pdf en jpg" is an unsupported entry with a note, and the lead/FAQ say honestly that output is PNG |
| percentage | calcul pourcentage (title "Calcul de pourcentage") | 90,500 KD 18 |
| vat | calcul tva (H1 adds HT/TTC) | 74,000 KD 18; "convertir ttc en ht" 8,100; "calcul tva ht ttc" 2,900 (report) |
| loan | simulateur prêt | 22,200 KD 19 |
| compound | intérêts composés | 5,400 KD 2 |
| word-counter | compteur de mots et de caractères | compteur de mots 18,100 KD 22; compteur de caractères 12,100 KD 4 (matrix rows) |

## URLs
/fr/outils-pdf/{fusionner-pdf,diviser-pdf,rotation-pdf,compresser-pdf,pdf-en-images,jpg-en-pdf}.html, /fr/calculateurs/{calcul-pourcentage,calcul-tva,simulateur-pret,interets-composes}.html, /fr/outils-texte/compteur-de-mots.html. Pages: a-propos, contact, confidentialite, conditions-utilisation; tools folder "outils".

## Decisions and doubts for native review
- VAT: rate_default 20 is only a prefilled value; rate_help says reduced rates exist and the user must enter the applicable one; no other rate is named anywhere. Labels "HT → TTC" / "TTC → HT" (short, fit 320 px). Name "Calcul TVA" rather than "Calculateur de TVA" to match the query.
- Loan: label "Taux d'intérêt annuel" is the nominal rate typed by the user; FAQ states it is not the TAEG. "Simulateur de prêt" also covers crédit / prêt immobilier in lead and syn.
- Compound: "Total versé" explicitly includes the initial capital (the script adds it); contributions are per compounding period.
- Percentage: "Évolution en pourcentage", "De / À" labels, "Total (y)" for the whole; FAQ covers the four blocks and points de pourcentage.
- Unsupported "Calculateur de salaire, d'impôt ou de pourboire" captures "salaire brut net" (368,000) and routes to vat/percentage/cat:calc; vat syn deliberately has no "brut/net" phrases. Unsupported "pdf en jpg" has the PNG note.
- Search words: stop/conn/filler lists include "en", "vers", "à" as connectors ("jpg en pdf"); apostrophe forms (d'un, l'âge) are kept in syn as typed with the typographic apostrophe; check that the search normalizes ’ and ' (see shared-code note).
- Typography: non-breaking space before : ; ? ! % and inside « ». Date months lower case (French convention).
- Output file names are ASCII French (pdf-fusionne.pdf, -extrait.pdf, -pivote.pdf, -compresse.pdf, images.pdf, page-N.png).
- Image/QR/other-category unsupported entries have empty `related` (tools not in the fr scope yet). Revisit when they are localized.

## Needs legal review
privacy.html and terms.html are faithful translations of the English drafts with the LEGAL REVIEW comment kept (plus a French note). Points to check for FR/BE/CH: RGPD/CNIL wording and rights (no CNIL/DPO reference was added), traceurs / stockage local rules, mentions légales (éditeur, hébergeur, directeur de la publication) which are legally required in France and are only placeholders here via {{{operator}}}, consumer-law limits on the liability clause, médiateur de la consommation, and governing-law/jurisdiction. None were added.

## Shared-code observations
- None blocking. Build prints only the existing staging-domain LAUNCH BLOCKER notice.
- Not verified: whether search normalization folds the typographic apostrophe (’) to a plain one; syn entries use ’.
