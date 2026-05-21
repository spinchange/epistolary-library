from __future__ import annotations

import argparse
import re
import time
import urllib.request
from pathlib import Path

TITLE = "Hyperion, or the Hermit in Greece"
SOURCE_URL = (
    "https://archive.org/download/859a1313-7b02-4c66-8010-dbe533c4412a/"
    "859a1313-7b02-4c66-8010-dbe533c4412a_djvu.txt"
)
AFTERWORD_MARKERS = {"afterword", "atterword"}
CORRESPONDENT_RE = re.compile(
    r"^(?P<correspondent>(?:Hyperion|Diotima)\s+to\s+(?:Bellarmin|Diotima|Hyperion))"
    r"(?:\s*\[(?P<numeral>[A-Z]+)\]?\]?)?(?:\s+\d+)?$"
)
PAGE_HEADER_RE = re.compile(r"^\d+\s+Hyperion, or the Hermit in Greece\s*$")
RUNNING_HEADER_RE = re.compile(r"^Volume\s+(?:One|Two)(?::\s+Book\s+(?:One|Two))?(?:\s+\d+)?\s*$")
BOOK_HEADING_RE = re.compile(r"^Book\s+(?:One|Two)(?:\s+\d+)?\s*$")
BARE_PAGE_NUMBER_RE = re.compile(r"^\d+\s*$")



def fetch_url(url: str, *, timeout: int = 20, attempts: int = 2, pause_seconds: float = 2.0) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Hermes Hyperion normalizer)"}
    request = urllib.request.Request(url, headers=headers)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="replace")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(pause_seconds * attempt)
    assert last_error is not None
    raise last_error



def _normalize_newlines(text: str) -> str:
    return text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")



