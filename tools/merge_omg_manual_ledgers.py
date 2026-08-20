"""Merge manually reviewed OMG SysML example ledgers.

The OMG PDF is not parsed by this module.  Human reviewers record one closed
textual example per ledger entry after visually checking the rendered pages.
This command only validates those records, assigns stable fixture names, and
materializes repository-owned source files.  Incomplete fragments, diagram
labels, and external-language bodies remain in the audit ledger but are never
silently promoted to executable fixtures.

Example::

    $ python -m tools.merge_omg_manual_ledgers
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
LEDGER_ROOT = ROOT / "docs" / "research" / "manual_pdf_review"
STATE_INVENTORY = ROOT / "docs" / "research" / "omg_sysml2_language_examples.json"
OUTPUT = ROOT / "docs" / "research" / "omg_sysml2_language_manual_inventory.json"
FIXTURE_ROOT = ROOT / "test" / "testfile" / "omg_sysml2_language" / "manual"


def _slug(value: str) -> str:
    """Return a stable, filesystem-safe fragment for a ledger identifier."""
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _state_entries() -> Iterable[Dict[str, Any]]:
    """Yield the previously reviewed state examples in legacy-compatible form."""
    payload = json.loads(STATE_INVENTORY.read_text(encoding="utf-8"))
    for item in payload.get("known_examples", []):
        yield {
            "id": item["id"],
            "clause": item["clause"],
            "printed_pages": item["printed_pages"],
            "physical_pages": [],
            "source_kind": "pdf_state_example",
            "source_code": item["code"],
            "completeness": "complete",
            "fixture_eligible": True,
            "dependencies": [],
            "notes": "Retained from the manually reviewed Section 7.18 ledger.",
            "legacy_fixture_name": item["fixture_name"],
        }


def _manual_entries() -> Iterable[Dict[str, Any]]:
    """Yield entries from every manually authored review ledger."""
    for path in sorted(LEDGER_ROOT.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        # New ledgers keep every visually reviewed source block in ``entries``
        # and classify it explicitly.  The compatibility default keeps older
        # manually reviewed ledgers materializable without rewriting them.
        for item in payload.get("entries", []):
            record = dict(item)
            if "fixture_eligible" not in record:
                record["fixture_eligible"] = (
                    record.get("parseability") == "independently_parseable"
                    if "parseability" in record
                    else True
                )
            if not record["fixture_eligible"] and not record.get("exclusion_reason"):
                record["exclusion_reason"] = (
                    "The reviewed source is a contextual fragment and requires an "
                    "enclosing grammar/model context before executable materialization."
                )
            record["review_ledger"] = str(path.relative_to(ROOT))
            yield record
        for item in payload.get("excluded_fragments", []):
            record = dict(item)
            record["fixture_eligible"] = False
            record["review_ledger"] = str(path.relative_to(ROOT))
            if not record.get("exclusion_reason"):
                record["exclusion_reason"] = record.get(
                    "notes", "The reviewed record is graphical-only and has no source block."
                )
            yield record


def _validate(entries: List[Dict[str, Any]]) -> None:
    """Reject duplicate IDs, missing provenance, and malformed source records."""
    ids = [entry.get("id") for entry in entries]
    if any(not isinstance(value, str) or not value for value in ids):
        raise ValueError("every manual OMG entry needs a non-empty id")
    if len(ids) != len(set(ids)):
        raise ValueError("manual OMG ledgers contain duplicate ids")
    for entry in entries:
        for key in ("clause", "printed_pages", "source_kind", "source_code", "completeness"):
            if key not in entry:
                raise ValueError("{} is missing {}".format(entry["id"], key))
        if not isinstance(entry.get("fixture_eligible"), bool):
            raise ValueError("{} needs a boolean fixture_eligible value".format(entry["id"]))
        if entry["fixture_eligible"] and entry["completeness"] not in {
            "complete",
            "complete_template",
        }:
            raise ValueError("eligible entry {} is not a closed source example".format(entry["id"]))
        if not entry["fixture_eligible"] and not entry.get("exclusion_reason"):
            raise ValueError("excluded entry {} needs an exclusion_reason".format(entry["id"]))
        if entry["fixture_eligible"] and (
            not isinstance(entry.get("source_code"), str) or not entry["source_code"].strip()
        ):
            raise ValueError("eligible entry {} has empty source_code".format(entry["id"]))
        if (
            entry["fixture_eligible"] is False
            and entry.get("source_code") is not None
            and not isinstance(entry["source_code"], str)
        ):
            raise ValueError("{} has non-text source_code".format(entry["id"]))


def build_inventory() -> Dict[str, Any]:
    """Build the checked-in inventory from manual ledgers only."""
    entries = list(_state_entries()) + list(_manual_entries())
    _validate(entries)
    result: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    for entry in entries:
        item = dict(entry)
        if item["fixture_eligible"]:
            item["fixture_name"] = item.get("legacy_fixture_name") or (
                "{}.sysml".format(_slug(item["id"]))
            )
            item.pop("legacy_fixture_name", None)
            result.append(item)
        else:
            excluded.append(item)
    result.sort(key=lambda item: (item["clause"], item["id"]))
    excluded.sort(key=lambda item: (item["clause"], item["id"]))
    return {
        "schema_version": 2,
        "source": "Human-reviewed OMG SysML 2.0 Language PDF examples",
        "source_url": "https://www.omg.org/spec/SysML/2.0/Language/PDF",
        "source_document": "formal/2026-03-02",
        "review_policy": (
            "Entries are transcribed and visually checked by a human reviewer. "
            "This manifest does not infer examples from PDF text extraction."
        ),
        "fixture_policy": (
            "Only complete textual SysML examples and complete representative "
            "templates become fixtures; excluded source records remain in "
            "excluded_entries with their verbatim text and reason."
        ),
        "entries": result,
        "excluded_entries": excluded,
        "reviewed_entry_count": len(entries),
    }


def materialize(inventory: Mapping[str, Any], destination: Optional[Path] = None) -> int:
    """Write all manually reviewed examples to the local fixture directory."""
    output = destination or FIXTURE_ROOT
    output.mkdir(parents=True, exist_ok=True)
    expected_names = {entry["fixture_name"] for entry in inventory["entries"]}
    for stale_path in output.glob("*.sysml"):
        if stale_path.name not in expected_names:
            stale_path.unlink()
    count = 0
    for entry in inventory["entries"]:
        (output / entry["fixture_name"]).write_text(
            entry["source_code"].rstrip() + "\n", encoding="utf-8"
        )
        count += 1
    return count


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Validate ledgers, write the inventory, and materialize local fixtures.

    :param arguments: Reserved command-line arguments, ignored.
    :type arguments: sequence[str], optional
    :return: Process exit status.
    :rtype: int
    """
    del arguments
    inventory = build_inventory()
    OUTPUT.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    count = materialize(inventory)
    print("materialized {} manually reviewed OMG examples".format(count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
