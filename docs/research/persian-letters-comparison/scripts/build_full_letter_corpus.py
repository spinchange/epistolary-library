from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LETTERS_DIR = ROOT / "letters"
NOTES_DIR = ROOT / "notes"

ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
ROMAN_CHARS = set(ROMAN_VALUES)

FRENCH_HEADING_RE = re.compile(r"^LETTRE\s+([IVXLCDM]+)\.?$")
ENGLISH_PREFIX_RE = re.compile(r"^(Letter|LETTER)\s+(.*)$")
ENGLISH_TOKEN_PART_RE = re.compile(r"^[IVXLCDMivxlcdm1jJlL/?.>\-]+$")

SOURCE_CONFIG = {
    "french_tome_1": {
        "lang": "french",
        "label": "French Tome I",
        "kind": "Project Gutenberg",
        "relpath": Path("raw/french_tome_1_pg30268.txt"),
        "range": (1, 88),
    },
    "french_tome_2": {
        "lang": "french",
        "label": "French Tome II",
        "kind": "Project Gutenberg",
        "relpath": Path("raw/french_tome_2_pg33856.txt"),
        "range": (89, 161),
    },
    "english_volume_1": {
        "lang": "english",
        "label": "English Volume I",
        "kind": "Internet Archive OCR",
        "relpath": Path("raw/english_volume_1_archive_ocr.txt"),
        "range": (1, 75),
        "body_start_hint": 1981,
    },
    "english_volume_2": {
        "lang": "english",
        "label": "English Volume II",
        "kind": "Internet Archive OCR",
        "relpath": Path("raw/english_volume_2_archive_ocr.txt"),
        "range": (76, 161),
        "body_start_hint": 443,
    },
}


@dataclass
class HeadingCandidate:
    list_index: int
    line_no: int
    line_text: str
    token_raw: str
    token_normalized: str
    parsed_number: int | None
    has_title: bool
    title_text: str


@dataclass
class Section:
    number: int
    roman: str
    source_key: str
    source_path: Path
    line_start: int
    line_end: int
    heading: str
    title: str
    subtitle: str
    raw_text: str
    clean_text: str
    match_type: str = "exact"
    match_similarity: float = 1.0
    heading_line_raw: str = ""
    heading_token_raw: str = ""
    heading_token_normalized: str = ""


def roman_to_int(text: str) -> int:
    total = 0
    prev = 0
    for ch in reversed(text):
        value = ROMAN_VALUES[ch]
        if value < prev:
            total -= value
        else:
            total += value
            prev = value
    return total


def int_to_roman(number: int) -> str:
    table = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    pieces: list[str] = []
    remaining = number
    for value, symbol in table:
        while remaining >= value:
            remaining -= value
            pieces.append(symbol)
    return "".join(pieces)


def slug_for_letter(number: int, roman: str) -> str:
    return f"{number:03d}-letter-{roman.lower()}"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def yaml_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


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


def join_wrapped_lines(lines: list[str]) -> str:
    if not lines:
        return ""
    pieces: list[str] = [lines[0].strip()]
    for raw_line in lines[1:]:
        line = raw_line.strip()
        if not line:
            continue
        prev = pieces[-1]
        if prev.endswith("¬"):
            pieces[-1] = prev[:-1] + line
        elif prev.endswith("-"):
            pieces[-1] = prev[:-1] + line
        else:
            pieces[-1] = prev + " " + line
    return pieces[-1].replace("\xad", "")


def is_probable_title_text(text: str) -> bool:
    if not text:
        return False
    upper = text.upper()
    alpha_chars = [ch for ch in text if ch.isalpha()]
    upper_ratio = (
        sum(1 for ch in alpha_chars if ch.isupper()) / len(alpha_chars)
        if alpha_chars
        else 0.0
    )
    short_enough = len(text.split()) <= 16
    return short_enough and (" TO " in upper or " THE SAME" in upper or upper_ratio >= 0.55)


def short_subtitle_candidate(text: str) -> bool:
    if not text:
        return False
    return len(text) <= 80 and len(text.split()) <= 10


