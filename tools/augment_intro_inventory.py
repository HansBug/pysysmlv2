"""Validate the reviewed Intro-deck inventory without extracting slide text.

The Intro deck is a visual source.  Explanatory prose is maintained in the
hand-authored ``intro_manual_notes_*.json`` ledgers; it must not be generated
from a PDF text layer because that layer mixes code, titles, footers and
diagram labels.  This command only validates that the reviewed slide set and
its source PDF are present.

Example::

    $ python -m tools.augment_intro_inventory --pdf /path/to/Intro.pdf
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "research" / "intro_textual_notation_inventory.json"


def augment(pdf: Path, inventory: Optional[Path] = None) -> int:
    """Validate a reviewed inventory against an explicitly supplied PDF.

    :param pdf: Local copy of the official Intro textual-notation PDF.
    :type pdf: pathlib.Path
    :param inventory: Optional inventory path, defaults to the checked-in
        Intro ledger.
    :type inventory: pathlib.Path, optional
    :return: Number of reviewed slides.
    :rtype: int
    :raises FileNotFoundError: If ``pdf`` or the inventory is absent.
    :raises ValueError: If generated visible text is present in the inventory.
    """
    source = inventory or INVENTORY
    payload: Dict[str, Any] = json.loads(source.read_text(encoding="utf-8"))
    slides = payload.get("slides")
    if not isinstance(slides, list):
        raise ValueError("Intro inventory has no slides list")
    count = 0
    for slide in slides:
        if not isinstance(slide, dict):
            raise ValueError("Intro inventory contains a non-object slide")
        number = slide.get("slide")
        if not isinstance(number, int):
            raise ValueError("Intro inventory slide has no integer slide number")
        if "pdf_visible_text" in slide:
            raise ValueError(
                "inventory contains generated pdf_visible_text; keep prose in "
                "the hand-authored intro_manual_notes ledger"
            )
        count += 1
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    return count


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Augment the checked-in inventory from a local PDF copy."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--inventory", type=Path, default=INVENTORY)
    options = parser.parse_args(arguments)
    print("augmented {} Intro PDF slides".format(augment(options.pdf, options.inventory)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
