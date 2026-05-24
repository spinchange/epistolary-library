# Project Gutenberg additions backlog

Created: 2026-05-24

Purpose: a durable multi-session research and execution backlog for expanding `epistolary-library` with additional Project Gutenberg works.

## Current library snapshot

As of this note, the library contains 21 books:
- 13 `epistolary`
- 8 `chaptered`

Coverage by century:
- 17th century: 2
- 18th century: 9
- 19th century: 8
- 20th century: 2

Current strengths:
- strong 18th-century British/European epistolary canon
- several parser-shape exemplars already covered (`LETTER I`, numeric `LETTER 1.`, direct `To ...`, mixed-case correspondent lines, Roman numerals, part/book/chapter fallback structures)
- a few frame/documentary `chaptered` works that are still relevant to the library’s broader interest in letter/journal/document forms

Current gaps worth exploring:
- more American epistolary fiction
- more 19th/early-20th century women-authored epistolary works
- diary/journal-shaped fiction that may fit `chaptered` today but point toward a future `diary` profile
- high-canon multi-volume epistolary works still absent from the public site
- French-language/source-language works that could justify a multilingual expansion track

## How to use this backlog

For each title below, work in this order:
1. verify the source URL still downloads usable plaintext or HTML
2. inspect actual heading grammar in the source text
3. classify honestly as one of:
   - compatible now as `epistolary`
   - compatible now as `chaptered`
   - compatible only after parser/normalization work
   - source available but not yet pipeline-ready
4. if implementation is attempted, use a temp build before touching the real content repo
5. only after verification, add `books/<id>/book.yaml` + `source.txt` and update `README.md`

## Priority 1 — strongest near-term candidates

### [ ] Aurelian; or, Rome in the Third Century — William Ware
- Gutenberg page: `https://www.gutenberg.org/ebooks/21953`
- Plaintext: `https://www.gutenberg.org/ebooks/21953.txt.utf-8`
- Why it belongs in the backlog:
  - Project Gutenberg explicitly exposes clean top-level `LETTER I.`, `LETTER II.` headings
  - first sampled section uses `FROM PISO TO FAUSTA.` directly under `LETTER I.`
  - thematically adjacent to the library’s core epistolary canon
- Current assessment:
  - likely **compatible now as `epistolary`**
  - likely parser shape: `LETTER I.` + uppercase correspondent line
- Sample evidence:
  - `LETTER I.`
  - `FROM PISO TO FAUSTA.`
- Next-session checklist:
  - [ ] temp-build under `epistolary`
  - [ ] inspect rendered TOC and one mid-book letter
  - [ ] add to `books/aurelian/` if clean

### [ ] Dangerous Connections, v. 1, 2, 3, 4 — Choderlos de Laclos
- Gutenberg page: `https://www.gutenberg.org/ebooks/45512`
- Plaintext: `https://www.gutenberg.org/ebooks/45512.txt.utf-8`
- Why it belongs in the backlog:
  - major missing epistolary title in the public-domain canon
  - Gutenberg plaintext shows real `LETTER I.`, `LETTER II.` sections with correspondent lines like `Cecilia Volanges _to_ Sophia Carnay...`
- Current assessment:
  - likely **compatible only after careful verification / possible normalization**, not a blind add
  - the source contains frontmatter/content-summary false positives before the real `LETTER I.`
  - may need the same kind of “skip summary before first real letter” care used in other Gutenberg epistolary imports
- Sample evidence:
  - frontmatter contains `LETTER CXXX.` before the real sequence
  - real text later begins:
    - `LETTER I.`
    - `Cecilia Volanges _to_ Sophia Carnay ...`
- Next-session checklist:
  - [ ] verify whether a temp build skips the early false-positive letter headings correctly
  - [ ] inspect whether inline italic correspondent lines parse cleanly
  - [ ] decide whether a narrow parser fix or a small normalization step is the better approach

### [ ] Love and Freindship [sic] — Jane Austen
- Gutenberg page: `https://www.gutenberg.org/ebooks/1212`
- Plaintext: `https://www.gutenberg.org/ebooks/1212.txt.utf-8`
- Why it belongs in the backlog:
  - adds another Austen epistolary text beyond `Lady Susan`
  - strong literary fit for the site’s curation
