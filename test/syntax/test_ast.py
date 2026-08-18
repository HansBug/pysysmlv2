"""Regression tests for the explicit, round-trippable SysML source AST."""

from dataclasses import fields
from inspect import Parameter, signature

import pytest

from pysysmlv2 import parse
from pysysmlv2.syntax import (
    ActionNodeMember,
    ActionUsageNode,
    ASTNode,
    BinaryExpression,
    Comment,
    Expression,
    MergeNode,
    Model,
    Package,
    PackageMember,
    PartDefinition,
    SendActionUsage,
    SourceSpan,
    StateDefinition,
    StateUsage,
    TransitionUsage,
    TransitionUsageMember,
)

pytestmark = pytest.mark.unit


def _package(result):
    """Return the first package element from a parsed model."""
    member = result.ast.members[0]
    assert isinstance(member, PackageMember)
    assert isinstance(member.element, Package)
    return member.element


def _element(package, index=0):
    """Return one typed package child."""
    member = package.members[index]
    assert isinstance(member, PackageMember)
    return member.element


def test_source_span_contains_child_and_keeps_source_path():
    span = SourceSpan(1, 1, 1, 20, "demo.sysml")
    assert span.contains(SourceSpan(1, 2, 1, 5, "demo.sysml"))
    assert span.source_path == "demo.sysml"


def test_ast_base_only_carries_provenance_and_requires_concrete_exporter():
    assert [item.name for item in fields(ASTNode)] == ["source_path", "span"]
    assert not hasattr(ASTNode, "children")
    with pytest.raises(NotImplementedError):
        ASTNode().to_sysml()
    with pytest.raises(NotImplementedError):
        str(ASTNode())


def test_concrete_grammar_fields_are_required_and_span_is_optional():
    parameters = signature(StateDefinition).parameters
    assert parameters["occurrence_definition_prefix"].default is Parameter.empty
    assert parameters["definition_declaration"].default is Parameter.empty
    assert parameters["state_def_body"].default is Parameter.empty
    state = _element(_package(parse("package Demo { state def Mode; }")))
    assert isinstance(state, StateDefinition)
    assert state.span is not None
    assert state.source_path is None


def test_parser_returns_explicit_package_and_state_definition_fields():
    result = parse("package Demo { state def Mode; }", "demo.sysml")
    assert result.ok
    assert isinstance(result.ast, Model)
    package = _package(result)
    state_definition = _element(package)
    assert isinstance(state_definition, StateDefinition)
    assert state_definition.definition_declaration.identification.declared_name == "Mode"
    assert state_definition.source_path == "demo.sysml"
    assert state_definition.span.line == 1


def test_state_body_keeps_explicit_entry_do_and_exit_memberships():
    source = "package Demo { state def Mode { entry ; do ; exit ; } }"
    state_definition = _element(_package(parse(source)))
    assert isinstance(state_definition, StateDefinition)
    assert [type(item).__name__ for item in state_definition.state_def_body.state_body_members] == [
        "EntryActionMember",
        "DoActionMember",
        "ExitActionMember",
    ]
    assert str(state_definition) == "state def Mode {\n    entry;\n    do;\n    exit;\n}"
    assert parse(str(state_definition)).ok


def test_state_usage_is_a_typed_package_member_and_round_trips():
    result = parse("package Demo { state Idle; }")
    state_usage = _element(_package(result))
    assert isinstance(state_usage, StateUsage)
    assert (
        state_usage.action_usage_declaration.usage_declaration.identification.declared_name
        == "Idle"
    )
    assert str(state_usage) == "state Idle;"
    assert parse(str(result.ast)).ok


def test_transition_usage_exposes_source_declaration_and_target_fields():
    source = "package Demo { state def S { transition T first Idle then Run; } }"
    state = _element(_package(parse(source)))
    transition_member = state.state_def_body.state_body_members[0]
    assert isinstance(transition_member, TransitionUsageMember)
    transition = transition_member.transition_usage
    assert isinstance(transition, TransitionUsage)
    assert transition.usage_declaration.identification.declared_name == "T"
    assert transition.is_first is True
    assert transition.source_feature_chain.qualified_names[0].segments == ["Idle"]
    assert transition.transition_succession_member.connector_end.segments == ["Run"]
    assert str(transition) == "transition T first Idle then Run;"
    assert parse(str(parse(source).ast)).ok


def test_expression_nodes_use_expression_intermediate_type():
    source = "package Demo { state def S { transition T first Idle if x + 1 then Run; } }"
    state = _element(_package(parse(source)))
    transition = state.state_def_body.state_body_members[0].transition_usage
    expression = transition.guard_expression_member.owned_expression
    assert isinstance(expression, Expression)
    assert isinstance(expression, BinaryExpression)
    assert all(item.name != "source_text" for item in fields(type(expression)))
    assert parse(str(parse(source).ast)).ok


def test_action_nodes_are_typed_statement_subclasses():
    source = "package Demo { action A { merge m; accept E; send x; assign x := y; terminate; } }"
    action = _element(_package(parse(source)))
    items = action.body.items
    assert all(isinstance(item, ActionNodeMember) for item in items)
    assert isinstance(items[0].action_node, MergeNode)
    assert {type(item.action_node).__name__ for item in items} == {
        "MergeNode",
        "AcceptNode",
        "SendNode",
        "AssignmentNode",
        "TerminateNode",
    }
    rendered = str(parse(source).ast)
    assert parse(rendered).ok


def test_action_usage_variants_are_exported_and_typed():
    source = "package Demo { state def S { entry send x; } }"
    state = _element(_package(parse(source)))
    action = state.state_def_body.state_body_members[0].state_action_usage
    assert isinstance(action, SendActionUsage)
    assert isinstance(action, ActionUsageNode)


def test_state_can_be_found_inside_structured_part_definition():
    package = _package(parse("package Demo { part def Vehicle { state def Mode; } }"))
    part = _element(package)
    assert isinstance(part, PartDefinition)
    nested = part.definition.body.items[0].element
    assert isinstance(nested, StateDefinition)
    assert parse(str(parse("package Demo { part def Vehicle { state def Mode; } ").ast)).ok


def test_model_owned_comment_remains_a_typed_node():
    result = parse("/* A note */ package Demo { }")
    assert result.ok
    package_member = result.ast.members[0]
    assert isinstance(package_member, PackageMember)
    assert isinstance(package_member.element, Comment)
    assert "/* A note */" in str(result.ast)


def test_multiple_top_level_packages_are_not_dropped():
    result = parse("package A { } package B { }")
    rendered = str(result.ast)
    assert result.ok
    assert [item.element.identification.declared_name for item in result.ast.members] == ["A", "B"]
    assert parse(rendered).ok
