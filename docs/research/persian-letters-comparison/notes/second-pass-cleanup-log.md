# Second-pass cleanup log

Created: 2026-05-25

Purpose: record targeted editorial repairs made after the first-pass corpus completion, especially where `english.clean.txt` had boundary spillover, truncated openings, or end-of-volume contamination.

## Repairs completed in this pass

### Boundary repairs
- `089-letter-lxxxix`
  - restored the missing latter half of the English clean witness
  - removed dependence on spillover into Letter XC
- `090-letter-xc`
  - removed leading spillover from Letter LXXXIX
  - restored title line `USBEK TO IBBEN, AT SMYRNA.`
- `124-letter-cxxiv`
  - removed final-line spillover into Letter CXXV
- `125-letter-cxxv`
  - restored title line and opening sentence from the raw witness range
- `130-letter-cxxx`
  - removed overrun into the opening of Letter CXXXI
- `131-letter-cxxxi`
  - restored title and opening paragraphs so the letter no longer begins mid-sentence
- `161-letter-clxi`
  - trimmed English clean text so it no longer runs into `THE END.` / `INDEX`

### Metadata repairs
Updated metadata where needed so English line ranges and/or title lines matched the repaired clean witnesses for:
- `089-letter-lxxxix`
- `090-letter-xc`
- `124-letter-cxxiv`
- `125-letter-cxxv`
- `130-letter-cxxx`
- `131-letter-cxxxi`

### Comparison-note updates
Revised comparison notes to reflect second-pass repairs for:
- `089-letter-lxxxix`
- `090-letter-xc`
- `124-letter-cxxiv`
- `125-letter-cxxv`
- `130-letter-cxxx`
- `131-letter-cxxxi`
- `161-letter-clxi`

## Repairs completed in a follow-up refinement pass

### Footnote / OCR debris repairs
- `016-letter-xvi`
  - removed title-note carryover, intrusive Zufagar and imam footnote matter, and trailing note residue
  - restored a continuous readable clean witness for the body and date line
- `067-letter-lxvii`
  - removed running-header fragments, footnote numbers, and page debris from the embedded `History of Apheridon and Astarte`
  - repaired split words and rejoined a broken transition near the Armenian-master episode
- `075-letter-lxxv`
  - removed Browning quotation carryover, page markers, and end-of-volume library / printer matter
  - rejoined the broken `de- / bate` opening paragraph and cleared note markers from the colonial argument
- `108-letter-cviii`
  - removed the intrusive Louis XV footnote from the middle of the paragraph
  - normalized several obvious OCR slips (`Rut` → `But`, `abb£` → `abbé`) where recovery was secure
- `122-letter-cxxii`
  - removed repeated note markers, a modern editorial intrusion (`Montesquieu did not foresee the “Negro question.”`), and stray page-number debris
  - restored continuous prose in the demographic / colonial argument

## Remaining likely cleanup targets
These still look like good candidates for a later editorial pass:
- letters with date / name discrepancies requiring witness checking
- letters whose English clean witness is readable but still locally noisy rather than cleanly publishable
- any place where the Davidson witness needs confirmation against a better scan rather than OCR alone

## Editorial principle reaffirmed
The goal of second-pass cleanup is not to silently rewrite Davidson into a new translation. It is to:
- repair obvious boundary errors
- remove non-textual debris where the recovery is secure
- keep provenance visible
- leave genuinely uncertain wording flagged rather than overconfidently normalized
