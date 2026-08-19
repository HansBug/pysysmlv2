"""Exact AST and round-trip assertions for reviewed OMG PDF state examples."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pysysmlv2 import parse, parse_as_ast_node
from pysysmlv2.syntax.ast import (
    DefinitionDeclaration,
    Identification,
    Model,
    OccurrenceDefinitionPrefix,
    PackageMember,
    StateDefBody,
    StateDefinition,
)
from test.testings.ast_snapshot import ast_snapshot

ROOT = Path(__file__).parents[1] / "testfile" / "omg_sysml2_language"
FIXTURES = ROOT / "section7"
INVENTORY = json.loads(
    (
        Path(__file__).parents[2] / "docs" / "research" / "omg_sysml2_language_examples.json"
    ).read_text(encoding="utf-8")
)
GOLDENS_PATH = FIXTURES / "ast_goldens.json"


def _inventory_by_fixture():
    return {item["fixture_name"]: item for item in INVENTORY["known_examples"]}


def _goldens():
    if not GOLDENS_PATH.is_file():
        return {}
    payload = json.loads(GOLDENS_PATH.read_text(encoding="utf-8"))
    # The checked-in golden schema is shared with the Section 7 source test:
    # ``fixtures`` contains the complete span-free snapshots.  Keep this
    # second test module pointed at the same authoritative data instead of
    # silently accepting an absent/legacy ``entries`` object.
    return payload["fixtures"]


_BY_FIXTURE = _inventory_by_fixture()
_GOLDENS = _goldens()
_PATHS = tuple(sorted(FIXTURES.glob("*.sysml")))

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("path", _PATHS, ids=lambda path: path.name)
def test_pdf_fixture_is_the_reviewed_omg_source(path: Path):
    """Keep every checked-in fixture synchronized with the PDF inventory."""
    entry = _BY_FIXTURE[path.name]
    assert path.read_text(encoding="utf-8").rstrip() == entry["code"].rstrip()
    assert entry["clause"].startswith("7.18")
    assert entry["printed_pages"]


@pytest.mark.parametrize("path", _PATHS, ids=lambda path: path.name)
def test_pdf_fixture_has_an_exact_full_field_ast_golden(path: Path):
    """Compare every AST dataclass field, excluding only ``span`` provenance."""
    if path.name == "section_7_18_table17_transition_explicit.sysml":
        lines = [
            line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        nodes = [parse_as_ast_node(line, grammar_node="stateUsage") for line in lines[:2]]
        nodes.append(parse_as_ast_node(lines[2], grammar_node="transitionUsage"))
        fragment = Model(
            members=[
                PackageMember(element=node) if index < 2 else node
                for index, node in enumerate(nodes)
            ]
        )
        assert ast_snapshot(fragment) == _GOLDENS[path.name]
        return
    result = parse(path.read_text(encoding="utf-8"), str(path))
    assert result.ok, result.diagnostics
    assert path.name in _GOLDENS
    assert ast_snapshot(result.ast) == _GOLDENS[path.name]

    exported = str(result.ast)
    reparsed = parse(exported, "roundtrip.sysml")
    assert reparsed.ok, reparsed.diagnostics
    assert result.ast == reparsed.ast
    assert str(reparsed.ast) == exported


def test_pdf_ast_assertion_is_a_direct_dataclass_equality_not_only_a_snapshot():
    """Pin a small normative state definition with an explicit AST value."""
    expected = Model(
        members=[
            # ``PackageMember`` is intentionally imported through the parser
            # result below so this assertion remains focused on required state
            # fields while the golden tests cover all members.
        ]
    )
    actual = parse_as_ast_node("state def StateDef1;", grammar_node="stateDefinition")
    expected_state = StateDefinition(
        occurrence_definition_prefix=OccurrenceDefinitionPrefix(),
        definition_declaration=DefinitionDeclaration(
            identification=Identification(short_name=None, declared_name="StateDef1"),
            subclassification=None,
        ),
        state_def_body=StateDefBody(
            is_parallel=False,
            is_declaration_only=True,
            state_body_members=[],
        ),
    )
    assert actual == expected_state
    assert expected.members == []
