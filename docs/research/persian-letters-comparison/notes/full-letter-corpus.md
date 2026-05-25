# Full letter corpus

This note records the first complete per-letter scaffold for *Lettres persanes* / *Persian Letters* in this workspace.

## Coverage

- Total letters scaffolded: 161
- French coverage: letters I-CLXI
- English coverage: letters I-CLXI
- Output root: `letters/`
- Completed comparison drafts: 161 / 161

## Per-letter folder contents

Each folder now contains:
- `french.txt` — raw extracted French letter
- `french.clean.txt` — dewrapped French paragraphs
- `english.txt` — raw extracted Davidson OCR letter
- `english.clean.txt` — mechanically cleaned English OCR letter
- `metadata.yaml` — provenance + heading-match details
- `comparison.md` — completed first-pass translation/comparison draft

## English heading quality

- Exact English heading matches: 161
- Fuzzy English heading matches: 0
- Fuzzy matches mean the OCR heading needed sequence-based interpretation rather than a clean exact numeral read.

## Cleanup policy

The English clean files are still OCR-derived. The cleanup pass currently:
- removes repeated running headers like `PERSIAN LETTERS.`
- removes isolated page numbers and signature marks
- removes repeated in-body `LETTER ...` page-header artifacts
- removes obvious footnote paragraphs that begin with digits
- dewraps line-broken paragraphs and rejoins hyphenated line wraps

What it does **not** guarantee yet:
- perfect elimination of every OCR artifact
- perfect recovery of every damaged heading numeral
- scholarly normalization of punctuation or capitalization
- clean separation of every boundary case where one letter bleeds into the next witness excerpt

## Known second-pass cleanup targets

Examples already surfaced during the first-pass drafting:
- boundary spillover around letters `089/090`, `124/125`, and `130/131`
- title / sender-recipient mismatches in some English witnesses
- date discrepancies across French/English clean texts
- heavy footnote intrusion in letters such as `016`, `067`, `075`, `108`, `122`
- end-of-volume contamination near `161`

## Status

- The first-pass translation/comparison run is complete across all 161 letters.
- The next stage is editorial refinement, not initial drafting.
