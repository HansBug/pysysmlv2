"""Lock reviewed OMG SysML 2.0 Section 7.18 examples to explicit AST goldens.

The PDF extraction inventory is only a local source ledger.  These tests read
the checked-in SysML snippets and checked-in dataclass snapshots; they never
read the PDF, an upstream checkout, or a network resource at test time.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import pytest

from pysysmlv2 import parse, parse_as_ast_node
from pysysmlv2.syntax import (
    ActionUsageDeclaration,
    DefinitionDeclaration,
    DottedQualifiedReference,
    FeatureSpecialization,
    FeatureSpecializationPart,
    Identification,
    Model,
    OccurrenceDefinitionPrefix,
    OccurrenceUsagePrefix,
    OwnedFeatureTyping,
    PackageMember,
    QualifiedReference,
    StateDefBody,
    StateDefinition,
    StateUsage,
    StateUsageBody,
    UsageDeclaration,
)
from test.testings.ast_snapshot import ast_snapshot

pytestmark = pytest.mark.unit


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = ROOT / "docs" / "research" / "omg_sysml2_language_examples.json"
FIXTURE_ROOT = ROOT / "test" / "testfile" / "omg_sysml2_language" / "section7"
GOLDENS_PATH = FIXTURE_ROOT / "ast_goldens.json"


def _load_examples() -> Tuple[Dict[str, Any], ...]:
    """Return the locally reviewed Section 7.18 examples in inventory order."""
    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    examples = payload.get("known_examples")
    if not isinstance(examples, list):
        raise ValueError("OMG SysML language inventory has no known_examples list")
    result = []
    for example in examples:
        if not isinstance(example, dict):
            raise ValueError("OMG SysML language inventory contains a non-object example")
        fixture_name = example.get("fixture_name")
        code = example.get("code")
        status = example.get("parse_status_current")
        if not isinstance(fixture_name, str) or not isinstance(code, str):
            raise ValueError("OMG SysML language inventory example lacks fixture_name or code")
        if status not in {"pass", "fail", "context_fragment"}:
            raise ValueError("OMG SysML language inventory has an unknown parser status")
        result.append(example)
    return tuple(result)


def _load_goldens() -> Dict[str, Any]:
    """Return the checked-in full-field AST snapshots for all fixtures."""
    payload = json.loads(GOLDENS_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("span_excluded") is not True:
        raise ValueError("OMG AST golden file uses an unsupported schema")
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, dict):
        raise ValueError("OMG AST golden file has no fixtures object")
    return fixtures


def _fixture_path(example: Dict[str, Any]) -> Path:
    """Resolve one inventory fixture name beneath the repository-owned root."""
    fixture_name = example["fixture_name"]
    path = FIXTURE_ROOT / fixture_name
    try:
        path.relative_to(FIXTURE_ROOT)
    except ValueError as error:
        raise ValueError("OMG fixture name escapes the fixture root") from error
    return path


def _fixture_ids(examples: Iterable[Dict[str, Any]]) -> Tuple[str, ...]:
    """Return stable pytest IDs with the inventory ID and checked-in filename."""
    return tuple("{}: {}".format(example["id"], example["fixture_name"]) for example in examples)


EXAMPLES = _load_examples()
GOLDENS = _load_goldens()


@pytest.mark.parametrize("example", EXAMPLES, ids=_fixture_ids(EXAMPLES))
def test_section_7_18_fixture_text_matches_the_reviewed_local_inventory(example):
    """Keep each checked-in source fixture synchronized with the local ledger."""
    path = _fixture_path(example)
    assert path.is_file()
    assert path.read_text(encoding="utf-8") == example["code"].rstrip() + "\n"


def test_section_7_18_fixture_directory_and_goldens_cover_the_complete_inventory():
    """Require source and expected AST data for every reviewed state example."""
    fixture_names = {example["fixture_name"] for example in EXAMPLES}
    assert {path.name for path in FIXTURE_ROOT.glob("*.sysml")} == fixture_names
    assert set(GOLDENS) == fixture_names


@pytest.mark.parametrize("example", EXAMPLES, ids=_fixture_ids(EXAMPLES))
def test_section_7_18_fixture_matches_full_ast_golden_and_round_trips(example):
    """Check every structural AST field before testing canonical reparsing."""
    path = _fixture_path(example)
    source = path.read_text(encoding="utf-8")
    if example["fixture_name"] == "section_7_18_table17_transition_explicit.sysml":
        # Table 17 places a transition usage beside two state usages as an
        # explanatory fragment.  It is not a complete rootNamespace because
        # transitions are legal only inside a state body.  Parse each concrete
        # production through its explicit grammar entry and compare the
        # assembled source model field-for-field.
        lines = [line.strip() for line in source.splitlines() if line.strip()]
        nodes = [parse_as_ast_node(line, grammar_node="stateUsage") for line in lines[:2]]
        nodes.append(parse_as_ast_node(lines[2], grammar_node="transitionUsage"))
        fragment = Model(
            members=[
                PackageMember(element=node) if index < 2 else node
                for index, node in enumerate(nodes)
            ]
        )
        expected = GOLDENS[example["fixture_name"]]
        assert ast_snapshot(fragment) == expected
        assert [str(node) for node in nodes] == [line.rstrip(";") + ";" for line in lines]
        return
    first = parse(source, str(path))
    assert first.ok, first.diagnostics
    expected = GOLDENS[example["fixture_name"]]
    assert ast_snapshot(first.ast) == expected

    exported = str(first.ast)
    second = parse(exported, "roundtrip/{}".format(path.name))
    assert second.ok, second.diagnostics
    assert ast_snapshot(second.ast) == expected
    assert str(second.ast) == exported


def test_simple_state_definition_matches_a_hand_constructed_ast():
    """Prove the smallest state definition maps to explicit concrete nodes."""
    result = parse("state def StateDef1;")
    expected = Model(
        [
            PackageMember(
                StateDefinition(
                    OccurrenceDefinitionPrefix(),
                    DefinitionDeclaration(Identification(declared_name="StateDef1")),
                    StateDefBody(is_declaration_only=True),
                )
            )
        ]
    )
    assert result.ok
    assert result.ast == expected
    assert ast_snapshot(result.ast) == ast_snapshot(expected)


def test_simple_state_usage_matches_a_hand_constructed_ast():
    """Prove a typed state usage retains its complete specialization relation."""
    result = parse("state state1 : StateDef1;")
    expected = Model(
        [
            PackageMember(
                StateUsage(
                    OccurrenceUsagePrefix(),
                    ActionUsageDeclaration(
                        UsageDeclaration(
                            Identification(declared_name="state1"),
                            FeatureSpecializationPart(
                                [
                                    FeatureSpecialization(
                                        ":",
                                        [
                                            OwnedFeatureTyping(
                                                DottedQualifiedReference(
                                                    [QualifiedReference(["StateDef1"])]
                                                )
                                            )
                                        ],
                                    )
                                ]
                            ),
                        )
                    ),
                    StateUsageBody(is_declaration_only=True),
                )
            )
        ]
    )
    assert result.ok
    assert result.ast == expected
    assert ast_snapshot(result.ast) == ast_snapshot(expected)