def _to_roman(number: int) -> str:
    numerals = [
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
    result: list[str] = []
    remaining = number
    for value, numeral in numerals:
        while remaining >= value:
            result.append(numeral)
            remaining -= value
    return "".join(result)



def _match_correspondent_heading(line: str) -> re.Match[str] | None:
    return CORRESPONDENT_RE.fullmatch(line.strip())



def _is_afterword_marker(line: str) -> bool:
    return line.strip().lower() in AFTERWORD_MARKERS



def _is_running_artifact(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return bool(
        PAGE_HEADER_RE.fullmatch(stripped)
        or RUNNING_HEADER_RE.fullmatch(stripped)
        or BOOK_HEADING_RE.fullmatch(stripped)
        or BARE_PAGE_NUMBER_RE.fullmatch(stripped)
        or stripped == "Continued"
    )



def _is_body_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if _match_correspondent_heading(stripped):
        return False
    if _is_running_artifact(stripped):
        return False
    letters = [ch for ch in stripped if ch.isalpha()]
    if len(letters) < 8:
        return False
    lowercase_letters = sum(1 for ch in letters if ch.islower())
    return lowercase_letters >= max(1, len(letters) // 4)



def _next_nonblank_index(lines: list[str], start: int) -> int | None:
    for index in range(start, len(lines)):
        if lines[index].strip():
            return index
    return None



def _is_real_letter_start(lines: list[str], index: int) -> bool:
    line = lines[index]
    if not _match_correspondent_heading(line):
        return False
    if "[" not in line:
        return False
    for lookahead in range(index + 1, min(len(lines), index + 13)):
        candidate = lines[lookahead].strip()
        if not candidate:
            continue
        if _match_correspondent_heading(candidate):
            return False
        if _is_running_artifact(candidate) or _is_afterword_marker(candidate):
            return False
        return _is_body_line(candidate)
    return False



def extract_hyperion_novel_text(text: str) -> str:
    lines = _normalize_newlines(text).split("\n")

    start_index = None
    for index in range(len(lines)):
        if _is_real_letter_start(lines, index):
            start_index = index
            break
    if start_index is None:
        raise ValueError("Could not locate the start of Hyperion's real letter sequence")

    end_index = len(lines)
    for index in range(start_index + 1, len(lines)):
        if _is_afterword_marker(lines[index]):
            end_index = index
            break

    body = "\n".join(lines[start_index:end_index]).strip()
    return re.sub(r"\n{3,}", "\n\n", body)



def _clean_body_lines(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    last_blank = False
    for line in lines:
        stripped = line.strip()
        if _is_running_artifact(stripped):
            continue
        if not stripped:
            if not last_blank and cleaned:
                cleaned.append("")
            last_blank = True
            continue
        cleaned.append(stripped)
        last_blank = False
    while cleaned and not cleaned[0]:
        cleaned.pop(0)
    while cleaned and not cleaned[-1]:
        cleaned.pop()
    return cleaned



def normalize_hyperion_source(text: str) -> str:
    novel_text = extract_hyperion_novel_text(text)
    lines = novel_text.split("\n")

    sections: list[tuple[str, list[str]]] = []
    current_correspondent: str | None = None
    current_body: list[str] = []
    counter = 0

    for line in lines:
        heading = _match_correspondent_heading(line)
        if heading:
            if current_correspondent is not None:
                sections.append((current_correspondent, _clean_body_lines(current_body)))
            current_correspondent = heading.group("correspondent")
            current_body = []
            counter += 1
            continue
        if current_correspondent is None:
            continue
        current_body.append(line)

    if current_correspondent is not None:
        sections.append((current_correspondent, _clean_body_lines(current_body)))

    if not sections:
        raise ValueError("Could not normalize any Hyperion letters from the OCR source")

    rendered: list[str] = []
    for order, (correspondent, body_lines) in enumerate(sections, start=1):
        rendered.append(f"{correspondent} [{_to_roman(order)}]")
        rendered.append("")
        rendered.extend(body_lines)
        rendered.append("")

    output = "\n".join(rendered).strip() + "\n"
    return re.sub(r"\n{3,}", "\n\n", output)



def write_provenance(path: Path) -> None:
    lines = [
        "# Hyperion provenance",
        "",
        "This book is normalized as a derivative of the Internet Archive DJVU plaintext OCR for *Hyperion, or the Hermit in Greece* by Friedrich Hölderlin, in Howard Gaskill's English translation.",
        "",
        "## Source",
        "",
        f"- Archive.org plaintext: {SOURCE_URL}",
        "- Book landing page: https://archive.org/details/859a1313-7b02-4c66-8010-dbe533c4412a",
        "- Publisher / edition context referenced in the file itself: Open Book Publishers, 2019",
        "",
        "## Normalization policy",
        "",
        "- Fetch the single Archive.org DJVU plaintext source.",
        "- Trim table-of-contents/front-matter OCR noise by starting at the first real letter heading followed by prose.",
        "- Stop before the OCR'd `Afterword` / `Atterword` back matter.",
        "- Drop running headers, running book/volume labels, `Continued`, and stray page-number artifacts.",
        "- Rebuild the letter sequence with canonical headings renumbered by encounter order rather than trusting OCR numerals.",
        "- Preserve the cleaned novel text as a normalized derivative of the Internet Archive DJVU plaintext OCR, not as a verbatim dump of the raw OCR stream.",
        "",
        "## Script",
        "",
        "Regenerate `source.txt` with:",
        "",
        "```bash",
        "python scripts/normalize_hyperion.py",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")



def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Hyperion's Archive.org OCR into a clean source.txt")
    parser.add_argument(
        "--input-url",
        default=SOURCE_URL,
        help="URL for the Archive.org OCR plaintext source",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("books/hyperion/source.txt"),
        help="Output path for the normalized source text",
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        default=Path("books/hyperion/provenance.md"),
        help="Where to write provenance metadata",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Per-request timeout in seconds",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=2,
        help="Attempts before giving up on the source fetch",
    )
    args = parser.parse_args()

    print(f"Fetching Hyperion OCR from {args.input_url}...", flush=True)
    raw_text = fetch_url(args.input_url, timeout=args.timeout, attempts=args.attempts)
    normalized = normalize_hyperion_source(raw_text)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(normalized, encoding="utf-8")
    args.provenance.parent.mkdir(parents=True, exist_ok=True)
    write_provenance(args.provenance)

    print(f"Wrote {args.output}")
    print(f"Wrote {args.provenance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
