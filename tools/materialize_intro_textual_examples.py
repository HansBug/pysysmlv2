"""Materialize the visually reviewed Intro-deck source panels.

The SysML snippets in ``intro_textual_notation_inventory.json`` and the
explanations in ``intro_manual_notes_*.json`` are checked-in, hand-reviewed
assets.  This utility does not read a PDF, infer prose, or invent comments. It
only places each exact ledger sentence immediately before its explicitly
named SysML element and applies conservative four-space indentation.

Example::

    $ python -m tools.materialize_intro_textual_examples
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "research" / "intro_textual_notation_inventory.json"
NOTE_FILES = (
    ROOT / "docs" / "research" / "intro_manual_notes_5_46.json",
    ROOT / "docs" / "research" / "intro_manual_notes_47_185.json",
    ROOT / "docs" / "research" / "intro_manual_notes_121_185.json",
)
DESTINATION = ROOT / "test" / "testfile" / "omg_intro_textual_notation"


def _brace_delta(source: str) -> int:
    """Count structural braces while ignoring quoted and commented source text."""
    delta = 0
    quote = ""
    escaped = False
    index = 0
    while index < len(source):
        character = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            index += 1
            continue
        if character == "/" and following == "/":
            break
        if character == "/" and following == "*":
            ending = source.find("*/", index + 2)
            if ending < 0:
                break
            index = ending + 2
            continue
        if character in ("'", '"'):
            quote = character
        elif character == "{":
            delta += 1
        elif character == "}":
            delta -= 1
        index += 1
    return delta


def _pretty_panel(code: str) -> str:
    """Apply stable structural indentation to a reviewed SysML code panel.

    :param code: Visually reviewed SysML panel text.
    :type code: str
    :return: Source text with stable whitespace and a final newline.
    :rtype: str
    """
    result: List[str] = []
    depth = 0
    in_block_comment = False
    for line in code.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        expanded = line.expandtabs(4).rstrip()
        stripped = expanded.strip()
        if not stripped:
            result.append("")
            continue
        leading_closures = 0
        for character in stripped:
            if character == "}":
                leading_closures += 1
            else:
                break
        line_depth = max(depth - leading_closures, 0)
        was_in_block_comment = in_block_comment
        opens_block_comment = "/*" in stripped and not stripped.startswith("//")
        closes_block_comment = "*/" in stripped
        if was_in_block_comment or stripped.startswith("*"):
            # A textual-representation/comment body may contain braces from a
            # different language. They do not participate in SysML nesting.
            line_depth = depth
        elif stripped.startswith(("from ", "to ", "and ", "or ")):
            line_depth += 1
        result.append(" " * (line_depth * 4) + stripped)
        if opens_block_comment and not closes_block_comment:
            in_block_comment = True
        if was_in_block_comment and closes_block_comment:
            in_block_comment = False
        if not was_in_block_comment and not opens_block_comment:
            depth = max(0, depth + _brace_delta(stripped))
    return "\n".join(result).strip() + "\n"


def _load_notes() -> Dict[str, List[Dict[str, Any]]]:
    """Load and validate the static, manually authored explanation ledgers."""
    notes: Dict[str, List[Dict[str, Any]]] = {}
    for path in NOTE_FILES:
        payload: Mapping[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        for slide, entries in payload.items():
            if not isinstance(entries, list):
                raise ValueError("note ledger slide {} is not a list".format(slide))
            if slide in notes:
                raise ValueError("duplicate note ledger slide {}".format(slide))
            normalized: List[Dict[str, Any]] = []
            for entry in entries:
                if not isinstance(entry, dict):
                    raise ValueError("note ledger slide {} has a non-object note".format(slide))
                anchor, text, occurrence = (
                    entry.get("anchor"),
                    entry.get("text"),
                    entry.get("occurrence", 1),
                )
                if (
                    not isinstance(anchor, str)
                    or not anchor
                    or not isinstance(text, str)
                    or not text
                    or not isinstance(occurrence, int)
                    or occurrence < 1
                ):
                    raise ValueError("note ledger slide {} has an invalid note".format(slide))
                normalized.append({"anchor": anchor, "occurrence": occurrence, "text": text})
            notes[slide] = normalized
    return notes


def _with_notes(code: str, notes: Iterable[Dict[str, Any]]) -> str:
    """Attach each note immediately before its semantic anchor."""
    lines = _pretty_panel(code).rstrip("\n").splitlines()
    pending: Dict[Tuple[str, int], List[str]] = {}
    for note in notes:
        key = (note["anchor"], note["occurrence"])
        pending.setdefault(key, []).append(note["text"])

    output: List[str] = []
    matched_occurrences: Dict[str, int] = {}
    attached: Dict[Tuple[str, int], bool] = {key: False for key in pending}
    for line in lines:
        stripped = line.strip()
        matching = []
        for anchor, occurrence in pending:
            if stripped.startswith(anchor):
                matched_occurrences[anchor] = matched_occurrences.get(anchor, 0) + 1
                if matched_occurrences[anchor] == occurrence:
                    matching.append((anchor, occurrence))
        for key in matching:
            indent = line[: len(line) - len(line.lstrip(" "))]
            output.extend(indent + "// " + text for text in pending[key])
            attached[key] = True
        output.append(line)
    missing = ["{} (occurrence {})".format(*key) for key, found in attached.items() if not found]
    if missing:
        raise ValueError("Intro note anchor not found: {}".format(", ".join(missing)))
    return "\n".join(output).rstrip() + "\n"


def materialize(destination: Optional[Path] = None) -> int:
    """Write every reviewed textual panel with its manual explanation notes.

    :param destination: Optional output directory, defaulting to the local
        repository-owned test asset path.
    :type destination: pathlib.Path, optional
    :return: Number of source panels written.
    :rtype: int
    :raises ValueError: If inventory or hand-authored notes are malformed.
    """
    payload: Dict[str, Any] = json.loads(INVENTORY.read_text(encoding="utf-8"))
    slides = payload.get("slides")
    if not isinstance(slides, list):
        raise ValueError("Intro inventory has no slides list")
    notes = _load_notes()
    output = destination or DESTINATION
    output.mkdir(parents=True, exist_ok=True)
    count = 0
    seen = set()
    for slide in slides:
        if not isinstance(slide, dict):
            raise ValueError("Intro inventory contains a non-object slide")
        number, code = slide.get("slide"), slide.get("code")
        if not isinstance(number, int) or not isinstance(code, str):
            raise ValueError("Intro inventory slide lacks slide number or code")
        key = str(number)
        seen.add(key)
        path = output / "intro_textual_slide_{:03d}.sysml".format(number)
        path.write_text(_with_notes(code, notes.get(key, [])), encoding="utf-8")
        count += 1
    unknown = sorted(set(notes) - seen, key=int)
    if unknown:
        raise ValueError(
            "note ledger has no corresponding inventory slides: {}".format(", ".join(unknown))
        )
    return count


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Materialize the default Intro-deck source set."""
    del arguments
    print("materialized {} Intro PDF panels".format(materialize()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
