"""Direct listener conformance tests for every supported syntax family.

The parser tests exercise complete documents.  This module deliberately uses
the public local grammar-entry API as well, so each handwritten listener
alternative is visited in isolation and its concrete AST can be round-tripped
without relying on an upstream checkout or an external fixture.
"""

import pytest

from pysysmlv2 import parse, parse_as_ast_node
from pysysmlv2.syntax import ast
from pysysmlv2.syntax.ast import (
    ActionNode,
    ActionNodeUsageDeclaration,
    AllExpression,
    ArgumentList,
    BinaryExpression,
    BodyExpression,
    BooleanLiteral,
    BracketExpression,
    CastExpression,
    CoalesceExpression,
    Comment,
    ConjugatedPortTyping,
    ConstructorExpression,
    Documentation,
    FeatureChainExpression,
    FeatureReferenceExpression,
    FunctionOperationExpression,
    IndexExpression,
    InfinityLiteral,
    IntegerLiteral,
    InvocationExpression,
    MetadataAccessExpression,
    MetadataCastExpression,
    NullExpression,
    OccurrenceUsagePrefix,
    OwnedFeatureTyping,
    ParenthesizedExpression,
    QualifiedReference,
    RealLiteral,
    RelationshipBody,
    ResultExpressionMember,
    SelectExpression,
    StringLiteral,
    TypeOperationExpression,
    UnaryExpression,
    ValuePart,
)
from pysysmlv2.syntax.listener import SysMLAstListener

pytestmark = pytest.mark.unit


class _FakeToken:
    """Minimal token double for listener-local defensive context tests."""

    def __init__(self, text="", token_index=0):
        self.text = text
        self.tokenIndex = token_index
        self.start = None
        self.stop = None

    def getText(self):
        """Return the token spelling expected by an ANTLR terminal."""
        return self.text


class _FakeContext:
    """Small context-shaped object used only to exercise impossible branches."""

    def __init__(self, text="", **values):
        self._context_text = text
        self.start = values.pop("start", None)
        self.stop = values.pop("stop", None)
        self._context_values = values

    def getText(self):
        """Return the supplied source spelling for listener text helpers."""
        return self._context_text

    def __getattr__(self, name):
        value = self._context_values.get(name)
        if callable(value):
            return value
        return lambda: value


def _fake_listener(*pairs, **children):
    """Return a listener whose child map contains ``context -> AST`` entries."""
    listener = SysMLAstListener("")
    listener.nodes.update(dict(pairs))
    listener.nodes.update(children)
    return listener


def _error(callback, context, *pairs, **children):
    """Assert that ``callback`` rejects an incomplete parser context."""
    with pytest.raises((ValueError, TypeError, AttributeError)):
        getattr(_fake_listener(*pairs, **children), callback)(context)


def _node(source, entry="ownedExpression"):
    """Parse one small child node for direct listener context tests."""
    return parse_as_ast_node(source, grammar_node=entry)


def test_listener_provenance_and_dispatch_guards():
    """Cover listener helper guards and the recovered-terminal callback."""
    listener = SysMLAstListener("")
    assert listener._token_text(None) == ""
    with pytest.raises(ValueError):
        listener._pass(_FakeContext(), _FakeContext())
    with pytest.raises(ValueError):
        listener._dotted_reference(_FakeContext(qualifiedName=[]))
    with pytest.raises(ValueError):
        listener._dotted_node(_FakeContext(qualifiedName=[]))
    with pytest.raises(ValueError):
        listener._source_items([_FakeContext()])
    assert listener._span(_FakeContext(start=_FakeToken(), stop=_FakeToken())) is None
    listener.visitErrorNode(object())


def test_listener_declared_typing_and_nonfeature_dispatch_contexts():
    """Exercise the explicit non-feature and declared-typing mappings."""
    listener = _fake_listener()
    owned = _node("A.B", "featureTyping")
    feature_typing = _FakeContext()
    listener.nodes[feature_typing] = owned
    non_feature_element = _FakeContext(featureTyping=feature_typing)
    listener.nodes[non_feature_element] = owned
    member_element = _FakeContext(nonFeatureElement=non_feature_element)
    listener.nodes[member_element] = owned

    listener.exitNonFeatureElement(non_feature_element)
    listener.exitMemberElement(member_element)
    non_feature_member = _FakeContext(memberElement=member_element, memberPrefix=_FakeContext())
    listener.exitNonFeatureMember(non_feature_member)

    # The dispatcher callbacks also have an intentional no-op path when the
    # parser selected an unsupported alternative.
    listener.exitNonFeatureElement(_FakeContext(featureTyping=None))
    listener.exitMemberElement(_FakeContext(nonFeatureElement=None))
    listener.exitNonFeatureMember(_FakeContext(memberElement=None))

    type_body = _FakeContext(nonFeatureMember=non_feature_member)
    listener.nodes[non_feature_member] = listener.node_for(non_feature_member)
    listener.exitTypeBodyElement(type_body)
    listener.exitTypeBodyElement(
        _FakeContext(nonFeatureMember=None, featureMember=None, aliasMember=None, importRule=None)
    )
    listener.exitTypeFeatureMember(_FakeContext())
    listener.exitOwnedFeatureMember(_FakeContext())
    _error("exitFeatureMember", _FakeContext())
    _error("exitFeatureReferenceExpression", _FakeContext(qualifiedName=None))
    _error("exitNonFeatureChainPrimaryExpression", _FakeContext(IDENTIFIER=None))


def test_listener_specialization_and_declared_feature_typing_contexts():
    """Cover explicit specialization operators and declared feature typing."""
    _error("exitFeatureSpecialization", _FakeContext())
    _error("exitConjugatedPortTyping", _FakeContext(qualifiedName=None))
    _error("exitGeneralType", _FakeContext(qualifiedName=[]))
    _error("exitFeatureTyping", _FakeContext())

    owned_ctx = _FakeContext()
    owned = _node("A.B", "featureTyping")
    typed_by_ctx = _FakeContext(featureTyping=owned_ctx, TYPED=_FakeToken())
    listener = _fake_listener((owned_ctx, owned))
    listener.exitTypings(_FakeContext(typedBy=typed_by_ctx, featureTyping=[]))

    defined_by_ctx = _FakeContext(featureTyping=owned_ctx, DEFINED=_FakeToken())
    listener.exitTypings(_FakeContext(typedBy=defined_by_ctx, featureTyping=[]))
    listener.exitTypings(_FakeContext(typedBy=typed_by_ctx, featureTyping=[owned_ctx]))
    listener.exitTypings(_FakeContext(typedBy=None, featureTyping=[]))

    typed_feature = _FakeContext()
    general_type = _FakeContext()
    body = _FakeContext()
    relationship = RelationshipBody(";")
    listener = _fake_listener(
        (typed_feature, _node("feature", "qualifiedName")),
        (general_type, _node("Type", "qualifiedName")),
        (body, relationship),
    )
    listener.exitFeatureTyping(
        _FakeContext(
            identification=None,
            qualifiedName=typed_feature,
            generalType=general_type,
            relationshipBody=body,
            ownedFeatureTyping=None,
            conjugatedPortTyping=None,
            COLON=_FakeToken(),
            SPECIALIZATION=None,
        )
    )
    _error(
        "exitFeatureTyping",
        _FakeContext(
            identification=None,
            qualifiedName=typed_feature,
            generalType=general_type,
            relationshipBody=body,
            ownedFeatureTyping=None,
            conjugatedPortTyping=None,
        ),
    )


def test_listener_expression_context_guards_and_optional_forms():
    """Cover expression alternatives that valid source cannot reach alone."""
    listener = _fake_listener()
    _error("exitLiteralExpression", _FakeContext())
    _error("exitConstructorExpression", _FakeContext(qualifiedName=None, argumentList=None))
    _error("exitFunctionBodyPart", _FakeContext(resultExpressionMember=_FakeContext()))
    _error("exitResultExpressionMember", _FakeContext(ownedExpression=_FakeContext()))
    _error("exitReturnFeatureMember", _FakeContext(featureElement=_FakeContext()))
    _error("exitSequenceExpressionList", _FakeContext(ownedExpression=[_FakeContext()]))
    _error("exitNamedArgument", _FakeContext(qualifiedName=None, ownedExpression=None))
    _error("exitArgumentExpressionMember", _FakeContext(ownedExpression=_FakeContext()))
    _error("exitFeatureValue", _FakeContext(ownedExpression=None))
    _error("exitValuePart", _FakeContext(featureValue=None))

    listener.exitBaseExpression(_FakeContext(REGULAR_COMMENT=_FakeToken("/* note */")))
    body_context = _FakeContext()
    listener.nodes[body_context] = _node("{ }", "bodyExpression")
    listener.exitBaseExpression(_FakeContext(bodyExpression=body_context))
    _error("exitBaseExpression", _FakeContext(AS=_FakeToken(), typeReference=None))

    reference_context = _FakeContext()
    argument_context = _FakeContext()
    listener = _fake_listener((reference_context, _node("A", "qualifiedName")))
    _error(
        "exitBaseExpression",
        _FakeContext(
            qualifiedName=reference_context,
            argumentList=argument_context,
            nullExpression=None,
            literalExpression=None,
            constructorExpression=None,
            bodyExpression=None,
        ),
        (reference_context, _node("A", "qualifiedName")),
    )
    metadata_context = _FakeContext()
    listener.nodes[metadata_context] = _node("A", "qualifiedName")
    listener.exitBaseExpression(
        _FakeContext(
            qualifiedName=metadata_context,
            METADATA=_FakeToken(),
            nullExpression=None,
            literalExpression=None,
            constructorExpression=None,
            bodyExpression=None,
        )
    )
    _error("exitBaseExpression", _FakeContext())

    operators = _fake_listener()
    assert operators._binary_operator(_FakeContext(QUESTION_QUESTION=_FakeToken())) == "??"

    expr_a = _node("A")
    expr_b = _node("B")
    expr_c = _node("C")
    first = _FakeContext()
    second = _FakeContext()
    third = _FakeContext()
    listener = _fake_listener((first, expr_a), (second, expr_b), (third, expr_c))
    listener.exitOwnedExpression(
        _FakeContext(IF=_FakeToken(), ownedExpression=[first, second, third])
    )

    toggle_calls = [0]

    def toggle_question_mark():
        toggle_calls[0] += 1
        return None if toggle_calls[0] == 1 else _FakeToken()

    left = _FakeContext()
    right = _FakeContext()
    listener = _fake_listener((left, expr_a), (right, expr_b))
    listener.exitOwnedExpression(
        _FakeContext(
            QUESTION_QUESTION=toggle_question_mark,
            ownedExpression=[left, right],
        )
    )

    type_context = _FakeContext()
    listener.nodes[type_context] = _node("T", "qualifiedName")
    listener.exitOwnedExpression(
        _FakeContext(
            ISTYPE=_FakeToken(),
            typeReference=type_context,
            ownedExpression=[left, right],
        )
    )
    listener.exitOwnedExpression(
        _FakeContext(
            AS=_FakeToken(),
            typeReference=type_context,
            ownedExpression=[left, right],
        )
    )
    _error("exitOwnedExpression", _FakeContext(PLUS=_FakeToken(), ownedExpression=[]))
    _error(
        "exitOwnedExpression",
        _FakeContext(ISTYPE=_FakeToken(), ownedExpression=[left], typeReference=None),
    )
    _error("exitOwnedExpression", _FakeContext(AT_SIGN=_FakeToken(), typeReference=None))
    _error(
        "exitOwnedExpression",
        _FakeContext(AS=_FakeToken(), ownedExpression=[left], typeReference=None),
    )
    _error("exitOwnedExpression", _FakeContext(ARROW=_FakeToken(), ownedExpression=[left]))
    arrow_member = _FakeContext()
    _error(
        "exitOwnedExpression",
        _FakeContext(ARROW=_FakeToken(), qualifiedName=arrow_member, ownedExpression=[left]),
    )
    arrow_result = _FakeContext()
    _error(
        "exitOwnedExpression",
        _FakeContext(
            ARROW=_FakeToken(),
            qualifiedName=type_context,
            argumentList=arrow_result,
            ownedExpression=[left],
        ),
        (type_context, _node("T", "qualifiedName")),
    )
    _error(
        "exitOwnedExpression",
        _FakeContext(argumentList=argument_context, ownedExpression=[left]),
    )
    _error(
        "exitOwnedExpression",
        _FakeContext(DOT=_FakeToken(), qualifiedName=arrow_member, ownedExpression=[left]),
    )
    _error(
        "exitOwnedExpression",
        _FakeContext(
            DOT_QUESTION=_FakeToken(), bodyExpression=arrow_result, ownedExpression=[left]
        ),
    )
    _error("exitOwnedExpression", _FakeContext(ALL=_FakeToken(), typeReference=None))
    _error("exitOwnedExpression", _FakeContext())

    for token_name in ("PLUS", "MINUS", "TILDE", "NOT"):
        _error(
            "exitOwnedExpression",
            _FakeContext(**{token_name: _FakeToken(), "ownedExpression": []}),
        )


