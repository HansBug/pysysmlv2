"""Unit tests for the ANTLR parser adapter."""

from dataclasses import fields

import pytest

from pysysmlv2.syntax import (
    ArgumentList,
    ASTParseError,
    BinaryExpression,
    BodyExpression,
    BracketExpression,
    ConjugatedPortTyping,
    Definition,
    DefinitionBody,
    DefinitionBodyItem,
    DefinitionDeclaration,
    DottedQualifiedReference,
    EndOccurrenceUsageElement,
    FeatureChainExpression,
    FeatureReferenceExpression,
    FeatureSpecialization,
    FunctionOperationExpression,
    Identification,
    IndexExpression,
    IntegerLiteral,
    ItemUsage,
    NonFeatureMember,
    OccurrenceDefinitionPrefix,
    OccurrenceUsagePrefix,
    OwnedFeatureTyping,
    PackageMember,
    PartDefinition,
    QualifiedReference,
    RawElement,
    ResultExpressionMember,
    ReturnFeatureMember,
    SelectExpression,
    SequenceExpression,
    StateDefBody,
    StateDefinition,
    TargetTransitionUsage,
    UnaryExpression,
    Usage,
    UsageDeclaration,
    parse,
    parse_as_ast_node,
    supported_grammar_entries,
)

pytestmark = pytest.mark.unit


def test_valid_package_has_no_diagnostics():
    result = parse("package Demo { part def Vehicle; }", "demo.sysml")
    assert result.ok
    assert result.diagnostics == []
    assert "package Demo" in str(result.ast)


def test_invalid_package_reports_structured_diagnostic():
    result = parse("package Demo {", "demo.sysml")
    assert not result.ok
    assert result.diagnostics[0].source_path == "demo.sysml"
    assert result.diagnostics[0].line == 1
    assert result.diagnostics[0].column > 0


def test_parser_diagnostic_ranges_are_one_based_and_eof_is_zero_width():
    """Use one-based exclusive ends for real tokens and zero-width EOFs."""
    token = parse("package Demo { part def X }").diagnostics[0]
    assert (token.line, token.column, token.end_line, token.end_column) == (1, 27, 1, 28)
    eof = parse("package Demo {").diagnostics[0]
    assert eof.end_column == eof.column


def test_ast_export_can_be_parsed_again():
    first = parse("package Demo { part def Vehicle; }")
    second = parse(str(first.ast))
    assert first.ok and second.ok
    assert str(second.ast) == str(first.ast)


def test_target_transition_shorthand_keeps_only_normative_orders():
    """Accept target trigger-before-guard and guard-only forms, not guard-first."""
    source = (
        "package Demo { state def S { state A; accept E if enabled then A; if enabled then A; } }"
    )
    result = parse(source, "target-orders.sysml")
    assert result.ok, result.diagnostics
    package = result.ast.members[0].element
    state = package.members[0].element
    target_nodes = [
        target.target_transition_usage
        for member in state.state_def_body.state_body_members
        for target in getattr(member, "target_transition_members", [])
    ]
    assert len(target_nodes) == 2
    assert all(isinstance(node, TargetTransitionUsage) for node in target_nodes)
    assert all(item.name != "guard_before_trigger" for item in fields(TargetTransitionUsage))
    exported = str(result.ast)
    assert "accept E if enabled then A;" in exported
    assert "if enabled then A;" in exported
    assert parse(exported, "target-orders-roundtrip.sysml").ok


def test_target_guard_first_is_rejected_but_full_transition_guard_first_remains_valid():
    """Keep target shorthand strict while retaining full transition ordering."""
    target = parse("package Demo { state def S { state A; if enabled accept E then A; } }")
    assert not target.ok
    assert target.diagnostics

    full = parse(
        "package Demo { state def S { state A; transition t first A if enabled accept E then A; } }"
    )
    assert full.ok, full.diagnostics
    package = full.ast.members[0].element
    state = package.members[0].element
    transition = state.state_def_body.state_body_members[-1].transition_usage
    assert transition.guard_before_trigger is True
    assert "if enabled accept E then A;" in str(full.ast)


def test_model_comment_before_package_survives_export():
    result = parse("/* note */ package Demo { }")
    assert result.ok
    assert "/* note */" in str(result.ast)
    assert parse(str(result.ast)).ok


def test_individual_definition_prefix_does_not_render_epsilon_as_multiplicity():
    source = "package Demo { individual part def Vehicle; }"
    first = parse(source, "individual.sysml")
    exported = str(first.ast)
    second = parse(exported, "individual-roundtrip.sysml")
    assert first.ok and second.ok
    assert "[]" not in exported
    assert str(second.ast) == exported


