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
from pysysmlv2.syntax import ast as ast_module

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
    assert [item.name for item in fields(ASTNode)] == ["span"]
    assert not hasattr(ASTNode, "children")
    with pytest.raises(NotImplementedError):
        ASTNode().to_sysml()
    with pytest.raises(NotImplementedError):
        str(ASTNode())


def test_source_path_is_owned_only_by_source_span():
    ast_node_types = [
        value
        for value in vars(ast_module).values()
        if isinstance(value, type) and issubclass(value, ASTNode)
    ]
    assert all(
        "source_path" not in {item.name for item in fields(node_type)}
        for node_type in ast_node_types
    )
    assert [item.name for item in fields(SourceSpan)][-1] == "source_path"


def test_ast_default_equality_ignores_span_provenance():
    first = ASTNode()
    first.span = SourceSpan(1, 1, 1, 4, "demo.sysml")
    second = ASTNode()
    second.span = SourceSpan(2, 1, 2, 4, "other.sysml")
    assert first == second


def test_concrete_grammar_fields_are_required_and_span_is_optional():
    parameters = signature(StateDefinition).parameters
    assert parameters["occurrence_definition_prefix"].default is Parameter.empty
    assert parameters["definition_declaration"].default is Parameter.empty
    assert parameters["state_def_body"].default is Parameter.empty
    state = _element(_package(parse("package Demo { state def Mode; }")))
    assert isinstance(state, StateDefinition)
    assert state.span is not None
    assert state.span.source_path is None


def test_parser_returns_explicit_package_and_state_definition_fields():
    result = parse("package Demo { state def Mode; }", "demo.sysml")
    assert result.ok
    assert isinstance(result.ast, Model)
    package = _package(result)
    state_definition = _element(package)
    assert isinstance(state_definition, StateDefinition)
    assert state_definition.definition_declaration.identification.declared_name == "Mode"
    assert state_definition.span.source_path == "demo.sysml"
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


def test_entry_transition_preserves_its_structured_guard_expression():
    source = "package Demo { state def S { entry; if g then T; } }"
    state_definition = _element(_package(parse(source)))
    entry = state_definition.state_def_body.state_body_members[0]
    assert entry.entry_transition_members[0].guard.reference.segments == ["g"]
    assert str(entry) == "entry; if g then T;"
    assert parse(str(parse(source).ast)).ok


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


def test_ast_concrete_exporters_cover_optional_and_prefix_alternatives():
    """Exercise handwritten exporters that are not selected by the smoke corpus."""
    a = ast_module

    def ref(name):
        return a.QualifiedReference([name])

    literal = a.BooleanLiteral("true")

    assert str(a.Identification(short_name="short")) == "<short>"
    assert str(a.ConjugatedPortTyping(ref("FuelPort"))) == "~FuelPort"

    declared_typing = a.DeclaredFeatureTyping(
        ref("feature"),
        ":",
        ref("Type"),
        a.RelationshipBody(";"),
        is_specialization=True,
        identification=a.Identification(declared_name="typingRelation"),
    )
    assert str(declared_typing) == "specialization typingRelation typing feature : Type;"
    assert (
        str(
            a.NonFeatureMember(
                a.OwnedFeatureTyping(a.DottedQualifiedReference([ref("T")])), "private"
            )
        )
        == "private T"
    )

    assert (
        str(
            a.OccurrenceUsagePrefix(
                is_derived=True,
                is_constant=True,
                extension_keywords=["variation"],
            )
        )
        == "derived constant variation"
    )
    assert (
        str(
            a.ControlNodePrefix(
                feature_direction="in",
                is_derived=True,
                is_abstract=True,
                is_variation=True,
                is_constant=True,
                is_individual=True,
                portion_kind="snapshot",
                extension_keywords=["readonly"],
            )
        )
        == "in derived abstract variation constant individual snapshot readonly"
    )

    assert str(a.RealLiteral("1.25")) == "1.25"
    assert str(a.InfinityLiteral()) == "*"
    assert str(a.CoalesceExpression(literal, a.IntegerLiteral("0"))) == "true ?? 0"
    assert (
        str(a.ConditionalExpression(literal, a.StringLiteral('"yes"'), a.NullExpression()))
        == 'if true ? "yes" else null'
    )
    assert str(a.TypeOperationExpression("@", ref("Meta"))) == "@Meta"
    assert str(a.TypeOperationExpression("hastype", ref("Type"), literal)) == "true hastype Type"
    assert str(a.CastExpression(a.IntegerLiteral("1"), ref("Integer"))) == "1 as Integer"
    assert str(a.MetadataAccessExpression(ref("model"))) == "model.metadata"
    assert str(a.MetadataCastExpression(ref("Metadata"))) == "(as Metadata)"
    assert str(a.AllExpression(ref("Vehicle"))) == "all Vehicle"

    assert (
        str(a.ReturnFeatureMember(a.RawElement(": Boolean;"), "public"))
        == "public return : Boolean;"
    )
    assert str(a.CommentExpression("/* note */")) == "/* note */"
    end_item = a.ItemUsage(a.OccurrenceUsagePrefix(), a.Usage(a.DefinitionBody(True)))
    assert str(a.EndOccurrenceUsageElement(end_item, "endName", "[1]", True)) == (
        "end endName [1] nonunique item;"
    )

    succession = a.TransitionSuccession(ref("Run"))
    assert str(a.TargetSuccession(succession, "Idle")) == "Idle then Run"
    guarded_target = a.GuardedTargetSuccession(a.GuardExpressionMember(literal), succession)
    assert str(guarded_target) == "if true then Run"
    assert str(a.DefaultTargetSuccession(succession)) == "else Run"
    action_target = a.ActionTargetSuccession(a.TargetSuccession(succession), a.DefinitionBody(True))
    assert str(action_target) == "then Run;"
    assert str(a.ActionTargetSuccessionMember(action_target, "protected")) == "protected then Run;"

    assert (
        str(
            a.PerformActionUsageDeclaration(
                action_usage_declaration=a.UsageDeclaration(
                    a.Identification(declared_name="Effect")
                ),
            )
        )
        == "Effect"
    )
    with pytest.raises(ValueError, match="payloadParameter requires"):
        a.PayloadParameter()

    declaration = a.PerformActionUsageDeclaration(
        action_usage_declaration=a.UsageDeclaration(a.Identification(declared_name="Effect")),
    )
    assert str(a.TransitionPerformActionUsage(declaration, a.ActionBody())) == "Effect { }"
    accept = a.AcceptNodeDeclaration(
        a.AcceptParameterPart(a.PayloadParameter(trigger_expression=literal))
    )
    assert str(a.AcceptActionUsage(accept, a.ActionBody())) == "accept true { }"
    assert str(a.StateSubactionMembership(a.StateSubactionKind.ENTRY)) == "entry;"

    assert (
        str(a.Package(a.Identification(declared_name="Lib"), is_library=True, is_standard=True))
        == "standard library package Lib { }"
    )
    assert a.structural_text(a.RealLiteral("3.0")) == "3.0"