def test_listener_expression_normal_callbacks_and_operator_tokens():
    """Cover successful listener branches for body, metadata, and operators."""
    listener = _fake_listener()
    type_child = _FakeContext()
    listener.nodes[type_child] = _node("T", "qualifiedName")
    body_child = _FakeContext()
    listener.nodes[body_child] = BodyExpression()
    listener.exitBaseExpression(_FakeContext(bodyExpression=body_child))
    listener.exitBaseExpression(_FakeContext(AS=_FakeToken(), typeReference=type_child))
    argument_child = _FakeContext()
    listener.nodes[argument_child] = ArgumentList()
    ref_child = _FakeContext()
    listener.nodes[ref_child] = _node("A", "qualifiedName")
    listener.exitBaseExpression(_FakeContext(qualifiedName=ref_child, argumentList=argument_child))
    listener.exitBaseExpression(_FakeContext(qualifiedName=ref_child, METADATA=_FakeToken()))

    expr_child = _FakeContext()
    listener.nodes[expr_child] = _node("A")
    prefix = _FakeContext()
    result_context = _FakeContext()
    listener.nodes[result_context] = ResultExpressionMember(_node("A"))
    listener.exitResultExpressionMember(
        _FakeContext(ownedExpression=expr_child, memberPrefix=prefix)
    )
    listener.exitFunctionBodyPart(
        _FakeContext(
            resultExpressionMember=result_context,
            definitionBodyItem=[],
            typeBodyElement=[],
            returnFeatureMember=[],
        )
    )
    _error(
        "exitFunctionBodyPart",
        _FakeContext(
            resultExpressionMember=result_context,
            definitionBodyItem=[],
            typeBodyElement=[],
            returnFeatureMember=[],
        ),
        (result_context, _node("A")),
    )
    raw_context = _FakeContext()
    listener.exitFeatureElement(raw_context)
    listener.nodes[raw_context] = listener.node_for(raw_context)
    listener.exitReturnFeatureMember(_FakeContext(featureElement=raw_context, memberPrefix=prefix))

    for name in (
        "IMPLIES",
        "EQ_EQ_EQ",
        "BANG_EQ_EQ",
        "PERCENT",
        "QUESTION_QUESTION",
        "HASTYPE",
        "AT_AT",
    ):
        assert listener._binary_operator(_FakeContext(**{name: _FakeToken()})) is not None

    left_context = _FakeContext()
    right_context = _FakeContext()
    listener = _fake_listener(
        (left_context, _node("A")),
        (right_context, _node("B")),
        (type_child, _node("T", "qualifiedName")),
        (ref_child, _node("f", "qualifiedName")),
        (argument_child, ArgumentList()),
        (body_child, BodyExpression()),
    )
    listener.exitOwnedExpression(
        _FakeContext(
            ISTYPE=_FakeToken(),
            typeReference=type_child,
            ownedExpression=[left_context, right_context],
        )
    )
    listener.exitOwnedExpression(
        _FakeContext(
            AS=_FakeToken(),
            typeReference=type_child,
            ownedExpression=[left_context, right_context],
        )
    )
    listener.exitOwnedExpression(
        _FakeContext(
            ARROW=_FakeToken(),
            qualifiedName=ref_child,
            argumentList=argument_child,
            ownedExpression=[left_context],
        )
    )
    listener.exitOwnedExpression(
        _FakeContext(
            argumentList=argument_child,
            ownedExpression=[left_context],
        )
    )
    listener.exitOwnedExpression(
        _FakeContext(
            DOT=_FakeToken(),
            qualifiedName=ref_child,
            ownedExpression=[left_context],
        )
    )
    listener.exitOwnedExpression(
        _FakeContext(
            DOT_QUESTION=_FakeToken(),
            bodyExpression=body_child,
            ownedExpression=[left_context],
        )
    )
    listener.exitOwnedExpression(
        _FakeContext(ALL=_FakeToken(), typeReference=type_child, ownedExpression=[])
    )

    default_expression = _FakeContext()
    listener.nodes[default_expression] = _node("A")
    listener.exitFeatureValue(
        _FakeContext(
            ownedExpression=default_expression,
            DEFAULT=_FakeToken(),
            COLON_EQ=_FakeToken(),
        )
    )


def test_listener_metadata_callbacks_cover_typed_and_defensive_paths():
    """Exercise metadata wrappers, alternatives, and validation branches."""
    listener = _fake_listener()

    owned_typing_context = _FakeContext()
    listener.nodes[owned_typing_context] = _node("A", "featureTyping")
    listener.exitPrefixMetadataUsage(_FakeContext(ownedFeatureTyping=owned_typing_context))
    _error(
        "exitPrefixMetadataMember",
        _FakeContext(prefixMetadataFeature=None, prefixMetadataUsage=None),
    )

    listener.exitMetadataFeatureDeclaration(
        _FakeContext(
            ownedFeatureTyping=owned_typing_context,
            identification=None,
            COLON=None,
            TYPED=_FakeToken(),
        )
    )
    _error(
        "exitMetadataFeatureDeclaration",
        _FakeContext(ownedFeatureTyping=_FakeContext(), identification=None),
    )
    invalid_identification = _FakeContext()
    listener.nodes[invalid_identification] = ast.RawElement("bad identification")
    _error(
        "exitMetadataFeatureDeclaration",
        _FakeContext(
            ownedFeatureTyping=owned_typing_context,
            identification=invalid_identification,
            COLON=None,
            TYPED=None,
        ),
        (owned_typing_context, listener.node_for(owned_typing_context)),
        (invalid_identification, ast.RawElement("bad identification")),
    )

    incomplete_metadata_body = _FakeContext(
        SEMI=None,
        metadataBodyElement=[_FakeContext()],
        definitionMember=[],
        metadataBodyUsageMember=[],
        aliasMember=[],
        importRule=[],
    )
    incomplete_metadata_body.children = []
    _error("exitMetadataBody", incomplete_metadata_body)
    _error(
        "exitMetadataBodyElement",
        _FakeContext(
            nonFeatureMember=None,
            metadataBodyFeatureMember=None,
            aliasMember=None,
            importRule=None,
        ),
    )

    reference_context = _FakeContext()
    body_context = _FakeContext()
    listener.nodes[reference_context] = QualifiedReference(["A"])
    listener.nodes[body_context] = ast.MetadataBody(declaration_only=True)
    _error(
        "exitMetadataBodyFeature",
        _FakeContext(
            ownedRedefinition=None,
            metadataBody=body_context,
            featureSpecializationPart=None,
            valuePart=None,
        ),
        (body_context, ast.MetadataBody(declaration_only=True)),
    )
    bad_specialization = _FakeContext()
    listener.nodes[bad_specialization] = ast.RawElement("bad specialization")
    _error(
        "exitMetadataBodyFeature",
        _FakeContext(
            ownedRedefinition=reference_context,
            metadataBody=body_context,
            featureSpecializationPart=bad_specialization,
            valuePart=None,
        ),
        (reference_context, QualifiedReference(["A"])),
        (body_context, ast.MetadataBody(declaration_only=True)),
        (bad_specialization, ast.RawElement("bad specialization")),
    )
    bad_value = _FakeContext()
    listener.nodes[bad_value] = ast.RawElement("bad value")
    _error(
        "exitMetadataBodyFeature",
        _FakeContext(
            ownedRedefinition=reference_context,
            metadataBody=body_context,
            featureSpecializationPart=None,
            valuePart=bad_value,
        ),
        (reference_context, QualifiedReference(["A"])),
        (body_context, ast.MetadataBody(declaration_only=True)),
        (bad_value, ast.RawElement("bad value")),
    )

    _error(
        "exitMetadataBodyUsage",
        _FakeContext(
            ownedRedefinition=None,
            metadataBody=None,
            featureSpecializationPart=None,
            valuePart=None,
        ),
    )
    _error(
        "exitMetadataBodyUsage",
        _FakeContext(
            ownedRedefinition=reference_context,
            metadataBody=body_context,
            featureSpecializationPart=bad_specialization,
            valuePart=None,
        ),
        (reference_context, QualifiedReference(["A"])),
        (body_context, ast.MetadataBody(declaration_only=True)),
        (bad_specialization, ast.RawElement("bad specialization")),
    )
    _error(
        "exitMetadataBodyUsage",
        _FakeContext(
            ownedRedefinition=reference_context,
            metadataBody=body_context,
            featureSpecializationPart=None,
            valuePart=bad_value,
        ),
        (reference_context, QualifiedReference(["A"])),
        (body_context, ast.MetadataBody(declaration_only=True)),
        (bad_value, ast.RawElement("bad value")),
    )

    declaration_context = _FakeContext()
    body_context = _FakeContext()
    listener.nodes[declaration_context] = ast.MetadataFeatureDeclaration(
        listener.node_for(owned_typing_context)
    )
    listener.nodes[body_context] = ast.MetadataBody(declaration_only=True)
    _error(
        "exitMetadataFeature",
        _FakeContext(
            metadataFeatureDeclaration=None,
            metadataBody=body_context,
            prefixMetadataMember=[],
            annotation=[],
        ),
        (body_context, ast.MetadataBody(declaration_only=True)),
    )
    bad_prefix = _FakeContext()
    listener.nodes[bad_prefix] = ast.RawElement("bad prefix")
    _error(
        "exitMetadataFeature",
        _FakeContext(
            metadataFeatureDeclaration=declaration_context,
            metadataBody=body_context,
            prefixMetadataMember=[bad_prefix],
            annotation=[],
        ),
        (declaration_context, listener.node_for(declaration_context)),
        (body_context, ast.MetadataBody(declaration_only=True)),
        (bad_prefix, ast.RawElement("bad prefix")),
    )
    bad_annotation = _FakeContext()
    listener.nodes[bad_annotation] = ast.RawElement("bad annotation")
    _error(
        "exitMetadataFeature",
        _FakeContext(
            metadataFeatureDeclaration=declaration_context,
            metadataBody=body_context,
            prefixMetadataMember=[],
            annotation=[bad_annotation],
        ),
        (declaration_context, listener.node_for(declaration_context)),
        (body_context, ast.MetadataBody(declaration_only=True)),
        (bad_annotation, ast.RawElement("bad annotation")),
    )


def test_listener_action_and_succession_validation_paths():
    """Exercise action-node, succession, and state-action callback guards."""
    error_callbacks = [
        "exitActionBodyItem",
        "exitActionNodePrefix",
        "exitControlNode",
        "exitMergeNode",
        "exitDecisionNode",
        "exitJoinNode",
        "exitForkNode",
        "exitAcceptNode",
        "exitSendNode",
        "exitAssignmentNode",
        "exitTerminateNode",
        "exitActionBodyParameter",
        "exitIfNode",
        "exitWhileLoopNode",
        "exitForLoopNode",
        "exitActionBehaviorMember",
        "exitActionNodeMember",
        "exitActionNode",
        "exitInitialNodeMember",
        "exitTargetSuccession",
        "exitGuardedTargetSuccession",
        "exitDefaultTargetSuccession",
        "exitActionTargetSuccession",
        "exitActionTargetSuccessionMember",
        "exitGuardedSuccession",
        "exitGuardedSuccessionMember",
        "exitStateActionUsage",
        "exitStatePerformActionUsage",
        "exitStateAcceptActionUsage",
        "exitStateSendActionUsage",
        "exitStateAssignmentActionUsage",
        "exitPayloadFeature",
        "exitNodeParameter",
        "exitAcceptParameterPart",
        "exitTriggerExpression",
        "exitAcceptNodeDeclaration",
        "exitSendNodeDeclaration",
        "exitAssignmentNodeDeclaration",
        "exitActionUsage",
        "exitPerformActionUsage",
        "exitActionDefinition",
        "exitEntryActionMember",
        "exitDoActionMember",
        "exitExitActionMember",
        "exitEntryTransitionMember",
        "exitTriggerActionMember",
        "exitGuardExpressionMember",
        "exitEffectBehaviorMember",
        "exitEffectBehaviorUsage",
        "exitTransitionPerformActionUsage",
        "exitTransitionAcceptActionUsage",
        "exitTransitionSendActionUsage",
        "exitTransitionAssignmentActionUsage",
        "exitTransitionSuccession",
        "exitConnectorEnd",
        "exitTransitionUsage",
        "exitTransitionUsageMember",
        "exitTargetTransitionUsage",
        "exitTargetTransitionUsageMember",
        "exitBehaviorUsageMember",
        "exitStateBodyItem",
        "exitStateDefinition",
        "exitStateUsage",
        "exitExhibitStateUsage",
    ]
    for callback in error_callbacks:
        _error(callback, _FakeContext())

    # Prefix and dispatcher successful branches are kept explicit in the test.
    ref_prefix = _FakeContext(featureDirection=_FakeContext("in"))
    prefix = _FakeContext(refPrefix=ref_prefix, usageExtensionKeyword=[])
    listener = SysMLAstListener("in")
    listener.exitControlNodePrefix(prefix)
    usage_prefix_context = _FakeContext()
    listener.nodes[usage_prefix_context] = OccurrenceUsagePrefix()
    action_decl_context = _FakeContext()
    listener.nodes[action_decl_context] = ActionNodeUsageDeclaration()
    listener.exitActionNodePrefix(
        _FakeContext(
            occurrenceUsagePrefix=usage_prefix_context,
            actionNodeUsageDeclaration=action_decl_context,
        )
    )
    child_context = _FakeContext()
    listener.nodes[child_context] = _node("A", "qualifiedName")
    listener.exitActionBehaviorMember(_FakeContext(actionNodeMember=child_context))
    listener.exitActionNode(_FakeContext(controlNode=child_context))


