"""Regression tests for the explicit, round-trippable SysML source AST."""

from dataclasses import fields
from inspect import Parameter, signature

import pytest

from pysysmlv2 import parse, parse_as_ast_node
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


def test_feature_declaration_keeps_relationship_productions_typed_and_round_trippable():
    """Compare every feature relationship alternative as a full AST value."""
    q = ast_module.QualifiedReference

    def dotted(*parts):
        """Build one dotted reference expected by the relation nodes."""
        return ast_module.DottedQualifiedReference([q([part]) for part in parts])

    cases = [
        (
            "a ~ B.C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                conjugation_part=ast_module.ConjugationPart("~", dotted("B", "C")),
            ),
        ),
        (
            "a conjugates B.C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                conjugation_part=ast_module.ConjugationPart("conjugates", dotted("B", "C")),
            ),
        ),
        (
            "a chains B.C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                relationship_parts=[ast_module.ChainingPart([q(["B"]), q(["C"])])],
            ),
        ),
        (
            "a inverse of B.C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                relationship_parts=[ast_module.InvertingPart(dotted("B", "C"))],
            ),
        ),
        (
            "a featured by B, C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                relationship_parts=[ast_module.TypeFeaturingPart([q(["B"]), q(["C"])])],
            ),
        ),
        (
            "a disjoint from B.C, C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                relationship_parts=[ast_module.DisjoiningPart([dotted("B", "C"), dotted("C")])],
            ),
        ),
        (
            "a unions B.C, C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                relationship_parts=[ast_module.UnioningPart([dotted("B", "C"), dotted("C")])],
            ),
        ),
        (
            "a intersects B.C, C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                relationship_parts=[ast_module.IntersectingPart([dotted("B", "C"), dotted("C")])],
            ),
        ),
        (
            "a differences B.C, C",
            ast_module.FeatureDeclaration(
                identification=ast_module.FeatureIdentification(declared_name="a"),
                relationship_parts=[ast_module.DifferencingPart([dotted("B", "C"), dotted("C")])],
            ),
        ),
    ]
    for source, expected in cases:
        actual = parse_as_ast_node(source, grammar_node="featureDeclaration")
        assert actual == expected
        rendered = str(actual)
        assert parse_as_ast_node(rendered, grammar_node="featureDeclaration") == expected


def test_source_span_contains_child_and_keeps_source_path():
    span = SourceSpan(1, 1, 1, 20, "demo.sysml")
    assert span.contains(SourceSpan(1, 2, 1, 5, "demo.sysml"))
    assert not span.contains(SourceSpan(1, 2, 1, 5, "other.sysml"))
    assert span.contains(SourceSpan(1, 2, 1, 5))
    assert span.source_path == "demo.sysml"


def test_source_span_contains_uses_known_paths_and_allows_unknown_paths():
    """Compare paths when available without rejecting partially annotated spans."""
    known = SourceSpan(1, 1, 3, 1, "demo.sysml")
    unknown = SourceSpan(1, 1, 3, 1)
    other = SourceSpan(1, 2, 2, 4, "other.sysml")
    assert known.contains(unknown)
    assert unknown.contains(known)
    assert not known.contains(other)


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


def test_view_rendering_usage_round_trips_reference_target():
    """Render a view rendering reference and its declaration-only body."""
    node = ast_module.ViewRenderingUsage(
        body=ast_module.DefinitionBody(declaration_only=True),
        reference=ast_module.QualifiedReference(["View"]),
    )
    assert node.usage is None
    assert str(node) == "View;"


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
    derived_conjugate = a.PortDefinition(
        a.DefinitionPrefix(),
        declaration,
        a.ConjugatedPortTyping(a.QualifiedReference(["P"])),
    )
    assert str(derived_conjugate) == "port def;"
    assert parse("package P { " + str(derived_conjugate) + " }").ok

    block_usage = a.Usage(a.DefinitionBody())
    assert str(a.EventOccurrenceUsage(prefix, block_usage)) == "event { }"
    payload_usage = a.Usage(a.RawElement("value"))
    assert str(a.EventOccurrenceUsage(prefix, payload_usage)) == "event value"


@pytest.mark.parametrize(
    ("source", "grammar_node"),
    [
        ("part def;", "partDefinition"),
        ("part def {}", "partDefinition"),
        ("occurrence def;", "occurrenceDefinition"),
        ("occurrence def {}", "occurrenceDefinition"),
        ("port def;", "portDefinition"),
        ("port def {}", "portDefinition"),
        ("attribute def;", "attributeDefinition"),
        ("attribute def {}", "attributeDefinition"),
        ("part;", "partUsage"),
        ("part {}", "partUsage"),
        ("occurrence;", "occurrenceUsage"),
        ("occurrence {}", "occurrenceUsage"),
        ("port;", "portUsage"),
        ("port {}", "portUsage"),
        ("attribute;", "attributeUsage"),
        ("attribute {}", "attributeUsage"),
    ],
)
def test_anonymous_definition_and_usage_forms_round_trip(source, grammar_node):
    """Keep anonymous semicolon and brace completions source-parseable."""
    del grammar_node  # The root parser is the supported entry for these families.
    node = _element(_package(parse("package P { " + source + " }")))
    rendered = str(node)
    reparsed = _element(_package(parse("package P { " + rendered + " }")))
    assert reparsed == node
    assert parse("package P { " + rendered + " }").ok