def extract_initial_heading_title_subtitle(lines: list[str], lang: str, fallback_heading: str) -> tuple[str, str, str]:
    paragraphs = split_paragraphs(lines)
    if not paragraphs:
        return fallback_heading, "", ""
    heading = join_wrapped_lines(paragraphs[0]) or fallback_heading
    title = ""
    subtitle = ""
    if len(paragraphs) >= 2:
        candidate = join_wrapped_lines(paragraphs[1])
        if lang == "french" or is_probable_title_text(candidate):
            title = candidate
    if len(paragraphs) >= 3:
        candidate = join_wrapped_lines(paragraphs[2])
        if short_subtitle_candidate(candidate):
            subtitle = candidate
    return heading, title, subtitle


def normalize_heading_token(token: str) -> str:
    pieces: list[str] = []
    for ch in token:
        if ch in {"1", "|", "!", "j", "l"}:
            pieces.append("I")
        elif ch.upper() in ROMAN_CHARS:
            pieces.append(ch.upper())
        elif ch in {" ", "/", "?", ".", ">", "-"}:
            continue
    return "".join(pieces)


def heading_token_variants(token_normalized: str) -> list[str]:
    variants: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        if value and value not in seen:
            seen.add(value)
            variants.append(value)

    add(token_normalized)
    if token_normalized.endswith("IL"):
        add(token_normalized[:-2] + "II")
    if token_normalized.endswith("IIL"):
        add(token_normalized[:-3] + "III")
    if token_normalized.endswith("L"):
        add(token_normalized[:-1] + "I")
    return variants


def best_heading_variant(candidate: HeadingCandidate, expected_number: int) -> tuple[str, int | None, float]:
    expected_roman = int_to_roman(expected_number)
    best_variant = candidate.token_normalized
    best_similarity = -1.0
    best_parsed: int | None = None
    for variant in heading_token_variants(candidate.token_normalized):
        similarity = SequenceMatcher(None, expected_roman, variant).ratio()
        parsed: int | None = None
        if variant and all(ch in ROMAN_CHARS for ch in variant):
            parsed = roman_to_int(variant)
        if similarity > best_similarity or (similarity == best_similarity and parsed == expected_number):
            best_variant = variant
            best_similarity = similarity
            best_parsed = parsed
    return best_variant, best_parsed, best_similarity


def extract_heading_token(remainder: str) -> str:
    parts: list[str] = []
    for part in remainder.strip().split():
        cleaned = part.strip()
        if not cleaned:
            continue
        if cleaned.isdigit():
            break
        if not ENGLISH_TOKEN_PART_RE.fullmatch(cleaned):
            break
        parts.append(cleaned)
    return " ".join(parts)


def candidate_title_context(lines: list[str], start_idx_zero_based: int) -> tuple[bool, str]:
    window = lines[start_idx_zero_based : min(len(lines), start_idx_zero_based + 14)]
    paragraphs = split_paragraphs(window)
    if len(paragraphs) >= 2:
        text = join_wrapped_lines(paragraphs[1])
        if is_probable_title_text(text):
            return True, text
    return False, ""


def collect_english_candidates(lines: list[str], body_start_hint: int) -> list[HeadingCandidate]:
    candidates: list[HeadingCandidate] = []
    for idx, line in enumerate(lines, start=1):
        if idx < body_start_hint:
            continue
        stripped = line.strip()
        match = ENGLISH_PREFIX_RE.match(stripped)
        if not match:
            continue
        token_raw = extract_heading_token(match.group(2))
        token_normalized = normalize_heading_token(token_raw)
        if not token_normalized:
            continue
        parsed_number = None
        if all(ch in ROMAN_CHARS for ch in token_normalized):
            try:
                parsed_number = roman_to_int(token_normalized)
            except KeyError:
                parsed_number = None
        has_title, title_text = candidate_title_context(lines, idx - 1)
        candidates.append(
            HeadingCandidate(
                list_index=len(candidates),
                line_no=idx,
                line_text=stripped,
                token_raw=token_raw,
                token_normalized=token_normalized,
                parsed_number=parsed_number,
                has_title=has_title,
                title_text=title_text,
            )
        )
    return candidates


