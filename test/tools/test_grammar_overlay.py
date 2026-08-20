"""Regression tests for the generated SysML v2 grammar overlay."""

import json
from pathlib import Path

import pytest

from tools import grammar_overlay

pytestmark = pytest.mark.unit


def _unmodified_grammar() -> str:
    """Return the reviewed upstream fragments needed for one overlay test."""
    return "\n\n".join(before for _, before, _ in grammar_overlay._TRANSFORMATIONS)


def test_overlay_applies_reviewed_sysml_state_compatibility_rules(tmp_path):
    grammar = tmp_path / "SysMLv2Parser.g4"
    grammar.write_text(_unmodified_grammar(), encoding="utf-8")

    assert grammar_overlay.apply_overlay(grammar)
    effective = grammar.read_text(encoding="utf-8")
    assert grammar_overlay._TRANSITION_USAGE_AFTER in effective
    assert grammar_overlay._TRANSITION_PERFORM_ACTION_USAGE_AFTER in effective
    assert grammar_overlay._TRANSITION_ACCEPT_ACTION_USAGE_AFTER in effective
    assert grammar_overlay._TRANSITION_SEND_ACTION_USAGE_AFTER in effective
    assert grammar_overlay._TRANSITION_ASSIGNMENT_ACTION_USAGE_AFTER in effective
    assert grammar_overlay._ACTION_USAGE_AFTER in effective
    assert not grammar_overlay.apply_overlay(grammar)


def test_overlay_rejects_unreviewed_upstream_rule_changes(tmp_path):
    grammar = tmp_path / "SysMLv2Parser.g4"
    grammar.write_text("rootNamespace : unexpected ;", encoding="utf-8")

    with pytest.raises(ValueError, match="Cannot apply"):
        grammar_overlay.apply_overlay(grammar)


def test_overlay_writes_lf_bytes(tmp_path):
    """Keep generated grammar bytes stable when the host newline is CRLF."""
    grammar = tmp_path / "SysMLv2Parser.g4"
    grammar.write_bytes(_unmodified_grammar().replace("\n", "\r\n").encode("utf-8"))

    assert grammar_overlay.apply_overlay(grammar)
    data = grammar.read_bytes()
    assert b"\r\n" not in data
    assert b"\n" in data


def test_manifest_records_automatic_upstream_and_effective_hashes():
    manifest = grammar_overlay.build_manifest("abc", "v2026.05.0", "1" * 64, "2" * 64)

    assert manifest == {
        "schema_version": 1,
        "upstream": {
            "revision": "abc",
            "describe": "v2026.05.0",
            "parser_sha256": "1" * 64,
        },
        "overlay": grammar_overlay.OVERLAY_IDENTIFIER,
        "overlay_notes": list(grammar_overlay.OVERLAY_NOTES),
        "effective_parser_sha256": "2" * 64,
    }
    assert json.loads(json.dumps(manifest)) == manifest


def test_every_overlay_transformation_has_a_review_note_and_generated_comment():
    """Keep grammar deltas auditable in both source and generated G4 text."""
    note_ids = {item["id"] for item in grammar_overlay.OVERLAY_NOTES}
    assert len(note_ids) == len(grammar_overlay.OVERLAY_NOTES)
    for item in grammar_overlay.OVERLAY_NOTES:
        assert item["official_evidence"]
        assert item["reason"]
        assert item["rules"]
        assert "https://" in item["official_evidence"]

    # Every replacement carries an in-G4 marker.  Several replacements share
    # one semantic note (the four transition effect variants).
    for _, _, after in grammar_overlay._TRANSFORMATIONS:
        assert "[pysysmlv2 overlay:" in after
        assert "Difference from pinned upstream ANTLR" in after
        assert "Upstream source:" in after
        assert "https://" in after

    generated = (
        grammar_overlay.Path(grammar_overlay.__file__).parents[1]
        / "pysysmlv2"
        / "syntax"
        / "generated"
        / "SysMLv2Parser.g4"
    )
    generated_text = generated.read_text(encoding="utf-8")
    for item in grammar_overlay.OVERLAY_NOTES:
        marker = "[pysysmlv2 overlay: {}]".format(item["id"])
        assert marker in generated_text


def test_target_transition_rule_remains_upstream_without_guard_first_overlay():
    """Keep target shorthand trigger-first or guard-only at the grammar boundary."""
    assert all(not item["id"].startswith("target-") for item in grammar_overlay.OVERLAY_NOTES)
    assert all(
        "targetTransitionUsage" not in before + after
        for _, before, after in grammar_overlay._TRANSFORMATIONS
    )

    root = Path(grammar_overlay.__file__).parents[1]
    generated = (root / "pysysmlv2/syntax/generated/SysMLv2Parser.g4").read_text(encoding="utf-8")
    upstream = (root / "upstream/sysml-v2-grammar/grammar/SysMLv2Parser.g4").read_text(
        encoding="utf-8"
    )

    def rule_body(text: str) -> str:
        start = text.rfind("\ntargetTransitionUsage\n") + 1
        return text[start:].split("\ntriggerActionMember\n", 1)[0]

    assert rule_body(generated) == rule_body(upstream)
