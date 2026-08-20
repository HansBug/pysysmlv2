"""Regression coverage for manually reviewed OMG Language-PDF fixtures.

The manual inventory is deliberately a local source ledger.  This test module
does not inspect the official PDF, invoke an upstream checkout, or fetch a
network resource.  It ensures that each reviewed source fragment is retained
verbatim in ``test/testfile`` and that every independently parseable fragment
reaches a stable, structurally equal AST round trip.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import pytest

from pysysmlv2 import parse, parse_as_ast_node
from pysysmlv2.syntax import Model, PackageMember

pytestmark = pytest.mark.unit


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = ROOT / "docs" / "research" / "omg_sysml2_language_manual_inventory.json"
FIXTURE_ROOT = ROOT / "test" / "testfile" / "omg_sysml2_language" / "manual"
TRANSITION_FRAGMENT_ID = "s7-18-table17-transition-explicit"
EARLY_LEDGER = ROOT / "docs" / "research" / "manual_pdf_review" / "section_7_1_7_5.json"
MID_LEDGER = (
    ROOT
    / "docs"
    / "research"
    / "manual_pdf_review"
    / "manual_sysml_v2_clause_7_6_7_12_7_15_ledger.json"
)
EARLY_PREFIXES = ("S72-", "S73-", "S74-", "S75-")
EARLY_EXCLUDED_IDS = {
    "S72-02",
    "S74-01",
    "S74-02",
    "S74-03",
    "S74-04",
    "S74-05",
    "S74-06",
    "S74-10",
    "S74-15",
    "S75-04",
    "S75-21",
}


def _entries() -> Tuple[Dict[str, Any], ...]:
    """Load the reviewed entries and reject incomplete ledger records.

    :return: Immutable sequence of normalized manual-inventory entries.
    :rtype: tuple[dict[str, object], ...]
    :raises ValueError: If a required entry value is missing or malformed.
    """
    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("OMG manual inventory has no entries list")
    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("OMG manual inventory contains a non-object entry")
        identifier = entry.get("id")
        fixture_name = entry.get("fixture_name")
        source_code = entry.get("source_code")
        clause = entry.get("clause")
        if not all(
            isinstance(value, str) and value
            for value in (identifier, fixture_name, source_code, clause)
        ):
            raise ValueError("OMG manual inventory entry lacks required source fields")
        normalized.append(entry)
    return tuple(normalized)


def _excluded_entries() -> Tuple[Dict[str, Any], ...]:
    """Load source records deliberately excluded from executable fixtures.

    :return: Immutable sequence of source records retained for provenance.
    :rtype: tuple[dict[str, object], ...]
    :raises ValueError: If the inventory does not describe an excluded source.
    """
    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    entries = payload.get("excluded_entries")
    if not isinstance(entries, list):
        raise ValueError("OMG manual inventory has no excluded_entries list")
    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("OMG manual inventory contains a non-object exclusion")
        required = ("id", "completeness", "exclusion_reason")
        if not all(isinstance(entry.get(key), str) and entry[key] for key in required):
            raise ValueError("OMG manual inventory exclusion lacks source fields")
        if entry.get("source_code") is not None and not isinstance(entry["source_code"], str):
            raise ValueError("OMG manual inventory exclusion has non-text source_code")
        if entry.get("fixture_eligible") is not False:
            raise ValueError("OMG manual inventory exclusion is fixture eligible")
        normalized.append(entry)
    return tuple(normalized)


def _fixture_path(entry: Dict[str, Any]) -> Path:
    """Resolve one ledger fixture beneath the repository-owned fixture root.

    :param entry: One normalized manual-inventory entry.
    :type entry: dict[str, object]
    :return: Resolved fixture path beneath :data:`FIXTURE_ROOT`.
    :rtype: pathlib.Path
    :raises ValueError: If the declared fixture path escapes the fixture root.
    """
    path = FIXTURE_ROOT / entry["fixture_name"]
    try:
        path.relative_to(FIXTURE_ROOT)
    except ValueError as error:
        raise ValueError("OMG manual fixture escapes its root") from error
    return path


def _ids(entries: Iterable[Dict[str, Any]]) -> Tuple[str, ...]:
    """Return readable stable pytest IDs for reviewed source examples.

    :param entries: Manual-inventory entries in ledger order.
    :type entries: iterable[dict[str, object]]
    :return: One stable identifier per entry.
    :rtype: tuple[str, ...]
    """
    return tuple("{}: {}".format(entry["id"], entry["fixture_name"]) for entry in entries)


ENTRIES = _entries()
EXCLUDED_ENTRIES = _excluded_entries()


def test_manual_inventory_fixture_directory_is_complete_and_nonduplicated():
    """Require a checked-in fixture for every reviewed manual source panel."""
    expected = {entry["fixture_name"] for entry in ENTRIES}
    assert len(expected) == len(ENTRIES)
    actual = {path.relative_to(FIXTURE_ROOT).as_posix() for path in FIXTURE_ROOT.rglob("*.sysml")}
    assert actual == expected


def test_manual_inventory_preserves_every_reviewed_early_pdf_source_record():
    """Account for all 46 visually reviewed Clause 7.1--7.5 source blocks.

    Fixtures are intentionally a strict subset: lexical/context fragments,
    visible PDF typos, a legacy source-version form, and ellipsis-containing
    examples remain in the inventory with their exact text and a reason rather
    than being silently normalized or dropped.
    """
    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    early_ledger = json.loads(EARLY_LEDGER.read_text(encoding="utf-8"))
    ledger_records = {entry["id"]: entry for entry in early_ledger["entries"]}
    inventory_records = {
        entry["id"]: entry
        for entry in (*ENTRIES, *EXCLUDED_ENTRIES)
        if entry["id"].startswith(EARLY_PREFIXES)
    }

    assert len(ledger_records) == 46
    assert set(inventory_records) == set(ledger_records)
    assert payload["reviewed_entry_count"] == len(ENTRIES) + len(EXCLUDED_ENTRIES)
    for identifier, ledger_record in ledger_records.items():
        inventory_record = inventory_records[identifier]
        assert inventory_record["source_code"] == ledger_record["source_code"]
        assert inventory_record["completeness"] == ledger_record["completeness"]
        assert inventory_record["fixture_eligible"] == ledger_record["fixture_eligible"]

    assert {
        entry["id"] for entry in EXCLUDED_ENTRIES if entry["id"].startswith(EARLY_PREFIXES)
    } == (EARLY_EXCLUDED_IDS)
    assert all(
        entry["exclusion_reason"]
        for entry in EXCLUDED_ENTRIES
        if entry["id"].startswith(EARLY_PREFIXES)
    )


def test_manual_inventory_preserves_the_clause_7_6_to_7_15_visual_ledger():
    """Retain every mid-section source record, including graphical exclusions."""
    ledger = json.loads(MID_LEDGER.read_text(encoding="utf-8"))
    source_records = {entry["id"]: entry for entry in ledger["entries"]}
    excluded_records = {entry["id"]: entry for entry in ledger["excluded_fragments"]}
    inventory_records = {
        entry["id"]: entry
        for entry in (*ENTRIES, *EXCLUDED_ENTRIES)
        if entry["id"].startswith(
            ("S76-", "S712-", "S713-", "S714-", "S715-", "X76-", "X713-", "X714-", "X715-")
        )
    }

    assert len(source_records) == 77
    assert len(excluded_records) == 5
    assert set(inventory_records) == set(source_records) | set(excluded_records)
    for identifier, source in {**source_records, **excluded_records}.items():
        record = inventory_records[identifier]
        assert record["source_code"] == source["source_code"]
        assert record["clause"] == source["clause"]
        assert record["completeness"] == source["completeness"]
        assert record["review_ledger"].endswith(MID_LEDGER.name)

    assert inventory_records["S76-08"]["fixture_eligible"] is False
    assert "variant part" in inventory_records["S76-08"]["exclusion_reason"]
    assert all(
        inventory_records[identifier]["fixture_eligible"] is False
        for identifier in excluded_records
    )


def test_manual_inventory_retains_every_record_from_every_json_ledger():
    """Keep every machine-readable manual ledger record in the merged inventory."""
    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    inventory_records = {entry["id"]: entry for entry in (*ENTRIES, *EXCLUDED_ENTRIES)}
    for ledger_path in sorted((ROOT / "docs" / "research" / "manual_pdf_review").glob("*.json")):
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        records = [*ledger.get("entries", []), *ledger.get("excluded_fragments", [])]
        for source in records:
            identifier = source["id"]
            assert identifier in inventory_records
            merged = inventory_records[identifier]
            assert merged["source_code"] == source.get("source_code")
            assert merged["review_ledger"].endswith(ledger_path.name)
            if source in ledger.get("excluded_fragments", []):
                assert merged["fixture_eligible"] is False
    assert payload["reviewed_entry_count"] == len(ENTRIES) + len(EXCLUDED_ENTRIES)


@pytest.mark.parametrize("entry", ENTRIES, ids=_ids(ENTRIES))
def test_manual_inventory_fixture_preserves_the_reviewed_source(entry: Dict[str, Any]):
    """Keep each local fixture byte-for-byte synchronized with its ledger text."""
    path = _fixture_path(entry)
    assert path.is_file()
    assert path.read_text(encoding="utf-8") == entry["source_code"].rstrip() + "\n"


def test_manual_transition_fragment_uses_its_actual_local_grammar_context():
    """Verify the Table 17 transition fragment without inventing a root context."""
    entry = next(item for item in ENTRIES if item["id"] == TRANSITION_FRAGMENT_ID)
    lines = [line.strip() for line in entry["source_code"].splitlines() if line.strip()]
    nodes = [parse_as_ast_node(line, grammar_node="stateUsage") for line in lines[:2]]
    transition = parse_as_ast_node(lines[2], grammar_node="transitionUsage")
    fragment = Model(
        members=[
            PackageMember(element=node) if index < 2 else node
            for index, node in enumerate([*nodes, transition])
        ]
    )
    assert str(fragment)
    assert str(parse_as_ast_node(str(transition), grammar_node="transitionUsage")) == str(
        transition
    )


@pytest.mark.parametrize(
    "entry",
    tuple(entry for entry in ENTRIES if entry["id"] != TRANSITION_FRAGMENT_ID),
    ids=lambda entry: "{}: {}".format(entry["id"], entry["fixture_name"]),
)
def test_manual_inventory_fixture_round_trips_with_full_ast_equality(entry: Dict[str, Any]):
    """Require stable AST export/reparse behavior for each complete source panel."""
    path = _fixture_path(entry)
    first = parse(path.read_text(encoding="utf-8"), str(path))
    assert first.ok, first.diagnostics
    exported = str(first.ast)
    second = parse(exported, "roundtrip/{}".format(path.name))
    assert second.ok, second.diagnostics
    assert first.ast == second.ast
    assert str(second.ast) == exported
