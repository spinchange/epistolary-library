# Future edition publication plan

## Decision

The `translator-note-draft.md` file is intended to become **front matter for a future published Persian Letters edition**, not a standalone research page on the current site.

## Current state

As of this note:

- `epistolary-library` still publishes only generated book pages under `dist/books/<book-id>/...`
- `book-engine` now supports optional book-level `front_matter` entries rendered before the main section sequence
- files under `docs/research/` are still **not** copied into the published `dist/` site on their own

## Implication

The translator's note can now be published cleanly **once a real Persian Letters book entry exists**. What still does not happen automatically is publication of research notes directly from `docs/research/`.

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
2. copy or derive a publishable `translator-note.md` into that book directory
3. declare it under `front_matter` in `book.yaml`
4. build and verify that `translators-note.html` appears before Letter I in the book TOC
5. keep the research version in `docs/research/` as the editorial working copy unless the edition workflow gets its own source directory

## Supported schema path

The engine now supports book-level front matter using this shape:

```yaml
front_matter:
  - id: translators-note
    title: Translator's Note
    source_file: translator-note.md
    source_format: markdown
```

## Status

- translator's note drafted: yes
- translator's note polished: yes
- note published on site: no
- note assigned to future Persian Letters edition path: yes
