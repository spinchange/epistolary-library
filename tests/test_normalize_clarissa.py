from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.normalize_clarissa import (  # noqa: E402
    END_MARKER,
    START_MARKER,
    VOLUMES,
    VolumeSource,
    build_clarissa_source,
    extract_gutenberg_main_text,
    extract_main_text_from_html,
    renumber_letter_headings,
    trim_to_first_letter,
)


def test_extract_gutenberg_main_text_strips_wrapper() -> None:
    text = """The Project Gutenberg eBook of Something

*** START OF THE PROJECT GUTENBERG EBOOK SAMPLE ***

LETTER I

MISS A, TO MISS B.

Body.

*** END OF THE PROJECT GUTENBERG EBOOK SAMPLE ***
"""

    main = extract_gutenberg_main_text(text)

    assert main.startswith("LETTER I")
    assert main.endswith("Body.")
    assert "START OF THE PROJECT GUTENBERG" not in main


def test_extract_main_text_from_html_starts_at_history_heading_and_skips_summary_letters() -> None:
    html = """
    <html><body>
      <p>The Project Gutenberg eBook of Clarissa Harlowe, Vol. 1</p>
      <h1>CLARISSA HARLOWE</h1>
      <h2>LETTERS OF VOLUME I</h2>
      <p>LETTER I. Miss Howe to Miss Clarissa Harlowe.—Summary text.</p>
      <h2>THE HISTORY OF CLARISSA HARLOWE</h2>
      <h2>LETTER I</h2>
      <h3>MISS ANNA HOWE, TO MISS CLARISSA HARLOWE JAN 10.</h3>
      <p>I am extremely concerned, my dearest friend.</p>
      <p>End of the Project Gutenberg eBook of Clarissa Harlowe, Vol. 1</p>
    </body></html>
    """

    main = extract_main_text_from_html(html)

    assert main.startswith("THE HISTORY OF CLARISSA HARLOWE")
    assert "LETTER I. Miss Howe to Miss Clarissa Harlowe.—Summary text." not in main
    assert "LETTER I" in main
    assert main.endswith("I am extremely concerned, my dearest friend.")
    assert "End of the Project Gutenberg eBook" not in main


def test_build_clarissa_source_wraps_all_volume_texts() -> None:
    fetched = [
        (VolumeSource(1, 9296), "LETTER I\n\nMISS A, TO MISS B.\n\nBody one.", "https://example.com/1"),
        (VolumeSource(2, 9798), "LETTER II\n\nMISS B, TO MISS A.\n\nBody two.", "https://example.com/2"),
    ]

    combined = build_clarissa_source(fetched)

    assert combined.startswith(START_MARKER)
    assert combined.endswith(END_MARKER + "\n")
    assert "[Source volume 1: https://example.com/1]" in combined
    assert "[Source volume 2: https://example.com/2]" in combined
    assert "LETTER I" in combined and "LETTER II" in combined


def test_renumber_letter_headings_makes_standalone_letter_ids_unique() -> None:
    text = """LETTER I

MISS A, TO MISS B.

Body one.

LETTER I. Summary line.

LETTER I

TO ROBERT LOVELACE, ESQ.

Body two.

LETTER I

MISS CLARISSA HARLOWE [IN CONTINUATION.]

Body three.

LETTER I

MR. LOVELACE

[IN CONTINUATION.]

THURSDAY, JULY 20.

Body four.
"""

    renumbered = renumber_letter_headings(text)

    assert "LETTER I\n\nMISS A, TO MISS B." in renumbered
    assert "LETTER II\n\nTO ROBERT LOVELACE, ESQ." in renumbered
    assert "LETTER III\n\nMISS CLARISSA HARLOWE [IN CONTINUATION.]" in renumbered
    assert "LETTER IV\n\nMR. LOVELACE\n\n[IN CONTINUATION.]\n\nTHURSDAY, JULY 20." in renumbered
    assert "LETTER I. Summary line." in renumbered


def test_trim_to_first_letter_drops_preface_and_summary_material() -> None:
    text = """CLARISSA HARLOWE

LETTERS OF VOLUME I

LETTER I

MISS HOWE TO MISS CLARISSA HARLOWE.

Summary line.

THE HISTORY OF CLARISSA HARLOWE

LETTER I

MISS A, TO MISS B.

Body one.
"""

    trimmed = trim_to_first_letter(text)

    assert trimmed.startswith("LETTER I")
    assert "Summary line" not in trimmed
    assert "THE HISTORY OF CLARISSA HARLOWE" not in trimmed
    assert "MISS A, TO MISS B." in trimmed


def test_volume_source_declares_all_nine_volumes_in_order() -> None:
    assert [volume.volume for volume in VOLUMES] == list(range(1, 10))
    assert VOLUMES[0].ebook_id == 9296
    assert VOLUMES[-1].ebook_id == 12398
