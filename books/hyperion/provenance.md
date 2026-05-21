# Hyperion provenance

This scaffold uses the Internet Archive DJVU plaintext for *Hyperion, or the Hermit in Greece* by Friedrich Hölderlin, in Howard Gaskill's English translation.

## Source

- Archive.org plaintext: https://archive.org/download/859a1313-7b02-4c66-8010-dbe533c4412a/859a1313-7b02-4c66-8010-dbe533c4412a_djvu.txt
- Book landing page: https://archive.org/details/859a1313-7b02-4c66-8010-dbe533c4412a
- Publisher / edition context referenced in the file itself: Open Book Publishers, 2019

## Current scaffold policy

- Store the downloaded plaintext OCR as `source.txt`.
- Treat the source as `plain-txt` rather than `gutenberg-txt`; no Gutenberg wrapper stripping is assumed.
- Parse letters with `hyperion-letters-v1`, which targets headings shaped like `Hyperion to Bellarmin [I]`.
- Preserve the raw OCR text for now rather than attempting editorial cleanup during scaffold creation.

## Known caveats

- The plaintext includes substantial front matter, licensing text, and OCR noise.
- Roman-numeral heading OCR is not perfectly clean in the raw file (for example, one early heading appears as `[IT]`).
- This scaffold verifies that the work can build as a real book entry, but it is not yet a fully normalized scholarly edition.
