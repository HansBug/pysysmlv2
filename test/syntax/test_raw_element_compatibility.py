"""Audit the deliberately private ``RawElement`` compatibility boundary."""

import ast as python_ast
import inspect
import json
import re
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Optional

import pytest

from pysysmlv2 import parse, parse_as_ast_node
from pysysmlv2.syntax import (
    ActorMember,
    ActorUsage,
    BindingConnectorAsUsage,
    BooleanLiteral,
    CalculationBody,
    ConcernFramedConcernUsage,
    ConnectorEnd,
    ConstraintRequirementConstraintUsage,
    ConstraintUsageDeclaration,
    DefinitionBody,
    DottedQualifiedReference,
    FeatureSpecialization,
    FeatureSpecializationPart,
    FramedConcernMember,
    Identification,
    Model,
    ObjectiveMember,
    ObjectiveRequirementUsage,
    OwnedFeatureTyping,
    Package,
    PackageMember,
    QualifiedReference,
    RawElement,
    ReferenceFramedConcernUsage,
    ReferenceRequirementConstraintUsage,
    ReferenceRequirementVerificationUsage,
    RequirementBody,
    RequirementConstraintMember,
    RequirementVerificationMember,
    RequirementVerificationRequirementUsage,
    ResultExpressionMember,
    StakeholderMember,
    StakeholderUsage,
    SubjectMember,
    SubjectUsage,
    SuccessionAsUsage,
    Usage,
    UsageDeclaration,
    UsagePrefix,
)
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
    """Require one auditable record for every listener raw-store callback."""
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
    grammar = (ROOT / "pysysmlv2" / "syntax" / "generated" / "SysMLv2Parser.g4").read_text(
        encoding="utf-8"
    )
    productions = {
        match.group(1) for match in re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9_]*)\s*$", grammar)
    }
    assert {entry["production"] for entry in entries} <= productions
    assert all(entry["production"] in source for entry in entries)
    assert all(entry["reason"] and entry["follow_up"] and entry["test"] for entry in entries)
    for entry in entries:
        test_file, separator, test_name = entry["test"].partition("::")
        assert separator == "::"
        test_path = ROOT / test_file
        assert test_path.is_file(), entry["test"]
        test_tree = python_ast.parse(test_path.read_text(encoding="utf-8"))
        test_names = {
            node.name
            for node in test_tree.body
            if isinstance(node, (python_ast.FunctionDef, python_ast.AsyncFunctionDef))
        }
        assert test_name in test_names, entry["test"]


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


def test_core_view_paths_are_typed():
    """View expose, rendering, and filter alternatives stay structured."""
    result = parse(
        "package Demo { view V { expose A::**; render asTreeDiagram; expose A::**[@Safety]; } }"
    )
    assert result.ok, result.diagnostics
    assert list(_walk(result.ast)) == []


def test_core_non_occurrence_paths_are_typed():
    """Supported attribute/reference/enum usage dispatchers stay typed."""
    result = parse("package Demo { attribute a; ref attribute r; enum E { one; } }")
    assert result.ok, result.diagnostics
    assert list(_walk(result.ast)) == []