def choose_english_heading(
    candidates: list[HeadingCandidate],
    cursor: int,
    expected_number: int,
    prev_expected_number: int,
) -> HeadingCandidate:
    expected_roman = int_to_roman(expected_number)
    best: tuple[float, HeadingCandidate] | None = None
    for offset, candidate in enumerate(candidates[cursor : min(len(candidates), cursor + 18)]):
        best_variant, parsed, similarity = best_heading_variant(candidate, expected_number)
        if parsed is not None and parsed <= prev_expected_number and similarity < 0.95:
            continue
        score = similarity
        if parsed == expected_number:
            score += 1.5
        if candidate.has_title:
            score += 0.35
        if candidate.line_text.startswith("Letter "):
            score += 0.1
        if best_variant != candidate.token_normalized:
            score += 0.05
        score -= offset * 0.03
        if score >= 0.62:
            if best is None or score > best[0]:
                best = (score, candidate)
    if best is None:
        raise RuntimeError(f"Could not find English heading for letter {expected_roman} from cursor {cursor}")
    return best[1]


def build_french_sections(source_key: str) -> dict[int, Section]:
    source = SOURCE_CONFIG[source_key]
    path = ROOT / source["relpath"]
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    starts: list[tuple[int, int, str]] = []
    for idx, line in enumerate(lines, start=1):
        match = FRENCH_HEADING_RE.match(line.strip())
        if not match:
            continue
        roman = match.group(1)
        starts.append((roman_to_int(roman), idx, roman))
    sections: dict[int, Section] = {}
    for position, (number, line_start, roman) in enumerate(starts):
        line_end = starts[position + 1][1] - 1 if position + 1 < len(starts) else len(lines)
        chunk_lines = lines[line_start - 1 : line_end]
        while chunk_lines and not chunk_lines[-1].strip():
            chunk_lines.pop()
        heading, title, subtitle = extract_initial_heading_title_subtitle(
            chunk_lines,
            lang="french",
            fallback_heading=f"LETTRE {roman}.",
        )
        clean_paragraphs = [join_wrapped_lines(paragraph) for paragraph in split_paragraphs(chunk_lines)]
        clean_text = "\n\n".join(text for text in clean_paragraphs if text).strip() + "\n"
        raw_text = "\n".join(chunk_lines).strip() + "\n"
        sections[number] = Section(
            number=number,
            roman=roman,
            source_key=source_key,
            source_path=path,
            line_start=line_start,
            line_end=line_end,
            heading=heading,
            title=title,
            subtitle=subtitle,
            raw_text=raw_text,
            clean_text=clean_text,
        )
    return sections


def is_english_artifact_paragraph(text: str, paragraph_index: int) -> bool:
    stripped = text.strip()
    upper = stripped.upper()
    if not stripped:
        return True
    if paragraph_index <= 1:
        return False
    if upper == "PERSIAN LETTERS.":
        return True
    if re.fullmatch(r"[0-9]+", stripped):
        return True
    if re.fullmatch(r"[IVXLCDMivxlcdm]+\.?", stripped) and len(stripped) <= 8:
        return True
    if re.fullmatch(r"[A-Z]", stripped):
        return True
    if re.fullmatch(r"[A-Z0-9]{1,4}", stripped):
        return True
    if upper.startswith("LETTER "):
        return True
    if stripped[0].isdigit():
        return True
    if paragraph_index > 1 and stripped.isupper() and 1 < len(stripped.split()) <= 6:
        return True
    if re.fullmatch(r"['’.,;:!?0-9IVXLCDM\- ]{1,14}", stripped):
        return True
    return False


def should_merge_with_previous(previous: str, current: str) -> bool:
    if not previous or not current:
        return False
    if previous.endswith((":", ";", "—")):
        return True
    if current[:1].islower() and previous[-1].isalnum():
        return True
    return False


def merge_continuation_paragraphs(paragraphs: list[str]) -> list[str]:
    merged: list[str] = []
    for paragraph in paragraphs:
        if merged and should_merge_with_previous(merged[-1], paragraph):
            merged[-1] = merged[-1].rstrip() + " " + paragraph.lstrip()
        else:
            merged.append(paragraph)
    return merged


