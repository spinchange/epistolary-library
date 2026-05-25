# Future edition publication plan

## Decision

The `translator-note-draft.md` file is intended to become **front matter for a future published Persian Letters edition**, not a standalone research page on the current site.

## Current limitation

As of this note:

- `epistolary-library` publishes only generated book pages under `dist/books/<book-id>/...`
- `book-engine` builds the site from `library.yaml` plus `books/*/book.yaml`
- the current schema has no support for standalone front-matter pages such as:
  - translator's note
  - introduction
  - editorial note
  - afterword
- files under `docs/research/` are **not** copied into the published `dist/` site

## Implication

The translator's note now lives in the right repository and version history, but it will not appear on the public site until a future Persian Letters edition exists **and** the publication path for front matter is implemented.

## Intended eventual placement

When `Persian Letters` is added to the library as a published edition, the translator's note should appear as one of these:

### preferred
A dedicated opening page before Letter I, linked from the book's table of contents.

Possible label/title:
- `Translator's Note`

Possible section order:
1. `Translator's Note`
2. `Letter I`
3. `Letter II`
4. ...

### fallback if the engine remains section-only
Represent the note as a synthetic opening section in the eventual edition build, provided the renderer can distinguish front matter from ordinary letters/chapters.

## Files to preserve for that future edition

Primary prose draft:
- `notes/translator-note-draft.md`

Supporting editorial rationale:
- `notes/translator-note-outline.md`
- `notes/second-pass-cleanup-log.md`

## Recommended future implementation path

If/when the Persian Letters edition is promoted from research corpus to site content:

1. add a real `books/persian-letters/` entry
2. extend `book-engine` schema/model to support optional front matter pages for a book
3. render those pages in the book TOC before the main section sequence
4. ingest `translator-note-draft.md` as the initial published front-matter page
5. keep the research version in `docs/research/` as the editorial working copy unless the edition workflow gets its own source directory

## Minimal engine feature implied

A future engine implementation would likely need something like optional book-level front matter, for example conceptually:

```yaml
front_matter:
  - id: translators-note
    title: Translator's Note
    source_file: translator-note.md
```

This is **not** implemented yet; it is only the conceptual target.

## Status

- translator's note drafted: yes
- translator's note polished: yes
- note published on site: no
- note assigned to future Persian Letters edition path: yes