@pytest.mark.parametrize(
    ("source", "grammar_node", "expected"),
    [
        pytest.param(
            "subject s;",
            "subjectMember",
            SubjectMember(
                SubjectUsage(
                    Usage(
                        body=DefinitionBody(declaration_only=True),
                        declaration=UsageDeclaration(Identification(declared_name="s")),
                    )
                )
            ),
            id="subject",
        ),
        pytest.param(
            "subject;",
            "subjectMember",
            SubjectMember(
                SubjectUsage(
                    Usage(body=DefinitionBody(declaration_only=True)),
                )
            ),
            id="subject-bare",
        ),
        pytest.param(
            "actor a;",
            "actorMember",
            ActorMember(
                ActorUsage(
                    Usage(
                        body=DefinitionBody(declaration_only=True),
                        declaration=UsageDeclaration(Identification(declared_name="a")),
                    )
                )
            ),
            id="actor",
        ),
        pytest.param(
            "actor;",
            "actorMember",
            ActorMember(
                ActorUsage(
                    Usage(body=DefinitionBody(declaration_only=True)),
                ),
            ),
            id="actor-bare",
        ),
        pytest.param(
            "stakeholder h;",
            "stakeholderMember",
            StakeholderMember(
                StakeholderUsage(
                    Usage(
                        body=DefinitionBody(declaration_only=True),
                        declaration=UsageDeclaration(Identification(declared_name="h")),
                    )
                )
            ),
            id="stakeholder",
        ),
        pytest.param(
            "stakeholder;",
            "stakeholderMember",
            StakeholderMember(
                StakeholderUsage(
                    Usage(body=DefinitionBody(declaration_only=True)),
                )
            ),
            id="stakeholder-bare",
        ),
        pytest.param(
            "assume constraint { }",
            "requirementConstraintMember",
            RequirementConstraintMember(
                kind="assume",
                requirement_constraint_usage=ConstraintRequirementConstraintUsage(
                    constraint_usage_declaration=ConstraintUsageDeclaration(),
                    calculation_body=CalculationBody(),
                ),
            ),
            id="assume-constraint",
        ),
        pytest.param(
            "frame concern C { }",
            "framedConcernMember",
            FramedConcernMember(
                framed_concern_usage=ConcernFramedConcernUsage(
                    constraint_usage_declaration=ConstraintUsageDeclaration(
                        usage_declaration=UsageDeclaration(
                            identification=Identification(declared_name="C")
                        )
                    ),
                    requirement_body=RequirementBody(),
                )
            ),
            id="frame-concern",
        ),
        pytest.param(
            "objective O { }",
            "objectiveMember",
            ObjectiveMember(
                objective_requirement_usage=ObjectiveRequirementUsage(
                    constraint_usage_declaration=ConstraintUsageDeclaration(
                        usage_declaration=UsageDeclaration(
                            identification=Identification(declared_name="O")
                        )
                    ),
                    requirement_body=RequirementBody(),
                )
            ),
            id="objective",
        ),
        pytest.param(
            "verify requirement V { }",
            "requirementVerificationMember",
            RequirementVerificationMember(
                requirement_verification_usage=RequirementVerificationRequirementUsage(
                    constraint_usage_declaration=ConstraintUsageDeclaration(
                        usage_declaration=UsageDeclaration(
                            identification=Identification(declared_name="V")
                        )
                    ),
                    requirement_body=RequirementBody(),
                )
            ),
            id="verify-requirement",
        ),
        pytest.param(
            "public subject #Meta s;",
            "subjectMember",
            SubjectMember(
                SubjectUsage(
                    Usage(
                        body=DefinitionBody(declaration_only=True),
                        declaration=UsageDeclaration(Identification(declared_name="s")),
                    ),
                    extension_keywords=["#Meta"],
                ),
                member_prefix="public",
            ),
            id="subject-extension-and-visibility",
        ),
        pytest.param(
            "assume x :> Y { }",
            "requirementConstraintMember",
            RequirementConstraintMember(
                kind="assume",
                requirement_constraint_usage=ReferenceRequirementConstraintUsage(
                    reference_subsetting=QualifiedReference(["x"]),
                    specialization=FeatureSpecializationPart(
                        [FeatureSpecialization(":>", [QualifiedReference(["Y"])])]
                    ),
                    requirement_body=RequirementBody(),
                ),
            ),
            id="assume-reference",
        ),
        pytest.param(
            "assume #Meta x { }",
            "requirementConstraintMember",
            RequirementConstraintMember(
                kind="assume",
                requirement_constraint_usage=ConstraintRequirementConstraintUsage(
                    constraint_usage_declaration=ConstraintUsageDeclaration(
                        usage_declaration=UsageDeclaration(
                            identification=Identification(declared_name="x")
                        )
                    ),
                    calculation_body=CalculationBody(),
                    extension_keywords=["#Meta"],
                    has_constraint_keyword=False,
                ),
            ),
            id="assume-extension",
        ),
        pytest.param(
            "frame x :> Y { }",
            "framedConcernMember",
            FramedConcernMember(
                framed_concern_usage=ReferenceFramedConcernUsage(
                    reference_subsetting=QualifiedReference(["x"]),
                    specialization=FeatureSpecializationPart(
                        [FeatureSpecialization(":>", [QualifiedReference(["Y"])])]
                    ),
                    requirement_body=RequirementBody(),
                )
            ),
            id="frame-reference",
        ),
        pytest.param(
            "frame #Meta C { }",
            "framedConcernMember",
            FramedConcernMember(
                framed_concern_usage=ConcernFramedConcernUsage(
                    constraint_usage_declaration=ConstraintUsageDeclaration(
                        usage_declaration=UsageDeclaration(
                            identification=Identification(declared_name="C")
                        )
                    ),
                    requirement_body=RequirementBody(),
                    extension_keywords=["#Meta"],
                    has_concern_keyword=False,
                )
            ),
            id="frame-extension",
        ),
        pytest.param(
            "objective #Meta O { }",
            "objectiveMember",
            ObjectiveMember(
                objective_requirement_usage=ObjectiveRequirementUsage(
                    constraint_usage_declaration=ConstraintUsageDeclaration(
                        usage_declaration=UsageDeclaration(
                            identification=Identification(declared_name="O")
                        )
                    ),
                    requirement_body=RequirementBody(),
                    extension_keywords=["#Meta"],
                )
            ),
            id="objective-extension",
        ),
        pytest.param(
            "verify x :> Y { }",
            "requirementVerificationMember",
            RequirementVerificationMember(
                requirement_verification_usage=ReferenceRequirementVerificationUsage(
                    reference_subsetting=QualifiedReference(["x"]),
                    specializations=[FeatureSpecialization(":>", [QualifiedReference(["Y"])])],
                    requirement_body=RequirementBody(),
                )
            ),
            id="verify-reference",
        ),
        pytest.param(
            "verify #Meta V { }",
            "requirementVerificationMember",
            RequirementVerificationMember(
                requirement_verification_usage=RequirementVerificationRequirementUsage(
                    constraint_usage_declaration=ConstraintUsageDeclaration(
                        usage_declaration=UsageDeclaration(
                            identification=Identification(declared_name="V")
                        )
                    ),
                    requirement_body=RequirementBody(),
                    extension_keywords=["#Meta"],
                    has_requirement_keyword=False,
                )
            ),
            id="verify-extension",
        ),
    ],
)
def test_requirement_relationship_nodes_are_field_exact_and_round_trip(
    source, grammar_node, expected
):
    """Assert relationship productions are typed without a raw fallback."""
    fragment = parse_as_ast_node(source, grammar_node=grammar_node)
    assert fragment == expected
    assert str(fragment) == source
    assert parse_as_ast_node(str(fragment), grammar_node=grammar_node) == expected


