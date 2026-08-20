"""Audit the deliberately private ``RawElement`` compatibility boundary."""

import ast as python_ast
import inspect
import json
from dataclasses import fields, is_dataclass
from pathlib import Path

import pytest

from pysysmlv2 import parse
from pysysmlv2.syntax import RawElement
from pysysmlv2.syntax.listener import SysMLAstListener

pytestmark = pytest.mark.unit


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs" / "research" / "raw_element_compatibility_ledger.json"


def _walk(value):
    """Yield every nested dataclass value except source-span provenance."""
    if isinstance(value, RawElement):
        yield value
        return
    if is_dataclass(value):
        for item in fields(value):
            if item.name != "span":
                yield from _walk(getattr(value, item.name))
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk(item)


def _ledger():
    """Load the checked-in RawElement production ledger."""
    payload = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    return payload["entries"]


def test_ledger_is_complete():
    """Require one reasoned record for every listener raw-store callback."""
    entries = _ledger()
    assert len({entry["id"] for entry in entries}) == len(entries)
    source = inspect.getsource(SysMLAstListener)
    tree = python_ast.parse(source)
    class_node = next(node for node in tree.body if isinstance(node, python_ast.ClassDef))
    raw_callbacks = {
        node.name
        for node in class_node.body
        if isinstance(node, (python_ast.FunctionDef, python_ast.AsyncFunctionDef))
        and node.name.startswith("exit")
        and any(
            isinstance(call, python_ast.Call)
            and isinstance(call.func, python_ast.Attribute)
            and call.func.attr == "_raw_store"
            for statement in node.body
            for call in python_ast.walk(statement)
        )
    }
    assert raw_callbacks == {entry["callback"] for entry in entries}
    assert all(entry["production"] in source for entry in entries)
    assert all(entry["reason"] and entry["follow_up"] and entry["test"] for entry in entries)


def test_core_state_paths_are_typed():
    """State, transition, guard, and target shorthand paths never become raw."""
    result = parse(
        "package Demo { state def S { state A; accept E if enabled then A; "
        "if enabled then A; transition t first A if enabled accept E then A; } }"
    )
    assert result.ok, result.diagnostics
    assert list(_walk(result.ast)) == []


def test_core_connection_and_interface_paths_are_typed():
    """Connection/interface productions use their explicit source nodes."""
    result = parse(
        "package Demo { item def A; item def B; connection c connect A to B; "
        "interface def I { end e; } }"
    )
    assert result.ok, result.diagnostics
    assert list(_walk(result.ast)) == []


def test_model_owned_annotations_are_typed():
    """Comments and documentation remain model nodes, not raw fragments."""
    result = parse("package Demo { comment Comment1 /* note */ doc /* docs */ part def Vehicle; }")
    assert result.ok, result.diagnostics
    assert list(_walk(result.ast)) == []


def test_core_package_paths_are_typed():
    """Package membership, imports, aliases, and filters stay structured."""
    result = parse("package Demo { import A::*; alias X for A; filter @Safety; }")
    assert result.ok, result.diagnostics
    assert list(_walk(result.ast)) == []


def test_core_non_occurrence_paths_are_typed():
    """Supported attribute/reference/enum usage dispatchers stay typed."""
    result = parse("package Demo { attribute a; ref attribute r; enum E { one; } }")
    assert result.ok, result.diagnostics
    assert list(_walk(result.ast)) == []


def test_ledger_does_not_claim_target_guard_first_support():
    """The deferred raw boundary must not reintroduce the removed target order."""
    text = LEDGER.read_text(encoding="utf-8")
    removed_overlay = "target-" + "transition-" + "trigger-guard-order"
    assert removed_overlay not in text
    assert "guard_before_trigger" not in text
