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

# Visual audit ledger: every rendered code panel was inspected page by page.
# Keeping the per-page cardinalities here catches both missing callouts and
# accidental duplicate prose, which a total-only assertion cannot detect.
EXPECTED_CALLOUT_COUNTS = {
    "5": 6,
    "6": 4,
    "7": 5,
    "8": 2,
    "9": 7,
    "10": 5,
    "11": 2,
    "12": 6,
    "13": 3,
    "14": 5,
    "15": 3,
    "16": 2,
    "17": 6,
    "18": 5,
    "20": 5,
    "21": 2,
    "22": 3,
    "23": 4,
    "24": 2,
    "25": 2,
    "27": 2,
    "28": 2,
    "29": 6,
    "30": 5,
    "31": 1,
    "32": 1,
    "33": 3,
    "34": 2,
    "35": 2,
    "36": 1,
    "37": 3,
    "38": 3,
    "39": 7,
    "40": 3,
    "41": 4,
    "42": 3,
    "43": 3,
    "44": 5,
    "45": 7,
    "46": 3,
    "47": 3,
    "48": 4,
    "49": 1,
    "50": 2,
    "51": 2,
    "52": 4,
    "53": 2,
    "54": 5,
    "55": 5,
    "56": 3,
    "57": 6,
    "58": 4,
    "59": 2,
    "60": 3,
    "61": 2,
    "63": 4,
    "65": 3,
    "67": 4,
    "68": 5,
    "69": 2,
    "70": 3,
    "71": 5,
    "72": 4,
    "73": 2,
    "74": 4,
    "75": 4,
    "76": 7,
    "77": 3,
    "78": 3,
    "79": 7,
    "80": 2,
    "81": 2,
    "82": 2,
    "83": 4,
    "84": 5,
    "85": 3,
    "86": 4,
    "87": 5,
    "88": 1,
    "89": 3,
    "90": 6,
    "91": 2,
    "92": 5,
    "93": 4,
    "94": 3,
    "95": 5,
    "96": 6,
    "97": 4,
    "98": 4,
    "99": 4,
    "100": 5,
    "101": 7,
    "102": 4,
    "103": 4,
    "104": 3,
    "105": 3,
    "106": 3,
    "107": 3,
    "108": 6,
    "109": 4,
    "110": 4,
    "111": 3,
    "112": 3,
    "113": 3,
    "114": 4,
    "115": 4,
    "116": 3,
    "117": 7,
    "118": 5,
    "119": 0,
    "121": 0,
    "122": 0,
    "123": 0,
    "124": 0,
    "126": 0,
    "127": 1,
    "128": 0,
    "129": 0,
    "130": 0,
    "131": 0,
    "132": 0,
    "133": 0,
    "134": 0,
    "135": 0,
    "136": 0,
    "137": 0,
    "138": 0,
    "139": 0,
    "140": 0,
    "141": 0,
    "142": 0,
    "143": 6,
    "145": 0,
    "147": 3,
    "148": 5,
    "149": 2,
    "150": 8,
    "152": 3,
    "153": 2,
    "154": 1,
    "155": 2,
    "156": 6,
    "158": 2,
    "159": 5,
    "161": 4,
    "162": 3,
    "164": 6,
    "165": 2,
    "166": 4,
    "167": 5,
    "168": 4,
    "169": 2,
    "170": 0,
    "171": 0,
    "172": 0,
    "173": 0,
    "174": 0,
    "175": 5,
    "176": 5,
    "177": 2,
    "179": 3,
    "180": 2,
    "181": 1,
    "182": 0,
    "183": 0,
    "184": 0,
    "185": 0,
}

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


def test_manual_callout_counts_match_the_visual_audit():
    """Lock every slide's reviewed callout count, including zero-callout pages."""
    assert set(NOTES) == set(EXPECTED_CALLOUT_COUNTS)
    assert {slide: len(entries) for slide, entries in NOTES.items()} == EXPECTED_CALLOUT_COUNTS
    assert sum(EXPECTED_CALLOUT_COUNTS.values()) == 499


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
