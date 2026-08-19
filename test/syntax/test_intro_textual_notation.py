"""Validate the manually reviewed Intro-to-SysML textual-notation assets.

The PDF itself is deliberately absent from runtime tests.  The inventory is
the reviewed code transcription and the note ledgers contain only exact
explanatory sentences copied from the rendered slides.  These tests prevent a
future maintainer from reintroducing page titles, code echoes or generated
boilerplate as SysML comments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

import pytest

from pysysmlv2 import parse
from test.testings.ast_snapshot import ast_snapshot
from tools.materialize_intro_textual_examples import _pretty_panel

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "research" / "intro_textual_notation_inventory.json"
NOTE_FILES = (
    ROOT / "docs" / "research" / "intro_manual_notes_5_46.json",
    ROOT / "docs" / "research" / "intro_manual_notes_47_185.json",
    ROOT / "docs" / "research" / "intro_manual_notes_121_185.json",
)
FIXTURE_ROOT = ROOT / "test" / "testfile" / "omg_intro_textual_notation"

pytestmark = pytest.mark.unit


def _slides() -> Dict[str, Dict[str, Any]]:
    payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
    return {str(item["slide"]): item for item in payload["slides"]}


def _parser_compatibility_gaps() -> Dict[str, str]:
    """Load reviewed panels outside the current SysML-only parser scope."""
    payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
    return {
        str(item["slide"]): str(item["reason"])
        for item in payload.get("parser_compatibility_gaps", [])
    }


def _notes() -> Dict[str, List[Dict[str, Any]]]:
    result: Dict[str, List[Dict[str, Any]]] = {}
    for path in NOTE_FILES:
        payload: Mapping[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        for slide, entries in payload.items():
            assert slide not in result
            result[slide] = [
                {
                    "anchor": entry["anchor"],
                    "occurrence": entry.get("occurrence", 1),
                    "text": entry["text"],
                }
                for entry in entries
            ]
    return result


SLIDES = _slides()
NOTES = _notes()
PARSER_COMPATIBILITY_GAPS = _parser_compatibility_gaps()


def _fixture(slide: str) -> Path:
    return FIXTURE_ROOT / "intro_textual_slide_{:03d}.sysml".format(int(slide))


def _remove_manual_comments(source: str, notes: Iterable[Dict[str, Any]]) -> str:
    """Remove only ledger comments, preserving comments present in source code."""
    injected = {"// " + note["text"] for note in notes}
    return (
        "\n".join(line for line in source.splitlines() if line.strip() not in injected).rstrip()
        + "\n"
    )


@pytest.mark.parametrize("slide", sorted(SLIDES, key=int))
def test_every_reviewed_slide_has_one_local_fixture(slide: str):
    """Keep the complete 167-panel reviewed source set checked in locally."""
    assert _fixture(slide).is_file()


@pytest.mark.parametrize("slide", sorted(SLIDES, key=int))
def test_fixture_preserves_reviewed_code_and_only_manual_comments(slide: str):
    """Compare fixture code exactly after removing the explicit note ledger."""
    source = _fixture(slide).read_text(encoding="utf-8")
    expected = _pretty_panel(SLIDES[slide]["code"])
    assert _remove_manual_comments(source, NOTES.get(slide, [])) == expected
    assert "Source: OMG" not in source
    assert "PDF release:" not in source
    assert "visible slide transcription" not in source
    assert "End visible slide transcription" not in source


@pytest.mark.parametrize("slide", sorted(NOTES, key=int))
def test_manual_explanation_text_is_present_as_an_ordinary_comment(slide: str):
    """Require every reviewed explanatory sentence to survive as ``//`` text."""
    source = _fixture(slide).read_text(encoding="utf-8")
    for note in NOTES[slide]:
        assert "// " + note["text"] in source


@pytest.mark.parametrize("slide", sorted(NOTES, key=int))
def test_manual_explanation_is_attached_to_its_explicit_semantic_anchor(slide: str):
    """Keep comments adjacent to the declared source element occurrence."""
    source_lines = _fixture(slide).read_text(encoding="utf-8").splitlines()
    for note in NOTES[slide]:
        anchor_index = [
            index
            for index, line in enumerate(source_lines)
            if line.strip().startswith(note["anchor"])
        ][note["occurrence"] - 1]
        comment = "// " + note["text"]
        attached = []
        cursor = anchor_index - 1
        while cursor >= 0 and source_lines[cursor].lstrip().startswith("// "):
            attached.append(source_lines[cursor].strip())
            cursor -= 1
        assert comment in attached


def test_no_intro_fixture_contains_generated_comment_markers():
    """Reject the former whole-page transcription implementation permanently."""
    forbidden = (
        "The following is a line-preserving transcription",
        "It is retained as ordinary comments",
        "End visible slide transcription.",
    )
    for path in FIXTURE_ROOT.glob("*.sysml"):
        source = path.read_text(encoding="utf-8")
        assert not any(marker in source for marker in forbidden), path


@pytest.mark.parametrize(
    "slide",
    sorted(
        (
            slide
            for slide, item in SLIDES.items()
            if item["completeness"] == "complete"
            and item["fixture_candidate"]
            and slide not in PARSER_COMPATIBILITY_GAPS
        ),
        key=int,
    ),
)
def test_parser_ready_intro_panels_have_exact_ast_and_round_trip(slide: str):
    """Parse every in-scope closed panel and compare its complete AST shape."""
    path = _fixture(slide)
    result = parse(path.read_text(encoding="utf-8"), str(path))
    assert result.ok, result.diagnostics
    reparsed = parse(str(result.ast), "roundtrip.sysml")
    assert reparsed.ok, reparsed.diagnostics
    assert ast_snapshot(result.ast) == ast_snapshot(reparsed.ast)
    assert str(reparsed.ast) == str(result.ast)


@pytest.mark.parametrize("slide", sorted(PARSER_COMPATIBILITY_GAPS, key=int))
def test_out_of_scope_intro_panels_remain_explicit_reviewed_assets(slide: str):
    """Keep known historical/contextual panels without accepting them silently."""
    item = SLIDES[slide]
    assert item["completeness"] == "complete"
    assert item["fixture_candidate"] is True
    path = _fixture(slide)
    result = parse(path.read_text(encoding="utf-8"), str(path))
    assert not result.ok
    assert result.diagnostics
    assert PARSER_COMPATIBILITY_GAPS[slide]
