from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
LETTERS_DIR = ROOT / "letters"

TARGETS = [
    {
        "number": 1,
        "roman": "I",
        "slug": "001-letter-i",
        "french_source": "french_tome_1",
        "english_source": "english_volume_1",
    },
    {
        "number": 2,
        "roman": "II",
        "slug": "002-letter-ii",
        "french_source": "french_tome_1",
        "english_source": "english_volume_1",
    },
    {
        "number": 76,
        "roman": "LXXVI",
        "slug": "076-letter-lxxvi",
        "french_source": "french_tome_1",
        "english_source": "english_volume_2",
    },
    {
        "number": 89,
        "roman": "LXXXIX",
        "slug": "089-letter-lxxxix",
        "french_source": "french_tome_2",
        "english_source": "english_volume_2",
    },
]

SOURCES = {
    "french_tome_1": {
        "lang": "french",
        "label": "French Tome I",
        "relpath": Path("raw/french_tome_1_pg30268.txt"),
        "heading_re": re.compile(r"^LETTRE\s+([IVXLCDM]+)\.$"),
        "kind": "Project Gutenberg",
    },
    "french_tome_2": {
        "lang": "french",
        "label": "French Tome II",
        "relpath": Path("raw/french_tome_2_pg33856.txt"),
        "heading_re": re.compile(r"^LETTRE\s+([IVXLCDM]+)\.$"),
        "kind": "Project Gutenberg",
    },
    "english_volume_1": {
        "lang": "english",
        "label": "English Volume I",
        "relpath": Path("raw/english_volume_1_archive_ocr.txt"),
        "heading_re": re.compile(r"^(?:Letter|LETTER)\s+([IVXLCDM]+)[\.?]\s*$"),
        "kind": "Internet Archive OCR",
    },
    "english_volume_2": {
        "lang": "english",
        "label": "English Volume II",
        "relpath": Path("raw/english_volume_2_archive_ocr.txt"),
        "heading_re": re.compile(r"^(?:Letter|LETTER)\s+([IVXLCDM]+)[\.?]\s*$"),
        "kind": "Internet Archive OCR",
    },
}

ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(s: str) -> int:
    total = 0
    prev = 0
    for ch in reversed(s):
        value = ROMAN_VALUES[ch]
        if value < prev:
            total -= value
        else:
            total += value
            prev = value
    return total


def relative_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def split_paragraphs(lines: list[str]) -> list[list[str]]:
    paragraphs: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.strip():
            current.append(line.rstrip())
        elif current:
            paragraphs.append(current)
            current = []
    if current:
        paragraphs.append(current)
    return paragraphs


def is_likely_english_title_block(paragraph: list[str]) -> bool:
    joined = " ".join(line.strip() for line in paragraph if line.strip())
    if not joined:
        return False
    upper_joined = joined.upper()
    alpha_chars = [ch for ch in joined if ch.isalpha()]
    upper_ratio = (
        sum(1 for ch in alpha_chars if ch.isupper()) / len(alpha_chars)
        if alpha_chars
        else 0.0
    )
    return (
        " TO " in upper_joined
        or " THE SAME" in upper_joined
        or upper_ratio >= 0.6
    )


def summarize_chunk(chunk_lines: list[str], lang: str) -> tuple[str, str, str]:
    paragraphs = split_paragraphs(chunk_lines)
    heading = " ".join(paragraphs[0]).strip() if paragraphs else ""
    title = ""
    subtitle = ""
    if len(paragraphs) >= 2:
        title = " ".join(line.strip() for line in paragraphs[1]).strip()
    if len(paragraphs) >= 3:
        candidate = " ".join(line.strip() for line in paragraphs[2]).strip()
        if len(candidate) <= 60 and len(candidate.split()) <= 8:
            subtitle = candidate
    if lang == "english" and len(paragraphs) >= 2 and not is_likely_english_title_block(paragraphs[1]):
        title = ""
        subtitle = ""
    return heading, title, subtitle


def is_valid_section_start(lines: list[str], start_idx: int, lang: str) -> bool:
    if lang != "english":
        return True
    window = lines[start_idx : min(len(lines), start_idx + 12)]
    paragraphs = split_paragraphs(window)
    if len(paragraphs) < 2:
        return False
    return is_likely_english_title_block(paragraphs[1])