@pytest.mark.parametrize(
    ("source", "node_type"),
    [
        ("true", BooleanLiteral),
        ('"text"', StringLiteral),
        ("1", IntegerLiteral),
        ("1.5", RealLiteral),
        ("*", InfinityLiteral),
        ("null", NullExpression),
        ("()", NullExpression),
        ("A", FeatureReferenceExpression),
        ("A()", InvocationExpression),
        ("A.metadata", MetadataAccessExpression),
        ("new A()", ConstructorExpression),
        ("{ }", BodyExpression),
        ("(as T)", MetadataCastExpression),
        ("(A, B)", ParenthesizedExpression),
        ("+A", UnaryExpression),
        ("-A", UnaryExpression),
        ("~A", UnaryExpression),
        ("not A", UnaryExpression),
        ("A and B", BinaryExpression),
        ("A or B", BinaryExpression),
        ("A implies B", BinaryExpression),
        ("A xor B", BinaryExpression),
        ("A | B", BinaryExpression),
        ("A & B", BinaryExpression),
        ("A == B", BinaryExpression),
        ("A != B", BinaryExpression),
        ("A === B", BinaryExpression),
        ("A !== B", BinaryExpression),
        ("A < B", BinaryExpression),
        ("A > B", BinaryExpression),
        ("A <= B", BinaryExpression),
        ("A >= B", BinaryExpression),
        ("A .. B", BinaryExpression),
        ("A + B", BinaryExpression),
        ("A - B", BinaryExpression),
        ("A * B", BinaryExpression),
        ("A / B", BinaryExpression),
        ("A % B", BinaryExpression),
        ("A ** B", BinaryExpression),
        ("A ^ B", BinaryExpression),
        ("A ?? B", CoalesceExpression),
        ("A istype T", TypeOperationExpression),
        ("A hastype T", TypeOperationExpression),
        ("A @ T", TypeOperationExpression),
        ("A as T", CastExpression),
        ("A @@ T", TypeOperationExpression),
        ("A meta T", TypeOperationExpression),
        ("@T", TypeOperationExpression),
        ("@@T", TypeOperationExpression),
        ("A[B]", BracketExpression),
        ("A#(B)", IndexExpression),
        ("A.B", FeatureChainExpression),
        ("A.?{ }", SelectExpression),
        ("A -> f()", FunctionOperationExpression),
        ("A -> f { }", FunctionOperationExpression),
        ("all T", AllExpression),
    ],
)
def test_owned_expression_alternatives_round_trip(source, node_type):
    """Visit each precedence-climbing expression alternative explicitly."""
    node = parse_as_ast_node(source, grammar_node="ownedExpression")
    assert isinstance(node, node_type)
    assert parse_as_ast_node(str(node), grammar_node="ownedExpression") == node


@pytest.mark.parametrize(
    ("source", "entry", "node_type"),
    [
        ("()", "argumentList", ArgumentList),
        ("(A, B)", "argumentList", ArgumentList),
        ("(x = A, y = B)", "argumentList", ArgumentList),
        ("~T", "featureTyping", ConjugatedPortTyping),
        ("A.B", "featureTyping", OwnedFeatureTyping),
        ("A", "qualifiedName", QualifiedReference),
        ("A::B", "qualifiedName", QualifiedReference),
        ("= A", "featureValue", ValuePart),
        (":= A", "featureValue", ValuePart),
        ("default = A", "featureValue", ValuePart),
        ("default := A", "featureValue", ValuePart),
        ("comment /* text */", "comment", Comment),
        ("comment about A, B /* text */", "comment", Comment),
        ("doc /* text */", "documentation", Documentation),
    ],
)
def test_listener_local_entries_round_trip(source, entry, node_type):
    """Exercise argument, declaration, value, and model-owned text callbacks."""
    node = parse_as_ast_node(source, grammar_node=entry)
    assert isinstance(node, node_type)
    assert parse_as_ast_node(str(node), grammar_node=entry) == node


def test_feature_value_keeps_default_colon_equals_operator():
    """Retain the distinct ``default :=`` concrete value operator."""
    node = parse_as_ast_node("default := A", grammar_node="featureValue")
    assert node.operator == "default :="
    assert str(node) == "default := A"


@pytest.mark.parametrize(
    "source",
    [
        "package Demo { action A; }",
        "package Demo { action A { } }",
        "package Demo { action A { merge m; decide d; join j; fork f; } }",
        "package Demo { action A { accept E; accept E { } } }",
        "package Demo { action A { send x; send x via channel; send x to target; send new M() via channel; } }",
        "package Demo { action A { assign x := y; assign a.b := y; } }",
        "package Demo { action A { terminate; terminate x; } }",
        "package Demo { action A { if x { } else { } if x { } else if y { } } }",
        "package Demo { action A { while x { } while x { } until done; loop { } } }",
        "package Demo { action A { for i in xs { } for i : Integer in xs { } } }",
        "action def A { first B then C; }",
        "action def A { first B; then C; }",
        "action def A { first B if x then C; }",
        "action def A { succession S first B if x then C; }",
        "action def A { while x { } until y; }",
        "action def A { for i : T in xs { } }",
        "action def A { accept E via p; accept after t; accept when x; }",
        "action def A { send x to y; send x via y to z; }",
        "action def A { assign a.b := x; }",
        "action def A { if x { } else if y { } }",
        "package Demo { state def S { entry; if x then B; do action A; exit; } }",
        "package Demo { state def S { transition T first A accept E if x then B; } }",
        "package Demo { state def S { transition T first A if x accept E then B; } }",
        "package Demo { state def S { transition T first A if x do action E; then B; } }",
        "package Demo { state def S { transition T first A accept E then B; } }",
        "package Demo { state def S { state A; then B; } }",
        "package Demo { state def S { state A; then B; state B; } }",
        "package Demo { state def S { state A; transition T first B then C; } }",
        "package Demo { state def S { state A; accept E then B; } }",
        "package Demo { state def S { state A; if x then B; } }",
        "package Demo { state def S { state A; transition T first B accept E if x then C; } }",
        "package Demo { state def S { state A; transition T first B if x accept E then C; } }",
        "package Demo { state def S { state A; transition T first B if x do action E; then C; } }",
        "package Demo { state def S { state A; transition T first B if x do accept E; then C; } }",
        "package Demo { state def S { state A; transition T first B if x do send E via C; then D; } }",
        "package Demo { state def S { state A; transition T first B if x do assign a := b; then C; } }",
        "package Demo { state def S { state Idle; } }",
        "package Demo { state Idle; exhibit state Idle; exhibit Idle; }",
        "package Demo { part def P { part p; item i; } }",
        "package Demo { item def I; }",
        "package Demo { part def P :> B; }",
        "package Demo { part def P specializes B; }",
        "package Demo { part def P { attribute x : T; } }",
        "package Demo { part def P { attribute x typed by T; } }",
        "package Demo { part def P { attribute x :> y; } }",
        "package Demo { part def P { attribute x subsets y; } }",
        "package Demo { part def P { attribute x references y; } }",
        "package Demo { part def P { attribute x crosses y; } }",
        "package Demo { part def P { attribute x redefines y; } }",
        "package Demo { part def P { attribute x ::> y; } }",
        "package Demo { part def P { ref part x : T; } }",
        "package Demo { part def P { in part x : T; } }",
        "package Demo { part def P { private part x : T; } }",
        "package Demo { part def P { individual part x : T; } }",
        "package Demo { part def P { variation part x : T; } }",
        "package Demo { part def P { derived part x : T; } }",
        "package Demo { part def P { constant part x : T; } }",
        "package Demo { part def P { port p : ~T; } }",
        "package Demo { part def P { alias A for B; } }",
        "package Demo { part def P { variant item x; } }",
        "package Demo { part def P { import A::*; } }",
        "library package Lib { }",
        "standard library package Std { }",
        "doc /* package documentation */ package Demo { }",
        "comment /* package comment */ package Demo { }",
    ],
)
def test_listener_complete_document_families_round_trip(source):
    """Exercise action, state, transition, containment, and document callbacks."""
    result = parse(source)
    assert result.ok, result.diagnostics
    rendered = str(result.ast)
    reparsed = parse(rendered)
    assert reparsed.ok, reparsed.diagnostics
    assert reparsed.ast == result.ast


def test_action_nodes_are_all_concrete_statement_nodes():
    """Confirm the action-node dispatcher exposes each concrete node family."""
    result = parse(
        "package Demo { action A { merge m; decide d; join j; fork f; "
        "accept E; send x; assign x := y; terminate; if x { }; while x { }; "
        "for i in xs { }; } }"
    )
    assert result.ok, result.diagnostics
    action = result.ast.members[0].element.members[0].element
    nodes = [item.action_node for item in action.body.items if hasattr(item, "action_node")]
    assert nodes
    assert all(isinstance(node, ActionNode) for node in nodes)


def test_listener_remaining_expression_and_action_branches():
    """Visit the remaining explicit expression and action-node guards."""

    def mapped(listener, node):
        context = _FakeContext()
        listener.nodes[context] = node
        return context

    expression = _node("A")
    listener = _fake_listener()
    feature_member = mapped(listener, ast.RawElement("feature"))
    listener.exitFeatureMember(_FakeContext(typeFeatureMember=feature_member))
    reference = mapped(listener, QualifiedReference(["A"]))
    listener.exitFeatureReferenceExpression(_FakeContext(qualifiedName=reference))
    listener.exitOccurrenceDefinitionPrefix(
        _FakeContext(
            basicDefinitionPrefix=_FakeContext(VARIATION=_FakeToken()),
            definitionExtensionKeyword=[],
            INDIVIDUAL=None,
        )
    )

    first = mapped(listener, expression)
    second = mapped(listener, expression)
    _error(
        "exitOwnedExpression",
        _FakeContext(IF=_FakeToken(), ownedExpression=[first, second]),
    )
    _error(
        "exitOwnedExpression",
        _FakeContext(ISTYPE=_FakeToken(), ownedExpression=[first, second]),
    )

    expression_context = mapped(listener, expression)
    toggle_calls = [0]

    def colon_equal():
        toggle_calls[0] += 1
        return None if toggle_calls[0] == 1 else _FakeToken()

    listener.exitFeatureValue(
        _FakeContext(
            ownedExpression=expression_context,
            DEFAULT=_FakeToken(),
            EQ=None,
            COLON_EQ=colon_equal,
        )
    )

    prefix = ast.OccurrenceUsagePrefix()
    body = ast.ActionBody()
    prefix_context = mapped(listener, prefix)
    body_context = mapped(listener, body)
    bad = ast.RawElement("bad")
    for callback in ("exitMergeNode", "exitDecisionNode", "exitJoinNode", "exitForkNode"):
        declaration_context = mapped(listener, bad)
        _error(
            callback,
            _FakeContext(
                controlNodePrefix=prefix_context,
                actionBody=body_context,
                usageDeclaration=declaration_context,
            ),
            (prefix_context, ast.ControlNodePrefix()),
            (body_context, body),
            (declaration_context, bad),
        )

    _error(
        "exitActionNodePrefix",
        _FakeContext(
            occurrenceUsagePrefix=prefix_context,
            actionNodeUsageDeclaration=bad,
        ),
        (prefix_context, prefix),
        (bad, ast.RawElement("bad declaration")),
    )
    _error(
        "exitAcceptNode",
        _FakeContext(
            occurrenceUsagePrefix=prefix_context,
            acceptNodeDeclaration=bad,
            actionBody=body_context,
        ),
        (prefix_context, prefix),
        (body_context, body),
    )

    for field in (
        "actionNodeUsageDeclaration",
        "actionUsageDeclaration",
        "nodeParameterMember",
        "senderReceiverPart",
    ):
        field_context = mapped(listener, bad)
        fields = {
            "occurrenceUsagePrefix": prefix_context,
            "actionBody": body_context,
            field: field_context,
        }
        _error(
            "exitSendNode",
            _FakeContext(**fields),
            (prefix_context, prefix),
            (body_context, body),
            (field_context, bad),
        )
    _error(
        "exitSendNode",
        _FakeContext(occurrenceUsagePrefix=prefix_context, actionBody=body_context),
        (prefix_context, prefix),
        (body_context, ast.RawElement("bad body")),
    )
    _error(
        "exitAssignmentNode",
        _FakeContext(
            occurrenceUsagePrefix=prefix_context,
            assignmentNodeDeclaration=bad,
            actionBody=body_context,
        ),
        (prefix_context, prefix),
        (body_context, body),
    )
    terminate_declaration = mapped(listener, bad)
    terminate_parameter = mapped(listener, bad)
    _error(
        "exitTerminateNode",
        _FakeContext(
            occurrenceUsagePrefix=prefix_context,
            actionNodeUsageDeclaration=terminate_declaration,
            nodeParameterMember=terminate_parameter,
            actionBody=body_context,
        ),
        (prefix_context, prefix),
        (body_context, body),
        (terminate_declaration, bad),
        (terminate_parameter, bad),
    )
    _error(
        "exitTerminateNode",
        _FakeContext(
            occurrenceUsagePrefix=prefix_context,
            nodeParameterMember=terminate_parameter,
            actionBody=body_context,
        ),
        (prefix_context, prefix),
        (body_context, body),
        (terminate_parameter, bad),
    )
    declaration_context = mapped(listener, bad)
    _error(
        "exitActionBodyParameter",
        _FakeContext(usageDeclaration=declaration_context, actionBodyItem=[]),
        (declaration_context, bad),
    )

    _error("exitIfNode", _FakeContext(actionBodyParameterMember=[]))
    condition_context = mapped(listener, expression)
    action_prefix_context = mapped(listener, ast.ActionNodePrefix(prefix))
    _error(
        "exitIfNode",
        _FakeContext(
            actionNodePrefix=action_prefix_context,
            expressionParameterMember=condition_context,
            actionBodyParameterMember=[],
        ),
        (action_prefix_context, ast.ActionNodePrefix(prefix)),
        (condition_context, expression),
    )
    then_context = mapped(listener, ast.ActionBodyParameter())
    else_context = mapped(listener, bad)
    _error(
        "exitIfNode",
        _FakeContext(
            actionNodePrefix=action_prefix_context,
            expressionParameterMember=condition_context,
            actionBodyParameterMember=[then_context, else_context],
        ),
        (action_prefix_context, ast.ActionNodePrefix(prefix)),
        (condition_context, expression),
        (then_context, ast.ActionBodyParameter()),
        (else_context, bad),
    )

    body_parameter = ast.ActionBodyParameter()
    body_parameter_context = mapped(listener, body_parameter)
    _error(
        "exitWhileLoopNode",
        _FakeContext(
            actionNodePrefix=action_prefix_context,
            UNTIL=_FakeToken(),
            expressionParameterMember=[condition_context],
            actionBodyParameterMember=body_parameter_context,
        ),
        (action_prefix_context, ast.ActionNodePrefix(prefix)),
        (condition_context, ast.RawElement("bad until")),
        (body_parameter_context, body_parameter),
    )
    _error(
        "exitWhileLoopNode",
        _FakeContext(
            actionNodePrefix=action_prefix_context,
            WHILE=_FakeToken(),
            expressionParameterMember=[condition_context],
            actionBodyParameterMember=body_parameter_context,
        ),
        (action_prefix_context, ast.ActionNodePrefix(prefix)),
        (condition_context, ast.RawElement("bad condition")),
        (body_parameter_context, body_parameter),
    )
    until_context = mapped(listener, ast.RawElement("bad until"))
    _error(
        "exitWhileLoopNode",
        _FakeContext(
            actionNodePrefix=action_prefix_context,
            WHILE=_FakeToken(),
            UNTIL=_FakeToken(),
            expressionParameterMember=[condition_context, until_context],
            actionBodyParameterMember=body_parameter_context,
        ),
        (action_prefix_context, ast.ActionNodePrefix(prefix)),
        (condition_context, expression),
        (until_context, ast.RawElement("bad until")),
        (body_parameter_context, body_parameter),
    )

    variable_context = _FakeContext(usageDeclaration=None)
    listener.exitForVariableDeclarationMember(variable_context)
    _error(
        "exitForVariableDeclarationMember",
        _FakeContext(usageDeclaration=variable_context),
        (variable_context, bad),
    )
    collection = ast.NodeParameter(expression)
    collection_context = mapped(listener, collection)
    _error(
        "exitForLoopNode",
        _FakeContext(
            actionNodePrefix=action_prefix_context,
            nodeParameterMember=None,
            actionBodyParameterMember=body_parameter_context,
        ),
        (action_prefix_context, ast.ActionNodePrefix(prefix)),
        (body_parameter_context, body_parameter),
    )
    _error(
        "exitForLoopNode",
        _FakeContext(
            actionNodePrefix=action_prefix_context,
            nodeParameterMember=collection_context,
            actionBodyParameterMember=body_parameter_context,
        ),
        (action_prefix_context, ast.ActionNodePrefix(prefix)),
        (collection_context, collection),
        (body_parameter_context, ast.RawElement("bad body")),
    )
    for_listener = _fake_listener(
        (action_prefix_context, ast.ActionNodePrefix(prefix)),
        (collection_context, collection),
        (body_parameter_context, body_parameter),
    )
    for_listener.parts[variable_context] = bad
    with pytest.raises(ValueError):
        for_listener.exitForLoopNode(
            _FakeContext(
                actionNodePrefix=action_prefix_context,
                forVariableDeclarationMember=variable_context,
                nodeParameterMember=collection_context,
                actionBodyParameterMember=body_parameter_context,
            )
        )