def test_send_routing_and_perform_action_preserve_their_concrete_choices():
    source = (
        "package Demo { action A { send payload via channel; "
        "send new M() to target; perform action B; } }"
    )
    first = parse(source, "routing.sysml")
    exported = str(first.ast)
    second = parse(exported, "routing-roundtrip.sysml")
    assert first.ok and second.ok
    assert "send payload via channel;" in exported
    assert "send new M() to target;" in exported
    assert "perform action B;" in exported
    assert "send payload() via channel;" not in exported
    assert "to;" not in exported
    assert str(second.ast) == exported


def test_bare_loop_and_assignment_target_binding_round_trip_without_epsilon_tokens():
    source = "package Demo { action A { loop { assign a.b := value; } until done; } }"
    first = parse(source, "control.sysml")
    assert first.ok
    exported = str(first.ast)
    assert "loop {" in exported
    assert "loop ()" not in exported
    assert "assign a.b := value;" in exported
    second = parse(exported, "control-roundtrip.sysml")
    assert second.ok
    assert str(second.ast) == exported


def test_function_reference_arrow_preserves_required_separator():
    source = "values -> reduce(result)"
    first = parse_as_ast_node(source, grammar_node="ownedExpression")
    exported = str(first)
    assert "-> reduce(result)" in exported
    second = parse_as_ast_node(exported, grammar_node="ownedExpression")
    assert second == first


def test_function_reference_arrow_body_has_a_pretty_separator():
    """Keep a space between an arrow member and its brace body."""
    node = parse_as_ast_node("x -> f { y }", grammar_node="ownedExpression")
    exported = str(node)
    assert "x -> f {" in exported
    assert parse_as_ast_node(exported, grammar_node="ownedExpression") == node


def test_dotted_owned_feature_typing_preserves_namespace_separators():
    source = "package Demo { part def C { attribute x : A::B.C::D; } }"
    first = parse(source, "qualified.sysml")
    assert first.ok
    exported = str(first.ast)
    assert ": A::B.C::D;" in exported
    second = parse(exported, "qualified-roundtrip.sysml")
    assert second.ok
    assert str(second.ast) == exported


@pytest.mark.parametrize("operator", ["subsets", "references", "crosses", "redefines"])
def test_dotted_specialization_preserves_each_qualified_name(operator):
    """Keep ``::`` namespace separators across a grammar-level dot."""
    source = "part p {} A::B.C::D;".format(operator)
    node = parse_as_ast_node(source, grammar_node="partUsage")
    expected = DottedQualifiedReference(
        [QualifiedReference(["A", "B"]), QualifiedReference(["C", "D"])]
    )
    reference = node.usage.declaration.specialization.specializations[0].references[0]
    assert reference == expected
    assert str(node) == source
    assert parse_as_ast_node(str(node), grammar_node="partUsage") == node


def test_dotted_transition_endpoint_preserves_each_qualified_name():
    """Keep dotted transition endpoints structured for later linking."""
    source = "transition A::B.C::D then E::F.G::H;"
    node = parse_as_ast_node(source, grammar_node="transitionUsage")
    expected = DottedQualifiedReference(
        [QualifiedReference(["E", "F"]), QualifiedReference(["G", "H"])]
    )
    assert node.transition_succession_member.connector_end == expected
    assert str(node) == source
    assert parse_as_ast_node(str(node), grammar_node="transitionUsage") == node


def test_model_owned_comment_preserves_its_annotation_targets():
    result = parse("comment about A, B /* note */", "comment.sysml")
    assert result.ok
    comment = result.ast.members[0]
    assert isinstance(comment, PackageMember)
    assert [item.segments for item in comment.element.about] == [["A"], ["B"]]
    assert str(result.ast) == "comment about A, B /* note */"