- Current assessment:
  - likely **compatible only after parser work**, not current drop-in support
  - Gutenberg plaintext uses inline ordinal patterns like:
    - `LETTER the FIRST From ISABEL to LAURA`
    - `LETTER 2nd LAURA to ISABEL`
    - `LETTER 8th LAURA to MARIANNE, in continuation`
  - also contains contents-page false positives before the real body
- Why it is interesting technically:
  - would extend current `LETTER ...` support from Roman numerals / digits / spelled ordinals into mixed ordinal forms like `2nd`, `3rd`, `4th`
- Next-session checklist:
  - [ ] identify first real letter start after contents/frontmatter
  - [ ] write a parser fixture covering `the FIRST` + `2nd` + `in continuation`
  - [ ] temp-build and inspect body/title splitting before adding

## Priority 2 — promising, but structurally trickier

### [ ] Daddy-Long-Legs — Jean Webster
- Gutenberg page: `https://www.gutenberg.org/ebooks/40426`
- Plaintext: `https://www.gutenberg.org/ebooks/40426.txt.utf-8`
- Why it belongs in the backlog:
  - well-known American epistolary novel
  - broadens the library’s early-20th-century coverage
  - women-authored, high-recognition, and explicitly tagged by Gutenberg as epistolary fiction
- Current assessment:
  - **source available**, but compatibility needs proof
  - the text opens with prose framing, then moves into dated entries and addressee lines such as:
    - `March 26th.`
    - `_Mr. D. L. L. Smith._`
    - `April 2d.`
    - `_Dear Daddy-Long-Legs_,`
  - this does not obviously match the current parser’s accepted Gutenberg letter grammars
- Likely status:
  - either a new epistolary heuristic or a fallback/normalization approach
- Next-session checklist:
  - [ ] find the true first recurring structural unit after the prose opening
  - [ ] decide whether these should be treated as letters, diary entries, or a mixed frame form
  - [ ] run a temp build under both `epistolary` and `chaptered` and keep the failure/success evidence

### [ ] Wieland; Or, The Transformation: An American Tale — Charles Brockden Brown
- Gutenberg page: `https://www.gutenberg.org/ebooks/792`
- Plaintext: `https://www.gutenberg.org/ebooks/792.txt.utf-8`
- Why it belongs in the backlog:
  - fits the library’s interest in framed/documentary narration even if not a pure letter-book
  - adds early American gothic adjacent to `Frankenstein` and `Dracula`
- Current assessment:
  - likely **compatible now as `chaptered`**
  - plaintext shows clean `Chapter I`, `Chapter II`, ... headings
  - opening prose is narratively addressed to a recipient, but top-level parser shape is chaptered
- Next-session checklist:
  - [ ] temp-build under `chaptered`
  - [ ] inspect whether the first body paragraph is preserved and not misread as a chapter title
  - [ ] decide whether it belongs on the public site under current curation rules

### [ ] Life-tangles : or, The journal of Rhoda Frith — Agnes Giberne
- Gutenberg page: `https://www.gutenberg.org/ebooks/78624`
- Plaintext: `https://www.gutenberg.org/ebooks/78624.txt.utf-8`
- Why it belongs in the backlog:
  - strong diary/journal adjacency
  - women-authored title that could broaden the library beyond the current core canon
- Current assessment:
  - likely **compatible now as `chaptered`**, but needs curation review
  - plaintext shows `CHAPTER I.`, `CHAPTER II.`, etc.
  - journal-style dated passages occur inside the chapter body (for example `_December 13th. Thursday Morning._`)
- Next-session checklist:
  - [ ] temp-build under `chaptered`
  - [ ] inspect whether chapter titles and embedded dated entries render naturally
  - [ ] decide whether this belongs in the public library now or should wait for a future `diary` profile

## Priority 3 — important research tracks, but likely not one-session additions

