from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.normalize_hyperion import (  # noqa: E402
    SOURCE_URL,
    extract_hyperion_novel_text,
    normalize_hyperion_source,
    write_provenance,
)


def test_extract_hyperion_novel_text_skips_toc_and_afterword() -> None:
    raw = """Hyperion, or the Hermit in Greece

Volume One

Book One

Hyperion to Bellarmin [I]
Hyperion to Bellarmin [IT]
Hyperion to Bellarmin [III]

Hyperion to Bellarmin [I]

The beloved soil of my fatherland gives me joy once more.

Hyperion to Bellarmin [II]

I have nothing I might truly call my own.

Atterword

Critical essay text.
"""

    novel = extract_hyperion_novel_text(raw)

    assert novel.startswith("Hyperion to Bellarmin [I]")
    assert "Hyperion to Bellarmin [IT]" not in novel
    assert "The beloved soil of my fatherland gives me joy once more." in novel
    assert "Atterword" not in novel
    assert "Critical essay text." not in novel



def test_normalize_hyperion_source_removes_running_artifacts_and_renumbers_letters() -> None:
    raw = """Hyperion, or the Hermit in Greece

Book One

Hyperion to Bellarmin [I]
Hyperion to Bellarmin [IT]

Hyperion to Bellarmin [I]

The beloved soil of my fatherland gives me joy once more.

8 Hyperion, or the Hermit in Greece

Volume One: Book One 9

Continued

Hyperion to Bellarmin [IT]

I have nothing I might truly call my own.

Book Two

Hyperion to Diotima [XL]

I write to you again, my Diotima.

Afterword

Not part of the novel.
"""

    normalized = normalize_hyperion_source(raw)

    assert normalized.startswith("Hyperion to Bellarmin [I]")
    assert "The beloved soil of my fatherland gives me joy once more." in normalized
    assert "Hyperion to Bellarmin [II]" in normalized
    assert "I have nothing I might truly call my own." in normalized
    assert "Hyperion to Diotima [III]" in normalized
    assert "I write to you again, my Diotima." in normalized
    assert "8 Hyperion, or the Hermit in Greece" not in normalized
    assert "Volume One: Book One 9" not in normalized
    assert "Continued" not in normalized
    assert "Afterword" not in normalized
    assert "Not part of the novel." not in normalized



def test_write_provenance_mentions_regeneration_command(tmp_path: Path) -> None:
    path = tmp_path / "provenance.md"

    write_provenance(path)

    content = path.read_text(encoding="utf-8")
    assert SOURCE_URL in content
    assert "python scripts/normalize_hyperion.py" in content
    assert "normalized derivative of the Internet Archive DJVU plaintext OCR" in content