@pytest.mark.parametrize(
    ("source", "grammar_node", "expected"),
    [
        pytest.param(
            "A and B",
            "ownedExpression",
            BinaryExpression(
                FeatureReferenceExpression(QualifiedReference(["A"])),
                "and",
                FeatureReferenceExpression(QualifiedReference(["B"])),
            ),
            id="owned-expression",
        ),
        pytest.param(
            "~FuelPort",
            "featureTyping",
            ConjugatedPortTyping(QualifiedReference(["FuelPort"])),
            id="conjugated-port-typing",
        ),
        pytest.param(
            ": ~FuelPort",
            "typings",
            FeatureSpecialization(
                ":",
                [ConjugatedPortTyping(QualifiedReference(["FuelPort"]))],
            ),
            id="typing-specialization-with-conjugated-port",
        ),
        pytest.param(
            "state def S;",
            "stateDefinition",
            StateDefinition(
                OccurrenceDefinitionPrefix(),
                DefinitionDeclaration(Identification(declared_name="S")),
                StateDefBody(is_parallel=False, is_declaration_only=True),
            ),
            id="state-definition",
        ),
        pytest.param(
            "part def Vehicle;",
            "partDefinition",
            PartDefinition(
                OccurrenceDefinitionPrefix(),
                Definition(
                    DefinitionDeclaration(Identification(declared_name="Vehicle")),
                    DefinitionBody(declaration_only=True),
                ),
            ),
            id="part-definition",
        ),
        pytest.param(
            "end named [0..1] nonunique item cart;",
            "definitionBodyItem",
            DefinitionBodyItem(
                EndOccurrenceUsageElement(
                    occurrence_usage=ItemUsage(
                        OccurrenceUsagePrefix(),
                        Usage(
                            DefinitionBody(declaration_only=True),
                            UsageDeclaration(Identification(declared_name="cart")),
                        ),
                    ),
                    name="named",
                    cross_multiplicity_text="[0..1]",
                    is_nonunique=True,
                )
            ),
            id="end-item-usage",
        ),
        pytest.param(
            "S;",
            "definition",
            Definition(
                DefinitionDeclaration(Identification(declared_name="S")),
                DefinitionBody(declaration_only=True),
            ),
            id="generic-definition",
        ),
        pytest.param(
            "{ a + b }",
            "bodyExpression",
            BodyExpression(
                [
                    NonFeatureMember(
                        OwnedFeatureTyping(DottedQualifiedReference([QualifiedReference(["a"])]))
                    ),
                    ResultExpressionMember(
                        UnaryExpression(
                            "+",
                            FeatureReferenceExpression(QualifiedReference(["b"])),
                        )
                    ),
                ]
            ),
            id="body-expression-with-typed-member",
        ),
        pytest.param(
            "{ return : Boolean; }",
            "bodyExpression",
            BodyExpression([ReturnFeatureMember(RawElement(": Boolean;"))]),
            id="body-expression-with-return-feature",
        ),
    ],
)
def test_parse_as_ast_node_builds_the_expected_concrete_node(source, grammar_node, expected):
    assert parse_as_ast_node(source, grammar_node=grammar_node) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            "x#(1)",
            IndexExpression(
                FeatureReferenceExpression(QualifiedReference(["x"])),
                ArgumentList(positional_arguments=[IntegerLiteral("1")]),
            ),
            id="index-expression",
        ),
        pytest.param(
            "x[1]",
            BracketExpression(
                FeatureReferenceExpression(QualifiedReference(["x"])),
                SequenceExpression([IntegerLiteral("1")]),
            ),
            id="bracket-expression",
        ),
        pytest.param(
            "x.y",
            FeatureChainExpression(
                FeatureReferenceExpression(QualifiedReference(["x"])),
                QualifiedReference(["y"]),
            ),
            id="feature-chain-expression",
        ),
        pytest.param(
            "x.?{1}",
            SelectExpression(
                FeatureReferenceExpression(QualifiedReference(["x"])),
                BodyExpression([ResultExpressionMember(IntegerLiteral("1"))]),
            ),
            id="select-expression",
        ),
        pytest.param(
            "x -> collect(1)",
            FunctionOperationExpression(
                FeatureReferenceExpression(QualifiedReference(["x"])),
                QualifiedReference(["collect"]),
                ArgumentList(positional_arguments=[IntegerLiteral("1")]),
            ),
            id="function-operation-expression",
        ),
    ],
)
def test_primary_expression_forms_keep_their_omg_concrete_syntax_choice(source, expected):
    first = parse_as_ast_node(source, grammar_node="ownedExpression")
    assert first == expected
    assert parse_as_ast_node(str(first), grammar_node="ownedExpression") == expected


def test_parse_as_ast_node_attaches_source_provenance_without_affecting_equality():
    node = parse_as_ast_node("A and B", grammar_node="ownedExpression", source_path="expr.sysml")
    assert node.span.source_path == "expr.sysml"
    assert not hasattr(node, "source_path")
    assert node == parse_as_ast_node("A and B", grammar_node="ownedExpression")


def test_parse_as_ast_node_requires_a_valid_fully_consumed_fragment():
    with pytest.raises(ASTParseError) as malformed:
        parse_as_ast_node("A and", grammar_node="ownedExpression", source_path="expr.sysml")
    assert malformed.value.diagnostics[0].source_path == "expr.sysml"

    with pytest.raises(ASTParseError) as trailing:
        parse_as_ast_node("A B", grammar_node="ownedExpression")
    assert trailing.value.diagnostics[0].message == "parser did not consume the full input"


def test_supported_grammar_entries_only_expose_explicit_ast_mappings():
    entries = supported_grammar_entries()
    assert entries == sorted(entries)
    assert {"ownedExpression", "partDefinition", "stateDefinition"} <= set(entries)
    assert "typeBodyElement" not in entries