### [ ] The American Diary of a Japanese Girl — Yoné Noguchi
- Gutenberg page: `https://www.gutenberg.org/ebooks/63256`
- Plaintext: `https://www.gutenberg.org/ebooks/63256.txt.utf-8`
- Why it belongs in the backlog:
  - expands the library’s cultural range and diary-form representation
  - likely a useful stress test for any future diary-like ingest path
- Current assessment:
  - **source available**, but probably **not pipeline-ready without deeper evaluation**
  - sampled text uses date-led diary writing such as `TOKIO, Sept. 23rd` rather than current letter/chapter grammar
- Next-session checklist:
  - [ ] determine whether there are any stable top-level chapter/book divisions later in the text
  - [ ] if not, classify as a future `diary`-profile candidate rather than forcing it into the current engine

### [ ] Letters of Two Brides — Honoré de Balzac
- Gutenberg page: `https://www.gutenberg.org/ebooks/22981`
- Why it belongs in the backlog:
  - obvious thematic/canonical fit
  - likely excellent public-site content if the source is usable
- Current assessment:
  - **ebook page exists**, but plaintext acquisition is still unresolved from quick inspection
  - common `.txt` URL patterns did not surface a straightforward plain-text file in the quick pass
  - may require HTML acquisition/normalization rather than plain-text download
- Next-session checklist:
  - [ ] inspect the ebook page for HTML download options and stable source links
  - [ ] decide whether source acquisition should be HTML-first rather than txt-first
  - [ ] only then sample heading grammar

### [ ] Les liaisons dangereuses (French) — Choderlos de Laclos
- Gutenberg page: `https://www.gutenberg.org/ebooks/52006`
- Plaintext: `https://www.gutenberg.org/ebooks/52006.txt.utf-8`
- Why it belongs in the backlog:
  - major canonical epistolary work in source language
  - useful if the library grows into a multilingual/public-domain correspondence archive
- Current assessment:
  - **source available**, clearly letter-structured (`LETTRE PREMIÈRE`, `LETTRE II`, etc.)
  - but this is a **language-expansion** decision as much as a parser question
- Next-session checklist:
  - [ ] decide whether French-language works are in scope for the public library now
  - [ ] compare with the English `Dangerous Connections` import path before doing duplicate canon work

### [ ] Lettres persanes, tome I — Montesquieu
- Gutenberg page: `https://www.gutenberg.org/ebooks/30268`
- Plaintext: `https://www.gutenberg.org/ebooks/30268.txt.utf-8`
- Why it belongs in the backlog:
  - canonical letter-novel
  - structurally promising: `LETTRE I.`, `LETTRE II.`, ...
- Current assessment:
  - **source available**, but likely **multi-volume / multilingual planning work** rather than a quick import
- Next-session checklist:
  - [ ] determine whether Gutenberg distributes the whole work across multiple tomes
  - [ ] decide whether to ingest by volume or normalize into a single entry
  - [ ] confirm public-library language scope before implementation work

## Nice-to-have / optional follow-up searches

These are not yet sampled, but they are worth keeping in mind for later Gutenberg reconnaissance:
- [ ] more Jane Austen juvenilia / short epistolary pieces adjacent to `Love and Freindship [sic]`
- [ ] additional Balzac correspondence fiction beyond `Letters of Two Brides`
- [ ] more American document/letter frame novels adjacent to `Wieland`
- [ ] more journal/diary fiction by women authors that could be `chaptered` today and `diary` later

## Suggested execution order for future sessions

1. `Aurelian; or, Rome in the Third Century`
2. `Dangerous Connections, v. 1, 2, 3, 4`
3. `Love and Freindship [sic]`
4. `Daddy-Long-Legs`
5. `Wieland; Or, The Transformation`
6. `Life-tangles : or, The journal of Rhoda Frith`
7. `Letters of Two Brides`
8. `The American Diary of a Japanese Girl`
9. French-language expansion track (`Les liaisons dangereuses`, `Lettres persanes`)

## Completion checklist for the backlog itself

- [x] analyze the current library contents
- [x] identify gaps in chronology/form/region
- [x] collect Gutenberg candidate titles already visible in the catalog
- [x] record source URLs or ebook pages
- [x] sample representative heading shapes for the strongest candidates
- [ ] work through the candidate titles one by one in future sessions