def test_listener_remaining_state_transition_and_containment_branches():
    """Visit state/transition and generic containment callbacks explicitly."""

    def mapped(listener, node):
        context = _FakeContext()
        listener.nodes[context] = node
        return context

    expression = _node("A")
    listener = _fake_listener()
    _error(
        "exitOwnedExpression",
        _FakeContext(AT_SIGN=_FakeToken(), ownedExpression=[], typeReference=None),
    )
    _error(
        "exitOwnedExpression",
        _FakeContext(ALL=_FakeToken(), ownedExpression=[], typeReference=None),
    )
    _error("exitOwnedExpression", _FakeContext(ownedExpression=[]))

    prefix_context = mapped(listener, ast.OccurrenceUsagePrefix())
    body_context = mapped(listener, ast.ActionBody())
    bad_declaration_context = mapped(listener, ast.RawElement("bad declaration"))
    _error(
        "exitActionNodePrefix",
        _FakeContext(
            occurrenceUsagePrefix=prefix_context,
            actionNodeUsageDeclaration=bad_declaration_context,
        ),
        (prefix_context, ast.OccurrenceUsagePrefix()),
        (bad_declaration_context, ast.RawElement("bad declaration")),
    )
    _error(
        "exitAcceptNode",
        _FakeContext(
            occurrenceUsagePrefix=prefix_context,
            acceptNodeDeclaration=bad_declaration_context,
            actionBody=body_context,
        ),
        (prefix_context, ast.OccurrenceUsagePrefix()),
        (body_context, ast.ActionBody()),
        (bad_declaration_context, ast.RawElement("bad declaration")),
    )
    assignment_declaration_context = mapped(listener, ast.RawElement("bad assignment"))
    _error(
        "exitAssignmentNode",
        _FakeContext(
            occurrenceUsagePrefix=prefix_context,
            assignmentNodeDeclaration=assignment_declaration_context,
            actionBody=body_context,
        ),
        (prefix_context, ast.OccurrenceUsagePrefix()),
        (body_context, ast.ActionBody()),
        (assignment_declaration_context, ast.RawElement("bad assignment")),
    )

    connector = QualifiedReference(["B"])
    transition = ast.TransitionSuccession(connector)
    transition_context = mapped(listener, transition)
    listener.exitDefaultTargetSuccession(
        _FakeContext(transitionSuccessionMember=transition_context)
    )
    usage_body = ast.DefinitionBody()
    usage_body_context = mapped(listener, usage_body)
    bad_succession_context = mapped(listener, ast.RawElement("bad succession"))
    _error(
        "exitActionTargetSuccession",
        _FakeContext(targetSuccession=bad_succession_context, usageBody=usage_body_context),
        (bad_succession_context, ast.RawElement("bad succession")),
        (usage_body_context, usage_body),
    )
    _error(
        "exitGuardedSuccession",
        _FakeContext(
            featureChainMember=mapped(listener, ast.FeatureChain([connector])),
            guardExpressionMember=mapped(listener, ast.GuardExpressionMember(expression)),
            transitionSuccessionMember=bad_succession_context,
            usageBody=bad_succession_context,
        ),
        (bad_succession_context, ast.RawElement("bad succession")),
    )
    valid_source = mapped(listener, ast.FeatureChain([connector]))
    valid_guard = mapped(listener, ast.GuardExpressionMember(expression))
    invalid_declaration = mapped(listener, ast.RawElement("bad declaration"))
    _error(
        "exitGuardedSuccession",
        _FakeContext(
            featureChainMember=valid_source,
            guardExpressionMember=valid_guard,
            transitionSuccessionMember=transition_context,
            usageBody=usage_body_context,
            usageDeclaration=invalid_declaration,
        ),
        (valid_source, ast.FeatureChain([connector])),
        (valid_guard, ast.GuardExpressionMember(expression)),
        (transition_context, transition),
        (usage_body_context, usage_body),
        (invalid_declaration, ast.RawElement("bad declaration")),
    )
    guarded_source_context = _FakeContext()
    guarded_guard_context = _FakeContext()
    guarded_target_context = _FakeContext()
    guarded_body_context = _FakeContext()
    _error(
        "exitGuardedSuccession",
        _FakeContext(
            featureChainMember=guarded_source_context,
            guardExpressionMember=guarded_guard_context,
            transitionSuccessionMember=guarded_target_context,
            usageBody=guarded_body_context,
        ),
        (guarded_source_context, ast.FeatureChain([connector])),
        (guarded_guard_context, ast.GuardExpressionMember(expression)),
        (guarded_target_context, ast.RawElement("bad target")),
        (guarded_body_context, ast.RawElement("bad body")),
    )

    accept_parameters = ast.AcceptParameterPart(ast.PayloadParameter(trigger_expression=expression))
    accept_parameters_context = mapped(listener, accept_parameters)
    accept_action = ast.AcceptNodeDeclaration(accept_parameters)
    accept_action_context = mapped(listener, accept_action)
    send_declaration = ast.SendNodeDeclaration(ast.NodeParameter(expression))
    send_declaration_context = mapped(listener, send_declaration)
    assignment_declaration = ast.AssignmentNodeDeclaration(
        ast.FeatureChain([connector]), ast.NodeParameter(expression)
    )
    assignment_declaration_context = mapped(listener, assignment_declaration)
    action_body = ast.ActionBody()
    action_body_context = mapped(listener, action_body)
    listener.exitStateAcceptActionUsage(
        _FakeContext(
            acceptNodeDeclaration=accept_action_context,
            actionBody=action_body_context,
        )
    )
    listener.exitStateSendActionUsage(
        _FakeContext(
            sendNodeDeclaration=send_declaration_context,
            actionBody=action_body_context,
        )
    )
    listener.exitStateAssignmentActionUsage(
        _FakeContext(
            assignmentNodeDeclaration=assignment_declaration_context,
            actionBody=action_body_context,
        )
    )
    payload_member_context = mapped(listener, ast.PayloadFeature())
    listener.exitPayloadFeatureMember(_FakeContext(payloadFeature=payload_member_context))
    listener.exitPayloadFeatureSpecializationPart(
        _FakeContext(featureSpecialization=[], multiplicityPart=None)
    )
    payload_parameter = ast.PayloadParameter(trigger_expression=expression)
    payload_parameter_context = mapped(listener, payload_parameter)
    invalid_via_context = mapped(listener, ast.RawElement("bad via"))
    _error(
        "exitAcceptParameterPart",
        _FakeContext(
            payloadParameterMember=payload_parameter_context,
            nodeParameterMember=invalid_via_context,
        ),
        (payload_parameter_context, payload_parameter),
        (invalid_via_context, ast.RawElement("bad via")),
    )
    accept_payload_context = _FakeContext()
    accept_via_context = _FakeContext()
    _error(
        "exitAcceptParameterPart",
        _FakeContext(
            payloadParameterMember=accept_payload_context,
            nodeParameterMember=accept_via_context,
        ),
        (accept_payload_context, payload_parameter),
        (accept_via_context, ast.RawElement("bad via")),
    )

    listener.exitActionNodeUsageDeclaration(_FakeContext(usageDeclaration=None))
    invalid_action_declaration = mapped(listener, ast.RawElement("bad declaration"))
    _error(
        "exitSendNodeDeclaration",
        _FakeContext(
            nodeParameterMember=mapped(listener, ast.NodeParameter(expression)),
            actionNodeUsageDeclaration=invalid_action_declaration,
        ),
        (invalid_action_declaration, ast.RawElement("bad declaration")),
    )
    send_parameter_context = _FakeContext()
    send_action_declaration_context = _FakeContext()
    _error(
        "exitSendNodeDeclaration",
        _FakeContext(
            nodeParameterMember=send_parameter_context,
            actionNodeUsageDeclaration=send_action_declaration_context,
        ),
        (send_parameter_context, ast.NodeParameter(expression)),
        (send_action_declaration_context, ast.RawElement("bad declaration")),
    )
    invalid_sender = mapped(listener, ast.RawElement("bad sender"))
    _error(
        "exitSendNodeDeclaration",
        _FakeContext(
            nodeParameterMember=mapped(listener, ast.NodeParameter(expression)),
            senderReceiverPart=invalid_sender,
        ),
        (invalid_sender, ast.RawElement("bad sender")),
    )
    send_sender_context = _FakeContext()
    _error(
        "exitSendNodeDeclaration",
        _FakeContext(
            nodeParameterMember=send_parameter_context,
            senderReceiverPart=send_sender_context,
        ),
        (send_parameter_context, ast.NodeParameter(expression)),
        (send_sender_context, ast.RawElement("bad sender")),
    )
    invalid_binding = mapped(listener, ast.RawElement("bad binding"))
    _error(
        "exitAssignmentNodeDeclaration",
        _FakeContext(
            assignmentTargetMember=invalid_binding,
            featureChainMember=mapped(listener, ast.FeatureChain([connector])),
            nodeParameterMember=mapped(listener, ast.NodeParameter(expression)),
        ),
        (invalid_binding, ast.RawElement("bad binding")),
    )
    binding_context = _FakeContext()
    target_context = _FakeContext()
    value_context = _FakeContext()
    _error(
        "exitAssignmentNodeDeclaration",
        _FakeContext(
            assignmentTargetMember=binding_context,
            featureChainMember=target_context,
            nodeParameterMember=value_context,
        ),
        (binding_context, ast.RawElement("bad binding")),
        (target_context, ast.FeatureChain([connector])),
        (value_context, ast.NodeParameter(expression)),
    )

    action_prefix = ast.OccurrenceUsagePrefix()
    action_prefix_context = mapped(listener, action_prefix)
    action_declaration = ast.ActionUsageDeclaration()
    action_declaration_context = mapped(listener, action_declaration)
    listener.exitActionUsage(
        _FakeContext(
            occurrenceUsagePrefix=action_prefix_context,
            actionUsageDeclaration=action_declaration_context,
            actionBody=None,
            TERMINATE=_FakeToken(),
            SEMI=_FakeToken(),
        )
    )
    perform_declaration = ast.PerformActionUsageDeclaration()
    perform_declaration_context = mapped(listener, perform_declaration)
    listener.exitPerformActionUsage(
        _FakeContext(
            occurrenceUsagePrefix=action_prefix_context,
            performActionUsageDeclaration=perform_declaration_context,
            actionBody=action_body_context,
        )
    )
    definition_prefix = ast.OccurrenceDefinitionPrefix()
    definition_prefix_context = mapped(listener, definition_prefix)
    definition_declaration = ast.DefinitionDeclaration()
    definition_declaration_context = mapped(listener, definition_declaration)
    listener.exitActionDefinition(
        _FakeContext(
            occurrenceDefinitionPrefix=definition_prefix_context,
            definitionDeclaration=definition_declaration_context,
            actionBody=action_body_context,
        )
    )

    guarded_context = _FakeContext()
    bad_guard_context = mapped(listener, ast.RawElement("bad guard"))
    guarded_context._context_values.update(
        {
            "guardExpressionMember": bad_guard_context,
            "transitionSuccessionMember": transition_context,
        }
    )
    _error(
        "exitEntryTransitionMember",
        _FakeContext(guardedTargetSuccession=guarded_context),
        (bad_guard_context, ast.RawElement("bad guard")),
        (transition_context, transition),
    )

    listener.exitEffectBehaviorUsage(_FakeContext(emptyActionUsage_=_FakeToken()))
    transition_declaration = ast.PerformActionUsageDeclaration()
    for callback, field in (
        ("exitTransitionPerformActionUsage", "performActionUsageDeclaration"),
        ("exitTransitionAcceptActionUsage", "acceptNodeDeclaration"),
        ("exitTransitionSendActionUsage", "sendNodeDeclaration"),
        ("exitTransitionAssignmentActionUsage", "assignmentNodeDeclaration"),
    ):
        declaration = transition_declaration
        if field == "acceptNodeDeclaration":
            declaration = accept_action
        elif field == "sendNodeDeclaration":
            declaration = send_declaration
        elif field == "assignmentNodeDeclaration":
            declaration = assignment_declaration
        declaration_context = mapped(listener, declaration)
        getattr(listener, callback)(
            _FakeContext(
                **{field: declaration_context, "LBRACE": _FakeToken(), "actionBodyItem": []}
            )
        )
        getattr(listener, callback)(
            _FakeContext(**{field: declaration_context, "SEMI": _FakeToken()})
        )

    listener.exitTargetTransitionUsage(
        _FakeContext(
            transitionSuccessionMember=transition_context,
            actionBody=action_body_context,
            TRANSITION=_FakeToken(),
            emptyParameterMember=[],
        )
    )
    listener.exitBehaviorUsageElement(_FakeContext())
    listener.exitSourceSuccessionMember(_FakeContext())
    listener.exitSourceSuccession(_FakeContext())

    non_behavior_context = mapped(listener, ast.RawElement("non-behavior"))
    listener.exitStateBodyItem(_FakeContext(nonBehaviorBodyItem=non_behavior_context))
    incomplete_entry_context = mapped(listener, ast.RawElement("bad entry"))
    _error(
        "exitStateBodyItem",
        _FakeContext(
            entryActionMember=incomplete_entry_context,
            entryTransitionMember=[],
        ),
        (incomplete_entry_context, ast.RawElement("bad entry")),
    )

    variant_context = _FakeContext()
    _error(
        "exitDefinitionBodyItemContent",
        _FakeContext(VARIANT=_FakeToken(), variantUsageElement=variant_context),
        (variant_context, ast.ASTNode()),
    )
    unassembled_content = _FakeContext()
    _error(
        "exitDefinitionBodyItem",
        _FakeContext(definitionBodyItemContent=unassembled_content),
    )
    item_context = _FakeContext()
    _error(
        "exitDefinitionBody",
        _FakeContext(definitionBodyItem=[item_context]),
        (item_context, ast.RawElement("not a definition body item")),
    )
    usage_context = mapped(listener, ast.RawElement("usage"))
    listener.exitEndOccurrenceUsageElement(
        _FakeContext(
            occurrenceUsageElement=usage_context,
            name=None,
            ownedCrossMultiplicityMember=None,
            NONUNIQUE=None,
        )
    )
    structure_context = mapped(listener, ast.RawElement("structure"))
    structure_member_prefix = _FakeContext()
    listener.exitStructureUsageMember(
        _FakeContext(structureUsageElement=structure_context, memberPrefix=structure_member_prefix),
    )
    listener.exitPackageDeclaration(_FakeContext(identification=None))
    listener.exitAnnotatingElement(_FakeContext())
    _error("exitUsageElement", _FakeContext())
    listener.exitOccurrenceUsageElement(_FakeContext())
    definition_element_context = mapped(listener, ast.RawElement("definition"))
    listener.exitDefinitionMember(
        _FakeContext(definitionElement=definition_element_context, memberPrefix=_FakeContext()),
    )
    structure_member_context = mapped(listener, ast.RawElement("structure member"))
    listener.exitNonBehaviorBodyItem(
        _FakeContext(structureUsageMember=structure_member_context),
    )
    _error("exitPackageBodyElement", _FakeContext())
    listener.exitPackageBodyElement(_FakeContext(elementFilterMember=_FakeContext()))
    listener.exitVariantUsageElement(_FakeContext())
    direct_bad_via_context = mapped(listener, ast.RawElement("bad via"))
    with pytest.raises(ValueError):
        listener.exitAcceptParameterPart(
            _FakeContext(
                payloadParameterMember=accept_parameters_context,
                nodeParameterMember=direct_bad_via_context,
            )
        )
    direct_bad_guard_context = mapped(listener, ast.RawElement("bad guard"))
    direct_guarded_context = _FakeContext(
        guardExpressionMember=direct_bad_guard_context,
        transitionSuccessionMember=transition_context,
    )
    with pytest.raises(ValueError):
        listener.exitEntryTransitionMember(
            _FakeContext(guardedTargetSuccession=direct_guarded_context)
        )
    definition_declaration_context = _FakeContext()
    definition_body_context = _FakeContext()
    _error(
        "exitDefinition",
        _FakeContext(
            definitionDeclaration=definition_declaration_context,
            definitionBody=definition_body_context,
        ),
        (definition_declaration_context, ast.RawElement("bad declaration")),
        (definition_body_context, ast.RawElement("bad body")),
    )
    part_prefix_context = _FakeContext()
    part_definition_context = _FakeContext()
    _error(
        "exitPartDefinition",
        _FakeContext(
            occurrenceDefinitionPrefix=part_prefix_context,
            definition=part_definition_context,
        ),
        (part_prefix_context, ast.RawElement("bad prefix")),
        (part_definition_context, ast.RawElement("bad definition")),
    )
    completion_context = _FakeContext()
    _error(
        "exitUsage",
        _FakeContext(usageCompletion=completion_context),
        (completion_context, ast.RawElement("bad completion")),
    )
    invalid_body_context = _FakeContext()
    _error(
        "exitUsageCompletion",
        _FakeContext(usageBody=invalid_body_context),
        (invalid_body_context, ast.RawElement("bad body")),
    )
    usage_prefix_context = _FakeContext()
    usage_context = _FakeContext()
    _error(
        "exitPartUsage",
        _FakeContext(
            occurrenceUsagePrefix=usage_prefix_context,
            usage=usage_context,
        ),
        (usage_prefix_context, ast.RawElement("bad prefix")),
        (usage_context, ast.RawElement("bad usage")),
    )
    _error(
        "exitItemUsage",
        _FakeContext(
            occurrenceUsagePrefix=usage_prefix_context,
            usage=usage_context,
        ),
        (usage_prefix_context, ast.RawElement("bad prefix")),
        (usage_context, ast.RawElement("bad usage")),
    )
    invalid_end_usage_context = _FakeContext()
    _error(
        "exitEndOccurrenceUsageElement",
        _FakeContext(occurrenceUsageElement=invalid_end_usage_context),
        (invalid_end_usage_context, ast.ASTNode()),
    )
    invalid_structure_context = _FakeContext()
    _error(
        "exitStructureUsageMember",
        _FakeContext(
            structureUsageElement=invalid_structure_context,
            memberPrefix=_FakeContext(),
        ),
        (invalid_structure_context, ast.ASTNode()),
    )
    invalid_definition_element_context = _FakeContext()
    _error(
        "exitDefinitionMember",
        _FakeContext(
            definitionElement=invalid_definition_element_context,
            memberPrefix=_FakeContext(),
        ),
        (invalid_definition_element_context, ast.ASTNode()),
    )
    definition_member_context = _FakeContext()
    listener.nodes[definition_member_context] = ast.RawElement("definition member")
    listener.exitNonBehaviorBodyItem(
        _FakeContext(definitionMember=definition_member_context),
    )
    invalid_package_element_context = _FakeContext()
    _error(
        "exitPackageMember",
        _FakeContext(
            definitionElement=invalid_package_element_context,
            memberPrefix=_FakeContext(),
        ),
        (invalid_package_element_context, ast.ASTNode()),
    )
    listener.exitPackageBody(_FakeContext(SEMI=_FakeToken()))