def test_ast_exporters_cover_remaining_optional_rendering_branches():
    """Exercise the final concrete exporter choices and source indentation path."""
    a = ast_module

    def ref(name):
        return a.QualifiedReference([name])

    assert a._relative_source("one\n  two") == "one\ntwo"
    assert a._relative_source("one") == "one"
    assert str(a.Identification(short_name="s", declared_name="State")) == "<s> State"
    assert (
        str(
            a.FeatureSpecializationPart(
                [a.FeatureSpecialization("subsets", [ref("Base")])], multiplicity_text="[1]"
            )
        )
        == "subsets Base [1]"
    )
    assert str(a.OccurrenceDefinitionPrefix("part", is_individual=True)) == "part individual"
    assert (
        str(a.OccurrenceUsagePrefix(is_abstract=True, portion_kind="snapshot"))
        == "abstract snapshot"
    )
    assert str(a.PerformActionUsageDeclaration(referenced_feature=ref("Effect"))) == "Effect"
    assert str(a.TransitionPerformActionUsage(a.PerformActionUsageDeclaration())) == ""


def test_expression_precedence_handles_conditional_and_coalesce_nodes():
    """Cover precedence lookup for the two non-binary expression subclasses."""
    a = ast_module
    reference = a.FeatureReferenceExpression(a.QualifiedReference(["value"]))
    assert a._expression_precedence(a.CoalesceExpression(reference, reference)) == 2
    assert a._expression_precedence(a.ConditionalExpression(reference, reference, reference)) == 1


def test_new_usage_nodes_cover_optional_prefix_and_completion_rendering():
    """Exercise optional typed-node exporter alternatives explicitly."""
    a = ast_module
    assert (
        str(
            a.UsagePrefix(
                is_abstract=True,
                is_variation=True,
                is_constant=True,
            )
        )
        == "abstract variation constant"
    )

    prefix = a.OccurrenceUsagePrefix()
    declaration = a.Definition(
        a.DefinitionDeclaration(),
        a.DefinitionBody(declaration_only=True),
    )
    usage = a.Usage(a.DefinitionBody(declaration_only=True))
    assert str(a.PartDefinition(prefix, declaration)) == "part def;"
    assert str(a.OccurrenceDefinition(prefix, declaration)) == "occurrence def;"
    assert str(a.IndividualDefinition(None, [], declaration)) == "individual def;"
    assert str(a.AttributeDefinition(a.DefinitionPrefix(), declaration)) == "attribute def;"
    assert str(a.AttributeUsage(a.UsagePrefix(), usage)) == "attribute;"
    assert str(a.PortUsage(prefix, usage)) == "port;"
    assert (
        str(
            a.PortDefinition(
                a.DefinitionPrefix(),
                declaration,
                a.ConjugatedPortTyping(a.QualifiedReference(["P"])),
            )
        )
        == "port def; ~P"
    )

    block_usage = a.Usage(a.DefinitionBody())
    assert str(a.EventOccurrenceUsage(prefix, block_usage)) == "event { }"
    payload_usage = a.Usage(a.RawElement("value"))
    assert str(a.EventOccurrenceUsage(prefix, payload_usage)) == "event value"