def _typed_connector_end(name: str) -> ConnectorEnd:
    """Build the expected connector-end field for a minimal oracle."""
    return ConnectorEnd(QualifiedReference([name]))


def _named_usage_declaration(name: str, type_name: Optional[str] = None) -> UsageDeclaration:
    """Build an exact optional declaration used by full connector forms."""
    specialization = None
    if type_name is not None:
        specialization = FeatureSpecializationPart(
            [
                FeatureSpecialization(
                    ":",
                    [
                        OwnedFeatureTyping(
                            DottedQualifiedReference([QualifiedReference([type_name])])
                        )
                    ],
                )
            ]
        )
    return UsageDeclaration(Identification(declared_name=name), specialization)


@pytest.mark.parametrize(
    ("source", "grammar_node", "expected"),
    [
        pytest.param(
            "bind a = b;",
            "bindingConnectorAsUsage",
            BindingConnectorAsUsage(
                UsagePrefix(),
                _typed_connector_end("a"),
                _typed_connector_end("b"),
                DefinitionBody(declaration_only=True),
            ),
            id="binding-shorthand",
        ),
        pytest.param(
            "binding ab bind a = b;",
            "bindingConnectorAsUsage",
            BindingConnectorAsUsage(
                UsagePrefix(),
                _typed_connector_end("a"),
                _typed_connector_end("b"),
                DefinitionBody(declaration_only=True),
                usage_declaration=_named_usage_declaration("ab"),
                has_binding_keyword=True,
            ),
            id="binding-named",
        ),
        pytest.param(
            "binding ab1 : AB bind a = b;",
            "bindingConnectorAsUsage",
            BindingConnectorAsUsage(
                UsagePrefix(),
                _typed_connector_end("a"),
                _typed_connector_end("b"),
                DefinitionBody(declaration_only=True),
                usage_declaration=_named_usage_declaration("ab1", "AB"),
                has_binding_keyword=True,
            ),
            id="binding-specialized",
        ),
        pytest.param(
            "first a then b;",
            "successionAsUsage",
            SuccessionAsUsage(
                UsagePrefix(),
                _typed_connector_end("a"),
                _typed_connector_end("b"),
                DefinitionBody(declaration_only=True),
            ),
            id="succession-shorthand",
        ),
        pytest.param(
            "succession s first a then b;",
            "successionAsUsage",
            SuccessionAsUsage(
                UsagePrefix(),
                _typed_connector_end("a"),
                _typed_connector_end("b"),
                DefinitionBody(declaration_only=True),
                usage_declaration=_named_usage_declaration("s"),
                has_succession_keyword=True,
            ),
            id="succession-named",
        ),
        pytest.param(
            "succession s1 : AB first a then b;",
            "successionAsUsage",
            SuccessionAsUsage(
                UsagePrefix(),
                _typed_connector_end("a"),
                _typed_connector_end("b"),
                DefinitionBody(declaration_only=True),
                usage_declaration=_named_usage_declaration("s1", "AB"),
                has_succession_keyword=True,
            ),
            id="succession-specialized",
        ),
    ],
)
def test_binding_and_succession_are_field_exact_and_round_trip(source, grammar_node, expected):
    """Assert every field of both connector productions and their dispatch."""
    fragment = parse_as_ast_node(source, grammar_node=grammar_node)
    assert fragment == expected
    assert str(fragment) == source
    assert parse_as_ast_node(str(fragment), grammar_node=grammar_node) == expected

    result = parse("package Demo { " + source + " }")
    assert result.ok, result.diagnostics
    assert result.ast == Model(
        members=[
            PackageMember(
                Package(
                    identification=Identification(declared_name="Demo"),
                    members=[PackageMember(expected)],
                )
            )
        ]
    )
    assert list(_walk(result.ast)) == []


def test_core_definition_paths_are_typed():
    """Keep common definition dispatchers out of the raw compatibility path."""
    result = parse("package Demo { item def Vehicle; state def State; }")
    assert result.ok, result.diagnostics
    assert list(_walk(result.ast)) == []


def test_ledger_does_not_claim_target_guard_first_support():
    """The deferred raw boundary must not reintroduce the removed target order."""
    text = LEDGER.read_text(encoding="utf-8")
    removed_overlay = "target-" + "transition-" + "trigger-guard-order"
    assert removed_overlay not in text
    assert "guard_before_trigger" not in text


def test_requirement_ast_bodies_render_each_optional_form():
    """Keep body and result-expression rendering parseable in isolation."""
    assert str(CalculationBody(declaration_only=True)) == ";"
    result_body = CalculationBody(
        result_expression_member=ResultExpressionMember(BooleanLiteral("true"))
    )
    assert str(result_body) == "{\n    true\n}"
    assert parse_as_ast_node(str(result_body), grammar_node="calculationBody") == result_body
