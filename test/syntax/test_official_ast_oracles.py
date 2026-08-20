"""Independent handwritten AST oracles for the reviewed state examples.

The broad Section 7 tests also compare parser output with checked-in snapshots.
Those snapshots are useful for drift detection, but a snapshot generated from
the parser cannot independently establish that the parser assembled the right
fields.  This module therefore constructs a focused set of state and
transition nodes directly from the public AST dataclasses and compares them
with the corresponding parsed nodes.  No expected value is loaded from a
parser result, JSON snapshot, upstream checkout, or network resource.

Only ``span`` provenance is intentionally outside dataclass equality.  Every
other field of each manually constructed node participates in the assertions,
including structured expressions, trigger payloads, effect actions, target
transition form, and the full-transition guard ordering flag.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pytest

from pysysmlv2 import parse
from pysysmlv2.syntax import (
    AcceptParameterPart,
    ActionBody,
    ActionUsage,
    ActionUsageDeclaration,
    ArgumentList,
    AttributeUsage,
    BehaviorUsageMember,
    BehaviorUsageStateMember,
    BracketExpression,
    Comment,
    ConstructorExpression,
    DefinitionBody,
    DefinitionBodyItem,
    DefinitionDeclaration,
    DoActionMember,
    DottedQualifiedReference,
    EffectBehaviorMember,
    EmptyActionUsage,
    EntryActionMember,
    EntryTransitionMember,
    ExitActionMember,
    FeatureChain,
    FeatureReferenceExpression,
    FeatureSpecialization,
    FeatureSpecializationPart,
    GuardExpressionMember,
    Identification,
    IntegerLiteral,
    NodeParameter,
    NonOccurrenceUsageMember,
    OccurrenceDefinitionPrefix,
    OccurrenceUsagePrefix,
    OwnedFeatureTyping,
    PayloadFeature,
    PayloadParameter,
    PerformActionUsageDeclaration,
    PortUsage,
    QualifiedReference,
    SendActionUsage,
    SenderReceiverPart,
    SendNodeDeclaration,
    SequenceExpression,
    StateDefBody,
    StateDefinition,
    StatePerformActionUsage,
    StateUsage,
    StateUsageBody,
    StructureUsageMember,
    TargetTransitionForm,
    TargetTransitionUsage,
    TargetTransitionUsageMember,
    TransitionPerformActionUsage,
    TransitionSuccession,
    TransitionUsage,
    TransitionUsageMember,
    TriggerActionMember,
    TriggerExpression,
    UnaryExpression,
    Usage,
    UsageDeclaration,
    UsagePrefix,
)

pytestmark = pytest.mark.unit


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "test" / "testfile" / "omg_sysml2_language" / "section7"


def _q(name: str) -> QualifiedReference:
    """Construct one unresolved qualified reference from its source spelling."""
    return QualifiedReference([name])


def _d(name: str) -> DottedQualifiedReference:
    """Construct one dotted-qualified reference with one qualified child."""
    return DottedQualifiedReference([_q(name)])


def _fc(name: str) -> FeatureChain:
    """Construct a one-segment feature chain."""
    return FeatureChain([_q(name)])


def _expr(name: str) -> FeatureReferenceExpression:
    """Construct a feature-reference expression for a single name."""
    return FeatureReferenceExpression(_q(name))


def _ident(name: str) -> Identification:
    """Construct an ordinary declared-name identification."""
    return Identification(declared_name=name)


def _decl(name: str, type_name: Optional[str] = None) -> UsageDeclaration:
    """Construct a usage declaration with an optional ``: Type`` relation."""
    specialization = None
    if type_name is not None:
        specialization = FeatureSpecializationPart(
            [FeatureSpecialization(":", [OwnedFeatureTyping(_d(type_name))])]
        )
    return UsageDeclaration(_ident(name), specialization)


def _empty_definition_body() -> DefinitionBody:
    """Construct the declaration-only generic definition body used by usages."""
    return DefinitionBody(declaration_only=True)


def _empty_action_body() -> ActionBody:
    """Construct the declaration-only action body used by state transitions."""
    return ActionBody(declaration_only=True)


def _typed_attribute(name: str, type_name: Optional[str] = "Boolean") -> NonOccurrenceUsageMember:
    """Construct an ``in attribute`` member with an optional type."""
    return NonOccurrenceUsageMember(
        AttributeUsage(
            UsagePrefix(feature_direction="in"),
            Usage(_empty_definition_body(), _decl(name, type_name)),
        )
    )


def _port(name: str = "commPort") -> StructureUsageMember:
    """Construct an untyped port member."""
    return StructureUsageMember(
        PortUsage(OccurrenceUsagePrefix(), Usage(_empty_definition_body(), _decl(name)))
    )


def _entry_action(
    name: Optional[str] = None,
    target: Optional[str] = None,
) -> EntryActionMember:
    """Construct an entry action, optionally followed by a target succession."""
    if name is None:
        action = EmptyActionUsage()
    else:
        action = StatePerformActionUsage(
            PerformActionUsageDeclaration(
                action_usage_declaration=_decl(name),
                is_action=True,
            ),
            _empty_action_body(),
        )
    transitions = []
    if target is not None:
        transitions.append(EntryTransitionMember(TransitionSuccession(_q(target))))
    return EntryActionMember(action, entry_transition_members=transitions)


def _state(name: str, body: Optional[StateUsageBody] = None) -> StateUsage:
    """Construct an untyped state usage and its state-body wrapper."""
    return StateUsage(
        OccurrenceUsagePrefix(),
        ActionUsageDeclaration(_decl(name)),
        body if body is not None else StateUsageBody(is_declaration_only=True),
    )


def _state_member(
    name: str,
    target: Optional[str] = None,
) -> BehaviorUsageStateMember:
    """Construct a state-body member with an optional target shorthand."""
    targets = []
    if target is not None:
        targets = [
            TargetTransitionUsageMember(
                TargetTransitionUsage(
                    TransitionSuccession(_q(target)),
                    _empty_action_body(),
                )
            )
        ]
    return BehaviorUsageStateMember(
        BehaviorUsageMember(_state(name)), target_transition_members=targets
    )


def _guard(name: str) -> GuardExpressionMember:
    """Construct a simple ``if name`` guard."""
    return GuardExpressionMember(_expr(name))


def _not_guard(name: str) -> GuardExpressionMember:
    """Construct a ``if not name`` guard with a structured unary expression."""
    return GuardExpressionMember(UnaryExpression("not ", _expr(name)))


def _signal_trigger(name: str, via: Optional[str] = None) -> TriggerActionMember:
    """Construct an ``accept Signal [via Port]`` trigger."""
    via_parameter = NodeParameter(_expr(via)) if via is not None else None
    payload = PayloadParameter(
        payload_feature=PayloadFeature(owned_feature_typing=OwnedFeatureTyping(_d(name)))
    )
    return TriggerActionMember(AcceptParameterPart(payload, via_parameter))


def _after_trigger() -> TriggerActionMember:
    """Construct the structured ``accept after 5[min]`` trigger."""
    duration = BracketExpression(
        IntegerLiteral("5"),
        SequenceExpression([_expr("min")]),
    )
    return TriggerActionMember(
        AcceptParameterPart(
            PayloadParameter(trigger_expression=TriggerExpression("after", duration))
        )
    )


def _power_up_effect() -> EffectBehaviorMember:
    """Construct the named ``do action powerUp : PowerUp;`` effect."""
    return EffectBehaviorMember(
        TransitionPerformActionUsage(
            PerformActionUsageDeclaration(
                action_usage_declaration=_decl("powerUp", "PowerUp"),
                is_action=True,
            ),
            _empty_action_body(),
        )
    )


def _timeout_effect(*, target_form: bool) -> EffectBehaviorMember:
    """Construct the ``send new TimeoutSignal() via commPort`` effect.

    Full ``TransitionUsage`` carries no action body for this effect, while the
    target shorthand in OnOff5 carries an explicit declaration-only body.
    """
    send = SendActionUsage(
        SendNodeDeclaration(
            NodeParameter(ConstructorExpression(_q("TimeoutSignal"), ArgumentList())),
            sender_receiver_part=SenderReceiverPart(via_parameter=NodeParameter(_expr("commPort"))),
        ),
        _empty_action_body() if target_form else None,
    )
    return EffectBehaviorMember(send)


def _transition(
    source: str,
    target: str,
    *,
    name: Optional[str] = None,
    trigger: Optional[TriggerActionMember] = None,
    guard: Optional[GuardExpressionMember] = None,
    effect: Optional[EffectBehaviorMember] = None,
    guard_before_trigger: bool = False,
) -> TransitionUsageMember:
    """Construct a complete transition with all grammar-owned fields explicit."""
    return TransitionUsageMember(
        TransitionUsage(
            _fc(source),
            TransitionSuccession(_q(target)),
            _empty_action_body(),
            usage_declaration=_decl(name) if name is not None else None,
            is_first=True,
            trigger_action_member=trigger,
            guard_expression_member=guard,
            effect_behavior_member=effect,
            guard_before_trigger=guard_before_trigger,
        )
    )


def _target(
    target: str,
    *,
    trigger: Optional[TriggerActionMember] = None,
    guard: Optional[GuardExpressionMember] = None,
    effect: Optional[EffectBehaviorMember] = None,
) -> TargetTransitionUsageMember:
    """Construct a normative target shorthand (trigger-before-guard or bare)."""
    return TargetTransitionUsageMember(
        TargetTransitionUsage(
            TransitionSuccession(_q(target)),
            _empty_action_body(),
            form=TargetTransitionForm.BARE,
            trigger_action_member=trigger,
            guard_expression_member=guard,
            effect_behavior_member=effect,
        )
    )


def _state_definition(name: str, members: list[object]) -> StateDefinition:
    """Construct a state definition with its ordered state-body members."""
    return StateDefinition(
        OccurrenceDefinitionPrefix(),
        DefinitionDeclaration(_ident(name)),
        StateDefBody(state_body_members=members),
    )


def _onoff3_oracle() -> StateDefinition:
    """Return the hand-authored AST for the complete OnOff3 state definition."""
    return _state_definition(
        "OnOff3",
        [
            _typed_attribute("isInitOff"),
            _typed_attribute("isEnabled"),
            _port(),
            _entry_action("init"),
            _transition("init", "off", guard=_guard("isInitOff")),
            _transition("init", "on", guard=_not_guard("isInitOff")),
            _state_member("off"),
            _state_member("on"),
            _transition(
                "off",
                "on",
                name="off_on",
                trigger=_signal_trigger("TurnOn", "commPort"),
                guard=_guard("isEnabled"),
            ),
            _transition(
                "on",
                "off",
                name="on_off",
                trigger=_after_trigger(),
                guard=_guard("isEnabled"),
            ),
        ],
    )


def _onoff1_oracle() -> StateDefinition:
    """Return the hand-authored AST for the transition-only OnOff1 model."""
    return _state_definition(
        "OnOff1",
        [
            _entry_action(target="off"),
            _state_member("off"),
            _state_member("on"),
            _transition("off", "on", name="off_on"),
            _transition("on", "off", name="on_off"),
        ],
    )


def _onoff2_oracle() -> StateDefinition:
    """Return the hand-authored AST for the triggered OnOff2 model."""
    return _state_definition(
        "OnOff2",
        [
            _port(),
            _entry_action(target="off"),
            _state_member("off"),
            _state_member("on"),
            _transition(
                "off",
                "on",
                name="off_on",
                trigger=_signal_trigger("TurnOn", "commPort"),
            ),
            _transition("on", "off", name="on_off", trigger=_after_trigger()),
        ],
    )


def _onoff4_oracle() -> StateDefinition:
    """Return the hand-authored AST for full-transition guard-first OnOff4."""
    return _state_definition(
        "OnOff4",
        [
            _typed_attribute("isInitOff", None),
            _typed_attribute("isEnabled", None),
            _port(),
            _entry_action("init"),
            _transition("init", "off", guard=_guard("isInitOff")),
            _transition("init", "on", guard=_not_guard("isInitOff")),
            _state_member("off"),
            _state_member("on"),
            _transition(
                "off",
                "on",
                name="off_on",
                trigger=_signal_trigger("TurnOn", "commPort"),
                guard=_guard("isEnabled"),
                effect=_power_up_effect(),
                guard_before_trigger=True,
            ),
            _transition(
                "on",
                "off",
                name="on_off",
                trigger=_after_trigger(),
                guard=_guard("isEnabled"),
                effect=_timeout_effect(target_form=False),
                guard_before_trigger=True,
            ),
        ],
    )


def _onoff5_oracle() -> StateDefinition:
    """Return the hand-authored AST for target shorthand OnOff5."""
    return _state_definition(
        "OnOff5",
        [
            _typed_attribute("isInitOff", None),
            _typed_attribute("isEnabled", None),
            _port(),
            EntryActionMember(
                EmptyActionUsage(),
                entry_transition_members=[
                    EntryTransitionMember(
                        TransitionSuccession(_q("off")), guard=_expr("isInitOff")
                    ),
                    EntryTransitionMember(
                        TransitionSuccession(_q("on")),
                        guard=UnaryExpression("not ", _expr("isInitOff")),
                    ),
                ],
            ),
            _state_member("off"),
            _state_member("on"),
        ],
    )


def _onoff5_oracle_with_transitions() -> StateDefinition:
    """Return OnOff5 with the two target transitions attached to states."""
    state = _onoff5_oracle()
    body = state.state_def_body
    body.state_body_members[4] = BehaviorUsageStateMember(
        BehaviorUsageMember(_state("off")),
        target_transition_members=[
            _target(
                "on",
                trigger=_signal_trigger("TurnOn", "commPort"),
                guard=_guard("isEnabled"),
                effect=_power_up_effect(),
            )
        ],
    )
    body.state_body_members[5] = BehaviorUsageStateMember(
        BehaviorUsageMember(_state("on")),
        target_transition_members=[
            _target(
                "off",
                trigger=_after_trigger(),
                guard=_guard("isEnabled"),
                effect=_timeout_effect(target_form=True),
            )
        ],
    )
    return state


def _onoff6_oracle() -> StateDefinition:
    """Return the hand-authored AST for OnOff6 terminate and target forms."""
    stop = ActionUsage(
        OccurrenceUsagePrefix(),
        ActionUsageDeclaration(_decl("stop")),
        _empty_action_body(),
        is_terminate=True,
    )
    return _state_definition(
        "OnOff6",
        [
            _port(),
            _entry_action(target="off"),
            BehaviorUsageStateMember(
                BehaviorUsageMember(_state("off")),
                target_transition_members=[
                    _target("on", trigger=_signal_trigger("TurnOn", "commPort")),
                    _target("stop", trigger=_signal_trigger("Abort", "commPort")),
                ],
            ),
            BehaviorUsageStateMember(
                BehaviorUsageMember(_state("on")),
                target_transition_members=[_target("done", trigger=_after_trigger())],
            ),
            BehaviorUsageStateMember(BehaviorUsageMember(stop)),
        ],
    )


def _table_state_actions_oracle() -> StateUsage:
    """Return the hand-authored Table 17 state-actions usage."""
    return StateUsage(
        OccurrenceUsagePrefix(),
        ActionUsageDeclaration(_decl("state1", "StateDef1")),
        StateUsageBody(
            state_body_members=[
                EntryActionMember(
                    StatePerformActionUsage(
                        PerformActionUsageDeclaration(referenced_feature=_q("action1")),
                        _empty_action_body(),
                    )
                ),
                DoActionMember(
                    StatePerformActionUsage(
                        PerformActionUsageDeclaration(referenced_feature=_q("action2")),
                        _empty_action_body(),
                    )
                ),
                ExitActionMember(
                    StatePerformActionUsage(
                        PerformActionUsageDeclaration(referenced_feature=_q("action3")),
                        _empty_action_body(),
                    )
                ),
            ]
        ),
    )


def _table_composite_sequential_oracle() -> StateUsage:
    """Return the hand-authored sequential composite state from Table 17."""
    transition = _transition(
        "state1",
        "state2",
        trigger=_signal_trigger("trigger1"),
        guard=_guard("guard1"),
        effect=EffectBehaviorMember(
            TransitionPerformActionUsage(
                PerformActionUsageDeclaration(referenced_feature=_q("action1"))
            )
        ),
    )
    return StateUsage(
        OccurrenceUsagePrefix(),
        ActionUsageDeclaration(_decl("compositeState1")),
        StateUsageBody(
            state_body_members=[
                EntryActionMember(
                    EmptyActionUsage(),
                    entry_transition_members=[
                        EntryTransitionMember(TransitionSuccession(_q("state1")))
                    ],
                ),
                _state_member("state1"),
                transition,
                _state_member("state2", target="done"),
            ]
        ),
    )


def _table_composite_parallel_oracle() -> StateUsage:
    """Return the hand-authored parallel composite state from Table 17."""

    def nested(name: str, target: str) -> BehaviorUsageStateMember:
        return BehaviorUsageStateMember(
            BehaviorUsageMember(
                _state(
                    name,
                    StateUsageBody(
                        state_body_members=[
                            EntryActionMember(
                                EmptyActionUsage(),
                                entry_transition_members=[
                                    EntryTransitionMember(TransitionSuccession(_q(target)))
                                ],
                            ),
                            _state_member(target),
                        ]
                    ),
                )
            )
        )

    return StateUsage(
        OccurrenceUsagePrefix(),
        ActionUsageDeclaration(_decl("compositeState2")),
        StateUsageBody(
            is_parallel=True,
            state_body_members=[nested("state1", "'state1.1'"), nested("state2", "'state2.1'")],
        ),
    )


def _parse_state(path_name: str) -> StateDefinition | StateUsage:
    """Parse one local fixture and return its final state element."""
    path = FIXTURE_ROOT / path_name
    result = parse(path.read_text(encoding="utf-8"), str(path))
    assert result.ok, result.diagnostics
    return result.ast.members[-1].element


@pytest.mark.parametrize(
    ("fixture_name", "oracle"),
    (
        ("section_7_18_3_onoff1.sysml", _onoff1_oracle),
        ("section_7_18_3_onoff2.sysml", _onoff2_oracle),
        ("section_7_18_3_onoff3.sysml", _onoff3_oracle),
        ("section_7_18_3_onoff4.sysml", _onoff4_oracle),
        ("section_7_18_3_onoff5.sysml", _onoff5_oracle_with_transitions),
        ("section_7_18_3_onoff6.sysml", _onoff6_oracle),
    ),
    ids=("OnOff1", "OnOff2", "OnOff3", "OnOff4", "OnOff5", "OnOff6"),
)
def test_state_example_matches_an_independent_handwritten_ast_oracle(fixture_name, oracle):
    """Compare every field of each OnOff state AST against hand-built nodes."""
    assert _parse_state(fixture_name) == oracle()


@pytest.mark.parametrize(
    ("fixture_name", "oracle"),
    (
        ("section_7_18_table17_state_actions.sysml", _table_state_actions_oracle),
        ("section_7_18_table17_composite_sequential.sysml", _table_composite_sequential_oracle),
        ("section_7_18_table17_composite_parallel.sysml", _table_composite_parallel_oracle),
    ),
    ids=("state-actions", "composite-sequential", "composite-parallel"),
)
def test_table_state_example_matches_an_independent_handwritten_ast_oracle(fixture_name, oracle):
    """Compare the state/transition table examples field-by-field."""
    assert _parse_state(fixture_name) == oracle()


def test_table17_state_definition_body_retains_the_model_owned_comment_node():
    """Verify that the body example preserves its model-owned comment field."""
    actual = _parse_state("section_7_18_table17_state_definition_body.sysml")
    expected = _state_definition(
        "StateDef1",
        [DefinitionBodyItem(Comment(body="/* members */"))],
    )
    assert actual == expected


def test_table17_transition_fragment_matches_a_handwritten_transition_oracle():
    """Verify the explicit transition fragment independently of its snapshot."""
    path = FIXTURE_ROOT / "section_7_18_table17_transition_explicit.sysml"
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    from pysysmlv2 import parse_as_ast_node

    actual = parse_as_ast_node(lines[2], grammar_node="transitionUsage")
    expected = _transition(
        "state1",
        "state2",
        trigger=_signal_trigger("trigger1"),
        guard=_guard("guard1"),
        effect=EffectBehaviorMember(
            TransitionPerformActionUsage(
                PerformActionUsageDeclaration(referenced_feature=_q("action1"))
            )
        ),
    ).transition_usage
    assert actual == expected