def test_listener_generic_definition_usage_guards_and_conjugated_port_passes():
    """Cover defensive generic-node paths and optional conjugated-port dispatch."""
    for callback, context in (
        (
            "exitNonOccurrenceUsageMember",
            _FakeContext(nonOccurrenceUsageElement=_FakeContext()),
        ),
        (
            "exitItemDefinition",
            _FakeContext(occurrenceDefinitionPrefix=_FakeContext(), definition=_FakeContext()),
        ),
        (
            "exitAttributeDefinition",
            _FakeContext(definitionPrefix=_FakeContext(), definition=_FakeContext()),
        ),
        (
            "exitAttributeUsage",
            _FakeContext(usagePrefix=_FakeContext(), usage=_FakeContext()),
        ),
        (
            "exitPortDefinition",
            _FakeContext(definitionPrefix=_FakeContext(), definition=_FakeContext()),
        ),
        (
            "exitPortUsage",
            _FakeContext(occurrenceUsagePrefix=_FakeContext(), usage=_FakeContext()),
        ),
    ):
        _error(callback, context)

    listener = _fake_listener()
    conjugated = ast.ConjugatedPortTyping(ast.QualifiedReference(["P"]))
    conjugated_context = _FakeContext()
    listener.nodes[conjugated_context] = conjugated
    member_context = _FakeContext(conjugatedPortDefinition=conjugated_context)
    listener.exitConjugatedPortDefinitionMember(member_context)
    assert listener.node_for(member_context) == conjugated

    port_conjugation_context = _FakeContext()
    listener.nodes[port_conjugation_context] = conjugated
    definition_context = _FakeContext(portConjugation=port_conjugation_context)
    listener.exitConjugatedPortDefinition(definition_context)
    assert listener.node_for(definition_context) == conjugated


def test_listener_new_typed_callbacks_cover_invalid_context_and_prefix_fallbacks():
    """Exercise the explicit error paths for the newly typed grammar entries."""
    for callback, context in (
        (
            "exitOccurrenceDefinition",
            _FakeContext(occurrenceDefinitionPrefix=_FakeContext(), definition=_FakeContext()),
        ),
        ("exitIndividualDefinition", _FakeContext(definition=_FakeContext())),
        (
            "exitReferenceUsage",
            _FakeContext(usage=_FakeContext(), refPrefix=None, endUsagePrefix=None),
        ),
        ("exitDefaultReferenceUsage", _FakeContext(usage=_FakeContext(), refPrefix=None)),
        (
            "exitOccurrenceUsage",
            _FakeContext(occurrenceUsagePrefix=_FakeContext(), usage=_FakeContext()),
        ),
        ("exitIndividualUsage", _FakeContext(usage=_FakeContext())),
        ("exitPortionUsage", _FakeContext(usage=_FakeContext())),
        (
            "exitEventOccurrenceUsage",
            _FakeContext(occurrenceUsagePrefix=_FakeContext(), usageCompletion=_FakeContext()),
        ),
    ):
        _error(callback, context)

    class _BareContext:
        """Provide only source text for the extension-prefix fallback."""

        start = None
        stop = None

        def getText(self):
            return "extension"

    listener = _fake_listener()
    assert listener._usage_prefix_from_ref_prefix(_BareContext()).extension_keywords == [
        "extension"
    ]

    # The selected child exists but has not been assembled, so the dispatcher
    # must retain the enclosing non-occurrence element as raw syntax.
    listener.exitNonOccurrenceUsageElement(
        _FakeContext(referenceUsage=_FakeContext(), defaultReferenceUsage=None, attributeUsage=None)
    )