def clean_english_chunk(chunk_lines: list[str], canonical_heading: str, title: str, subtitle: str) -> str:
    paragraphs = split_paragraphs(chunk_lines)
    output: list[str] = [canonical_heading]
    if title:
        output.append(title)
    if subtitle:
        output.append(subtitle)
    body_paragraphs: list[str] = []
    for index, paragraph in enumerate(paragraphs[1:], start=1):
        text = join_wrapped_lines(paragraph)
        if is_english_artifact_paragraph(text, index):
            continue
        if title and text == title:
            continue
        if subtitle and text == subtitle:
            continue
        body_paragraphs.append(text)
    output.extend(merge_continuation_paragraphs(body_paragraphs))
    return "\n\n".join(text for text in output if text).strip() + "\n"


def build_english_sections(source_key: str) -> dict[int, Section]:
    source = SOURCE_CONFIG[source_key]
    path = ROOT / source["relpath"]
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start_number, end_number = source["range"]
    body_start_hint = source["body_start_hint"]
    candidates = collect_english_candidates(lines, body_start_hint)

    accepted: list[HeadingCandidate] = []
    cursor = 0
    prev_expected = start_number - 1
    for expected_number in range(start_number, end_number + 1):
        chosen = choose_english_heading(candidates, cursor, expected_number, prev_expected)
        accepted.append(chosen)
        cursor = chosen.list_index + 1
        prev_expected = expected_number

    sections: dict[int, Section] = {}
    for position, expected_number in enumerate(range(start_number, end_number + 1)):
        chosen = accepted[position]
        next_line_start = accepted[position + 1].line_no if position + 1 < len(accepted) else len(lines) + 1
        line_start = chosen.line_no
        line_end = next_line_start - 1
        chunk_lines = lines[line_start - 1 : line_end]
        while chunk_lines and not chunk_lines[-1].strip():
            chunk_lines.pop()
        canonical_heading = f"Letter {int_to_roman(expected_number)}."
        heading, title, subtitle = extract_initial_heading_title_subtitle(
            chunk_lines,
            lang="english",
            fallback_heading=canonical_heading,
        )
        if not title and chosen.has_title:
            title = chosen.title_text
        clean_text = clean_english_chunk(chunk_lines, canonical_heading, title, subtitle)
        raw_text = "\n".join(chunk_lines).strip() + "\n"
        interpreted_token, parsed, similarity = best_heading_variant(chosen, expected_number)
        match_type = "exact" if parsed == expected_number else "fuzzy"
        sections[expected_number] = Section(
            number=expected_number,
            roman=int_to_roman(expected_number),
            source_key=source_key,
            source_path=path,
            line_start=line_start,
            line_end=line_end,
            heading=canonical_heading,
            title=title,
            subtitle=subtitle,
            raw_text=raw_text,
            clean_text=clean_text,
            match_type=match_type,
            match_similarity=similarity,
            heading_line_raw=chosen.line_text,
            heading_token_raw=chosen.token_raw,
            heading_token_normalized=interpreted_token,
        )
    return sections


def build_comparison_stub(number: int, roman: str, french: Section, english: Section) -> str:
    return f"""# Letter {roman} comparison scaffold

- Letter number: {number}
- French source: {SOURCE_CONFIG[french.source_key]['label']}
- English source: {SOURCE_CONFIG[english.source_key]['label']}

## Source handles
- French raw excerpt: `french.txt`
- French clean excerpt: `french.clean.txt`
- English raw excerpt: `english.txt`
- English clean excerpt: `english.clean.txt`
- Metadata: `metadata.yaml`

## Fresh translation draft

_TODO: translate the French letter into fresh contemporary English._

## Comparison against Davidson

_TODO: compare the fresh translation against the Davidson version in `english.clean.txt`._

## Initial observations
- French heading: `{french.heading}`
- French title line: `{french.title}`
- English canonical heading: `{english.heading}`
- English title line: `{english.title}`
- English heading match type: `{english.match_type}`
- English OCR heading source: `{english.heading_line_raw}`
- Alignment key: letter number `{number}` / Roman numeral `{roman}`
- Reminder: English clean text is mechanically normalized from OCR and should still be checked against the raw excerpt in difficult places.
"""