def test_connection_and_interface_ast_nodes_render_every_explicit_alternative():
    """Exercise the complete connection/interface AST exporter surface."""
    a = ast_module
    reference = a.QualifiedReference(["Port"])
    specialization = a.FeatureSpecializationPart()

    assert str(a.FeatureIdentification("short", "Long")) == "<short> Long"
    assert str(a.FeatureIdentification("short")) == "<short>"
    assert str(a.FeatureIdentification()) == ""
    feature = a.FeatureDeclaration(
        identification=a.FeatureIdentification(declared_name="end"),
        specialization=specialization,
        is_all=True,
        conjugation_part=a.ConjugationPart(
            "~",
            a.DottedQualifiedReference([a.QualifiedReference(["Port"])]),
        ),
        relationship_parts=[
            a.ChainingPart([a.QualifiedReference(["Source"]), a.QualifiedReference(["Target"])]),
        ],
    )
    assert str(feature) == "all end ~ Port chains Source.Target"

    cross = a.OwnedCrossFeature(
        basic_feature_prefix="ref",
        feature_declaration=feature,
        basic_usage_prefix=a.UsagePrefix(feature_direction="in"),
        usage_declaration=a.UsageDeclaration(a.Identification(declared_name="usage")),
    )
    assert str(a.OwnedCrossFeature()) == ""
    assert str(a.EndUsagePrefix(cross)).startswith("end ref")
    usage = a.Usage(a.DefinitionBody(declaration_only=True))
    assert str(a.EndFeatureUsage(a.EndUsagePrefix(cross), feature, usage)).endswith(";")

    connector_a = a.ConnectorEnd(reference, "[1]", "source", "::>")
    connector_b = a.ConnectorEnd(a.QualifiedReference(["Target"]), name="target")
    binary_connector = a.BinaryConnectorPart(connector_a, connector_b)
    nary_connector = a.NaryConnectorPart([connector_a, connector_b])
    assert str(binary_connector) == "[1] source ::> Port to target Target"
    assert str(nary_connector) == "([1] source ::> Port, target Target)"

    definition = a.Definition(
        a.DefinitionDeclaration(a.Identification(declared_name="C")),
        a.DefinitionBody(declaration_only=True),
    )
    assert str(a.ConnectionDefinition(a.OccurrenceDefinitionPrefix(), definition)) == (
        "connection def C;"
    )
    named_connection = a.ConnectionUsage(
        a.OccurrenceUsagePrefix(),
        a.DefinitionBody(declaration_only=True),
        usage_declaration=a.UsageDeclaration(a.Identification(declared_name="c")),
        connector_part=binary_connector,
    )
    shorthand_connection = a.ConnectionUsage(
        a.OccurrenceUsagePrefix(),
        a.DefinitionBody(declaration_only=True),
        connector_part=nary_connector,
        has_connection_keyword=False,
    )
    assert str(named_connection) == "connection c connect [1] source ::> Port to target Target;"
    assert str(shorthand_connection) == "connect ([1] source ::> Port, target Target);"
    assert (
        str(a.ConnectionUsage(a.OccurrenceUsagePrefix(), a.DefinitionBody(True))) == "connection;"
    )

    interface_a = a.InterfaceEnd(reference, "[1]", "source", "references")
    interface_b = a.InterfaceEnd(a.QualifiedReference(["Target"]), name="target")
    binary_interface = a.BinaryInterfacePart(interface_a, interface_b)
    nary_interface = a.NaryInterfacePart([interface_a, interface_b])
    assert str(binary_interface) == "[1] source references Port to target Target"
    assert str(nary_interface) == "([1] source references Port, target Target)"
    interface_body = a.InterfaceBody(
        items=[a.InterfaceNonOccurrenceUsageMember(a.RawElement("attribute a;"), "private")]
    )
    assert "private attribute a;" in str(interface_body)
    assert str(a.InterfaceBody(declaration_only=True)) == ";"
    assert str(a.DefaultInterfaceEnd(usage)) == "end;"
    occurrence_member = a.InterfaceOccurrenceUsageMember(
        a.RawElement("part p;"), "public", a.SourceSuccession()
    )
    assert str(occurrence_member) == "then public part p;"
    assert str(a.InterfaceOccurrenceUsageMember(a.RawElement("part p;"))) == "part p;"
    assert str(a.InterfaceNonOccurrenceUsageMember(a.RawElement("attribute a;"))) == (
        "attribute a;"
    )
    assert str(a.VariantUsageMember(a.RawElement("part p;"), "private")) == (
        "private variant part p;"
    )

    connected_declaration = a.InterfaceUsageDeclaration(
        usage_declaration=a.UsageDeclaration(a.Identification(declared_name="i")),
        interface_part=binary_interface,
        has_connect_keyword=True,
    )
    direct_declaration = a.InterfaceUsageDeclaration(interface_part=nary_interface)
    assert str(connected_declaration) == ("i connect [1] source references Port to target Target")
    assert str(direct_declaration) == "([1] source references Port, target Target)"
    assert str(a.InterfaceUsageDeclaration()) == ""
    assert (
        str(
            a.InterfaceDefinition(
                a.OccurrenceDefinitionPrefix(),
                a.DefinitionDeclaration(a.Identification(declared_name="I")),
                a.InterfaceBody(declaration_only=True),
            )
        )
        == "interface def I;"
    )
    assert (
        str(
            a.InterfaceUsage(
                a.OccurrenceUsagePrefix(),
                connected_declaration,
                a.InterfaceBody(declaration_only=True),
            )
        )
        == "interface i connect [1] source references Port to target Target;"
    )