def test_listener_namespace_import_and_definition_dispatch_guards():
    """Cover explicit namespace/import guards and the raw compatibility branch."""
    listener = _fake_listener()

    # An alias without an identification is a valid grammar alternative; the
    # target and relationship body remain typed children.
    target_context = _FakeContext()
    body_context = _FakeContext()
    listener.nodes[target_context] = ast.QualifiedReference(["Target"])
    listener.nodes[body_context] = ast.RelationshipBody(";")
    alias_context = _FakeContext(
        name=[],
        LT=None,
        qualifiedName=target_context,
        relationshipBody=body_context,
        memberPrefix=_FakeContext(),
    )
    listener.exitAliasMember(alias_context)
    assert listener.node_for(alias_context) == ast.AliasMember(
        target=ast.QualifiedReference(["Target"]),
        relationship_body=ast.RelationshipBody(";"),
    )

    # Every required child guard is explicit instead of silently creating a
    # partially populated AST node.
    for callback, context in (
        (
            "exitAliasMember",
            _FakeContext(
                name=[],
                qualifiedName=None,
                relationshipBody=None,
                memberPrefix=_FakeContext(),
            ),
        ),
        ("exitMembershipImport", _FakeContext(qualifiedName=None)),
        ("exitNamespaceImportDirect", _FakeContext(qualifiedName=None)),
        (
            "exitNamespaceImport",
            _FakeContext(filterPackage=None, qualifiedName=None),
        ),
        (
            "exitFilterPackageImportDeclaration",
            _FakeContext(membershipImport=None, namespaceImportDirect=None),
        ),
        ("exitFilterPackageMember", _FakeContext(ownedExpression=None)),
        (
            "exitFilterPackage",
            _FakeContext(filterPackageImportDeclaration=None, filterPackageMember=[]),
        ),
        ("exitImportDeclaration", _FakeContext(membershipImport=None, namespaceImport=None)),
        ("exitImportRule", _FakeContext(importDeclaration=None, relationshipBody=None)),
        (
            "exitElementFilterMember",
            _FakeContext(ownedExpression=None, memberPrefix=_FakeContext()),
        ),
    ):
        _error(callback, context)

    # The generic body dispatcher still has an explicit, lossless fallback for
    # grammar alternatives that do not yet have a typed node.
    raw_context = _FakeContext(
        ALIAS=None,
        VARIANT=None,
        definitionElement=None,
        nonOccurrenceUsageElement=None,
    )
    listener.exitDefinitionBodyItemContent(raw_context)
    assert isinstance(listener.node_for(raw_context), ast.RawElement)

    listener.exitNonBehaviorBodyItem(
        _FakeContext(
            importRule=None,
            aliasMember=None,
            definitionMember=None,
            structureUsageMember=None,
            nonOccurrenceUsageMember=None,
        )
    )

    # Import is a required typed child of a definition body item; a wrong
    # listener value must fail rather than be treated as a generic element.
    import_context = _FakeContext()
    listener.nodes[import_context] = ast.RawElement("import A::*;")
    _error(
        "exitDefinitionBodyItem",
        _FakeContext(
            importRule=import_context,
            sourceSuccessionMember=None,
            memberPrefix=None,
            definitionBodyItemContent=None,
            endOccurrenceUsageElement=None,
            occurrenceUsageElement=None,
        ),
        (import_context, ast.RawElement("import A::*;")),
    )


@pytest.mark.parametrize(
    "source",
    [
        "package P { connection def C; }",
        "package P { connection c connect a to b; }",
        "package P { connection c connect (a, b, c); }",
        "package P { interface def I; }",
        "package P { interface i connect a to b; }",
        "package P { interface (a, b); }",
        "package P { interface def I { end p : P; } }",
        "package P { interface def I { alias A for B; import X::*; } }",
    ],
)
def test_connection_and_interface_productions_are_typed_and_nested(source):
    """Exercise connection/interface listeners through real grammar dispatch."""
    result = parse(source)
    assert result.ok, result.diagnostics
    package = result.ast.members[0].element
    element = package.members[0].element
    assert not isinstance(element, ast.RawElement)
    assert isinstance(
        element,
        (
            ast.ConnectionDefinition,
            ast.ConnectionUsage,
            ast.InterfaceDefinition,
            ast.InterfaceUsage,
        ),
    )
    rendered = str(result.ast)
    reparsed = parse(rendered)
    assert reparsed.ok, reparsed.diagnostics
    assert reparsed.ast == result.ast

    if isinstance(element, ast.ConnectionDefinition):
        assert isinstance(element.definition, ast.Definition)
    if isinstance(element, ast.ConnectionUsage):
        assert isinstance(element.connector_part, ast.ConnectorPart)
    if isinstance(element, ast.InterfaceDefinition):
        assert isinstance(element.interface_body, ast.InterfaceBody)
        if element.interface_body.items:
            assert all(isinstance(item, ast.SourceElement) for item in element.interface_body.items)
    if isinstance(element, ast.InterfaceUsage):
        assert isinstance(element.interface_usage_declaration, ast.InterfaceUsageDeclaration)


def test_connection_and_interface_definitions_preserve_nested_states():
    """States nested in connection/interface definitions remain discoverable."""
    for source in (
        "package P { connection def C { state def S; } }",
        "package P { interface def I { state def S; } }",
    ):
        result = parse(source)
        assert result.ok, result.diagnostics
        outer = result.ast.members[0].element.members[0].element
        body = (
            outer.definition.body
            if isinstance(outer, ast.ConnectionDefinition)
            else outer.interface_body
        )
        nested = body.items[0]
        assert isinstance(nested, ast.DefinitionBodyItem)
        assert isinstance(nested.element, ast.StateDefinition)