def write_letter_folder(number: int, french: Section, english: Section) -> dict[str, object]:
    roman = int_to_roman(number)
    slug = slug_for_letter(number, roman)
    letter_dir = LETTERS_DIR / slug
    letter_dir.mkdir(parents=True, exist_ok=True)

    french_raw_path = letter_dir / "french.txt"
    french_clean_path = letter_dir / "french.clean.txt"
    english_raw_path = letter_dir / "english.txt"
    english_clean_path = letter_dir / "english.clean.txt"
    metadata_path = letter_dir / "metadata.yaml"
    comparison_path = letter_dir / "comparison.md"

    write_text(french_raw_path, french.raw_text)
    write_text(french_clean_path, french.clean_text)
    write_text(english_raw_path, english.raw_text)
    write_text(english_clean_path, english.clean_text)

    metadata = f"""letter_number: {number}
roman: {roman}
slug: {slug}
status:
  french_extracted: true
  french_cleaned: true
  english_extracted: true
  english_cleaned: true
  fresh_translation_started: false
  comparison_notes_started: false
alignment:
  compare_by_letter_number: true
  caution: "French and English physical volume boundaries differ; use letter number as the primary key."
french:
  source_label: "{SOURCE_CONFIG[french.source_key]['label']}"
  source_kind: "{SOURCE_CONFIG[french.source_key]['kind']}"
  source_file: "{relative_to_root(french.source_path)}"
  line_start: {french.line_start}
  line_end: {french.line_end}
  heading: "{yaml_escape(french.heading)}"
  title: "{yaml_escape(french.title)}"
  subtitle: "{yaml_escape(french.subtitle)}"
english:
  source_label: "{SOURCE_CONFIG[english.source_key]['label']}"
  source_kind: "{SOURCE_CONFIG[english.source_key]['kind']}"
  source_file: "{relative_to_root(english.source_path)}"
  line_start: {english.line_start}
  line_end: {english.line_end}
  heading: "{yaml_escape(english.heading)}"
  title: "{yaml_escape(english.title)}"
  subtitle: "{yaml_escape(english.subtitle)}"
  heading_match_type: "{english.match_type}"
  heading_match_similarity: {english.match_similarity:.3f}
  heading_line_raw: "{yaml_escape(english.heading_line_raw)}"
  heading_token_raw: "{yaml_escape(english.heading_token_raw)}"
  heading_token_normalized: "{yaml_escape(english.heading_token_normalized)}"
outputs:
  french_raw_file: "{relative_to_root(french_raw_path)}"
  french_clean_file: "{relative_to_root(french_clean_path)}"
  english_raw_file: "{relative_to_root(english_raw_path)}"
  english_clean_file: "{relative_to_root(english_clean_path)}"
  comparison_file: "{relative_to_root(comparison_path)}"
"""
    write_text(metadata_path, metadata)
    write_text(comparison_path, build_comparison_stub(number, roman, french, english))

    return {
        "number": number,
        "roman": roman,
        "slug": slug,
        "directory": relative_to_root(letter_dir),
        "french_range": f"{french.line_start}-{french.line_end}",
        "english_range": f"{english.line_start}-{english.line_end}",
        "english_match_type": english.match_type,
        "english_similarity": english.match_similarity,
        "english_heading_raw": english.heading_line_raw,
    }


def build_manifest(rows: list[dict[str, object]]) -> None:
    exact_count = sum(1 for row in rows if row["english_match_type"] == "exact")
    fuzzy_rows = [row for row in rows if row["english_match_type"] == "fuzzy"]
    lines = [
        "generated_by: scripts/build_full_letter_corpus.py",
        "generated_scope:",
        "  description: \"Full per-letter Persian Letters corpus with raw French, clean French, raw English OCR, and clean English OCR derivatives.\"",
        "summary:",
        f"  total_letters: {len(rows)}",
        f"  french_letters: {len(rows)}",
        f"  english_letters: {len(rows)}",
        f"  english_heading_exact: {exact_count}",
        f"  english_heading_fuzzy: {len(fuzzy_rows)}",
        "  english_body_start_hints:",
        f"    volume_1: {SOURCE_CONFIG['english_volume_1']['body_start_hint']}",
        f"    volume_2: {SOURCE_CONFIG['english_volume_2']['body_start_hint']}",
        "fuzzy_letters:" if fuzzy_rows else "fuzzy_letters: []",
    ]
    for row in fuzzy_rows:
        lines.extend(
            [
                f"  - number: {row['number']}",
                f"    roman: \"{row['roman']}\"",
                f"    similarity: {row['english_similarity']:.3f}",
                f"    raw_heading: \"{yaml_escape(str(row['english_heading_raw']))}\"",
            ]
        )
    lines.append("letters:")
    for row in rows:
        lines.extend(
            [
                f"  - number: {row['number']}",
                f"    roman: \"{row['roman']}\"",
                f"    slug: \"{row['slug']}\"",
                f"    directory: \"{row['directory']}\"",
                f"    french_line_range: \"{row['french_range']}\"",
                f"    english_line_range: \"{row['english_range']}\"",
                f"    english_match_type: \"{row['english_match_type']}\"",
            ]
        )
    write_text(LETTERS_DIR / "manifest.yaml", "\n".join(lines) + "\n")


