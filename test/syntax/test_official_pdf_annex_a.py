"""Independent AST and round-trip checks for the reviewed Annex A.3 example.

The fixture is a repository-owned transcription of the complete ``part def
Vehicle`` source block on printed page 637 of the OMG SysML 2.0 Language
Specification (physical page 669 in the reviewed PDF).  The expected AST is
constructed directly from public dataclasses rather than derived from a
parser result or a checked-in snapshot.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from pysysmlv2 import parse, parse_as_ast_node
from pysysmlv2.syntax.ast import (
    ActionBody,
    AttributeUsage,
    Definition,
    DefinitionBody,
    DefinitionBodyItem,
    DefinitionDeclaration,
    DottedQualifiedReference,
    ExhibitStateUsage,
    FeatureSpecialization,
    FeatureSpecializationPart,
    Identification,
    OccurrenceDefinitionPrefix,
    OccurrenceUsagePrefix,
    OwnedFeatureTyping,
    PartDefinition,
    PerformActionUsage,
    PerformActionUsageDeclaration,
    PortUsage,
    QualifiedReference,
    StateUsageBody,
    Usage,
    UsageDeclaration,
    UsagePrefix,
)

pytestmark = pytest.mark.unit


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    ROOT
    / "test"
    / "testfile"
    / "omg_sysml2_language"
    / "manual"
    / "annex_a"
    / "a3_vehicle_definition.sysml"
)
LEDGER = ROOT / "docs" / "research" / "manual_pdf_review" / "annex_a_3_vehicle_definition.json"


def _entry() -> dict:
    """Load the repository-owned provenance record for the fixture."""
    payload = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert payload["scope"]["clause"] == "A.3 Definitions"
    assert payload["scope"]["printed_pages"] == [636, 637]
    assert payload["scope"]["physical_pages"] == [668, 669]
    assert len(payload["entries"]) == 1
    return payload["entries"][0]


ENTRY = _entry()


def _qualified(*segments: str) -> QualifiedReference:
    """Construct one unresolved qualified reference from explicit segments."""
    return QualifiedReference(list(segments))


def _owned_typing(*segments: str) -> OwnedFeatureTyping:
    """Construct an owned ``:`` typing from its qualified-name segments."""
    return OwnedFeatureTyping(DottedQualifiedReference([_qualified(*segments)]))


def _specialization(operator: str, *segments: str) -> FeatureSpecialization:
    """Construct one explicit feature-specialization relation."""
    reference = _owned_typing(*segments) if operator == ":" else _qualified(*segments)
    return FeatureSpecialization(operator, [reference])


def _usage_declaration(name: str, specialization: FeatureSpecialization) -> UsageDeclaration:
    """Construct a named usage declaration with one required specialization."""
    return UsageDeclaration(
        identification=Identification(declared_name=name),
        specialization=FeatureSpecializationPart([specialization]),
    )


def _attribute(name: str, operator: str, *segments: str) -> DefinitionBodyItem:
    """Construct one manually expected attribute body item."""
    return DefinitionBodyItem(
        element=AttributeUsage(
            usage_prefix=UsagePrefix(),
            usage=Usage(
                body=DefinitionBody(declaration_only=True),
                declaration=_usage_declaration(name, _specialization(operator, *segments)),
            ),
        )
    )


def _port(name: str, type_name: str) -> DefinitionBodyItem:
    """Construct one manually expected port body item."""
    return DefinitionBodyItem(
        element=PortUsage(
            occurrence_usage_prefix=OccurrenceUsagePrefix(),
            usage=Usage(
                body=DefinitionBody(declaration_only=True),
                declaration=_usage_declaration(name, _specialization(":", type_name)),
            ),
        )
    )


def _perform_action(name: str) -> DefinitionBodyItem:
    """Construct one manually expected performed action body item."""
    return DefinitionBodyItem(
        element=PerformActionUsage(
            occurrence_usage_prefix=OccurrenceUsagePrefix(),
            declaration=PerformActionUsageDeclaration(
                action_usage_declaration=UsageDeclaration(
                    identification=Identification(declared_name=name)
                ),
                is_action=True,
            ),
            body=ActionBody(declaration_only=True),
        )
    )


def _expected_vehicle() -> PartDefinition:
    """Build the full field-level AST expected for the Annex A.3 Vehicle block."""
    items: List[DefinitionBodyItem] = [
        _attribute("mass", ":>", "ISQ", "mass"),
        _attribute("dryMass", ":>", "ISQ", "mass"),
        _attribute("cargoMass", ":>", "ISQ", "mass"),
        _attribute("position", ":>", "ISQ", "length"),
        _attribute("velocity", ":>", "ISQ", "speed"),
        _attribute("acceleration", ":>", "ISQ", "acceleration"),
        _attribute("electricalPower", ":>", "ISQ", "power"),
        _attribute("Tmax", ":>", "ISQ", "temperature"),
        _attribute("maintenanceTime", ":", "Time", "DateTime"),
        _attribute("brakePedalDepressed", ":", "Boolean"),
        _port("ignitionCmdPort", "IgnitionCmdPort"),
        _port("pwrCmdPort", "PwrCmdPort"),
        _port("vehicleToRoadPort", "VehicleToRoadPort"),
        _perform_action("providePower"),
        _perform_action("provideBraking"),
        _perform_action("controlDirection"),
        _perform_action("performSelfTest"),
        _perform_action("applyParkingBrake"),
        _perform_action("senseTemperature"),
        DefinitionBodyItem(
            element=ExhibitStateUsage(
                occurrence_usage_prefix=OccurrenceUsagePrefix(),
                state_usage_body=StateUsageBody(is_declaration_only=True),
                state_usage_declaration=UsageDeclaration(
                    identification=Identification(declared_name="vehicleStates")
                ),
            )
        ),
    ]
    return PartDefinition(
        occurrence_definition_prefix=OccurrenceDefinitionPrefix(),
        definition=Definition(
            declaration=DefinitionDeclaration(
                identification=Identification(declared_name="Vehicle")
            ),
            body=DefinitionBody(items=items),
        ),
    )


def test_annex_a_vehicle_fixture_matches_the_visual_review_ledger() -> None:
    """Keep the checked-in Annex A.3 source equal to its local ledger."""
    assert FIXTURE.read_text(encoding="utf-8") == ENTRY["source_code"] + "\n"


def test_annex_a_vehicle_source_matches_the_handwritten_full_field_ast() -> None:
    """Compare every non-span AST field with the direct dataclass oracle."""
    actual = parse_as_ast_node(FIXTURE.read_text(encoding="utf-8"), "partDefinition")
    assert actual == _expected_vehicle()


def test_annex_a_vehicle_model_round_trips_after_canonical_formatting() -> None:
    """Ensure the complete Annex A.3 source reparses after AST export."""
    source = FIXTURE.read_text(encoding="utf-8")
    first = parse(source, str(FIXTURE))
    assert first.ok, first.diagnostics
    exported = str(first.ast)
    second = parse(exported, "annex-a-roundtrip.sysml")
    assert second.ok, second.diagnostics
    assert first.ast == second.ast
    assert str(second.ast) == exported