def test_listener_connection_interface_and_feature_defensive_paths():
    """Cover every explicit validation branch for connection/interface nodes."""
    listener = _fake_listener()
    reference = ast.QualifiedReference(["A"])
    connector_end = ast.ConnectorEnd(reference)
    interface_end = ast.InterfaceEnd(reference)

    # Connector-part dispatch and assembly.
    binary_ctx = _FakeContext()
    nary_ctx = _FakeContext()
    listener.nodes[binary_ctx] = ast.BinaryConnectorPart(connector_end, connector_end)
    listener.nodes[nary_ctx] = ast.NaryConnectorPart([connector_end, connector_end])
    listener.exitConnectorPart(_FakeContext(binaryConnectorPart=binary_ctx, naryConnectorPart=None))
    listener.exitConnectorPart(_FakeContext(binaryConnectorPart=None, naryConnectorPart=nary_ctx))
    _error("exitConnectorPart", _FakeContext(binaryConnectorPart=None, naryConnectorPart=None))
    _error("exitBinaryConnectorPart", _FakeContext(connectorEndMember=[]))
    _error("exitNaryConnectorPart", _FakeContext(connectorEndMember=[]))

    # Required and optional connection fields reject the wrong typed child.
    prefix_ctx = _FakeContext()
    definition_ctx = _FakeContext()
    body_ctx = _FakeContext()
    listener.nodes[prefix_ctx] = ast.OccurrenceDefinitionPrefix()
    listener.nodes[definition_ctx] = ast.Definition(
        ast.DefinitionDeclaration(), ast.DefinitionBody(declaration_only=True)
    )
    listener.nodes[body_ctx] = ast.DefinitionBody(declaration_only=True)
    listener.exitConnectionDefinition(
        _FakeContext(occurrenceDefinitionPrefix=prefix_ctx, definition=definition_ctx)
    )
    connection_context = _FakeContext(
        occurrenceUsagePrefix=prefix_ctx,
        usageBody=body_ctx,
        usageDeclaration=None,
        valuePart=None,
        connectorPart=None,
        CONNECTION=_FakeToken("connection"),
    )
    listener.nodes[prefix_ctx] = ast.OccurrenceUsagePrefix()
    listener.exitConnectionUsage(connection_context)
    for key, value in (
        ("occurrenceUsagePrefix", ast.RawElement("bad")),
        ("usageBody", ast.RawElement("bad")),
        ("usageDeclaration", ast.RawElement("bad")),
        ("valuePart", ast.RawElement("bad")),
        ("connectorPart", ast.RawElement("bad")),
    ):
        values = {
            "occurrenceUsagePrefix": prefix_ctx,
            "usageBody": body_ctx,
            "usageDeclaration": None,
            "valuePart": None,
            "connectorPart": None,
            "CONNECTION": None,
        }
        child = _FakeContext()
        listener.nodes[child] = value
        values[key] = child
        _error(
            "exitConnectionUsage",
            _FakeContext(**values),
            (prefix_ctx, ast.OccurrenceUsagePrefix()),
            (body_ctx, ast.DefinitionBody(declaration_only=True)),
            (child, value),
        )

    _error(
        "exitConnectionDefinition",
        _FakeContext(occurrenceDefinitionPrefix=prefix_ctx, definition=definition_ctx),
        (prefix_ctx, ast.OccurrenceDefinitionPrefix()),
        (definition_ctx, ast.RawElement("bad")),
    )

    # Interface endpoint/part validation and assembly.
    interface_binary_ctx = _FakeContext()
    interface_nary_ctx = _FakeContext()
    listener.nodes[interface_binary_ctx] = ast.BinaryInterfacePart(interface_end, interface_end)
    listener.nodes[interface_nary_ctx] = ast.NaryInterfacePart([interface_end, interface_end])
    listener.exitInterfacePart(
        _FakeContext(binaryInterfacePart=interface_binary_ctx, naryInterfacePart=None)
    )
    listener.exitInterfacePart(
        _FakeContext(binaryInterfacePart=None, naryInterfacePart=interface_nary_ctx)
    )
    _error("exitInterfacePart", _FakeContext(binaryInterfacePart=None, naryInterfacePart=None))
    _error("exitBinaryInterfacePart", _FakeContext(interfaceEndMember=[]))
    _error("exitNaryInterfacePart", _FakeContext(interfaceEndMember=[]))
    _error("exitInterfaceEnd", _FakeContext(ownedReferenceSubsetting=None))

    interface_prefix_ctx = _FakeContext()
    interface_declaration_ctx = _FakeContext()
    interface_body_ctx = _FakeContext()
    listener.nodes[interface_prefix_ctx] = ast.OccurrenceDefinitionPrefix()
    listener.nodes[interface_declaration_ctx] = ast.DefinitionDeclaration()
    listener.nodes[interface_body_ctx] = ast.InterfaceBody(declaration_only=True)
    listener.exitInterfaceDefinition(
        _FakeContext(
            occurrenceDefinitionPrefix=interface_prefix_ctx,
            definitionDeclaration=interface_declaration_ctx,
            interfaceBody=interface_body_ctx,
        )
    )
    listener.nodes[interface_prefix_ctx] = ast.OccurrenceUsagePrefix()
    usage_declaration_ctx = _FakeContext()
    listener.nodes[usage_declaration_ctx] = ast.InterfaceUsageDeclaration()
    listener.exitInterfaceUsage(
        _FakeContext(
            occurrenceUsagePrefix=interface_prefix_ctx,
            interfaceUsageDeclaration=usage_declaration_ctx,
            interfaceBody=interface_body_ctx,
        )
    )
    for callback, context in (
        (
            "exitInterfaceDefinition",
            _FakeContext(
                occurrenceDefinitionPrefix=None,
                definitionDeclaration=interface_declaration_ctx,
                interfaceBody=interface_body_ctx,
            ),
        ),
        (
            "exitInterfaceDefinition",
            _FakeContext(
                occurrenceDefinitionPrefix=interface_prefix_ctx,
                definitionDeclaration=None,
                interfaceBody=interface_body_ctx,
            ),
        ),
        (
            "exitInterfaceDefinition",
            _FakeContext(
                occurrenceDefinitionPrefix=interface_prefix_ctx,
                definitionDeclaration=interface_declaration_ctx,
                interfaceBody=None,
            ),
        ),
        (
            "exitInterfaceUsage",
            _FakeContext(
                occurrenceUsagePrefix=None,
                interfaceUsageDeclaration=usage_declaration_ctx,
                interfaceBody=interface_body_ctx,
            ),
        ),
        (
            "exitInterfaceUsage",
            _FakeContext(
                occurrenceUsagePrefix=interface_prefix_ctx,
                interfaceUsageDeclaration=None,
                interfaceBody=interface_body_ctx,
            ),
        ),
        (
            "exitInterfaceUsage",
            _FakeContext(
                occurrenceUsagePrefix=interface_prefix_ctx,
                interfaceUsageDeclaration=usage_declaration_ctx,
                interfaceBody=None,
            ),
        ),
    ):
        _error(callback, context)

    _error(
        "exitInterfaceDefinition",
        _FakeContext(
            occurrenceDefinitionPrefix=interface_prefix_ctx,
            definitionDeclaration=None,
            interfaceBody=interface_body_ctx,
        ),
        (interface_prefix_ctx, ast.OccurrenceDefinitionPrefix()),
        (interface_body_ctx, ast.InterfaceBody(declaration_only=True)),
    )
    _error(
        "exitInterfaceDefinition",
        _FakeContext(
            occurrenceDefinitionPrefix=interface_prefix_ctx,
            definitionDeclaration=interface_declaration_ctx,
            interfaceBody=None,
        ),
        (interface_prefix_ctx, ast.OccurrenceDefinitionPrefix()),
        (interface_declaration_ctx, ast.DefinitionDeclaration()),
    )
    _error(
        "exitInterfaceUsage",
        _FakeContext(
            occurrenceUsagePrefix=interface_prefix_ctx,
            interfaceUsageDeclaration=None,
            interfaceBody=interface_body_ctx,
        ),
        (interface_prefix_ctx, ast.OccurrenceUsagePrefix()),
        (interface_body_ctx, ast.InterfaceBody(declaration_only=True)),
    )
    _error(
        "exitInterfaceUsage",
        _FakeContext(
            occurrenceUsagePrefix=interface_prefix_ctx,
            interfaceUsageDeclaration=usage_declaration_ctx,
            interfaceBody=None,
        ),
        (interface_prefix_ctx, ast.OccurrenceUsagePrefix()),
        (usage_declaration_ctx, ast.InterfaceUsageDeclaration()),
    )

    # Interface body dispatch preserves each grammar alternative and source
    # succession, while malformed children fail explicitly.
    body_child = _FakeContext()
    listener.nodes[body_child] = ast.DefinitionBodyItem(element=ast.RawElement("part p;"))
    listener.exitInterfaceBodyItem(
        _FakeContext(
            definitionMember=body_child,
            variantUsageMember=None,
            interfaceNonOccurrenceUsageMember=None,
            interfaceOccurrenceUsageMember=None,
            sourceSuccessionMember=None,
            aliasMember=None,
            importRule=None,
        )
    )
    variant_child = _FakeContext()
    listener.nodes[variant_child] = ast.VariantUsageMember(ast.RawElement("part p;"))
    listener.exitInterfaceBodyItem(
        _FakeContext(
            definitionMember=None,
            variantUsageMember=variant_child,
            interfaceNonOccurrenceUsageMember=None,
            interfaceOccurrenceUsageMember=None,
            sourceSuccessionMember=None,
            aliasMember=None,
            importRule=None,
        )
    )
    non_occurrence_child = _FakeContext()
    listener.nodes[non_occurrence_child] = ast.InterfaceNonOccurrenceUsageMember(
        ast.RawElement("attribute a;")
    )
    listener.exitInterfaceBodyItem(
        _FakeContext(
            definitionMember=None,
            variantUsageMember=None,
            interfaceNonOccurrenceUsageMember=non_occurrence_child,
            interfaceOccurrenceUsageMember=None,
            sourceSuccessionMember=None,
            aliasMember=None,
            importRule=None,
        )
    )
    occurrence_child = _FakeContext()
    listener.nodes[occurrence_child] = ast.InterfaceOccurrenceUsageMember(ast.RawElement("part p;"))
    listener.exitInterfaceBodyItem(
        _FakeContext(
            definitionMember=None,
            variantUsageMember=None,
            interfaceNonOccurrenceUsageMember=None,
            interfaceOccurrenceUsageMember=occurrence_child,
            sourceSuccessionMember=None,
            aliasMember=None,
            importRule=None,
        )
    )
    source_child = _FakeContext()
    listener.nodes[source_child] = ast.SourceSuccession()
    listener.exitInterfaceBodyItem(
        _FakeContext(
            definitionMember=None,
            variantUsageMember=None,
            interfaceNonOccurrenceUsageMember=None,
            interfaceOccurrenceUsageMember=occurrence_child,
            sourceSuccessionMember=source_child,
            aliasMember=None,
            importRule=None,
        )
    )
    alias_child = _FakeContext()
    listener.nodes[alias_child] = ast.AliasMember(
        target=reference, relationship_body=ast.RelationshipBody(";")
    )
    import_child = _FakeContext()
    listener.nodes[import_child] = ast.ImportRule(
        import_declaration=ast.NamespaceImport(reference),
        relationship_body=ast.RelationshipBody(";"),
    )
    for key, child in (("aliasMember", alias_child), ("importRule", import_child)):
        listener.exitInterfaceBodyItem(
            _FakeContext(
                definitionMember=None,
                variantUsageMember=None,
                interfaceNonOccurrenceUsageMember=None,
                interfaceOccurrenceUsageMember=None,
                sourceSuccessionMember=None,
                aliasMember=child if key == "aliasMember" else None,
                importRule=child if key == "importRule" else None,
            )
        )
    _error(
        "exitInterfaceBodyItem",
        _FakeContext(
            definitionMember=None,
            variantUsageMember=None,
            interfaceNonOccurrenceUsageMember=None,
            interfaceOccurrenceUsageMember=None,
            sourceSuccessionMember=None,
            aliasMember=None,
            importRule=None,
        ),
    )
    _error(
        "exitInterfaceBodyItem",
        _FakeContext(
            definitionMember=None,
            variantUsageMember=None,
            interfaceNonOccurrenceUsageMember=None,
            interfaceOccurrenceUsageMember=occurrence_child,
            sourceSuccessionMember=source_child,
            aliasMember=None,
            importRule=None,
        ),
        (occurrence_child, ast.RawElement("bad")),
    )
    _error(
        "exitInterfaceBodyItem",
        _FakeContext(
            definitionMember=None,
            variantUsageMember=None,
            interfaceNonOccurrenceUsageMember=None,
            interfaceOccurrenceUsageMember=occurrence_child,
            sourceSuccessionMember=source_child,
            aliasMember=None,
            importRule=None,
        ),
        (source_child, ast.RawElement("bad")),
        (occurrence_child, ast.InterfaceOccurrenceUsageMember(ast.RawElement("part p;"))),
    )

    member_usage_child = _FakeContext()
    listener.nodes[member_usage_child] = ast.RawElement("attribute a;")
    listener.exitInterfaceNonOccurrenceUsageMember(
        _FakeContext(
            interfaceNonOccurrenceUsageElement=member_usage_child,
            memberPrefix=_FakeContext(),
        )
    )
    _error(
        "exitInterfaceNonOccurrenceUsageMember",
        _FakeContext(interfaceNonOccurrenceUsageElement=None, memberPrefix=_FakeContext()),
    )
    interface_non_occurrence_child = _FakeContext()
    listener.nodes[interface_non_occurrence_child] = ast.RawElement("attribute a;")
    listener.exitInterfaceNonOccurrenceUsageElement(
        _FakeContext(
            referenceUsage=interface_non_occurrence_child,
            attributeUsage=None,
            enumerationUsage=None,
            bindingConnectorAsUsage=None,
            successionAsUsage=None,
        )
    )
    listener.exitInterfaceNonOccurrenceUsageElement(
        _FakeContext(
            referenceUsage=interface_non_occurrence_child,
            attributeUsage=None,
            enumerationUsage=None,
            bindingConnectorAsUsage=None,
            successionAsUsage=None,
        )
    )
    raw_non_occurrence_context = _FakeContext(
        referenceUsage=None,
        attributeUsage=None,
        enumerationUsage=None,
        bindingConnectorAsUsage=None,
        successionAsUsage=None,
    )
    listener.exitInterfaceNonOccurrenceUsageElement(raw_non_occurrence_context)
    assert isinstance(listener.node_for(raw_non_occurrence_context), ast.RawElement)
    listener.exitInterfaceOccurrenceUsageMember(
        _FakeContext(
            interfaceOccurrenceUsageElement=member_usage_child,
            memberPrefix=_FakeContext(),
        )
    )
    _error(
        "exitInterfaceOccurrenceUsageMember",
        _FakeContext(interfaceOccurrenceUsageElement=None, memberPrefix=_FakeContext()),
    )
    occurrence_element_child = _FakeContext()
    listener.nodes[occurrence_element_child] = ast.RawElement("part p;")
    listener.exitInterfaceOccurrenceUsageElement(
        _FakeContext(
            defaultInterfaceEnd=occurrence_element_child,
            endOccurrenceUsageElement=None,
            structureUsageElement=None,
            behaviorUsageElement=None,
        )
    )
    listener.exitInterfaceOccurrenceUsageElement(
        _FakeContext(
            defaultInterfaceEnd=occurrence_element_child,
            endOccurrenceUsageElement=None,
            structureUsageElement=None,
            behaviorUsageElement=None,
        )
    )
    _error(
        "exitInterfaceOccurrenceUsageElement",
        _FakeContext(
            defaultInterfaceEnd=None,
            endOccurrenceUsageElement=None,
            structureUsageElement=None,
            behaviorUsageElement=None,
        ),
    )
    raw_occurrence_context = _FakeContext(
        defaultInterfaceEnd=occurrence_element_child,
        endOccurrenceUsageElement=None,
        structureUsageElement=None,
        behaviorUsageElement=None,
    )
    listener.nodes[occurrence_element_child] = ast.RawElement("bad")
    listener.exitInterfaceOccurrenceUsageElement(raw_occurrence_context)
    assert isinstance(listener.node_for(raw_occurrence_context), ast.RawElement)
    unassembled_occurrence_context = _FakeContext(
        defaultInterfaceEnd=occurrence_element_child,
        endOccurrenceUsageElement=None,
        structureUsageElement=None,
        behaviorUsageElement=None,
    )
    listener.nodes.pop(occurrence_element_child)
    listener.exitInterfaceOccurrenceUsageElement(unassembled_occurrence_context)
    assert isinstance(listener.node_for(unassembled_occurrence_context), ast.RawElement)
    listener.nodes[occurrence_element_child] = ast.RawElement("bad")
    usage_child = _FakeContext()
    listener.nodes[usage_child] = ast.Usage(ast.DefinitionBody(declaration_only=True))
    listener.exitDefaultInterfaceEnd(_FakeContext(usage=usage_child))
    _error("exitDefaultInterfaceEnd", _FakeContext(usage=None))
    listener.exitInterfaceUsageDeclaration(
        _FakeContext(usageDeclaration=None, valuePart=None, interfacePart=None, CONNECT=None)
    )
    _error(
        "exitInterfaceUsageDeclaration",
        _FakeContext(
            usageDeclaration=usage_child,
            valuePart=None,
            interfacePart=None,
            CONNECT=None,
        ),
        (usage_child, ast.RawElement("bad")),
    )

    unassembled_interface_body_item = _FakeContext()
    _error(
        "exitInterfaceBody",
        _FakeContext(SEMI=None, interfaceBodyItem=[unassembled_interface_body_item]),
    )
    _error(
        "exitInterfaceUsageDeclaration",
        _FakeContext(
            usageDeclaration=None,
            valuePart=usage_child,
            interfacePart=None,
            CONNECT=None,
        ),
        (usage_child, ast.RawElement("bad")),
    )
    _error(
        "exitInterfaceUsageDeclaration",
        _FakeContext(
            usageDeclaration=None,
            valuePart=None,
            interfacePart=usage_child,
            CONNECT=None,
        ),
        (usage_child, ast.RawElement("bad")),
    )

    # Feature/end wrappers: cover both alternatives and their required-child guards.
    name_context = _FakeContext()
    listener.values[name_context] = "feature"
    listener.exitFeatureIdentification(_FakeContext(name=[name_context], LT=None))
    listener.exitFeatureIdentification(
        _FakeContext(name=[name_context, name_context], LT=_FakeToken("<"))
    )
    _error("exitFeatureIdentification", _FakeContext(name=[]))

    feature_identification_context = _FakeContext()
    specialization_context = _FakeContext()
    listener.nodes[feature_identification_context] = ast.FeatureIdentification(declared_name="f")
    listener.nodes[specialization_context] = ast.FeatureSpecializationPart()
    listener.exitFeatureDeclaration(
        _FakeContext(
            featureIdentification=feature_identification_context,
            featureSpecializationPart=specialization_context,
            ALL=_FakeToken("all"),
            conjugationPart=None,
            featureRelationshipPart=[],
        )
    )
    _error(
        "exitFeatureDeclaration",
        _FakeContext(
            featureIdentification=feature_identification_context,
            featureSpecializationPart=specialization_context,
            ALL=None,
            conjugationPart=None,
            featureRelationshipPart=[],
        ),
        (feature_identification_context, ast.RawElement("bad")),
    )
    _error(
        "exitFeatureDeclaration",
        _FakeContext(
            featureIdentification=feature_identification_context,
            featureSpecializationPart=specialization_context,
            ALL=None,
            conjugationPart=None,
            featureRelationshipPart=[],
        ),
        (specialization_context, ast.RawElement("bad")),
        (feature_identification_context, ast.FeatureIdentification(declared_name="f")),
    )

    basic_feature_context = _FakeContext()
    feature_declaration_context = _FakeContext()
    listener.values[basic_feature_context] = "end"
    listener.nodes[feature_declaration_context] = ast.FeatureDeclaration()
    listener.exitOwnedCrossFeature(
        _FakeContext(
            basicFeaturePrefix=basic_feature_context, featureDeclaration=feature_declaration_context
        )
    )
    _error(
        "exitOwnedCrossFeature",
        _FakeContext(basicFeaturePrefix=basic_feature_context, featureDeclaration=None),
    )
    basic_usage_context = _FakeContext(
        featureDirection=None,
        DERIVED=None,
        ABSTRACT=None,
        VARIATION=None,
        CONSTANT=None,
    )
    listener.exitOwnedCrossFeature(
        _FakeContext(
            basicFeaturePrefix=None, basicUsagePrefix=basic_usage_context, usageDeclaration=None
        )
    )
    _error("exitOwnedCrossFeature", _FakeContext(basicFeaturePrefix=None, basicUsagePrefix=None))

    cross_context = _FakeContext()
    listener.nodes[cross_context] = ast.OwnedCrossFeature()
    listener.exitOwnedCrossFeatureMember(_FakeContext(ownedCrossFeature=cross_context))
    end_prefix_context = _FakeContext()
    listener.nodes[end_prefix_context] = ast.EndUsagePrefix(ast.OwnedCrossFeature())
    completion_context = _FakeContext()
    listener.nodes[completion_context] = ast.Usage(ast.DefinitionBody(declaration_only=True))
    listener.exitEndUsagePrefix(_FakeContext(ownedCrossFeatureMember=cross_context))
    listener.exitEndFeatureUsage(
        _FakeContext(
            endUsagePrefix=end_prefix_context,
            featureDeclaration=feature_declaration_context,
            usageCompletion=completion_context,
        ),
    )
    _error("exitEndUsagePrefix", _FakeContext(ownedCrossFeatureMember=None))
    _error(
        "exitEndFeatureUsage",
        _FakeContext(
            endUsagePrefix=None,
            featureDeclaration=feature_declaration_context,
            usageCompletion=completion_context,
        ),
    )
    _error(
        "exitEndFeatureUsage",
        _FakeContext(
            endUsagePrefix=end_prefix_context,
            featureDeclaration=None,
            usageCompletion=completion_context,
        ),
        (end_prefix_context, ast.EndUsagePrefix(ast.OwnedCrossFeature())),
    )
    _error(
        "exitEndFeatureUsage",
        _FakeContext(
            endUsagePrefix=end_prefix_context,
            featureDeclaration=feature_declaration_context,
            usageCompletion=None,
        ),
        (end_prefix_context, ast.EndUsagePrefix(ast.OwnedCrossFeature())),
        (feature_declaration_context, ast.FeatureDeclaration()),
    )