def build_notes(rows: list[dict[str, object]]) -> None:
    exact_count = sum(1 for row in rows if row["english_match_type"] == "exact")
    fuzzy_rows = [row for row in rows if row["english_match_type"] == "fuzzy"]
    note_lines = [
        "# Full letter corpus",
        "",
        "This note records the first complete per-letter scaffold for *Lettres persanes* / *Persian Letters* in this workspace.",
        "",
        "## Coverage",
        "",
        f"- Total letters scaffolded: {len(rows)}",
        "- French coverage: letters I-CLXI",
        "- English coverage: letters I-CLXI",
        "- Output root: `letters/`",
        "",
        "## Per-letter folder contents",
        "",
        "Each folder now contains:",
        "- `french.txt` — raw extracted French letter",
        "- `french.clean.txt` — dewrapped French paragraphs",
        "- `english.txt` — raw extracted Davidson OCR letter",
        "- `english.clean.txt` — mechanically cleaned English OCR letter",
        "- `metadata.yaml` — provenance + heading-match details",
        "- `comparison.md` — translation/comparison stub",
        "",
        "## English heading quality",
        "",
        f"- Exact English heading matches: {exact_count}",
        f"- Fuzzy English heading matches: {len(fuzzy_rows)}",
        "- Fuzzy matches mean the OCR heading needed sequence-based interpretation rather than a clean exact numeral read.",
        "",
        "## Cleanup policy",
        "",
        "The English clean files are still OCR-derived. The cleanup pass currently:",
        "- removes repeated running headers like `PERSIAN LETTERS.`",
        "- removes isolated page numbers and signature marks",
        "- removes repeated in-body `LETTER ...` page-header artifacts",
        "- removes obvious footnote paragraphs that begin with digits",
        "- dewraps line-broken paragraphs and rejoins hyphenated line wraps",
        "",
        "What it does **not** guarantee yet:",
        "- perfect elimination of every OCR artifact",
        "- perfect recovery of every damaged heading numeral",
        "- scholarly normalization of punctuation or capitalization",
        "",
        "## Sample fuzzy letters",
        "",
    ]
    for row in fuzzy_rows[:20]:
        note_lines.append(
            f"- Letter {row['roman']} — OCR heading source: `{row['english_heading_raw']}`"
        )
    write_text(NOTES_DIR / "full-letter-corpus.md", "\n".join(note_lines) + "\n")


def main() -> None:
    french_sections: dict[int, Section] = {}
    french_sections.update(build_french_sections("french_tome_1"))
    french_sections.update(build_french_sections("french_tome_2"))

    english_sections: dict[int, Section] = {}
    english_sections.update(build_english_sections("english_volume_1"))
    english_sections.update(build_english_sections("english_volume_2"))

    rows: list[dict[str, object]] = []
    for number in range(1, 162):
        if number not in french_sections:
            raise RuntimeError(f"Missing French section for letter {number}")
        if number not in english_sections:
            raise RuntimeError(f"Missing English section for letter {number}")
        rows.append(write_letter_folder(number, french_sections[number], english_sections[number]))

    build_manifest(rows)
    build_notes(rows)

    exact_count = sum(1 for row in rows if row["english_match_type"] == "exact")
    fuzzy_count = len(rows) - exact_count
    print(f"Generated {len(rows)} letter folders")
    print(f"English heading matches: {exact_count} exact / {fuzzy_count} fuzzy")


if __name__ == "__main__":
    main()
