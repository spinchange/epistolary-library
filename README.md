# epistolary-library

Reference content repo for `book-engine`.

This repository stores:
- library metadata
- per-book metadata
- raw source texts
- demo/sample texts for parser verification

## Included books

- `lady-susan` — Jane Austen, `epistolary` profile
- `chaptered-sample` — short demo novella, `chaptered` profile
- `tom-sawyer` — Mark Twain, public-domain `chaptered` profile

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