def extract_sections(source_key: str) -> dict[str, object]:
    source = SOURCES[source_key]
    path = ROOT / source["relpath"]
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    starts: list[tuple[str, int]] = []
    for idx, line in enumerate(lines):
        m = source["heading_re"].match(line.strip())
        if m and is_valid_section_start(lines, idx, source["lang"]):
            starts.append((m.group(1), idx))
    sections: dict[str, dict[str, object]] = {}
    for i, (roman, start_idx) in enumerate(starts):
        end_idx = starts[i + 1][1] - 1 if i + 1 < len(starts) else len(lines) - 1
        chunk_lines = lines[start_idx : end_idx + 1]
        while chunk_lines and not chunk_lines[-1].strip():
            chunk_lines.pop()
        heading, title, subtitle = summarize_chunk(chunk_lines, source["lang"])
        sections[roman] = {
            "number": roman_to_int(roman),
            "roman": roman,
            "line_start": start_idx + 1,
            "line_end": end_idx + 1,
            "heading": heading,
            "title": title,
            "subtitle": subtitle,
            "text": "\n".join(chunk_lines).strip() + "\n",
        }
    return {"path": path, "lines": lines, "sections": sections}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def yaml_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build_outputs() -> list[dict[str, object]]:
    LETTERS_DIR.mkdir(parents=True, exist_ok=True)
    extracted = {key: extract_sections(key) for key in SOURCES}
    manifest_rows: list[dict[str, object]] = []

    for target in TARGETS:
        letter_dir = LETTERS_DIR / target["slug"]
        letter_dir.mkdir(parents=True, exist_ok=True)

        french = extracted[target["french_source"]]["sections"][target["roman"]]
        english = extracted[target["english_source"]]["sections"][target["roman"]]
        french_heading = yaml_escape(french["heading"])
        french_title = yaml_escape(french["title"])
        french_subtitle = yaml_escape(french["subtitle"])
        english_heading = yaml_escape(english["heading"])
        english_title = yaml_escape(english["title"])
        english_subtitle = yaml_escape(english["subtitle"])

        write_text(letter_dir / "french.txt", french["text"])
        write_text(letter_dir / "english.txt", english["text"])

        metadata = f"""letter_number: {target['number']}
roman: {target['roman']}
slug: {target['slug']}
status:
  french_extracted: true
  english_extracted: true
  fresh_translation_started: false
  comparison_notes_started: false
alignment:
  compare_by_letter_number: true
  caution: "French and English physical volume boundaries differ; use letter number as the primary key."
french:
  source_label: "{SOURCES[target['french_source']]['label']}"
  source_kind: "{SOURCES[target['french_source']]['kind']}"
  source_file: "{relative_to_root(extracted[target['french_source']]['path'])}"
  line_start: {french['line_start']}
  line_end: {french['line_end']}
  heading: "{french_heading}"
  title: "{french_title}"
  subtitle: "{french_subtitle}"
english:
  source_label: "{SOURCES[target['english_source']]['label']}"
  source_kind: "{SOURCES[target['english_source']]['kind']}"
  source_file: "{relative_to_root(extracted[target['english_source']]['path'])}"
  line_start: {english['line_start']}
  line_end: {english['line_end']}
  heading: "{english_heading}"
  title: "{english_title}"
  subtitle: "{english_subtitle}"
outputs:
  french_excerpt_file: "{relative_to_root(letter_dir / 'french.txt')}"
  english_excerpt_file: "{relative_to_root(letter_dir / 'english.txt')}"
  comparison_file: "{relative_to_root(letter_dir / 'comparison.md')}"
"""
        write_text(letter_dir / "metadata.yaml", metadata)

        comparison = f"""# Letter {target['roman']} comparison scaffold

- Letter number: {target['number']}
- French source: {SOURCES[target['french_source']]['label']}
- English source: {SOURCES[target['english_source']]['label']}

## Source handles
- French excerpt: `french.txt`
- English excerpt: `english.txt`
- Metadata: `metadata.yaml`

## Fresh translation draft

_TODO: translate the French letter into fresh contemporary English._

## Comparison against Davidson

_TODO: compare the fresh translation against the Davidson version in `english.txt`._

## Initial observations
- French heading: `{french['heading']}`
- French title line: `{french['title']}`
- English heading: `{english['heading']}`
- English title line: `{english['title']}`
- Alignment key: letter number `{target['number']}` / Roman numeral `{target['roman']}`
- Reminder: the English OCR still contains page-break artifacts and occasional line-break noise.
"""
        write_text(letter_dir / "comparison.md", comparison)

        manifest_rows.append(
            {
                "number": target["number"],
                "roman": target["roman"],
                "slug": target["slug"],
                "dir": relative_to_root(letter_dir),
                "french_lines": (french["line_start"], french["line_end"]),
                "english_lines": (english["line_start"], english["line_end"]),
            }
        )

    manifest_lines = [
        "generated_by: scripts/extract_sample_letters.py",
        "generated_scope:",
        "  description: \"Initial per-letter extraction scaffold for Persian Letters translation/comparison.\"",
        "  letters:",
    ]
    for row in manifest_rows:
        manifest_lines.extend(
            [
                f"    - number: {row['number']}",
                f"      roman: \"{row['roman']}\"",
                f"      slug: \"{row['slug']}\"",
                f"      directory: \"{row['dir']}\"",
                f"      french_line_range: \"{row['french_lines'][0]}-{row['french_lines'][1]}\"",
                f"      english_line_range: \"{row['english_lines'][0]}-{row['english_lines'][1]}\"",
            ]
        )
    write_text(LETTERS_DIR / "manifest.yaml", "\n".join(manifest_lines) + "\n")

    note = [
        "# Per-letter extraction scaffold",
        "",
        "This scaffold turns the earlier source-level workspace into concrete letter-level working folders.",
        "",
        "## Included sample letters",
        "",
    ]
    for row in manifest_rows:
        note.extend(
            [
                f"- Letter {row['roman']} (`{row['dir']}`)",
                f"  - French line range: {row['french_lines'][0]}-{row['french_lines'][1]}",
                f"  - English line range: {row['english_lines'][0]}-{row['english_lines'][1]}",
            ]
        )
    note.extend(
        [
            "",
            "## Folder contents",
            "",
            "Each letter folder contains:",
            "- `french.txt` — extracted French source text for that letter",
            "- `english.txt` — extracted Davidson/Archive English text for the same letter number",
            "- `metadata.yaml` — source file and line-range provenance",
            "- `comparison.md` — placeholder for fresh translation + comparison notes",
            "",
            "## Why this scaffold matters",
            "",
            "- It validates extraction at the start of the work (`I`, `II`).",
            "- It validates cross-volume alignment (`LXXVI`, `LXXXIX`).",
            "- It preserves provenance so later cleanup and translation can cite the exact raw line ranges.",
            "- It keeps the comparison keyed by letter number rather than by physical volume.",
        ]
    )
    write_text(ROOT / "notes/per-letter-scaffold.md", "\n".join(note) + "\n")

    return manifest_rows


if __name__ == "__main__":
    rows = build_outputs()
    for row in rows:
        print(f"Letter {row['roman']}: {row['dir']}")
