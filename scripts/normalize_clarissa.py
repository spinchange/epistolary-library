from __future__ import annotations

import argparse
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

TITLE = "Clarissa Harlowe; or, the History of a Young Lady"
START_MARKER = f"*** START OF THE PROJECT GUTENBERG EBOOK {TITLE.upper()} ***"
END_MARKER = f"*** END OF THE PROJECT GUTENBERG EBOOK {TITLE.upper()} ***"


@dataclass(frozen=True)
class VolumeSource:
    volume: int
    ebook_id: int

    @property
    def page_url(self) -> str:
        return f"https://www.gutenberg.org/ebooks/{self.ebook_id}"

    @property
    def text_url(self) -> str:
        return f"https://www.gutenberg.org/ebooks/{self.ebook_id}.txt.utf-8"

    @property
    def cache_text_url(self) -> str:
        return f"https://www.gutenberg.org/cache/epub/{self.ebook_id}/pg{self.ebook_id}.txt"

    @property
    def html_url(self) -> str:
        return f"https://www.gutenberg.org/cache/epub/{self.ebook_id}/pg{self.ebook_id}-images.html"

    @property
    def all_urls(self) -> list[str]:
        return [self.text_url, self.cache_text_url, self.html_url, f"{self.page_url}.html.images"]


VOLUMES: list[VolumeSource] = [
    VolumeSource(1, 9296),
    VolumeSource(2, 9798),
    VolumeSource(3, 9881),
    VolumeSource(4, 10462),
    VolumeSource(5, 10799),
    VolumeSource(6, 11364),
    VolumeSource(7, 11889),
    VolumeSource(8, 12180),
    VolumeSource(9, 12398),
]


