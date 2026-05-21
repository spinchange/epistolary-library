# Hyperion provenance

This book is normalized as a derivative of the Internet Archive DJVU plaintext OCR for *Hyperion, or the Hermit in Greece* by Friedrich Hölderlin, in Howard Gaskill's English translation.

## Source

- Archive.org plaintext: https://archive.org/download/859a1313-7b02-4c66-8010-dbe533c4412a/859a1313-7b02-4c66-8010-dbe533c4412a_djvu.txt
- Book landing page: https://archive.org/details/859a1313-7b02-4c66-8010-dbe533c4412a
- Publisher / edition context referenced in the file itself: Open Book Publishers, 2019

## Normalization policy

- Fetch the single Archive.org DJVU plaintext source.
- Trim table-of-contents/front-matter OCR noise by starting at the first real letter heading followed by prose.
- Stop before the OCR'd `Afterword` / `Atterword` back matter.
- Drop running headers, running book/volume labels, `Continued`, and stray page-number artifacts.
- Rebuild the letter sequence with canonical headings renumbered by encounter order rather than trusting OCR numerals.
- Preserve the cleaned novel text as a normalized derivative of the Internet Archive DJVU plaintext OCR, not as a verbatim dump of the raw OCR stream.

## Script

Regenerate `source.txt` with:

```bash
python scripts/normalize_hyperion.py
```
