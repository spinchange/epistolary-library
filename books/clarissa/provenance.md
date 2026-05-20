# Clarissa provenance

This book is normalized from the nine-volume English Project Gutenberg edition of *Clarissa Harlowe; or, the History of a Young Lady*.

## Volumes

- Volume 1 — ebook #9296 — https://www.gutenberg.org/ebooks/9296
- Volume 2 — ebook #9798 — https://www.gutenberg.org/ebooks/9798
- Volume 3 — ebook #9881 — https://www.gutenberg.org/ebooks/9881
- Volume 4 — ebook #10462 — https://www.gutenberg.org/ebooks/10462
- Volume 5 — ebook #10799 — https://www.gutenberg.org/ebooks/10799
- Volume 6 — ebook #11364 — https://www.gutenberg.org/ebooks/11364
- Volume 7 — ebook #11889 — https://www.gutenberg.org/ebooks/11889
- Volume 8 — ebook #12180 — https://www.gutenberg.org/ebooks/12180
- Volume 9 — ebook #12398 — https://www.gutenberg.org/ebooks/12398

## Normalization policy

- Fetch each volume in order, preferring plain text URLs and falling back to cached HTML when needed.
- Strip each volume's Gutenberg wrapper.
- Concatenate the normalized volume bodies into one synthetic `source.txt`.
- Preserve letter ordering while globally renumbering true top-level letter headings in the combined source.
- Exclude the separate Gutenberg item `Clarissa: preface, hints of prefaces, and postscript` unless explicitly added later.

## Script

Regenerate `source.txt` with:

```bash
python scripts/normalize_clarissa.py
```
