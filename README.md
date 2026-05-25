# epistolary-library

Reference content repo for `book-engine`.

This repository stores:
- library metadata
- per-book metadata
- raw source texts
- demo/sample texts for parser verification

## Included books

- `lady-susan` — Jane Austen, `epistolary` profile
- `diary-of-a-nobody` — George and Weedon Grossmith, public-domain `chaptered` profile with authorial chapter synopses preserved
- `humphry-clinker` — Tobias Smollett, public-domain `epistolary` profile using direct Gutenberg `To ...` letter headers
- `clarissa` — Samuel Richardson, public-domain `epistolary` profile normalized from Project Gutenberg's nine-volume English edition
- `pamela` — Samuel Richardson, public-domain `epistolary` profile using Gutenberg `LETTER I` headings plus uppercase salutation lines
- `evelina` — Fanny Burney, public-domain `epistolary` profile using Gutenberg `LETTER I` headings plus mixed-case correspondent/location lines and inline continuation notes
- `eloisa` — Jean-Jacques Rousseau, public-domain `epistolary` profile using Gutenberg `Letter I. To Eloisa.`-style inline correspondent headings from the 1761 English translation
- `self-made-merchant` — George Horace Lorimer, public-domain `epistolary` profile using Roman-numeral letter headings plus datelines and italicized salutations
- `letters-of-a-portuguese-nun` — Guilleragues, public-domain `epistolary` profile using Gutenberg `LETTER I` headings plus a global `FROM ... TO ...` correspondent title block
- `letters-of-abelard-and-heloise` — Peter Abelard and Héloïse, public-domain `epistolary` profile using Gutenberg `LETTER I.` headings plus italic correspondent lines including mixed-case `_Abelard_ to _Heloise._`
- `hyperion` — Friedrich Hölderlin, `epistolary` profile using a plain-text Hyperion-specific parser for `Hyperion to Bellarmin [I]` headings
- `sorrows-of-young-werther` — J.W. von Goethe, public-domain `chaptered` profile using Gutenberg's two-book structure plus the editor's closing section
- `notes-from-the-underground` — Fyodor Dostoyevsky, public-domain `chaptered` profile using Gutenberg's two-part structure
- `adolphe` — Benjamin Constant, public-domain French `chaptered` profile with appendix sections preserved
- `frankenstein` — Mary Wollstonecraft Shelley, public-domain `chaptered` profile for *Frankenstein; or, the Modern Prometheus*, preserving Walton's opening letters alongside the numbered chapters
- `dracula` — Bram Stoker, public-domain `chaptered` profile for *Dracula*, preserving the chapter-level documentary headings across journals, diaries, letters, and newspaper clippings
- `hunger` — Knut Hamsun, public-domain `chaptered` profile for *Hunger*, preserving Gutenberg's four-part structure without inventing spurious book-level sections from wrapped prose
- `kempton-wace-letters` — Jack London and Anna Strunsky, public-domain `epistolary` profile for *The Kempton-Wace Letters*, using Roman-numeral letter sections followed by uppercase `FROM ... TO ...` correspondent headers
- `fanny-hill` — John Cleland, public-domain `epistolary` profile for *Memoirs of Fanny Hill*, using Gutenberg `LETTER THE FIRST` / `LETTER THE SECOND` headings plus `Madam,` salutation lines
- `emily-montague` — Frances Brooke, public-domain `epistolary` profile for *The History of Emily Montague*, using Gutenberg numeric `LETTER 1.` headings plus mixed correspondent, dateline, and lowercase `To ...` letter openings
- `aurelian` — William Ware, public-domain `epistolary` profile for *Aurelian; or, Rome in the Third Century*, using Gutenberg `LETTER I.` headings plus uppercase `FROM PISO TO FAUSTA.` correspondent lines
- `dangerous-connections` — Choderlos de Laclos, public-domain `epistolary` profile for *Dangerous Connections, v. 1, 2, 3, 4*, using Gutenberg `LETTER I.` headings plus split italic correspondent headers while skipping the prefatory quoted letter excerpt before the real sequence
- `love-and-freindship` — Jane Austen, public-domain `epistolary` profile for *Love and Freindship [sic]*, normalized from Gutenberg's anthology plaintext and parsed via mixed `LETTER the FIRST` / `LETTER 2nd` / `LETTER the 9th` headings
- `love-letters-between-a-nobleman-and-his-sister` — Aphra Behn, public-domain epistolary novel added under the `chaptered` profile to preserve Gutenberg's three-part framing and embedded correspondence in *Love-Letters Between a Nobleman and His Sister*
- `wieland` — Charles Brockden Brown, public-domain documentary/frame-gothic novel added under the `chaptered` profile because Gutenberg exposes it as a clean `Chapter I`–`Chapter XXVII` sequence
- `life-tangles` — Agnes Giberne, public-domain journal-shaped novel added under the `chaptered` profile because Gutenberg exposes it as a clean `CHAPTER I.`–`CHAPTER XXIII.` sequence with dated journal material embedded inside chapters

## Local build

If `book-engine` is installed:

```bash
book-engine build . --output dist
```

If you are developing both repos side by side without installing the package:

```bash
PYTHONPATH='C:/Users/executor/Documents/book-engine/src' python -m book_engine.cli build . --output dist
```

## Adding another book

1. Create a folder under `books/<book-id>/`
2. Add `book.yaml`
3. Add the raw text source file referenced by `source_file`
4. Set `profile` to one of:
   - `epistolary`
   - `chaptered`
5. Build the site and verify generated HTML in `dist/`

Example `book.yaml`:

```yaml
id: new-book
title: New Book
author: Public Domain Author
year: 1899
source_file: source.txt
source_format: gutenberg-txt
profile: chaptered
parser: gutenberg-chapters-v1
theme: classic-paper
description: Short description for the library index.
```

## GitHub Actions

This repo includes Pages automation at `.github/workflows/build-and-deploy.yml`.
It:
- checks out this repo
- checks out `spinchange/book-engine`
- installs the engine
- builds `dist/`
- uploads the static site to GitHub Pages

## Git identity hygiene

This repo includes a `.mailmap` so tools that honor mailmap normalize the old `cduffy@ranchcryogenics.com` identity to `spinchange@gmail.com`.

To pin the repo-local author identity for future commits:

```bash
git config user.name 'Chris Duffy'
git config user.email 'spinchange@gmail.com'
```