class _BlockHTMLToText(HTMLParser):
    BLOCK_TAGS = {
        "p",
        "div",
        "section",
        "article",
        "header",
        "footer",
        "li",
        "ul",
        "ol",
        "table",
        "tr",
        "td",
        "th",
        "blockquote",
        "pre",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "br":
            self._parts.append("\n")
        elif tag in self.BLOCK_TAGS:
            self._parts.append("\n\n")

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        tag = tag.lower()
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n\n")

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if self._skip_depth:
            return
        if data:
            self._parts.append(data)

    def text(self) -> str:
        text = unescape("".join(self._parts)).replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\ufeff", "")
        text = re.sub(r"\n[ \t]+", "\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def fetch_url(url: str, *, timeout: int = 20, attempts: int = 2, pause_seconds: float = 2.0) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Hermes Clarissa normalizer)"}
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


def extract_gutenberg_main_text(text: str) -> str:
    normalized = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    generic_start = re.search(r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*", normalized)
    generic_end = re.search(r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*", normalized)
    if not generic_start or not generic_end:
        raise ValueError("Could not locate Project Gutenberg start/end markers in plain text source")
    return normalized[generic_start.end() : generic_end.start()].strip()


def extract_main_text_from_html(html: str) -> str:
    parser = _BlockHTMLToText()
    parser.feed(html)
    text = parser.text()
    lines = [line.strip() for line in text.split("\n")]

    start_idx = None
    for idx, line in enumerate(lines):
        if line.upper() == "THE HISTORY OF CLARISSA HARLOWE":
            start_idx = idx
            break
    if start_idx is None:
        for idx, line in enumerate(lines):
            if line.upper() == "CLARISSA HARLOWE":
                start_idx = idx
                break
    if start_idx is None:
        raise ValueError("Could not locate Clarissa title or history heading in HTML source")

    end_idx = len(lines)
    footer_patterns = (
        "End of the Project Gutenberg eBook of",
        "End of Project Gutenberg's",
        "*** END OF THE PROJECT GUTENBERG EBOOK",
    )
    for idx in range(start_idx, len(lines)):
        line = lines[idx]
        if any(line.startswith(prefix) for prefix in footer_patterns):
            end_idx = idx
            break

    body_lines = lines[start_idx:end_idx]
    body = "\n".join(body_lines)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body


def fetch_volume_main_text(volume: VolumeSource, *, timeout: int, attempts: int) -> tuple[str, str]:
    errors: list[str] = []
    for url in volume.all_urls:
        try:
            raw = fetch_url(url, timeout=timeout, attempts=attempts)
            if url.endswith(".html") or url.endswith(".html.images"):
                return extract_main_text_from_html(raw), url
            return extract_gutenberg_main_text(raw), url
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{url} -> {exc}")
    joined = "\n".join(errors)
    raise RuntimeError(f"Failed to fetch volume {volume.volume} from any known URL:\n{joined}")


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


def _is_uppercaseish(line: str) -> bool:
    letters = [ch for ch in line if ch.isalpha()]
    if not letters:
        return False
    uppercase_letters = sum(1 for ch in letters if ch.isupper())
    return uppercase_letters / len(letters) >= 0.7



def _looks_like_date_line(line: str) -> bool:
    header = line.strip().upper()
    if not header:
        return False
    month_tokens = {
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "SEPT",
        "OCT",
        "NOV",
        "DEC",
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    }
    return any(token in header for token in month_tokens) and any(ch.isdigit() for ch in header)



def _looks_like_correspondent_header(line: str, next_line: str = "", third_line: str = "") -> bool:
    first_upper = line.strip().upper()
    if not first_upper:
        return False
    if (
        first_upper.startswith("TO ")
        or first_upper.startswith("FROM ")
        or ((_is_uppercaseish(line) and " TO " in first_upper))
        or ((_is_uppercaseish(line) and " FROM " in first_upper))
        or "[IN " in first_upper
        or "[ENCLOSED " in first_upper
    ):
        return True

    second_upper = next_line.strip().upper()
    if _is_uppercaseish(line) and (
        second_upper.startswith("[IN ") or second_upper.startswith("[ENCLOSED ")
    ):
        return True

    if _is_uppercaseish(line) and _looks_like_date_line(next_line):
        return True

    if _is_uppercaseish(line) and (
        second_upper.startswith("[IN ") or second_upper.startswith("[ENCLOSED ")
    ) and _looks_like_date_line(third_line):
        return True

    return False



def _find_first_real_letter_index(lines: list[str]) -> int | None:
    history_markers = [
        index for index, line in enumerate(lines) if line.strip().upper().startswith("THE HISTORY OF ")
    ]
    search_start = history_markers[-1] if history_markers else 0

    for index in range(search_start, len(lines)):
        stripped = lines[index].strip()
        if not re.fullmatch(r"LETTER\s+[IVXLCDM]+\.?", stripped):
            continue
        tail = [candidate.strip() for candidate in lines[index + 1 : index + 6] if candidate.strip()]
        first = tail[0] if len(tail) > 0 else ""
        second = tail[1] if len(tail) > 1 else ""
        third = tail[2] if len(tail) > 2 else ""
        if _looks_like_correspondent_header(first, second, third):
            return index
    return None



def renumber_letter_headings(text: str) -> str:
    lines = text.split("\n")
    counter = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not re.fullmatch(r"LETTER\s+[IVXLCDM]+\.?", stripped):
            continue
        tail = [candidate.strip() for candidate in lines[index + 1 : index + 6] if candidate.strip()]
        first = tail[0] if len(tail) > 0 else ""
        second = tail[1] if len(tail) > 1 else ""
        third = tail[2] if len(tail) > 2 else ""
        if not _looks_like_correspondent_header(first, second, third):
            continue
        counter += 1
        lines[index] = re.sub(r"LETTER\s+[IVXLCDM]+\.?", f"LETTER {_to_roman(counter)}", line)
    return "\n".join(lines)



def trim_to_first_letter(text: str) -> str:
    lines = text.split("\n")
    index = _find_first_real_letter_index(lines)
    if index is not None:
        return "\n".join(lines[index:]).strip()
    return text.strip()


def build_clarissa_source(volumes: list[tuple[VolumeSource, str, str]]) -> str:
    parts = [
        START_MARKER,
        "",
        TITLE.upper(),
        "",
        "by SAMUEL RICHARDSON",
        "",
        "Normalized from the nine-volume Project Gutenberg edition for epistolary-library.",
        "",
    ]
    for volume, main_text, fetched_url in volumes:
        parts.extend(
            [
                f"[Source volume {volume.volume}: {fetched_url}]",
                "",
                trim_to_first_letter(main_text.strip()),
                "",
            ]
        )
    combined_body = renumber_letter_headings("\n".join(parts))
    return "\n".join([combined_body, END_MARKER, ""])


def write_provenance(path: Path) -> None:
    lines = [
        "# Clarissa provenance",
        "",
        "This book is normalized from the nine-volume English Project Gutenberg edition of *Clarissa Harlowe; or, the History of a Young Lady*.",
        "",
        "## Volumes",
        "",
    ]
    for volume in VOLUMES:
        lines.append(f"- Volume {volume.volume} — ebook #{volume.ebook_id} — {volume.page_url}")
    lines.extend(
        [
            "",
            "## Normalization policy",
            "",
            "- Fetch each volume in order, preferring plain text URLs and falling back to cached HTML when needed.",
            "- Strip each volume's Gutenberg wrapper.",
            "- Concatenate the normalized volume bodies into one synthetic `source.txt`.",
            "- Preserve letter ordering while globally renumbering true top-level letter headings in the combined source.",
            "- Exclude the separate Gutenberg item `Clarissa: preface, hints of prefaces, and postscript` unless explicitly added later.",
            "",
            "## Script",
            "",
            "Regenerate `source.txt` with:",
            "",
            "```bash",
            "python scripts/normalize_clarissa.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Clarissa's nine Gutenberg volumes into one source.txt")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("books/clarissa/source.txt"),
        help="Output path for the normalized source text",
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        default=Path("books/clarissa/provenance.md"),
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
        help="Attempts per URL before trying the next fallback URL",
    )
    args = parser.parse_args()

    fetched: list[tuple[VolumeSource, str, str]] = []
    for volume in VOLUMES:
        print(f"Fetching volume {volume.volume} (ebook #{volume.ebook_id})...", flush=True)
        main_text, fetched_url = fetch_volume_main_text(volume, timeout=args.timeout, attempts=args.attempts)
        print(f"  OK: {fetched_url} ({len(main_text)} chars)", flush=True)
        fetched.append((volume, main_text, fetched_url))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_clarissa_source(fetched), encoding="utf-8")
    args.provenance.parent.mkdir(parents=True, exist_ok=True)
    write_provenance(args.provenance)
    print(f"Wrote {args.output}")
    print(f"Wrote {args.provenance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
