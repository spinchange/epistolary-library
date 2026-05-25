# Persian Letters translation + comparison workspace

Created: 2026-05-25

Purpose: prepare a working set for translating Montesquieu's *Lettres persanes* and comparing a fresh English translation against the 1892 John Davidson translation on the Internet Archive.

## Local source files

### French original
- `raw/french_tome_1_pg30268.txt`
- `raw/french_tome_2_pg33856.txt`

### English comparison source
- `raw/english_volume_1_archive_ocr.txt`
- `raw/english_volume_2_archive_ocr.txt`

These English files are Archive OCR / djvu text exports, not yet hand-cleaned.

## Confirmed source URLs

### Project Gutenberg — French
- Tome I: `https://www.gutenberg.org/ebooks/30268`
- Plain text used locally: `https://www.gutenberg.org/cache/epub/30268/pg30268.txt`
- Tome II: `https://www.gutenberg.org/ebooks/33856`
- Plain text used locally: `https://www.gutenberg.org/ebooks/33856.txt.utf-8`

### Internet Archive — English translation by John Davidson
- Volume I item: `https://archive.org/details/32882019070534-persianletters`
- Volume I OCR text used locally: `https://archive.org/download/32882019070534-persianletters/HighRes_32882019070534_djvu.txt`
- Volume II item: `https://archive.org/details/32882019070518-persianletters`
- Volume II OCR text used locally: `https://archive.org/download/32882019070518-persianletters/HighRes_32882019070518_djvu.txt`

### Better fallback inputs if OCR cleanup becomes painful
For both Archive volumes, the detail pages also expose:
- PDF
- ABBYY GZ
- djvu XML

Those may be better than raw OCR text for a more reliable downstream cleanup pass.

## Important structural finding

The French Gutenberg volume split does **not** match the English Archive volume split.

### French Gutenberg letter ranges
- Tome I: letters `I` through `LXXXVIII` (1–88)
- Tome II: letters `LXXXIX` through `CLXI` (89–161)

### English Archive translation letter ranges
- Volume I appears to cover letters `I` through `LXXV` (1–75)
- Volume II begins at `LXXVI` (76) and continues through the end

This means comparison must be done **by letter number**, not by volume boundary.

## Immediate workflow recommendation

1. Clean each source enough to isolate real body text from title pages, contents, and OCR junk.
2. Split both French and English into per-letter units keyed by letter number.
3. Translate from the French original letter-by-letter.
4. Compare each fresh translation against the Davidson translation for the same letter number.
5. Keep notes on:
   - omitted phrases
   - archaic choices in Davidson
   - mistranscriptions from Archive OCR
   - places where the French edition and English edition seem to differ editorially

## Per-letter scaffold status

A full per-letter corpus now exists under `letters/` for **all 161 letters**.

Key files:
- `letters/manifest.yaml` — full manifest with counts and line ranges
- `notes/full-letter-corpus.md` — corpus summary and cleanup policy
- `notes/per-letter-scaffold.md` — earlier 4-letter pilot note
- `scripts/build_full_letter_corpus.py` — reproducible full-corpus builder
- `scripts/extract_sample_letters.py` — earlier 4-letter pilot extractor

Each per-letter folder now contains:
- `french.txt` — raw French excerpt
- `french.clean.txt` — dewrapped French paragraphs
- `english.txt` — raw English OCR excerpt
- `english.clean.txt` — mechanically cleaned English OCR excerpt
- `metadata.yaml` — provenance plus English heading-match diagnostics
- `comparison.md` — placeholder for translation/comparison work

Current corpus summary:
- total letters scaffolded: `161`
- English heading matches: `161 exact`, `0 fuzzy`

Current limitation:
- the English clean files are meaningfully better than the raw OCR, but they are still OCR-derived comparison text rather than a fully corrected edition
- some paragraph joins and residual OCR blemishes still need human review during translation/comparison

## Concrete next pass

The next useful implementation step is:
- begin actual translation/comparison drafts from the cleaned per-letter folders
- prioritize a pilot batch such as `I`, `II`, `XXVII`, `LXXVI`, `XCVII`, and `CII`
- correct any residual OCR trouble spots in-place as they are encountered during real comparison work