def test_listener_binding_and_succession_defensive_paths():
    """Cover required child validation for binding and succession usages."""
    reference = ast.QualifiedReference(["A"])
    connector_end = ast.ConnectorEnd(reference)
    body = ast.DefinitionBody(declaration_only=True)

    def context(listener, prefix, ends, declaration=None, usage_body=body):
        prefix_context = _FakeContext()
        end_contexts = [_FakeContext(), _FakeContext()]
        declaration_context = _FakeContext() if declaration is not None else None
        body_context = _FakeContext()
        listener.nodes[prefix_context] = prefix
        for end_context, end in zip(end_contexts, ends):
            listener.nodes[end_context] = end
        if declaration_context is not None:
            listener.nodes[declaration_context] = declaration
        listener.nodes[body_context] = usage_body
        return _FakeContext(
            usagePrefix=prefix_context,
            usageDeclaration=declaration_context,
            connectorEndMember=end_contexts,
            usageBody=body_context,
        )

    def expect_error(listener, callback, parser_context):
        with pytest.raises((ValueError, TypeError, AttributeError)):
            getattr(listener, callback)(parser_context)

    # Each production has the same four required-child guards. Keep the
    # contexts independent so every branch is exercised without relying on
    # parser recovery or private listener state.
    for callback in ("exitBindingConnectorAsUsage", "exitSuccessionAsUsage"):
        listener = _fake_listener()
        expect_error(
            listener,
            callback,
            context(listener, ast.RawElement("bad prefix"), [connector_end, connector_end]),
        )

        listener = _fake_listener()
        one_end_context = _FakeContext()
        body_context = _FakeContext()
        prefix_context = _FakeContext()
        listener.nodes[prefix_context] = ast.UsagePrefix()
        listener.nodes[one_end_context] = connector_end
        listener.nodes[body_context] = body
        expect_error(
            listener,
            callback,
            _FakeContext(
                usagePrefix=prefix_context,
                usageDeclaration=None,
                connectorEndMember=[one_end_context],
                usageBody=body_context,
            ),
        )

        listener = _fake_listener()
        expect_error(
            listener,
            callback,
            context(
                listener,
                ast.UsagePrefix(),
                [connector_end, connector_end],
                declaration=ast.RawElement("bad declaration"),
            ),
        )

        listener = _fake_listener()
        expect_error(
            listener,
            callback,
            context(
                listener,
                ast.UsagePrefix(),
                [connector_end, connector_end],
                usage_body=ast.RawElement("bad body"),
            ),
        )


def test_listener_relation_and_body_error_paths_are_explicitly_covered():
    """Exercise defensive branches for relationship and body dispatch rules."""

    def mapped(listener, node):
        context = _FakeContext()
        listener.nodes[context] = node
        return context

    listener = _fake_listener()
    bad = mapped(listener, ast.RawElement("bad"))
    _error(
        "exitConjugationPart",
        _FakeContext(ownedConjugation=bad),
        (bad, ast.RawElement("bad")),
    )
    _error(
        "exitInvertingPart",
        _FakeContext(ownedFeatureInverting=bad),
        (bad, ast.RawElement("bad")),
    )

    for callback, child_name in (
        ("exitTypeFeaturingPart", "ownedTypeFeaturing"),
        ("exitDisjoiningPart", "ownedDisjoining"),
        ("exitUnioningPart", "unioning"),
        ("exitIntersectingPart", "intersecting"),
        ("exitDifferencingPart", "differencing"),
    ):
        child = _FakeContext()
        _error(
            callback,
            _FakeContext(**{child_name: [child]}),
            (child, ast.RawElement("bad")),
        )

    _error("exitTypeRelationshipPart", _FakeContext())
    _error("exitFeatureRelationshipPart", _FakeContext())

    bad_conjugation = mapped(listener, ast.RawElement("bad conjugation"))
    _error(
        "exitFeatureDeclaration",
        _FakeContext(
            featureIdentification=None,
            featureSpecializationPart=None,
            conjugationPart=bad_conjugation,
            featureRelationshipPart=[],
        ),
        (bad_conjugation, ast.RawElement("bad conjugation")),
    )
    bad_relationship = mapped(listener, ast.RawElement("bad relationship"))
    _error(
        "exitFeatureDeclaration",
        _FakeContext(
            featureIdentification=None,
            featureSpecializationPart=None,
            conjugationPart=None,
            featureRelationshipPart=[bad_relationship],
        ),
        (bad_relationship, ast.RawElement("bad relationship")),
    )

    bad_usage = mapped(listener, ast.RawElement("bad usage"))
    _error(
        "exitReturnParameterMember",
        _FakeContext(usageElement=bad_usage),
        (bad_usage, ast.RawElement("bad usage")),
    )
    invalid_usage = mapped(listener, object())
    _error(
        "exitReturnParameterMember",
        _FakeContext(usageElement=invalid_usage),
        (invalid_usage, object()),
    )
    _error("exitCalculationBodyItem", _FakeContext())
    raw_calculation_item = _FakeContext(actionBodyItem=_FakeContext())
    listener.exitCalculationBodyItem(raw_calculation_item)
    assert isinstance(listener.node_for(raw_calculation_item), ast.RawElement)

    _error("exitCaseBodyItem", _FakeContext())
    _error("exitRequirementBodyItem", _FakeContext())
    _error("exitViewDefinitionBodyItem", _FakeContext())
    _error("exitViewBodyItem", _FakeContext())

    view_body = _FakeContext(SEMI=_FakeToken(), viewBodyItem=[])
    listener.exitViewBody(view_body)
    assert listener.node_for(view_body) == ast.ViewBody(declaration_only=True)

    _error(
        "exitEnumerationUsageMember",
        _FakeContext(enumeratedValue=bad_usage),
        (bad_usage, ast.RawElement("bad usage")),
    )
    _error(
        "exitEnumeratedValue",
        _FakeContext(usage=bad_usage),
        (bad_usage, ast.RawElement("bad usage")),
    )


def test_listener_dependency_and_definition_validation_paths():
    """Cover dependency endpoint splitting and typed definition guards."""

    def mapped(listener, node):
        context = _FakeContext()
        listener.nodes[context] = node
        return context

    listener = _fake_listener()
    first = mapped(listener, QualifiedReference(["A"]))
    second = mapped(listener, QualifiedReference(["B"]))
    identification = mapped(listener, ast.Identification(declared_name="D"))
    declaration = _FakeContext(
        qualifiedName=[first, second],
        identification=identification,
    )
    body = mapped(listener, ast.RelationshipBody("connect A to B"))
    dependency = _FakeContext(
        qualifiedName=[],
        dependencyDeclaration=declaration,
        relationshipBody=body,
        prefixMetadataAnnotation=[],
    )
    listener.exitDependency(dependency)
    result = listener.node_for(dependency)
    assert isinstance(result, ast.Dependency)
    assert result.source_references == [ast.QualifiedReference(["A"])]
    assert result.target_references == [ast.QualifiedReference(["B"])]

    declaration_without_identification = _FakeContext(
        qualifiedName=[first, second],
        identification=None,
    )
    dependency_without_identification = _FakeContext(
        qualifiedName=[],
        dependencyDeclaration=declaration_without_identification,
        relationshipBody=body,
        prefixMetadataAnnotation=[],
    )
    listener.exitDependency(dependency_without_identification)
    assert isinstance(listener.node_for(dependency_without_identification), ast.Dependency)

    no_target_body = mapped(listener, ast.RelationshipBody("A to B"))
    no_target_dependency = _FakeContext(
        qualifiedName=[],
        dependencyDeclaration=None,
        identification=None,
        TO=None,
        relationshipBody=no_target_body,
        prefixMetadataAnnotation=[],
    )
    listener.exitDependency(no_target_dependency)
    assert isinstance(listener.node_for(no_target_dependency), ast.Dependency)
    invalid_dependency_body = _FakeContext()
    _error(
        "exitDependency",
        _FakeContext(
            qualifiedName=[],
            dependencyDeclaration=None,
            identification=None,
            TO=None,
            relationshipBody=invalid_dependency_body,
            prefixMetadataAnnotation=[],
        ),
        (invalid_dependency_body, object()),
    )

    for callback in (
        "exitEnumerationDefinition",
        "exitAllocationDefinition",
        "exitFlowDefinition",
        "exitRenderingDefinition",
        "exitMetadataDefinition",
        "exitExtendedDefinition",
    ):
        _error(callback, _FakeContext())

    _error("exitCalculationDefinition", _FakeContext())
    prefix = mapped(listener, ast.OccurrenceDefinitionPrefix())
    bad_declaration = mapped(listener, ast.RawElement("bad declaration"))
    bad_body = mapped(listener, ast.RawElement("bad body"))
    _error(
        "exitCalculationDefinition",
        _FakeContext(
            occurrenceDefinitionPrefix=prefix,
            definitionDeclaration=bad_declaration,
            calculationBody=bad_body,
        ),
        (prefix, ast.OccurrenceDefinitionPrefix()),
        (bad_declaration, ast.RawElement("bad declaration")),
        (bad_body, ast.RawElement("bad body")),
    )
    declaration = mapped(listener, ast.DefinitionDeclaration())
    invalid_body = mapped(listener, object())
    _error(
        "exitCalculationDefinition",
        _FakeContext(
            occurrenceDefinitionPrefix=prefix,
            definitionDeclaration=declaration,
            calculationBody=invalid_body,
        ),
        (prefix, ast.OccurrenceDefinitionPrefix()),
        (declaration, ast.DefinitionDeclaration()),
        (invalid_body, object()),
    )
    _error("exitFlowEnd", _FakeContext(qualifiedName=[]))


def test_listener_usage_validation_and_raw_fallback_paths():
    """Cover typed usage guards and the two intentional raw compatibility exits."""

    _error("exitRequirementUsage", _FakeContext())
    listener = _fake_listener()
    prefix_context = _FakeContext()
    body_context = _FakeContext()
    listener.nodes[prefix_context] = ast.OccurrenceUsagePrefix()
    listener.nodes[body_context] = ast.RequirementBody()
    with pytest.raises(ValueError):
        listener.exitRequirementUsage(
            _FakeContext(
                occurrenceUsagePrefix=prefix_context,
                constraintUsageDeclaration=None,
                requirementBody=body_context,
            )
        )

    for callback in (
        "exitCalculationUsage",
        "exitConstraintUsage",
        "exitCaseUsage",
        "exitViewUsage",
        "exitViewRenderingUsage",
        "exitRenderingUsage",
        "exitAllocationUsage",
        "exitMessage",
        "exitFlowUsage",
        "exitSuccessionFlowUsage",
        "exitIncludeUseCaseUsage",
        "exitAssertConstraintUsage",
        "exitSatisfyRequirementUsage",
        "exitEnumerationUsage",
    ):
        _error(callback, _FakeContext())

    listener = _fake_listener()
    structure_context = _FakeContext()
    listener.exitStructureUsageElement(structure_context)
    assert isinstance(listener.node_for(structure_context), ast.RawElement)
    definition_context = _FakeContext()
    listener.exitDefinitionElement(definition_context)
    assert isinstance(listener.node_for(definition_context), ast.RawElement)
