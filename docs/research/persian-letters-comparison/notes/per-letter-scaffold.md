# Per-letter extraction scaffold

This scaffold turns the earlier source-level workspace into concrete letter-level working folders.

## Included sample letters

- Letter I (`letters/001-letter-i`)
  - French line range: 943-973
  - English line range: 1981-2020
- Letter II (`letters/002-letter-ii`)
  - French line range: 974-1018
  - English line range: 2021-2076
- Letter LXXVI (`letters/076-letter-lxxvi`)
  - French line range: 5635-5705
  - English line range: 443-539
- Letter LXXXIX (`letters/089-letter-lxxxix`)
  - French line range: 87-122
  - English line range: 1606-1760

## Folder contents

Each letter folder contains:
- `french.txt` — extracted French source text for that letter
- `english.txt` — extracted Davidson/Archive English text for the same letter number
- `metadata.yaml` — source file and line-range provenance
- `comparison.md` — placeholder for fresh translation + comparison notes

## Why this scaffold matters

- It validates extraction at the start of the work (`I`, `II`).
- It validates cross-volume alignment (`LXXVI`, `LXXXIX`).
- It preserves provenance so later cleanup and translation can cite the exact raw line ranges.
- It keeps the comparison keyed by letter number rather than by physical volume.
