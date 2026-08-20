"""Assemble the handwritten SysML source AST from ANTLR contexts.

The generated parser recognizes the concrete syntax; this module owns the
explicit, production-by-production mapping into :mod:`pysysmlv2.syntax.ast`.
It is intentionally boring to read: every meaningful grammar alternative has
an ``exitXXX`` callback, while one-child dispatch and epsilon rules are
represented by an explicit pass-through or a small listener-local value.  No
``exitEveryRule``, reflection-driven dataclass construction, source scanner,
or generic opaque fallback is used for expressions, actions, states, or
transitions.

The listener creates a source AST only.  Names remain unresolved and derived
semantic properties such as transition ``source``/``target`` are deferred to
the future workspace/linker layer.  A :class:`SourceSpan`, including its
optional source path, is attached after each concrete node is constructed so
grammar-required dataclass fields remain required while provenance can be
omitted by callers constructing a node directly.

The few private lossless compatibility branches are enumerated in
``docs/research/raw_element_compatibility_ledger.json``.  They are limited to
deferred non-core productions and parser-recovery fragments; a valid core
expression, action, state, transition, import, alias, filter, connection, or
interface must be assembled as its explicit typed node.

.. list-table:: Listener roadmap
   :header-rows: 1

   * - Callback family
     - Nodes assembled
   * - Names/declarations
     - Identification, qualified references, declarations, specializations.
   * - Namespace membership
     - Alias members, membership/namespace imports, filtered imports, and
       package filter expressions.
   * - Expressions
     - Literals, recursive operators, calls, indexing, access, constructors,
       metadata forms, and argument lists.
   * - Actions
     - Action bodies, state action variants, trigger parameters, and the
       principal action-node statements.
   * - States/transitions
     - State bodies, entry/do/exit members, behavior members, transitions,
       guards, effects, and succession targets.
   * - Documents
     - Packages, package-member visibility, comments, documentation, and the
       root model.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from antlr4.tree.Tree import ErrorNode, TerminalNode

from .ast import (
    AcceptActionUsage,
    AcceptNode,
    AcceptNodeDeclaration,
    AcceptParameterPart,
    ActionBody,
    ActionBodyParameter,
    ActionDefinition,
    ActionNode,
    ActionNodeMember,
    ActionNodePrefix,
    ActionNodeUsageDeclaration,
    ActionTargetSuccession,
    ActionTargetSuccessionMember,
    ActionUsage,
    ActionUsageDeclaration,
    ActionUsageNode,
    AliasMember,
    AllExpression,
    AllocationDefinition,
    AllocationUsage,
    AllocationUsageDeclaration,
    AnalysisCaseDefinition,
    AnalysisCaseUsage,
    ArgumentList,
    AssertConstraintUsage,
    AssignmentActionUsage,
    AssignmentNode,
    AssignmentNodeDeclaration,
    AttributeDefinition,
    AttributeUsage,
    BehaviorUsageMember,
    BehaviorUsageStateMember,
    BinaryConnectorPart,
    BinaryExpression,
    BinaryInterfacePart,
    BodyExpression,
    BooleanLiteral,
    BracketExpression,
    CalculationBody,
    CalculationDefinition,
    CalculationUsage,
    CaseBody,
    CaseDefinition,
    CaseUsage,
    CastExpression,
    ChainingPart,
    CoalesceExpression,
    Comment,
    CommentExpression,
    ConcernDefinition,
    ConcernUsage,
    ConditionalExpression,
    ConjugatedPortTyping,
    ConjugationPart,
    ConnectionDefinition,
    ConnectionUsage,
    ConnectorEnd,
    ConnectorPart,
    ConstraintDefinition,
    ConstraintUsage,
    ConstraintUsageDeclaration,
    ConstructorExpression,
    ControlNodePrefix,
    DecisionNode,
    DeclaredFeatureTyping,
    DefaultInterfaceEnd,
    DefaultTargetSuccession,
    Definition,
    DefinitionBody,
    DefinitionBodyItem,
    DefinitionDeclaration,
    DefinitionPrefix,
    Dependency,
    DifferencingPart,
    DisjoiningPart,
    DoActionMember,
    Documentation,
    DottedQualifiedReference,
    EffectBehaviorMember,
    ElementFilterMember,
    EmptyActionUsage,
    EndFeatureUsage,
    EndOccurrenceUsageElement,
    EndUsagePrefix,
    EntryActionMember,
    EntryTransitionMember,
    EnumeratedValue,
    EnumerationBody,
    EnumerationDefinition,
    EnumerationUsage,
    EnumerationUsageMember,
    EventOccurrenceUsage,
    ExhibitStateUsage,
    ExitActionMember,
    Expression,
    ExtendedDefinition,
    FeatureChain,
    FeatureChainExpression,
    FeatureDeclaration,
    FeatureIdentification,
    FeatureReferenceExpression,
    FeatureRelationshipPart,
    FeatureSpecialization,
    FeatureSpecializationPart,
    FilterPackage,
    FlowDeclaration,
    FlowDefinition,
    FlowUsage,
    ForkNode,
    ForLoopNode,
    FunctionBodyItem,
    FunctionOperationExpression,
    GuardedSuccession,
    GuardedSuccessionMember,
    GuardedTargetSuccession,
    GuardExpressionMember,
    Identification,
    IfNode,
    ImportDeclaration,
    ImportRule,
    IncludeUseCaseUsage,
    IndexExpression,
    IndividualDefinition,
    IndividualUsage,
    InfinityLiteral,
    InitialNodeMember,
    IntegerLiteral,
    InterfaceBody,
    InterfaceDefinition,
    InterfaceEnd,
    InterfaceNonOccurrenceUsageMember,
    InterfaceOccurrenceUsageMember,
    InterfacePart,
    InterfaceUsage,
    InterfaceUsageDeclaration,
    IntersectingPart,
    InvertingPart,
    InvocationExpression,
    ItemDefinition,
    ItemUsage,
    JoinNode,
    MembershipImport,
    MergeNode,
    Message,
    MessageDeclaration,
    MetadataAccessExpression,
    MetadataBody,
    MetadataBodyFeature,
    MetadataBodyUsage,
    MetadataCastExpression,
    MetadataDefinition,
    MetadataFeature,
    MetadataFeatureDeclaration,
    Model,
    NamedArgument,
    NamespaceImport,
    NaryConnectorPart,
    NaryInterfacePart,
    NodeParameter,
    NonFeatureMember,
    NonOccurrenceUsageMember,
    NullExpression,
    OccurrenceDefinition,
    OccurrenceDefinitionPrefix,
    OccurrenceUsage,
    OccurrenceUsagePrefix,
    OwnedCrossFeature,
    OwnedFeatureTyping,
    Package,
    PackageMember,
    ParenthesizedExpression,
    PartDefinition,
    PartUsage,
    PayloadFeature,
    PayloadParameter,
    PerformActionUsage,
    PerformActionUsageDeclaration,
    PortDefinition,
    PortionUsage,
    PortUsage,
    QualifiedReference,
    RawElement,
    RealLiteral,
    Reference,
    ReferenceUsage,
    RelationshipBody,
    RenderingDefinition,
    RenderingUsage,
    RequirementBody,
    RequirementDefinition,
    RequirementUsage,
    ResultExpressionMember,
    ReturnFeatureMember,
    ReturnParameterMember,
    SatisfyRequirementUsage,
    SelectExpression,
    SendActionUsage,
    SenderReceiverPart,
    SendNode,
    SendNodeDeclaration,
    SendNodeUsageDeclaration,
    SequenceExpression,
    SourceElement,
    SourceSpan,
    SourceSuccession,
    StateDefBody,
    StateDefinition,
    StatePerformActionUsage,
    StateUsage,
    StateUsageBody,
    StringLiteral,
    StructureUsageMember,
    SubclassificationPart,
    SuccessionFlowUsage,
    TargetSuccession,
    TargetTransitionForm,
    TargetTransitionUsage,
    TargetTransitionUsageMember,
    TerminateNode,
    TransitionPerformActionUsage,
    TransitionSuccession,
    TransitionUsage,
    TransitionUsageMember,
    TriggerActionMember,
    TriggerExpression,
    TypeFeaturingPart,
    TypeOperationExpression,
    UnaryExpression,
    UnioningPart,
    Usage,
    UsageDeclaration,
    UsagePrefix,
    UseCaseDefinition,
    UseCaseUsage,
    ValuePart,
    VariantUsage,
    VerificationCaseDefinition,
    VerificationCaseUsage,
    ViewBody,
    ViewDefinition,
    ViewDefinitionBody,
    ViewpointDefinition,
    ViewpointUsage,
    ViewRenderingUsage,
    ViewUsage,
    WhileLoopNode,
    _relative_source,
)
from .generated.SysMLv2Parser import SysMLv2Parser
from .generated.SysMLv2ParserListener import SysMLv2ParserListener


class SysMLAstListener(SysMLv2ParserListener):
    """Build explicit source-AST nodes while walking one parse tree.

    :param source_text: Complete source text being walked.
    :type source_text: str
    :param source_path: Original path or URI, defaults to ``None``.
    :type source_path: str, optional
    :ivar source_text: Complete source text.
    :vartype source_text: str
    :ivar source_path: Original path or URI.
    :vartype source_path: str, optional

    Example::

        >>> from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
        >>> from pysysmlv2.syntax.generated.SysMLv2Lexer import SysMLv2Lexer
        >>> from pysysmlv2.syntax.generated.SysMLv2Parser import SysMLv2Parser
        >>> source = "package Demo { state def S; }"
        >>> parser = SysMLv2Parser(CommonTokenStream(SysMLv2Lexer(InputStream(source))))
        >>> tree = parser.rootNamespace()
        >>> listener = SysMLAstListener(source)
        >>> ParseTreeWalker().walk(listener, tree)
        >>> isinstance(listener.node_for(tree), Model)
        True
    """

    def __init__(self, source_text: str, source_path: Optional[str] = None) -> None:
        super().__init__()
        self.source_text = source_text
        self.source_path = source_path
        self.nodes: Dict[Any, SourceElement] = {}
        self.values: Dict[Any, str] = {}
        self.parts: Dict[Any, Any] = {}

    # ------------------------------------------------------------------
    # Provenance and listener-local values
    # ------------------------------------------------------------------

    def _text(self, ctx: Any) -> str:
        """Return the exact source slice occupied by ``ctx``."""
        if isinstance(ctx, TerminalNode):
            return ctx.getText()
        start_token = ctx.start
        stop_token = ctx.stop
        if start_token is not None and stop_token is not None:
            start = start_token.start
            stop = stop_token.stop
            if start is not None and stop is not None and start >= 0 and stop >= start:
                return self.source_text[start : stop + 1]
        return ctx.getText()

    def _span(self, ctx: Any) -> Optional[SourceSpan]:
        """Return the source range occupied by ``ctx``."""
        start_token = ctx.start
        stop_token = ctx.stop
        if start_token is None or stop_token is None:
            return None
        start = start_token.start
        stop = stop_token.stop
        if start is None or stop is None or start < 0 or stop < start:
            return None
        before_start = self.source_text[:start]
        before_end = self.source_text[: stop + 1]
        return SourceSpan(
            before_start.count("\n") + 1,
            start - (before_start.rfind("\n") + 1) + 1,
            before_end.count("\n") + 1,
            stop + 1 - (before_end.rfind("\n") + 1) + 1,
            self.source_path,
        )

    def _store(self, ctx: Any, node: SourceElement) -> None:
        """Store ``node`` and attach its source provenance explicitly."""
        node.span = self._span(ctx)
        self.nodes[ctx] = node

    def _child(self, ctx: Any) -> Optional[SourceElement]:
        """Return a previously assembled direct child, if present."""
        if ctx is None:
            return None
        return self.nodes.get(ctx)

    def _pass(self, ctx: Any, child_ctx: Any) -> None:
        """Pass a typed child through a pure grammar dispatch rule."""
        child = self._child(child_ctx)
        if child is None:
            raise ValueError("listener child production was not assembled")
        self.nodes[ctx] = child

    def _raw(self, ctx: Any) -> RawElement:
        """Preserve an unsupported non-state/non-expression grammar element."""
        return RawElement(_relative_source(self._text(ctx)))

    def _raw_store(self, ctx: Any) -> None:
        """Store a narrow compatibility fragment for an unrelated grammar rule."""
        self._store(ctx, self._raw(ctx))

    def _name_value(self, ctx: Any) -> str:
        """Return a completed name token value."""
        return self.values[ctx]

    def _token_text(self, token: Any) -> str:
        """Return one terminal token's source spelling."""
        return token.getText() if token is not None else ""

    def _member_prefix(self, ctx: Any) -> Optional[str]:
        """Return an optional visibility indicator from ``memberPrefix``."""
        text = self._text(ctx).strip()
        return text or None

    def _alias_node(self, ctx: Any, member_prefix: Optional[str] = None) -> AliasMember:
        """Build an alias node from either alias grammar production.

        ``aliasMember`` owns ``memberPrefix`` while the factored alias
        alternative in ``definitionBodyItemContent`` receives that prefix
        from its enclosing ``definitionBodyItem``.  Both productions share
        the remaining named fields, so this helper keeps their assembly
        identical without introducing a text-based fallback.
        """
        names = [self._name_value(item) for item in ctx.name()]
        identification = None
        if names:
            identification = Identification(
                short_name=names[0] if ctx.LT() is not None else None,
                declared_name=(names[1] if ctx.LT() is not None else names[0]),
            )
        target = self._child(ctx.qualifiedName())
        body = self._child(ctx.relationshipBody())
        if not isinstance(target, QualifiedReference) or not isinstance(body, RelationshipBody):
            raise ValueError("alias requires qualifiedName and relationshipBody")
        return AliasMember(
            target=target,
            relationship_body=body,
            identification=identification,
            member_prefix=member_prefix,
        )

    def _dotted_reference(self, ctx: Any) -> Reference:
        """Assemble a reference without flattening namespace separators."""
        names = [self._child(item) for item in ctx.qualifiedName()]
        references = [item for item in names if isinstance(item, QualifiedReference)]
        if not references:
            raise ValueError("dotted reference requires at least one qualified name")
        if len(references) == 1:
            return references[0]
        return DottedQualifiedReference(references)

    @staticmethod
    def _is_reference(value: Any) -> bool:
        """Return whether ``value`` is either supported unresolved reference form."""
        return isinstance(value, (QualifiedReference, DottedQualifiedReference))

    def _dotted_node(self, ctx: Any) -> DottedQualifiedReference:
        """Assemble a dotted reference while retaining each qualified-name child."""
        names = [self._child(item) for item in ctx.qualifiedName()]
        references = [item for item in names if isinstance(item, QualifiedReference)]
        if not references:
            raise ValueError("dotted reference requires at least one qualified name")
        node = DottedQualifiedReference(references)
        node.span = self._span(ctx)
        return node

    def _source_items(self, contexts: Sequence[Any]) -> List[SourceElement]:
        """Return assembled source elements, rejecting missing children."""
        items: List[SourceElement] = []
        for context in contexts:
            item = self._child(context)
            if not isinstance(item, SourceElement):
                raise ValueError("listener child production was not assembled")
            items.append(item)
        return items

    def _direct_source_items(self, ctx: Any) -> List[SourceElement]:
        """Return typed direct children in grammar source order.

        ``metadataBody`` has two brace alternatives with different child
        production names.  Inspecting its direct parse-tree children keeps
        their source order without flattening nested metadata bodies or
        introducing a grammar-specific text scanner.
        """
        items: List[SourceElement] = []
        for child in ctx.children or []:
            item = self._child(child)
            if isinstance(item, SourceElement):
                items.append(item)
        return items

    def node_for(self, tree: Any) -> SourceElement:
        """Return the AST node assembled for a walked parser context.

        :param tree: Parser context previously visited by this listener.
        :type tree: object
        :return: Corresponding source AST node.
        :rtype: :class:`pysysmlv2.syntax.ast.ASTNode`
        :raises KeyError: If no explicit callback assembled ``tree``.

        Example::

            >>> listener = SysMLAstListener("")
            >>> isinstance(listener.node_for, object)
            True
        """
        return self.nodes[tree]

    def visitTerminal(self, node: TerminalNode) -> None:
        """Ignore terminals; production callbacks read their explicit fields."""
        del node

    def visitErrorNode(self, node: ErrorNode) -> None:
        """Ignore recovered terminals; parser diagnostics own the error."""
        del node

    # ------------------------------------------------------------------
    # Names, references, and declarations
    # ------------------------------------------------------------------

    def exitPrefixMetadataFeature(self, ctx: SysMLv2Parser.PrefixMetadataFeatureContext) -> None:
        """Pass a ``#`` metadata feature prefix through its wrapper."""
        self._pass(ctx, ctx.ownedFeatureTyping())

    def exitPrefixMetadataUsage(self, ctx: SysMLv2Parser.PrefixMetadataUsageContext) -> None:
        """Pass a ``#`` metadata usage prefix through its wrapper."""
        self._pass(ctx, ctx.ownedFeatureTyping())

    def exitPrefixMetadataMember(self, ctx: SysMLv2Parser.PrefixMetadataMemberContext) -> None:
        """Pass the selected ``#`` metadata prefix alternative."""
        child = ctx.prefixMetadataFeature() or ctx.prefixMetadataUsage()
        if child is None:
            raise ValueError("prefixMetadataMember has no alternative")
        self._pass(ctx, child)

    def exitName(self, ctx: SysMLv2Parser.NameContext) -> None:
        """Record the source spelling of one grammar ``name``."""
        self.values[ctx] = self._text(ctx).strip()

    def exitIdentification(self, ctx: SysMLv2Parser.IdentificationContext) -> None:
        """Assemble optional short and declared names."""
        names = [self._name_value(item) for item in ctx.name()]
        self._store(
            ctx,
            Identification(
                short_name=names[0] if len(names) == 2 else None,
                declared_name=names[-1] if names else None,
            ),
        )

    def exitQualifiedName(self, ctx: SysMLv2Parser.QualifiedNameContext) -> None:
        """Assemble an unresolved qualified reference."""
        self._store(
            ctx,
            QualifiedReference(
                segments=[self._name_value(item) for item in ctx.name()],
                is_absolute=ctx.DOLLAR() is not None,
            ),
        )

    def exitBasicFeaturePrefix(self, ctx: SysMLv2Parser.BasicFeaturePrefixContext) -> None:
        """Record one owned-cross-feature prefix without flattening its owner."""
        self.values[ctx] = self._text(ctx).strip()

    def exitFeatureIdentification(self, ctx: SysMLv2Parser.FeatureIdentificationContext) -> None:
        """Assemble the short and declared names of a feature declaration."""
        names = [self._name_value(item) for item in ctx.name()]
        if not names:
            raise ValueError("featureIdentification requires a name")
        self._store(
            ctx,
            FeatureIdentification(
                short_name=names[0] if ctx.LT() is not None else None,
                declared_name=names[-1],
            ),
        )

    def exitOwnedConjugation(self, ctx: SysMLv2Parser.OwnedConjugationContext) -> None:
        """Assemble the dotted qualified name owned by a conjugation part."""
        self._store(ctx, self._dotted_node(ctx))

    def exitConjugationPart(self, ctx: SysMLv2Parser.ConjugationPartContext) -> None:
        """Assemble the explicit conjugation operator and target reference."""
        target = self._child(ctx.ownedConjugation())
        if not isinstance(target, DottedQualifiedReference):
            raise ValueError("conjugationPart requires ownedConjugation")
        operator = "~" if ctx.TILDE() is not None else "conjugates"
        self._store(ctx, ConjugationPart(operator, target))

    def exitOwnedFeatureInverting(self, ctx: SysMLv2Parser.OwnedFeatureInvertingContext) -> None:
        """Assemble the dotted qualified name owned by an inverse relation."""
        self._store(ctx, self._dotted_node(ctx))

    def exitChainingPart(self, ctx: SysMLv2Parser.ChainingPartContext) -> None:
        """Assemble ``chains`` and its ordered qualified-name targets."""
        self._store(ctx, ChainingPart(self._dotted_node(ctx).qualified_names))

    def exitInvertingPart(self, ctx: SysMLv2Parser.InvertingPartContext) -> None:
        """Assemble ``inverse of`` and its owned feature reference."""
        target = self._child(ctx.ownedFeatureInverting())
        if not isinstance(target, DottedQualifiedReference):
            raise ValueError("invertingPart requires ownedFeatureInverting")
        self._store(ctx, InvertingPart(target))

    def exitOwnedTypeFeaturing(self, ctx: SysMLv2Parser.OwnedTypeFeaturingContext) -> None:
        """Pass an owned type-featuring qualified name through its wrapper."""
        self._pass(ctx, ctx.qualifiedName())

    def exitTypeFeaturingPart(self, ctx: SysMLv2Parser.TypeFeaturingPartContext) -> None:
        """Assemble ``featured by`` and its ordered type targets."""
        targets = [self._child(item) for item in ctx.ownedTypeFeaturing()]
        if not targets or not all(isinstance(item, QualifiedReference) for item in targets):
            raise ValueError("typeFeaturingPart requires owned type references")
        self._store(ctx, TypeFeaturingPart(targets))

    def exitOwnedDisjoining(self, ctx: SysMLv2Parser.OwnedDisjoiningContext) -> None:
        """Assemble one dotted disjointed qualified name."""
        self._store(ctx, self._dotted_node(ctx))

    def exitDisjoiningPart(self, ctx: SysMLv2Parser.DisjoiningPartContext) -> None:
        """Assemble ``disjoint from`` and its ordered type targets."""
        targets = [self._child(item) for item in ctx.ownedDisjoining()]
        if not targets or not all(isinstance(item, DottedQualifiedReference) for item in targets):
            raise ValueError("disjoiningPart requires owned disjoining references")
        self._store(ctx, DisjoiningPart(targets))

    def exitUnioning(self, ctx: SysMLv2Parser.UnioningContext) -> None:
        """Assemble one dotted unioned qualified name."""
        self._store(ctx, self._dotted_node(ctx))

    def exitUnioningPart(self, ctx: SysMLv2Parser.UnioningPartContext) -> None:
        """Assemble ``unions`` and its ordered type targets."""
        targets = [self._child(item) for item in ctx.unioning()]
        if not targets or not all(isinstance(item, DottedQualifiedReference) for item in targets):
            raise ValueError("unioningPart requires unioning references")
        self._store(ctx, UnioningPart(targets))

    def exitIntersecting(self, ctx: SysMLv2Parser.IntersectingContext) -> None:
        """Assemble one dotted intersected qualified name."""
        self._store(ctx, self._dotted_node(ctx))

    def exitIntersectingPart(self, ctx: SysMLv2Parser.IntersectingPartContext) -> None:
        """Assemble ``intersects`` and its ordered type targets."""
        targets = [self._child(item) for item in ctx.intersecting()]
        if not targets or not all(isinstance(item, DottedQualifiedReference) for item in targets):
            raise ValueError("intersectingPart requires intersecting references")
        self._store(ctx, IntersectingPart(targets))

    def exitDifferencing(self, ctx: SysMLv2Parser.DifferencingContext) -> None:
        """Assemble one dotted differenced qualified name."""
        self._store(ctx, self._dotted_node(ctx))

    def exitDifferencingPart(self, ctx: SysMLv2Parser.DifferencingPartContext) -> None:
        """Assemble ``differences`` and its ordered type targets."""
        targets = [self._child(item) for item in ctx.differencing()]
        if not targets or not all(isinstance(item, DottedQualifiedReference) for item in targets):
            raise ValueError("differencingPart requires differencing references")
        self._store(ctx, DifferencingPart(targets))

    def exitTypeRelationshipPart(self, ctx: SysMLv2Parser.TypeRelationshipPartContext) -> None:
        """Pass one explicit type-relationship alternative."""
        child = (
            ctx.disjoiningPart()
            or ctx.unioningPart()
            or ctx.intersectingPart()
            or ctx.differencingPart()
        )
        if child is None:
            raise ValueError("typeRelationshipPart has no alternative")
        self._pass(ctx, child)

    def exitFeatureRelationshipPart(
        self, ctx: SysMLv2Parser.FeatureRelationshipPartContext
    ) -> None:
        """Pass one explicit feature-relationship alternative."""
        child = (
            ctx.typeRelationshipPart()
            or ctx.chainingPart()
            or ctx.invertingPart()
            or ctx.typeFeaturingPart()
        )
        if child is None:
            raise ValueError("featureRelationshipPart has no alternative")
        self._pass(ctx, child)

    def exitFeatureDeclaration(self, ctx: SysMLv2Parser.FeatureDeclarationContext) -> None:
        """Assemble feature name, specialization, conjugation, and relationships."""
        identification = (
            self._child(ctx.featureIdentification()) if ctx.featureIdentification() else None
        )
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        conjugation = self._child(ctx.conjugationPart()) if ctx.conjugationPart() else None
        relationships = [self._child(item) for item in ctx.featureRelationshipPart()]
        if identification is not None and not isinstance(identification, FeatureIdentification):
            raise ValueError("featureDeclaration identification was not assembled")
        if specialization is not None and not isinstance(specialization, FeatureSpecializationPart):
            raise ValueError("featureDeclaration specialization was not assembled")
        if conjugation is not None and not isinstance(conjugation, ConjugationPart):
            raise ValueError("featureDeclaration conjugation was not assembled")
        if not all(isinstance(item, FeatureRelationshipPart) for item in relationships):
            raise ValueError("featureDeclaration relationship was not assembled")
        self._store(
            ctx,
            FeatureDeclaration(
                identification=(
                    identification if isinstance(identification, FeatureIdentification) else None
                ),
                specialization=(
                    specialization
                    if isinstance(specialization, FeatureSpecializationPart)
                    else None
                ),
                is_all=ctx.ALL() is not None,
                conjugation_part=conjugation if isinstance(conjugation, ConjugationPart) else None,
                relationship_parts=[
                    item for item in relationships if isinstance(item, FeatureRelationshipPart)
                ],
            ),
        )

    def exitOwnedCrossFeatureMember(
        self, ctx: SysMLv2Parser.OwnedCrossFeatureMemberContext
    ) -> None:
        """Pass the owned cross-feature through its one-child wrapper."""
        self._pass(ctx, ctx.ownedCrossFeature())

    def exitOwnedCrossFeature(self, ctx: SysMLv2Parser.OwnedCrossFeatureContext) -> None:
        """Assemble the feature and usage alternatives of an owned cross feature."""
        if ctx.basicFeaturePrefix() is not None:
            declaration = self._child(ctx.featureDeclaration())
            if not isinstance(declaration, FeatureDeclaration):
                raise ValueError("ownedCrossFeature requires featureDeclaration")
            self._store(
                ctx,
                OwnedCrossFeature(
                    basic_feature_prefix=self.values.get(ctx.basicFeaturePrefix(), ""),
                    feature_declaration=declaration,
                ),
            )
            return
        basic = ctx.basicUsagePrefix()
        if basic is None:
            raise ValueError("ownedCrossFeature has no alternative")
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        self._store(
            ctx,
            OwnedCrossFeature(
                basic_usage_prefix=self._usage_prefix_from_ref_prefix(basic),
                usage_declaration=(
                    declaration if isinstance(declaration, UsageDeclaration) else None
                ),
            ),
        )

    def exitEndUsagePrefix(self, ctx: SysMLv2Parser.EndUsagePrefixContext) -> None:
        """Assemble the required ``end`` prefix and cross-feature child."""
        cross_feature = self._child(ctx.ownedCrossFeatureMember())
        if not isinstance(cross_feature, OwnedCrossFeature):
            raise ValueError("endUsagePrefix requires ownedCrossFeature")
        self._store(ctx, EndUsagePrefix(cross_feature))

    def exitEndFeatureUsage(self, ctx: SysMLv2Parser.EndFeatureUsageContext) -> None:
        """Assemble an end feature declaration and its usage completion."""
        prefix = self._child(ctx.endUsagePrefix())
        declaration = self._child(ctx.featureDeclaration())
        completion = self._child(ctx.usageCompletion())
        if not isinstance(prefix, EndUsagePrefix):
            raise ValueError("endFeatureUsage requires EndUsagePrefix")
        if not isinstance(declaration, FeatureDeclaration):
            raise ValueError("endFeatureUsage requires FeatureDeclaration")
        if not isinstance(completion, Usage):
            raise ValueError("endFeatureUsage requires usage completion")
        self._store(ctx, EndFeatureUsage(prefix, declaration, completion))

    def exitAliasMember(self, ctx: SysMLv2Parser.AliasMemberContext) -> None:
        """Assemble an alias member with its explicit names and target."""
        self._store(ctx, self._alias_node(ctx, self._member_prefix(ctx.memberPrefix())))

    def exitMembershipImport(self, ctx: SysMLv2Parser.MembershipImportContext) -> None:
        """Assemble a membership import and its optional ``::*`` suffix."""
        target = self._child(ctx.qualifiedName())
        if not isinstance(target, QualifiedReference):
            raise ValueError("membershipImport requires qualifiedName")
        self._store(ctx, MembershipImport(target, is_all_members=ctx.STAR_STAR() is not None))

    def exitNamespaceImportDirect(self, ctx: SysMLv2Parser.NamespaceImportDirectContext) -> None:
        """Assemble the direct namespace wildcard used by filtered imports."""
        target = self._child(ctx.qualifiedName())
        if not isinstance(target, QualifiedReference):
            raise ValueError("namespaceImportDirect requires qualifiedName")
        self._store(ctx, NamespaceImport(target, is_recursive=ctx.STAR_STAR() is not None))

    def exitNamespaceImport(self, ctx: SysMLv2Parser.NamespaceImportContext) -> None:
        """Assemble a namespace wildcard or pass a filtered import package."""
        if ctx.filterPackage() is not None:
            self._pass(ctx, ctx.filterPackage())
            return
        target = self._child(ctx.qualifiedName())
        if not isinstance(target, QualifiedReference):
            raise ValueError("namespaceImport requires qualifiedName")
        self._store(ctx, NamespaceImport(target, is_recursive=ctx.STAR_STAR() is not None))

    def exitFilterPackageImportDeclaration(
        self, ctx: SysMLv2Parser.FilterPackageImportDeclarationContext
    ) -> None:
        """Pass the direct import alternative inside a filtered package."""
        child = ctx.membershipImport() or ctx.namespaceImportDirect()
        if child is None:
            raise ValueError("filterPackageImportDeclaration has no alternative")
        self._pass(ctx, child)

    def exitFilterPackageMember(self, ctx: SysMLv2Parser.FilterPackageMemberContext) -> None:
        """Pass the typed expression enclosed by one filter bracket pair."""
        expression = self._child(ctx.ownedExpression())
        if not isinstance(expression, Expression):
            raise ValueError("filterPackageMember requires ownedExpression")
        self._pass(ctx, ctx.ownedExpression())

    def exitFilterPackage(self, ctx: SysMLv2Parser.FilterPackageContext) -> None:
        """Assemble a filtered import with ordered predicate expressions."""
        declaration = self._child(ctx.filterPackageImportDeclaration())
        filters = [self._child(item) for item in ctx.filterPackageMember()]
        if not isinstance(declaration, ImportDeclaration) or not all(
            isinstance(item, Expression) for item in filters
        ):
            raise ValueError("filterPackage has incomplete import or filter fields")
        self._store(
            ctx,
            FilterPackage(
                import_declaration=declaration,
                filters=[item for item in filters if isinstance(item, Expression)],
            ),
        )

    def exitImportDeclaration(self, ctx: SysMLv2Parser.ImportDeclarationContext) -> None:
        """Pass the selected membership or namespace import alternative."""
        child = ctx.membershipImport() or ctx.namespaceImport()
        if child is None:
            raise ValueError("importDeclaration has no alternative")
        self._pass(ctx, child)

    def exitImportRule(self, ctx: SysMLv2Parser.ImportRuleContext) -> None:
        """Assemble visibility, ``all``, declaration, and relationship body."""
        declaration = self._child(ctx.importDeclaration())
        body = self._child(ctx.relationshipBody())
        if not isinstance(declaration, ImportDeclaration) or not isinstance(body, RelationshipBody):
            raise ValueError("importRule has incomplete required fields")
        self._store(
            ctx,
            ImportRule(
                import_declaration=declaration,
                relationship_body=body,
                visibility=(
                    self._text(ctx.visibilityIndicator()).strip()
                    if ctx.visibilityIndicator() is not None
                    else None
                ),
                is_all=ctx.ALL() is not None,
            ),
        )

    def exitElementFilterMember(self, ctx: SysMLv2Parser.ElementFilterMemberContext) -> None:
        """Assemble a package filter member from its typed expression."""
        expression = self._child(ctx.ownedExpression())
        if not isinstance(expression, Expression):
            raise ValueError("elementFilterMember requires ownedExpression")
        self._store(
            ctx,
            ElementFilterMember(
                expression=expression,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitNonFeatureElement(self, ctx: SysMLv2Parser.NonFeatureElementContext) -> None:
        """Pass the supported feature-typing non-feature alternative through."""
        if ctx.featureTyping() and self._child(ctx.featureTyping()) is not None:
            self._pass(ctx, ctx.featureTyping())

    def exitMemberElement(self, ctx: SysMLv2Parser.MemberElementContext) -> None:
        """Pass the supported non-feature member element through its dispatcher."""
        if ctx.nonFeatureElement() and self._child(ctx.nonFeatureElement()) is not None:
            self._pass(ctx, ctx.nonFeatureElement())

    def exitNonFeatureMember(self, ctx: SysMLv2Parser.NonFeatureMemberContext) -> None:
        """Assemble a prefixed owned-feature-typing member explicitly."""
        element = self._child(ctx.memberElement())
        if isinstance(element, OwnedFeatureTyping):
            self._store(
                ctx,
                NonFeatureMember(
                    owned_feature_typing=element,
                    member_prefix=self._member_prefix(ctx.memberPrefix()),
                ),
            )

    def exitTypeBodyElement(self, ctx: SysMLv2Parser.TypeBodyElementContext) -> None:
        """Pass a mapped type-body alternative without an opaque fallback."""
        children = [
            ctx.nonFeatureMember(),
            ctx.featureMember(),
            ctx.aliasMember(),
            ctx.importRule(),
        ]
        for child in children:
            if child is not None and self._child(child) is not None:
                self._pass(ctx, child)
                return

    def exitTypeFeatureMember(self, ctx: SysMLv2Parser.TypeFeatureMemberContext) -> None:
        """Retain an unimplemented ``member`` feature with its owned prefix."""
        self._raw_store(ctx)

    def exitOwnedFeatureMember(self, ctx: SysMLv2Parser.OwnedFeatureMemberContext) -> None:
        """Retain an unimplemented owned feature with its owned prefix."""
        self._raw_store(ctx)

    def exitFeatureMember(self, ctx: SysMLv2Parser.FeatureMemberContext) -> None:
        """Pass the retained feature-member alternative through its dispatcher."""
        child = ctx.typeFeatureMember() or ctx.ownedFeatureMember()
        if child is None:
            raise ValueError("featureMember has no alternative")
        self._pass(ctx, child)

    def exitFeatureReferenceExpression(
        self, ctx: SysMLv2Parser.FeatureReferenceExpressionContext
    ) -> None:
        """Wrap a feature-reference production around its qualified name."""
        reference = self._child(ctx.qualifiedName())
        if not isinstance(reference, QualifiedReference):
            raise ValueError("featureReferenceExpression requires qualifiedName")
        self._store(ctx, FeatureReferenceExpression(reference))

    def exitFeatureChainMember(self, ctx: SysMLv2Parser.FeatureChainMemberContext) -> None:
        """Assemble ordered dotted qualified-name members."""
        names = [self._child(item) for item in ctx.qualifiedName()]
        self._store(
            ctx,
            FeatureChain(
                qualified_names=[item for item in names if isinstance(item, QualifiedReference)]
            ),
        )

    def exitNonFeatureChainPrimaryExpression(
        self, ctx: SysMLv2Parser.NonFeatureChainPrimaryExpressionContext
    ) -> None:
        """Assemble the identifier-only assignment-target-binding production."""
        identifier = ctx.IDENTIFIER()
        if identifier is None:
            raise ValueError("nonFeatureChainPrimaryExpression requires IDENTIFIER")
        self._store(
            ctx,
            FeatureReferenceExpression(
                QualifiedReference([identifier.getText()]),
            ),
        )

    def exitAssignmentTargetBinding(
        self, ctx: SysMLv2Parser.AssignmentTargetBindingContext
    ) -> None:
        """Pass the structured assignment target binding expression."""
        self._pass(ctx, ctx.nonFeatureChainPrimaryExpression())

    def exitAssignmentTargetParameter(
        self, ctx: SysMLv2Parser.AssignmentTargetParameterContext
    ) -> None:
        """Pass an optional binding before the assignment target dot."""
        if ctx.assignmentTargetBinding() is None:
            self.parts[ctx] = None
            return
        self._pass(ctx, ctx.assignmentTargetBinding())

    def exitAssignmentTargetMember(self, ctx: SysMLv2Parser.AssignmentTargetMemberContext) -> None:
        """Pass the optional assignment-target binding wrapper."""
        parameter = ctx.assignmentTargetParameter()
        child = self._child(parameter)
        if child is None:
            self.parts[ctx] = None
            return
        self._pass(ctx, parameter)

    def exitTypeReference(self, ctx: SysMLv2Parser.TypeReferenceContext) -> None:
        """Pass the single qualified name through the type-reference rule."""
        self._pass(ctx, ctx.qualifiedName())

    def exitOwnedSubclassification(self, ctx: SysMLv2Parser.OwnedSubclassificationContext) -> None:
        """Pass one superclass reference through its grammar wrapper."""
        self._pass(ctx, ctx.qualifiedName())

    def exitSubclassificationPart(self, ctx: SysMLv2Parser.SubclassificationPartContext) -> None:
        """Assemble the subclassification operator and ordered references."""
        operator = ":>" if ctx.COLON_GT() is not None else "specializes"
        references = [self._child(item) for item in ctx.ownedSubclassification()]
        self._store(
            ctx,
            SubclassificationPart(
                operator=operator,
                supertype_references=[
                    item for item in references if isinstance(item, QualifiedReference)
                ],
            ),
        )

    def exitFeatureSpecializationPart(
        self, ctx: SysMLv2Parser.FeatureSpecializationPartContext
    ) -> None:
        """Assemble explicit feature specializations and multiplicity spelling."""
        specializations = [self._child(item) for item in ctx.featureSpecialization()]
        multiplicity = (
            self._text(ctx.multiplicityPart()).strip() if ctx.multiplicityPart() else None
        )
        self._store(
            ctx,
            FeatureSpecializationPart(
                specializations=[
                    item for item in specializations if isinstance(item, FeatureSpecialization)
                ],
                multiplicity_text=multiplicity,
            ),
        )

    def exitFeatureSpecialization(self, ctx: SysMLv2Parser.FeatureSpecializationContext) -> None:
        """Pass one concrete specialization alternative through its dispatcher."""
        child = (
            ctx.typings()
            or ctx.subsettings()
            or ctx.references()
            or ctx.crosses()
            or ctx.redefinitions()
        )
        if child is None:
            raise ValueError("featureSpecialization has no alternative")
        self._pass(ctx, child)

    def exitTypings(self, ctx: SysMLv2Parser.TypingsContext) -> None:
        """Assemble a typing specialization without collapsing its references."""
        child = ctx.typedBy()
        typing_nodes = []
        if child is not None:
            typing_nodes.append(self._child(child.featureTyping()))
        typing_nodes.extend(self._child(item) for item in ctx.featureTyping())
        operator = ":"
        if child is not None and child.TYPED() is not None:
            operator = "typed by"
        elif child is not None and child.DEFINED() is not None:
            operator = "defined by"
        self._store(
            ctx,
            FeatureSpecialization(
                operator=operator,
                references=[
                    item
                    for item in typing_nodes
                    if isinstance(
                        item,
                        (
                            QualifiedReference,
                            OwnedFeatureTyping,
                            ConjugatedPortTyping,
                            DeclaredFeatureTyping,
                        ),
                    )
                ],
            ),
        )

    def exitTypedBy(self, ctx: SysMLv2Parser.TypedByContext) -> None:
        """Pass the nested feature-typing production."""
        self._pass(ctx, ctx.featureTyping())

    def exitFeatureTyping(self, ctx: SysMLv2Parser.FeatureTypingContext) -> None:
        """Assemble one owned, conjugated, or declared typing alternative."""
        if ctx.ownedFeatureTyping():
            self._pass(ctx, ctx.ownedFeatureTyping())
            return
        if ctx.conjugatedPortTyping():
            self._pass(ctx, ctx.conjugatedPortTyping())
            return
        identification = self._child(ctx.identification()) if ctx.identification() else None
        typed_feature = self._child(ctx.qualifiedName())
        general_type = self._child(ctx.generalType())
        body = self._child(ctx.relationshipBody())
        if (
            not isinstance(typed_feature, QualifiedReference)
            or not self._is_reference(general_type)
            or not isinstance(body, RelationshipBody)
        ):
            raise ValueError("declared featureTyping has incomplete required fields")
        self._store(
            ctx,
            DeclaredFeatureTyping(
                typed_feature=typed_feature,
                operator=":" if ctx.COLON() is not None else "typed by",
                general_type=general_type,
                relationship_body=body,
                is_specialization=ctx.SPECIALIZATION() is not None,
                identification=identification
                if isinstance(identification, Identification)
                else None,
            ),
        )

    def exitOwnedFeatureTyping(self, ctx: SysMLv2Parser.OwnedFeatureTypingContext) -> None:
        """Assemble the complete dotted owned feature-typing reference."""
        self._store(ctx, OwnedFeatureTyping(self._dotted_node(ctx)))

    def exitConjugatedPortTyping(self, ctx: SysMLv2Parser.ConjugatedPortTypingContext) -> None:
        """Assemble the distinct ``~ qualifiedName`` port-typing form."""
        reference = self._child(ctx.qualifiedName())
        if not isinstance(reference, QualifiedReference):
            raise ValueError("conjugatedPortTyping requires qualifiedName")
        self._store(ctx, ConjugatedPortTyping(reference))

    def exitGeneralType(self, ctx: SysMLv2Parser.GeneralTypeContext) -> None:
        """Assemble the dotted general type used by declared feature typing."""
        self._store(ctx, self._dotted_reference(ctx))

    def exitSubsettings(self, ctx: SysMLv2Parser.SubsettingsContext) -> None:
        """Assemble a subsetting specialization."""
        references = [self._child(ctx.subsets().ownedSubsetting())]
        references.extend(self._child(item) for item in ctx.ownedSubsetting())
        self._store(
            ctx,
            FeatureSpecialization(
                operator=":>" if ctx.subsets().COLON_GT() is not None else "subsets",
                references=[item for item in references if self._is_reference(item)],
            ),
        )

    def exitSubsets(self, ctx: SysMLv2Parser.SubsetsContext) -> None:
        """Pass the nested owned-subsetting reference."""
        self._pass(ctx, ctx.ownedSubsetting())

    def exitOwnedSubsetting(self, ctx: SysMLv2Parser.OwnedSubsettingContext) -> None:
        """Assemble the complete dotted owned-subsetting reference."""
        self._store(ctx, self._dotted_reference(ctx))

    def exitReferences(self, ctx: SysMLv2Parser.ReferencesContext) -> None:
        """Assemble a reference specialization."""
        self._store(
            ctx,
            FeatureSpecialization(
                operator="::>" if ctx.COLON_COLON_GT() is not None else "references",
                references=[self._child(ctx.ownedReferenceSubsetting())],
            ),
        )

    def exitOwnedReferenceSubsetting(
        self, ctx: SysMLv2Parser.OwnedReferenceSubsettingContext
    ) -> None:
        """Assemble a dotted owned-reference chain as a qualified reference."""
        self._store(ctx, self._dotted_reference(ctx))

    def exitCrosses(self, ctx: SysMLv2Parser.CrossesContext) -> None:
        """Assemble a cross-subsetting specialization."""
        self._store(
            ctx,
            FeatureSpecialization(
                operator="=>" if ctx.FAT_ARROW() is not None else "crosses",
                references=[self._child(ctx.ownedCrossSubsetting())],
            ),
        )

    def exitOwnedCrossSubsetting(self, ctx: SysMLv2Parser.OwnedCrossSubsettingContext) -> None:
        """Assemble an owned cross-subsetting qualified-name chain."""
        self._store(ctx, self._dotted_reference(ctx))

    def exitRedefinitions(self, ctx: SysMLv2Parser.RedefinitionsContext) -> None:
        """Assemble a redefinition specialization."""
        references = [self._child(ctx.redefines().ownedRedefinition())]
        references.extend(self._child(item) for item in ctx.ownedRedefinition())
        self._store(
            ctx,
            FeatureSpecialization(
                operator=":>>" if ctx.redefines().COLON_GT_GT() is not None else "redefines",
                references=[item for item in references if self._is_reference(item)],
            ),
        )

    def exitRedefines(self, ctx: SysMLv2Parser.RedefinesContext) -> None:
        """Pass one owned-redefinition reference."""
        self._pass(ctx, ctx.ownedRedefinition())

    def exitOwnedRedefinition(self, ctx: SysMLv2Parser.OwnedRedefinitionContext) -> None:
        """Assemble an owned-redefinition qualified-name chain."""
        self._store(ctx, self._dotted_reference(ctx))

    def exitDefinitionDeclaration(self, ctx: SysMLv2Parser.DefinitionDeclarationContext) -> None:
        """Assemble optional identification and subclassification fields."""
        identification = self._child(ctx.identification()) if ctx.identification() else None
        subclassification = (
            self._child(ctx.subclassificationPart()) if ctx.subclassificationPart() else None
        )
        self._store(
            ctx,
            DefinitionDeclaration(
                identification=identification
                if isinstance(identification, Identification)
                else None,
                subclassification=(
                    subclassification
                    if isinstance(subclassification, SubclassificationPart)
                    else None
                ),
            ),
        )

    def exitUsageDeclaration(self, ctx: SysMLv2Parser.UsageDeclarationContext) -> None:
        """Assemble optional usage identification and specialization."""
        identification = self._child(ctx.identification()) if ctx.identification() else None
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        self._store(
            ctx,
            UsageDeclaration(
                identification=identification
                if isinstance(identification, Identification)
                else None,
                specialization=(
                    specialization
                    if isinstance(specialization, FeatureSpecializationPart)
                    else None
                ),
            ),
        )

    def exitOccurrenceDefinitionPrefix(
        self, ctx: SysMLv2Parser.OccurrenceDefinitionPrefixContext
    ) -> None:
        """Assemble occurrence-definition prefix flags and extension text."""
        basic = (
            "abstract"
            if ctx.basicDefinitionPrefix() and ctx.basicDefinitionPrefix().ABSTRACT()
            else None
        )
        if ctx.basicDefinitionPrefix() and ctx.basicDefinitionPrefix().VARIATION():
            basic = "variation"
        self._store(
            ctx,
            OccurrenceDefinitionPrefix(
                basic_definition_keyword=basic,
                is_individual=ctx.INDIVIDUAL() is not None,
                extension_keywords=[
                    self._text(item).strip() for item in ctx.definitionExtensionKeyword()
                ],
            ),
        )

    def exitOccurrenceUsagePrefix(self, ctx: SysMLv2Parser.OccurrenceUsagePrefixContext) -> None:
        """Assemble occurrence-usage prefix flags and extension text."""
        ref = ctx.basicUsagePrefix()
        direction = None
        if ref and ref.refPrefix() and ref.refPrefix().featureDirection():
            direction = self._text(ref.refPrefix().featureDirection()).strip()
        self._store(
            ctx,
            OccurrenceUsagePrefix(
                feature_direction=direction,
                is_derived=bool(ref and ref.refPrefix() and ref.refPrefix().DERIVED()),
                is_abstract=bool(ref and ref.refPrefix() and ref.refPrefix().ABSTRACT()),
                is_variation=bool(ref and ref.refPrefix() and ref.refPrefix().VARIATION()),
                is_constant=bool(ref and ref.refPrefix() and ref.refPrefix().CONSTANT()),
                is_reference=bool(ref and ref.REF()),
                is_individual=ctx.INDIVIDUAL() is not None,
                portion_kind=self._text(ctx.portionKind()).strip() if ctx.portionKind() else None,
                extension_keywords=[
                    self._text(item).strip() for item in ctx.usageExtensionKeyword()
                ],
            ),
        )

    def exitBasicDefinitionPrefix(self, ctx: SysMLv2Parser.BasicDefinitionPrefixContext) -> None:
        """Record the selected ``abstract`` or ``variation`` definition prefix."""
        self.values[ctx] = self._text(ctx).strip()

    def exitDefinitionExtensionKeyword(
        self, ctx: SysMLv2Parser.DefinitionExtensionKeywordContext
    ) -> None:
        """Record one definition extension keyword without flattening its owner."""
        self.values[ctx] = self._text(ctx).strip()

    def exitDefinitionPrefix(self, ctx: SysMLv2Parser.DefinitionPrefixContext) -> None:
        """Assemble the shared non-occurrence definition prefix."""
        basic = (
            self._text(ctx.basicDefinitionPrefix()).strip() if ctx.basicDefinitionPrefix() else None
        )
        self._store(
            ctx,
            DefinitionPrefix(
                basic_definition_keyword=basic,
                extension_keywords=[
                    self._text(item).strip() for item in ctx.definitionExtensionKeyword()
                ],
            ),
        )

    def exitRefPrefix(self, ctx: SysMLv2Parser.RefPrefixContext) -> None:
        """Record the token spelling of the generic reference prefix."""
        self.values[ctx] = self._text(ctx).strip()

    def exitBasicUsagePrefix(self, ctx: SysMLv2Parser.BasicUsagePrefixContext) -> None:
        """Record the generic usage prefix before its optional ``ref`` token."""
        self.values[ctx] = self._text(ctx).strip()

    def exitUnextendedUsagePrefix(self, ctx: SysMLv2Parser.UnextendedUsagePrefixContext) -> None:
        """Record the unextended usage prefix alternative."""
        self.values[ctx] = self._text(ctx).strip()

    def exitUsageExtensionKeyword(self, ctx: SysMLv2Parser.UsageExtensionKeywordContext) -> None:
        """Record one usage extension keyword in source order."""
        self.values[ctx] = self._text(ctx).strip()

    def exitUsagePrefix(self, ctx: SysMLv2Parser.UsagePrefixContext) -> None:
        """Assemble the generic prefix used by attributes and references."""
        unextended = ctx.unextendedUsagePrefix()
        basic = unextended.basicUsagePrefix() if unextended else None
        ref = basic.refPrefix() if basic and basic.refPrefix() else None
        direction = (
            self._text(ref.featureDirection()).strip() if ref and ref.featureDirection() else None
        )
        self._store(
            ctx,
            UsagePrefix(
                feature_direction=direction,
                is_derived=bool(ref and ref.DERIVED()),
                is_abstract=bool(ref and ref.ABSTRACT()),
                is_variation=bool(ref and ref.VARIATION()),
                is_constant=bool(ref and ref.CONSTANT()),
                is_reference=bool(basic and basic.REF()),
                extension_keywords=[
                    self._text(item).strip() for item in ctx.usageExtensionKeyword()
                ],
            ),
        )

    # ------------------------------------------------------------------
    # Expressions and argument structure
    # ------------------------------------------------------------------

    def exitLiteralBoolean(self, ctx: SysMLv2Parser.LiteralBooleanContext) -> None:
        """Assemble a boolean literal leaf."""
        self._store(ctx, BooleanLiteral(self._text(ctx).strip()))

    def exitLiteralString(self, ctx: SysMLv2Parser.LiteralStringContext) -> None:
        """Assemble a quoted string literal leaf."""
        self._store(ctx, StringLiteral(self._text(ctx).strip()))

    def exitLiteralInteger(self, ctx: SysMLv2Parser.LiteralIntegerContext) -> None:
        """Assemble an integer literal leaf."""
        self._store(ctx, IntegerLiteral(self._text(ctx).strip()))

    def exitLiteralReal(self, ctx: SysMLv2Parser.LiteralRealContext) -> None:
        """Assemble a real literal leaf."""
        self._store(ctx, RealLiteral(self._text(ctx).strip()))

    def exitLiteralInfinity(self, ctx: SysMLv2Parser.LiteralInfinityContext) -> None:
        """Assemble the ``*`` infinity literal leaf."""
        self._store(ctx, InfinityLiteral())

    def exitLiteralExpression(self, ctx: SysMLv2Parser.LiteralExpressionContext) -> None:
        """Pass the selected literal alternative through its dispatcher."""
        child = (
            ctx.literalBoolean()
            or ctx.literalString()
            or ctx.literalInteger()
            or ctx.literalReal()
            or ctx.literalInfinity()
        )
        if child is None:
            raise ValueError("literalExpression has no alternative")
        self._pass(ctx, child)

    def exitNullExpression(self, ctx: SysMLv2Parser.NullExpressionContext) -> None:
        """Assemble ``null`` and empty-parenthesis expression alternatives."""
        self._store(ctx, NullExpression(parenthesized=ctx.LPAREN() is not None))

    def exitConstructorExpression(self, ctx: SysMLv2Parser.ConstructorExpressionContext) -> None:
        """Assemble ``new`` with a type reference and explicit argument list."""
        reference = self._child(ctx.qualifiedName())
        arguments = self._child(ctx.argumentList())
        if not isinstance(reference, QualifiedReference) or not isinstance(arguments, ArgumentList):
            raise ValueError("constructorExpression requires qualifiedName and argumentList")
        self._store(ctx, ConstructorExpression(reference, arguments))

    def exitBodyExpression(self, ctx: SysMLv2Parser.BodyExpressionContext) -> None:
        """Assemble a brace-delimited function body from its item list."""
        items = self.parts.get(ctx.functionBodyPart(), [])
        self._store(ctx, BodyExpression(items=items))

    def exitFunctionBodyPart(self, ctx: SysMLv2Parser.FunctionBodyPartContext) -> None:
        """Collect function-body items and an optional result expression."""
        contexts = [
            *ctx.definitionBodyItem(),
            *ctx.typeBodyElement(),
            *ctx.returnFeatureMember(),
        ]
        items = self._source_items(contexts)
        if ctx.resultExpressionMember():
            items.append(self._child(ctx.resultExpressionMember()))
        if not all(isinstance(item, FunctionBodyItem) for item in items):
            raise ValueError("functionBodyPart contains an unsupported body item")
        self.parts[ctx] = items

    def exitResultExpressionMember(self, ctx: SysMLv2Parser.ResultExpressionMemberContext) -> None:
        """Assemble a function-body result expression with its prefix."""
        expression = self._child(ctx.ownedExpression())
        if not isinstance(expression, Expression):
            raise ValueError("resultExpressionMember requires an Expression")
        self._store(
            ctx,
            ResultExpressionMember(
                expression=expression,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitFeatureElement(self, ctx: SysMLv2Parser.FeatureElementContext) -> None:
        """Preserve an unimplemented generic feature at the explicit bridge."""
        self._raw_store(ctx)

    def exitReturnFeatureMember(self, ctx: SysMLv2Parser.ReturnFeatureMemberContext) -> None:
        """Assemble a function body's ``return`` feature relationship."""
        feature = self._child(ctx.featureElement())
        if not isinstance(feature, RawElement):
            raise ValueError("returnFeatureMember requires a retained featureElement")
        self._store(
            ctx,
            ReturnFeatureMember(
                feature_element=feature,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitBaseExpression(self, ctx: SysMLv2Parser.BaseExpressionContext) -> None:
        """Assemble the concrete base-expression alternatives."""
        if ctx.nullExpression():
            self._pass(ctx, ctx.nullExpression())
            return
        if ctx.REGULAR_COMMENT():
            self._store(ctx, CommentExpression(self._text(ctx).strip()))
            return
        if ctx.literalExpression():
            self._pass(ctx, ctx.literalExpression())
            return
        if ctx.constructorExpression():
            self._pass(ctx, ctx.constructorExpression())
            return
        if ctx.bodyExpression():
            self._pass(ctx, ctx.bodyExpression())
            return
        if ctx.AS():
            reference = self._child(ctx.typeReference())
            if not isinstance(reference, QualifiedReference):
                raise ValueError("metadata cast requires typeReference")
            self._store(ctx, MetadataCastExpression(reference))
            return
        reference = self._child(ctx.qualifiedName())
        if isinstance(reference, QualifiedReference):
            if ctx.argumentList():
                arguments = self._child(ctx.argumentList())
                if not isinstance(arguments, ArgumentList):
                    raise ValueError("invocation requires argumentList")
                self._store(
                    ctx, InvocationExpression(FeatureReferenceExpression(reference), arguments)
                )
                return
            if ctx.METADATA():
                self._store(ctx, MetadataAccessExpression(reference))
                return
            self._store(ctx, FeatureReferenceExpression(reference))
            return
        if ctx.LPAREN():
            sequence = (
                self._child(ctx.sequenceExpressionList()) if ctx.sequenceExpressionList() else None
            )
            self._store(
                ctx,
                ParenthesizedExpression(
                    sequence=sequence if isinstance(sequence, SequenceExpression) else None
                ),
            )
            return
        raise ValueError("baseExpression has no assembled alternative")

    def exitSequenceExpressionList(self, ctx: SysMLv2Parser.SequenceExpressionListContext) -> None:
        """Assemble ordered comma-separated expressions."""
        expressions = [self._child(item) for item in ctx.ownedExpression()]
        if not all(isinstance(item, Expression) for item in expressions):
            raise ValueError("ownedExpression child was not assembled as Expression")
        self._store(
            ctx,
            SequenceExpression(
                elements=[item for item in expressions if isinstance(item, Expression)]
            ),
        )

    def exitPositionalArgumentList(self, ctx: SysMLv2Parser.PositionalArgumentListContext) -> None:
        """Collect positional arguments without creating a wrapper node."""
        self.parts[ctx] = [
            item
            for item in (self._child(expr) for expr in ctx.ownedExpression())
            if isinstance(item, Expression)
        ]

    def exitNamedArgument(self, ctx: SysMLv2Parser.NamedArgumentContext) -> None:
        """Assemble one named argument."""
        name = self._child(ctx.qualifiedName())
        expression = self._child(ctx.ownedExpression())
        if not isinstance(name, QualifiedReference) or not isinstance(expression, Expression):
            raise ValueError("namedArgument requires qualifiedName and ownedExpression")
        self._store(ctx, NamedArgument(name, expression))

    def exitNamedArgumentList(self, ctx: SysMLv2Parser.NamedArgumentListContext) -> None:
        """Collect named arguments without retaining a redundant list wrapper."""
        self.parts[ctx] = [
            item
            for item in (self._child(arg) for arg in ctx.namedArgument())
            if isinstance(item, NamedArgument)
        ]

    def exitArgumentList(self, ctx: SysMLv2Parser.ArgumentListContext) -> None:
        """Assemble positional or named arguments with their grammar choice."""
        positional: List[Expression] = []
        named: List[NamedArgument] = []
        if ctx.positionalArgumentList():
            positional = self.parts.get(ctx.positionalArgumentList(), [])
        elif ctx.namedArgumentList():
            named = self.parts.get(ctx.namedArgumentList(), [])
        self._store(ctx, ArgumentList(positional_arguments=positional, named_arguments=named))

    def exitArgumentMember(self, ctx: SysMLv2Parser.ArgumentMemberContext) -> None:
        """Pass an argument expression through its semantic-free wrapper."""
        self._pass(ctx, ctx.ownedExpression())

    def exitArgumentExpressionMember(
        self, ctx: SysMLv2Parser.ArgumentExpressionMemberContext
    ) -> None:
        """Pass a trigger argument expression through its wrapper."""
        self._pass(ctx, ctx.ownedExpression())

    def _binary_operator(self, ctx: Any) -> Optional[str]:
        """Return the explicit binary operator token selected by ``ctx``."""
        if ctx.IMPLIES() is not None:
            return "implies"
        if ctx.OR() is not None:
            return "or"
        if ctx.AND() is not None:
            return "and"
        if ctx.XOR() is not None:
            return "xor"
        if ctx.PIPE() is not None:
            return "|"
        if ctx.AMP() is not None:
            return "&"
        if ctx.EQ_EQ() is not None:
            return "=="
        if ctx.BANG_EQ() is not None:
            return "!="
        if ctx.EQ_EQ_EQ() is not None:
            return "==="
        if ctx.BANG_EQ_EQ() is not None:
            return "!=="
        if ctx.LT() is not None:
            return "<"
        if ctx.GT() is not None:
            return ">"
        if ctx.LE() is not None:
            return "<="
        if ctx.GE() is not None:
            return ">="
        if ctx.DOT_DOT() is not None:
            return ".."
        if ctx.PLUS() is not None:
            return "+"
        if ctx.MINUS() is not None:
            return "-"
        if ctx.STAR() is not None:
            return "*"
        if ctx.SLASH() is not None:
            return "/"
        if ctx.PERCENT() is not None:
            return "%"
        if ctx.STAR_STAR() is not None:
            return "**"
        if ctx.CARET() is not None:
            return "^"
        if ctx.QUESTION_QUESTION() is not None:
            return "??"
        if ctx.ISTYPE() is not None:
            return "istype"
        if ctx.HASTYPE() is not None:
            return "hastype"
        if ctx.AT_SIGN() is not None:
            return "@"
        if ctx.AS() is not None:
            return "as"
        if ctx.AT_AT() is not None:
            return "@@"
        if ctx.META() is not None:
            return "meta"
        return None

    def exitOwnedExpression(self, ctx: SysMLv2Parser.OwnedExpressionContext) -> None:
        """Assemble every concrete recursive ``ownedExpression`` alternative."""
        expressions = [self._child(item) for item in ctx.ownedExpression()]
        if ctx.IF():
            if len(expressions) != 3:
                raise ValueError("conditional expression requires three operands")
            self._store(ctx, ConditionalExpression(expressions[0], expressions[1], expressions[2]))
            return
        if ctx.QUESTION_QUESTION():
            self._store(ctx, CoalesceExpression(expressions[0], expressions[1]))
            return
        operator = self._binary_operator(ctx)
        if operator is not None and len(expressions) == 2:
            if operator == "??":
                self._store(ctx, CoalesceExpression(expressions[0], expressions[1]))
            elif operator in {"istype", "hastype", "@", "@@", "as", "meta"}:
                reference = self._child(ctx.typeReference())
                if not isinstance(reference, QualifiedReference):
                    raise ValueError("type operation requires typeReference")
                if operator == "as":
                    self._store(ctx, CastExpression(expressions[0], reference))
                else:
                    self._store(ctx, TypeOperationExpression(operator, reference, expressions[0]))
            else:
                self._store(ctx, BinaryExpression(expressions[0], operator, expressions[1]))
            return
        if ctx.PLUS() or ctx.MINUS() or ctx.TILDE() or ctx.NOT():
            if len(expressions) != 1:
                raise ValueError("unary expression requires one operand")
            token = "+" if ctx.PLUS() else "-" if ctx.MINUS() else "~" if ctx.TILDE() else "not "
            self._store(ctx, UnaryExpression(token, expressions[0]))
            return
        if expressions and (
            ctx.ISTYPE()
            or ctx.HASTYPE()
            or (ctx.AT_SIGN() and ctx.typeReference())
            or ctx.AT_AT()
            or ctx.META()
        ):
            reference = self._child(ctx.typeReference())
            if not isinstance(reference, QualifiedReference):
                raise ValueError("infix type operation requires typeReference")
            operator = (
                "istype"
                if ctx.ISTYPE()
                else "hastype"
                if ctx.HASTYPE()
                else "@"
                if ctx.AT_SIGN()
                else "@@"
                if ctx.AT_AT()
                else "meta"
            )
            self._store(ctx, TypeOperationExpression(operator, reference, expressions[0]))
            return
        if ctx.AT_SIGN() or ctx.AT_AT():
            reference = self._child(ctx.typeReference())
            if not isinstance(reference, QualifiedReference):
                raise ValueError("prefix type operation requires typeReference")
            self._store(ctx, TypeOperationExpression("@" if ctx.AT_SIGN() else "@@", reference))
            return
        if ctx.AS() and len(expressions) == 1:
            reference = self._child(ctx.typeReference())
            if not isinstance(reference, QualifiedReference):
                raise ValueError("cast requires typeReference")
            self._store(ctx, CastExpression(expressions[0], reference))
            return
        if ctx.LBRACK():
            sequence = (
                self._child(ctx.sequenceExpressionList()) if ctx.sequenceExpressionList() else None
            )
            self._store(
                ctx,
                BracketExpression(
                    expressions[0],
                    sequence if isinstance(sequence, SequenceExpression) else None,
                ),
            )
            return
        if ctx.ARROW():
            reference_context = ctx.qualifiedName()
            if reference_context is None:
                raise ValueError("arrow expression has no function reference")
            member = self._child(reference_context)
            result_context = ctx.bodyExpression() or ctx.argumentList()
            result = self._child(result_context) if result_context is not None else None
            if not isinstance(member, QualifiedReference):
                raise ValueError("arrow expression requires member and result")
            if not isinstance(result, (BodyExpression, ArgumentList)):
                raise ValueError("arrow expression requires body or arguments")
            self._store(ctx, FunctionOperationExpression(expressions[0], member, result))
            return
        if ctx.HASH():
            sequence = (
                self._child(ctx.sequenceExpressionList()) if ctx.sequenceExpressionList() else None
            )
            args = ArgumentList(
                positional_arguments=(
                    sequence.elements if isinstance(sequence, SequenceExpression) else []
                )
            )
            self._store(ctx, IndexExpression(expressions[0], args))
            return
        if ctx.argumentList():
            arguments = self._child(ctx.argumentList())
            if not isinstance(arguments, ArgumentList):
                raise ValueError("invocation requires argumentList")
            self._store(ctx, InvocationExpression(expressions[0], arguments))
            return
        if ctx.DOT() and ctx.qualifiedName():
            member = self._child(ctx.qualifiedName())
            if not isinstance(member, QualifiedReference):
                raise ValueError("feature access requires qualifiedName")
            self._store(ctx, FeatureChainExpression(expressions[0], member))
            return
        if ctx.DOT_QUESTION():
            body = self._child(ctx.bodyExpression())
            if not isinstance(body, BodyExpression):
                raise ValueError("safe body access requires bodyExpression")
            self._store(ctx, SelectExpression(expressions[0], body))
            return
        if ctx.ALL():
            reference = self._child(ctx.typeReference())
            if not isinstance(reference, QualifiedReference):
                raise ValueError("all expression requires typeReference")
            self._store(ctx, AllExpression(reference))
            return
        if ctx.baseExpression():
            self._pass(ctx, ctx.baseExpression())
            return
        raise ValueError("ownedExpression alternative was not assembled")

    # ------------------------------------------------------------------
    # Values, action bodies, and action parameters
    # ------------------------------------------------------------------

    def exitFeatureValue(self, ctx: SysMLv2Parser.FeatureValueContext) -> None:
        """Assemble a value operator and structured expression."""
        expression = self._child(ctx.ownedExpression())
        if not isinstance(expression, Expression):
            raise ValueError("featureValue requires ownedExpression")
        operator = "="
        if ctx.DEFAULT() is not None:
            operator = "default"
            if ctx.COLON_EQ() is not None:
                operator += " :="
            elif ctx.EQ() is not None:
                operator += " ="
        elif ctx.COLON_EQ() is not None:
            operator = ":="
        self._store(ctx, ValuePart(operator, expression))

    def exitValuePart(self, ctx: SysMLv2Parser.ValuePartContext) -> None:
        """Pass the structured feature value through its wrapper."""
        self._pass(ctx, ctx.featureValue())

    def exitActionUsageDeclaration(self, ctx: SysMLv2Parser.ActionUsageDeclarationContext) -> None:
        """Assemble optional usage declaration and value fields."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        self._store(
            ctx,
            ActionUsageDeclaration(
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
            ),
        )

    def exitPerformActionUsageDeclaration(
        self, ctx: SysMLv2Parser.PerformActionUsageDeclarationContext
    ) -> None:
        """Assemble the two concrete perform-declaration alternatives."""
        reference = (
            self._child(ctx.ownedReferenceSubsetting()) if ctx.ownedReferenceSubsetting() else None
        )
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        self._store(
            ctx,
            PerformActionUsageDeclaration(
                referenced_feature=reference if self._is_reference(reference) else None,
                action_usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                specialization=(
                    specialization
                    if isinstance(specialization, FeatureSpecializationPart)
                    else None
                ),
                value_part=value if isinstance(value, ValuePart) else None,
                is_action=ctx.ACTION() is not None,
            ),
        )

    def exitActionBody(self, ctx: SysMLv2Parser.ActionBodyContext) -> None:
        """Assemble a semicolon or ordered action-body statement list."""
        if ctx.SEMI() is not None:
            self._store(ctx, ActionBody(declaration_only=True))
            return
        self._store(ctx, ActionBody(items=self._source_items(ctx.actionBodyItem())))

    def exitReturnParameterMember(self, ctx: SysMLv2Parser.ReturnParameterMemberContext) -> None:
        """Assemble a calculation/case return parameter member."""
        usage = self._child(ctx.usageElement())
        if not isinstance(usage, SourceElement):
            raise ValueError("returnParameterMember requires usageElement")
        self._store(
            ctx,
            ReturnParameterMember(
                usage_element=usage,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitCalculationBodyItem(self, ctx: SysMLv2Parser.CalculationBodyItemContext) -> None:
        """Pass action or return members through ``calculationBodyItem``."""
        child = ctx.actionBodyItem() or ctx.returnParameterMember()
        if child is None:
            raise ValueError("calculationBodyItem has no alternative")
        if self._child(child) is None:
            self._raw_store(ctx)
        else:
            self._pass(ctx, child)

    def _calculation_body(self, ctx: Any, body_type: Any) -> None:
        """Build calculation/case bodies from their explicit child rules."""
        if ctx.SEMI() is not None:
            self._store(ctx, body_type(declaration_only=True))
            return
        part = ctx.calculationBodyPart() if hasattr(ctx, "calculationBodyPart") else None
        items = []
        result = None
        if part is not None:
            items = [self._child(item) for item in part.calculationBodyItem()]
            result = (
                self._child(part.resultExpressionMember())
                if part.resultExpressionMember()
                else None
            )
        self._store(
            ctx,
            body_type(
                items=[item for item in items if isinstance(item, SourceElement)],
                result_expression_member=(
                    result if isinstance(result, ResultExpressionMember) else None
                ),
            ),
        )

    def exitCalculationBody(self, ctx: SysMLv2Parser.CalculationBodyContext) -> None:
        """Assemble a calculation body."""
        self._calculation_body(ctx, CalculationBody)

    def exitCaseBody(self, ctx: SysMLv2Parser.CaseBodyContext) -> None:
        """Assemble a case body."""
        self._calculation_body(ctx, CaseBody)

    def exitCaseBodyItem(self, ctx: SysMLv2Parser.CaseBodyItemContext) -> None:
        """Pass case action/return members or retain a typed fragment."""
        child = (
            ctx.actionBodyItem()
            or ctx.returnParameterMember()
            or ctx.subjectMember()
            or ctx.actorMember()
            or ctx.objectiveMember()
        )
        if child is None:
            raise ValueError("caseBodyItem has no alternative")
        if self._child(child) is None:
            self._raw_store(ctx)
        else:
            self._pass(ctx, child)

    def exitRequirementBodyItem(self, ctx: SysMLv2Parser.RequirementBodyItemContext) -> None:
        """Pass definition members or preserve a requirement-specific member."""
        child = (
            ctx.definitionBodyItem()
            or ctx.subjectMember()
            or ctx.requirementConstraintMember()
            or ctx.framedConcernMember()
            or ctx.requirementVerificationMember()
            or ctx.actorMember()
            or ctx.stakeholderMember()
        )
        if child is None:
            raise ValueError("requirementBodyItem has no alternative")
        if self._child(child) is None:
            self._raw_store(ctx)
        else:
            self._pass(ctx, child)

    def exitRequirementBody(self, ctx: SysMLv2Parser.RequirementBodyContext) -> None:
        """Assemble a requirement body with ordered members."""
        if ctx.SEMI() is not None:
            self._store(ctx, RequirementBody(declaration_only=True))
            return
        self._store(ctx, RequirementBody(items=self._source_items(ctx.requirementBodyItem())))

    def exitViewDefinitionBodyItem(self, ctx: SysMLv2Parser.ViewDefinitionBodyItemContext) -> None:
        """Pass view definition members through their explicit alternatives."""
        child = ctx.definitionBodyItem() or ctx.elementFilterMember() or ctx.viewRenderingMember()
        if child is None:
            raise ValueError("viewDefinitionBodyItem has no alternative")
        if self._child(child) is None:
            self._raw_store(ctx)
        else:
            self._pass(ctx, child)

    def exitViewDefinitionBody(self, ctx: SysMLv2Parser.ViewDefinitionBodyContext) -> None:
        """Assemble a view-definition body."""
        if ctx.SEMI() is not None:
            self._store(ctx, ViewDefinitionBody(declaration_only=True))
            return
        self._store(ctx, ViewDefinitionBody(items=self._source_items(ctx.viewDefinitionBodyItem())))

    def exitViewBodyItem(self, ctx: SysMLv2Parser.ViewBodyItemContext) -> None:
        """Pass view-body members through their explicit alternatives."""
        child = (
            ctx.definitionBodyItem()
            or ctx.elementFilterMember()
            or ctx.viewRenderingMember()
            or ctx.expose()
        )
        if child is None:
            raise ValueError("viewBodyItem has no alternative")
        if self._child(child) is None:
            self._raw_store(ctx)
        else:
            self._pass(ctx, child)

    def exitViewBody(self, ctx: SysMLv2Parser.ViewBodyContext) -> None:
        """Assemble a view usage body."""
        if ctx.SEMI() is not None:
            self._store(ctx, ViewBody(declaration_only=True))
            return
        self._store(ctx, ViewBody(items=self._source_items(ctx.viewBodyItem())))

    def exitEnumerationUsageMember(self, ctx: SysMLv2Parser.EnumerationUsageMemberContext) -> None:
        """Assemble metadata, visibility, and an enumerated value."""
        value = self._child(ctx.enumeratedValue())
        if not isinstance(value, EnumeratedValue):
            raise ValueError("enumerationUsageMember requires enumeratedValue")
        self._store(
            ctx,
            EnumerationUsageMember(
                enumerated_value=value,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
                prefix_metadata=[self._text(item).strip() for item in ctx.prefixMetadataMember()],
            ),
        )

    def exitEnumeratedValue(self, ctx: SysMLv2Parser.EnumeratedValueContext) -> None:
        """Assemble an enumerated value from its usage completion."""
        usage = self._child(ctx.usage())
        if not isinstance(usage, Usage):
            raise ValueError("enumeratedValue requires usage")
        self._store(ctx, EnumeratedValue(usage=usage, is_enum=ctx.ENUM() is not None))

    def exitEnumerationBody(self, ctx: SysMLv2Parser.EnumerationBodyContext) -> None:
        """Assemble an enumeration body."""
        if ctx.SEMI() is not None:
            self._store(ctx, EnumerationBody(declaration_only=True))
            return
        members = []
        for child in ctx.children or []:
            node = self._child(child)
            if isinstance(node, SourceElement):
                members.append(node)
        self._store(ctx, EnumerationBody(items=members))

    def exitActionBodyItem(self, ctx: SysMLv2Parser.ActionBodyItemContext) -> None:
        """Pass or assemble one action-body alternative without text collapse."""
        if ctx.nonBehaviorBodyItem():
            self._pass(ctx, ctx.nonBehaviorBodyItem())
            return
        if ctx.initialNodeMember():
            self._pass(ctx, ctx.initialNodeMember())
            return
        if ctx.actionBehaviorMember():
            self._pass(ctx, ctx.actionBehaviorMember())
            return
        if ctx.guardedSuccessionMember():
            self._pass(ctx, ctx.guardedSuccessionMember())
            return
        raise ValueError("actionBodyItem alternative was not assembled")

    def exitControlNodePrefix(self, ctx: SysMLv2Parser.ControlNodePrefixContext) -> None:
        """Assemble the narrower prefix used by control nodes."""
        ref = ctx.refPrefix()
        direction = None
        if ref is not None and ref.featureDirection() is not None:
            direction = self._text(ref.featureDirection()).strip()
        self._store(
            ctx,
            ControlNodePrefix(
                feature_direction=direction,
                is_derived=bool(ref and ref.DERIVED()),
                is_abstract=bool(ref and ref.ABSTRACT()),
                is_variation=bool(ref and ref.VARIATION()),
                is_constant=bool(ref and ref.CONSTANT()),
                is_individual=ctx.INDIVIDUAL() is not None,
                portion_kind=self._text(ctx.portionKind()).strip() if ctx.portionKind() else None,
                extension_keywords=[
                    self._text(item).strip() for item in ctx.usageExtensionKeyword()
                ],
            ),
        )

    def exitActionNodePrefix(self, ctx: SysMLv2Parser.ActionNodePrefixContext) -> None:
        """Assemble an action-node prefix and optional action declaration."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = (
            self._child(ctx.actionNodeUsageDeclaration())
            if ctx.actionNodeUsageDeclaration()
            else None
        )
        if not isinstance(prefix, OccurrenceUsagePrefix):
            raise ValueError("actionNodePrefix requires occurrenceUsagePrefix")
        if declaration is not None and not isinstance(declaration, ActionNodeUsageDeclaration):
            raise ValueError("actionNodePrefix action declaration was not assembled")
        self._store(
            ctx,
            ActionNodePrefix(
                occurrence_usage_prefix=prefix,
                action_node_usage_declaration=declaration,
            ),
        )

    def exitControlNode(self, ctx: SysMLv2Parser.ControlNodeContext) -> None:
        """Pass one concrete control-node alternative."""
        child = ctx.mergeNode() or ctx.decisionNode() or ctx.joinNode() or ctx.forkNode()
        if child is None:
            raise ValueError("controlNode has no alternative")
        self._pass(ctx, child)

    def exitMergeNode(self, ctx: SysMLv2Parser.MergeNodeContext) -> None:
        """Assemble a merge node with its optional declaration and body."""
        prefix = self._child(ctx.controlNodePrefix())
        body = self._child(ctx.actionBody())
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        if not isinstance(prefix, ControlNodePrefix) or not isinstance(body, ActionBody):
            raise ValueError("mergeNode has incomplete required fields")
        if declaration is not None and not isinstance(declaration, UsageDeclaration):
            raise ValueError("mergeNode declaration was not assembled")
        self._store(ctx, MergeNode(prefix, body, declaration))

    def exitDecisionNode(self, ctx: SysMLv2Parser.DecisionNodeContext) -> None:
        """Assemble a decision node with its optional declaration and body."""
        prefix = self._child(ctx.controlNodePrefix())
        body = self._child(ctx.actionBody())
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        if not isinstance(prefix, ControlNodePrefix) or not isinstance(body, ActionBody):
            raise ValueError("decisionNode has incomplete required fields")
        if declaration is not None and not isinstance(declaration, UsageDeclaration):
            raise ValueError("decisionNode declaration was not assembled")
        self._store(ctx, DecisionNode(prefix, body, declaration))

    def exitJoinNode(self, ctx: SysMLv2Parser.JoinNodeContext) -> None:
        """Assemble a join node with its optional declaration and body."""
        prefix = self._child(ctx.controlNodePrefix())
        body = self._child(ctx.actionBody())
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        if not isinstance(prefix, ControlNodePrefix) or not isinstance(body, ActionBody):
            raise ValueError("joinNode has incomplete required fields")
        if declaration is not None and not isinstance(declaration, UsageDeclaration):
            raise ValueError("joinNode declaration was not assembled")
        self._store(ctx, JoinNode(prefix, body, declaration))

    def exitForkNode(self, ctx: SysMLv2Parser.ForkNodeContext) -> None:
        """Assemble a fork node with its optional declaration and body."""
        prefix = self._child(ctx.controlNodePrefix())
        body = self._child(ctx.actionBody())
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        if not isinstance(prefix, ControlNodePrefix) or not isinstance(body, ActionBody):
            raise ValueError("forkNode has incomplete required fields")
        if declaration is not None and not isinstance(declaration, UsageDeclaration):
            raise ValueError("forkNode declaration was not assembled")
        self._store(ctx, ForkNode(prefix, body, declaration))

    def exitAcceptNode(self, ctx: SysMLv2Parser.AcceptNodeContext) -> None:
        """Assemble a complete accept action node."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.acceptNodeDeclaration())
        body = self._child(ctx.actionBody())
        if not isinstance(prefix, OccurrenceUsagePrefix):
            raise ValueError("acceptNode requires occurrenceUsagePrefix")
        if not isinstance(declaration, AcceptNodeDeclaration) or not isinstance(body, ActionBody):
            raise ValueError("acceptNode has incomplete required fields")
        self._store(ctx, AcceptNode(prefix, declaration, body))

    def exitSendNode(self, ctx: SysMLv2Parser.SendNodeContext) -> None:
        """Assemble a complete send action node and its declaration choice."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        action_node_declaration = (
            self._child(ctx.actionNodeUsageDeclaration())
            if ctx.actionNodeUsageDeclaration()
            else None
        )
        action_usage_declaration = (
            self._child(ctx.actionUsageDeclaration()) if ctx.actionUsageDeclaration() else None
        )
        parameter = self._child(ctx.nodeParameterMember()) if ctx.nodeParameterMember() else None
        sender = self._child(ctx.senderReceiverPart()) if ctx.senderReceiverPart() else None
        if not isinstance(prefix, OccurrenceUsagePrefix):
            raise ValueError("sendNode requires occurrenceUsagePrefix")
        if action_node_declaration is not None and not isinstance(
            action_node_declaration, ActionNodeUsageDeclaration
        ):
            raise ValueError("sendNode action declaration was not assembled")
        if action_usage_declaration is not None and not isinstance(
            action_usage_declaration, ActionUsageDeclaration
        ):
            raise ValueError("sendNode usage declaration was not assembled")
        if ctx.nodeParameterMember() is not None and not isinstance(parameter, NodeParameter):
            raise ValueError("sendNode parameter was not assembled")
        if sender is not None and not isinstance(sender, SenderReceiverPart):
            raise ValueError("sendNode sender/receiver part was not assembled")
        body = self._child(ctx.actionBody())
        if not isinstance(body, ActionBody):
            raise ValueError("sendNode body was not assembled")
        self._store(
            ctx,
            SendNode(
                occurrence_usage_prefix=prefix,
                declaration=SendNodeUsageDeclaration(
                    send_parameter=parameter if isinstance(parameter, NodeParameter) else None,
                    action_node_usage_declaration=(
                        action_node_declaration
                        if isinstance(action_node_declaration, ActionNodeUsageDeclaration)
                        else None
                    ),
                    action_usage_declaration=(
                        action_usage_declaration
                        if isinstance(action_usage_declaration, ActionUsageDeclaration)
                        else None
                    ),
                    sender_receiver_part=sender if isinstance(sender, SenderReceiverPart) else None,
                ),
                action_body=body,
            ),
        )

    def exitAssignmentNode(self, ctx: SysMLv2Parser.AssignmentNodeContext) -> None:
        """Assemble a complete assignment action node."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.assignmentNodeDeclaration())
        body = self._child(ctx.actionBody())
        if not isinstance(prefix, OccurrenceUsagePrefix):
            raise ValueError("assignmentNode requires occurrenceUsagePrefix")
        if not isinstance(declaration, AssignmentNodeDeclaration) or not isinstance(
            body, ActionBody
        ):
            raise ValueError("assignmentNode has incomplete required fields")
        self._store(ctx, AssignmentNode(prefix, declaration, body))

    def exitTerminateNode(self, ctx: SysMLv2Parser.TerminateNodeContext) -> None:
        """Assemble a terminate node with optional parameter and declaration."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = (
            self._child(ctx.actionNodeUsageDeclaration())
            if ctx.actionNodeUsageDeclaration()
            else None
        )
        parameter = self._child(ctx.nodeParameterMember()) if ctx.nodeParameterMember() else None
        body = self._child(ctx.actionBody())
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(body, ActionBody):
            raise ValueError("terminateNode has incomplete required fields")
        if declaration is not None and not isinstance(declaration, ActionNodeUsageDeclaration):
            raise ValueError("terminateNode declaration was not assembled")
        if parameter is not None and not isinstance(parameter, NodeParameter):
            raise ValueError("terminateNode parameter was not assembled")
        self._store(
            ctx,
            TerminateNode(
                occurrence_usage_prefix=prefix,
                action_body=body,
                action_node_usage_declaration=declaration,
                node_parameter=parameter,
            ),
        )

    def exitExpressionParameterMember(
        self, ctx: SysMLv2Parser.ExpressionParameterMemberContext
    ) -> None:
        """Pass an expression through the action-node parameter wrapper."""
        self._pass(ctx, ctx.ownedExpression())

    def exitActionBodyParameterMember(
        self, ctx: SysMLv2Parser.ActionBodyParameterMemberContext
    ) -> None:
        """Pass a structured action body through its member wrapper."""
        self._pass(ctx, ctx.actionBodyParameter())

    def exitActionBodyParameter(self, ctx: SysMLv2Parser.ActionBodyParameterContext) -> None:
        """Assemble a brace-delimited action body used by control flow."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        if declaration is not None and not isinstance(declaration, UsageDeclaration):
            raise ValueError("actionBodyParameter declaration was not assembled")
        self._store(
            ctx,
            ActionBodyParameter(
                items=self._source_items(ctx.actionBodyItem()),
                action_declaration=declaration,
            ),
        )

    def exitIfNodeParameterMember(self, ctx: SysMLv2Parser.IfNodeParameterMemberContext) -> None:
        """Pass a nested if node through the else-branch wrapper."""
        self._pass(ctx, ctx.ifNode())

    def exitIfNode(self, ctx: SysMLv2Parser.IfNodeContext) -> None:
        """Assemble an if node and its optional else branch."""
        prefix = self._child(ctx.actionNodePrefix())
        condition = self._child(ctx.expressionParameterMember())
        bodies = [self._child(item) for item in ctx.actionBodyParameterMember()]
        nested = self._child(ctx.ifNodeParameterMember()) if ctx.ifNodeParameterMember() else None
        if not isinstance(prefix, ActionNodePrefix) or not isinstance(condition, Expression):
            raise ValueError("ifNode has incomplete condition or prefix")
        if not bodies or not isinstance(bodies[0], ActionBodyParameter):
            raise ValueError("ifNode requires then action body")
        else_body = nested if isinstance(nested, IfNode) else None
        if len(bodies) > 1:
            if not isinstance(bodies[1], ActionBodyParameter):
                raise ValueError("ifNode else action body was not assembled")
            else_body = bodies[1]
        self._store(ctx, IfNode(prefix, condition, bodies[0], else_body))

    def exitWhileLoopNode(self, ctx: SysMLv2Parser.WhileLoopNodeContext) -> None:
        """Assemble while and empty-loop forms with optional until guard."""
        prefix = self._child(ctx.actionNodePrefix())
        expression_contexts = ctx.expressionParameterMember()
        condition = None
        until = None
        if ctx.WHILE() is not None:
            condition = self._child(expression_contexts[0]) if expression_contexts else None
            if ctx.UNTIL() is not None and len(expression_contexts) > 1:
                until = self._child(expression_contexts[1])
        elif ctx.UNTIL() is not None and expression_contexts:
            until = self._child(expression_contexts[0])
        body = self._child(ctx.actionBodyParameterMember())
        if not isinstance(prefix, ActionNodePrefix) or not isinstance(body, ActionBodyParameter):
            raise ValueError("whileLoopNode has incomplete required fields")
        if condition is not None and not isinstance(condition, Expression):
            raise ValueError("whileLoopNode condition was not assembled")
        if until is not None and not isinstance(until, Expression):
            raise ValueError("whileLoopNode until condition was not assembled")
        self._store(
            ctx,
            WhileLoopNode(
                action_node_prefix=prefix,
                loop_kind="while" if ctx.WHILE() is not None else "loop",
                body=body,
                condition=condition,
                until_condition=until,
            ),
        )

    def exitForVariableDeclarationMember(
        self, ctx: SysMLv2Parser.ForVariableDeclarationMemberContext
    ) -> None:
        """Pass an optional for-loop variable declaration."""
        if ctx.usageDeclaration() is None:
            self.parts[ctx] = None
            return
        declaration = self._child(ctx.usageDeclaration())
        if not isinstance(declaration, UsageDeclaration):
            raise ValueError("for variable declaration was not assembled")
        self.parts[ctx] = declaration

    def exitForLoopNode(self, ctx: SysMLv2Parser.ForLoopNodeContext) -> None:
        """Assemble a for-loop node with structured collection expression."""
        prefix = self._child(ctx.actionNodePrefix())
        variable = self.parts.get(ctx.forVariableDeclarationMember())
        collection = self._child(ctx.nodeParameterMember())
        body = self._child(ctx.actionBodyParameterMember())
        if not isinstance(prefix, ActionNodePrefix) or not isinstance(collection, NodeParameter):
            raise ValueError("forLoopNode has incomplete prefix or collection")
        if not isinstance(body, ActionBodyParameter):
            raise ValueError("forLoopNode body was not assembled")
        if variable is not None and not isinstance(variable, UsageDeclaration):
            raise ValueError("forLoopNode variable declaration was not assembled")
        self._store(
            ctx,
            ForLoopNode(
                action_node_prefix=prefix,
                collection=collection,
                body=body,
                variable_declaration=variable,
            ),
        )

    def exitActionBehaviorMember(self, ctx: SysMLv2Parser.ActionBehaviorMemberContext) -> None:
        """Pass action-node or behavior-usage alternatives."""
        child = ctx.actionNodeMember() or ctx.behaviorUsageMember()
        if child is None:
            raise ValueError("actionBehaviorMember has no alternative")
        self._pass(ctx, child)

    def exitActionNodeMember(self, ctx: SysMLv2Parser.ActionNodeMemberContext) -> None:
        """Assemble an action-node statement with its member prefix."""
        child = self._child(ctx.actionNode())
        if not isinstance(child, ActionNode):
            raise ValueError("actionNodeMember requires actionNode")
        self._store(
            ctx,
            ActionNodeMember(
                action_node=child,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitActionNode(self, ctx: SysMLv2Parser.ActionNodeContext) -> None:
        """Pass one concrete action-node statement alternative."""
        child = (
            ctx.controlNode()
            or ctx.sendNode()
            or ctx.acceptNode()
            or ctx.assignmentNode()
            or ctx.terminateNode()
            or ctx.ifNode()
            or ctx.whileLoopNode()
            or ctx.forLoopNode()
        )
        if child is None:
            raise ValueError("actionNode has no alternative")
        self._pass(ctx, child)

    def exitRelationshipBody(self, ctx: SysMLv2Parser.RelationshipBodyContext) -> None:
        """Preserve relationship-body syntax as an explicit non-state node."""
        # The enclosing AST node owns indentation when it renders a nested
        # body.  Retaining absolute source indentation here would make a
        # second parse of canonical output change this field and break AST
        # equality for otherwise identical models.
        self._store(ctx, RelationshipBody(_relative_source(self._text(ctx))))

    def exitInitialNodeMember(self, ctx: SysMLv2Parser.InitialNodeMemberContext) -> None:
        """Assemble an action body's initial ``first`` node member."""
        target = self._child(ctx.qualifiedName())
        body = self._child(ctx.relationshipBody())
        if not isinstance(target, QualifiedReference) or not isinstance(body, RelationshipBody):
            raise ValueError("initialNodeMember has incomplete required fields")
        self._store(
            ctx,
            InitialNodeMember(
                target=target,
                relationship_body=body,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitTargetSuccession(self, ctx: SysMLv2Parser.TargetSuccessionContext) -> None:
        """Assemble an ordinary source-end to target succession."""
        connector = self._child(ctx.connectorEndMember())
        if isinstance(connector, ConnectorEnd):
            connector = connector.reference
        if not self._is_reference(connector):
            raise ValueError("targetSuccession requires connector-end reference")
        self._store(
            ctx,
            TargetSuccession(
                target=TransitionSuccession(connector),
                source_end_text=self._text(ctx.sourceEndMember()).strip()
                if ctx.sourceEndMember()
                else None,
            ),
        )

    def exitGuardedTargetSuccession(
        self, ctx: SysMLv2Parser.GuardedTargetSuccessionContext
    ) -> None:
        """Assemble a guarded target succession."""
        guard = self._child(ctx.guardExpressionMember())
        target = self._child(ctx.transitionSuccessionMember())
        if not isinstance(guard, GuardExpressionMember) or not isinstance(
            target, TransitionSuccession
        ):
            raise ValueError("guardedTargetSuccession has incomplete required fields")
        self._store(ctx, GuardedTargetSuccession(guard=guard, target=target))

    def exitDefaultTargetSuccession(
        self, ctx: SysMLv2Parser.DefaultTargetSuccessionContext
    ) -> None:
        """Assemble an ``else`` target succession."""
        target = self._child(ctx.transitionSuccessionMember())
        if not isinstance(target, TransitionSuccession):
            raise ValueError("defaultTargetSuccession requires transition succession")
        self._store(ctx, DefaultTargetSuccession(target=target))

    def exitActionTargetSuccession(self, ctx: SysMLv2Parser.ActionTargetSuccessionContext) -> None:
        """Assemble a target succession and its generic usage body."""
        succession_ctx = (
            ctx.targetSuccession() or ctx.guardedTargetSuccession() or ctx.defaultTargetSuccession()
        )
        succession = self._child(succession_ctx)
        body = self._child(ctx.usageBody())
        if not isinstance(body, DefinitionBody):
            raise ValueError("actionTargetSuccession requires usage body")
        if not isinstance(
            succession,
            (TargetSuccession, GuardedTargetSuccession, DefaultTargetSuccession),
        ):
            raise ValueError("actionTargetSuccession has no assembled succession")
        self._store(ctx, ActionTargetSuccession(succession=succession, body=body))

    def exitActionTargetSuccessionMember(
        self, ctx: SysMLv2Parser.ActionTargetSuccessionMemberContext
    ) -> None:
        """Assemble an action target succession with member visibility."""
        succession = self._child(ctx.actionTargetSuccession())
        if not isinstance(succession, ActionTargetSuccession):
            raise ValueError("actionTargetSuccessionMember requires succession")
        self._store(
            ctx,
            ActionTargetSuccessionMember(
                target_succession=succession,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitGuardedSuccession(self, ctx: SysMLv2Parser.GuardedSuccessionContext) -> None:
        """Assemble an action-body guarded succession."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        source = self._child(ctx.featureChainMember())
        guard = self._child(ctx.guardExpressionMember())
        target = self._child(ctx.transitionSuccessionMember())
        body = self._child(ctx.usageBody())
        if not isinstance(source, FeatureChain) or not isinstance(guard, GuardExpressionMember):
            raise ValueError("guardedSuccession requires source and guard")
        if not isinstance(target, TransitionSuccession) or not isinstance(body, DefinitionBody):
            raise ValueError("guardedSuccession has incomplete target or body")
        if declaration is not None and not isinstance(declaration, UsageDeclaration):
            raise ValueError("guardedSuccession declaration was not assembled")
        self._store(
            ctx,
            GuardedSuccession(
                source=source,
                guard=guard,
                target=target,
                body=body,
                usage_declaration=declaration,
                has_succession_keyword=ctx.SUCCESSION() is not None,
            ),
        )

    def exitGuardedSuccessionMember(
        self, ctx: SysMLv2Parser.GuardedSuccessionMemberContext
    ) -> None:
        """Assemble a guarded succession member with visibility."""
        succession = self._child(ctx.guardedSuccession())
        if not isinstance(succession, GuardedSuccession):
            raise ValueError("guardedSuccessionMember requires succession")
        self._store(
            ctx,
            GuardedSuccessionMember(
                succession=succession,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitStateActionUsage(self, ctx: SysMLv2Parser.StateActionUsageContext) -> None:
        """Pass the explicit state action variant or empty action."""
        if ctx.emptyActionUsage_():
            self._store(ctx, EmptyActionUsage())
            return
        child = (
            ctx.statePerformActionUsage()
            or ctx.stateAcceptActionUsage()
            or ctx.stateSendActionUsage()
            or ctx.stateAssignmentActionUsage()
        )
        if child is None:
            raise ValueError("stateActionUsage has no alternative")
        self._pass(ctx, child)

    def exitStatePerformActionUsage(
        self, ctx: SysMLv2Parser.StatePerformActionUsageContext
    ) -> None:
        """Assemble a state perform action declaration and body."""
        declaration = self._child(ctx.performActionUsageDeclaration())
        body = self._child(ctx.actionBody())
        if not isinstance(declaration, PerformActionUsageDeclaration) or not isinstance(
            body, ActionBody
        ):
            raise ValueError("state perform action requires declaration and body")
        self._store(ctx, StatePerformActionUsage(declaration=declaration, body=body))

    def exitStateAcceptActionUsage(self, ctx: SysMLv2Parser.StateAcceptActionUsageContext) -> None:
        """Assemble a state accept action declaration and body."""
        declaration = self._child(ctx.acceptNodeDeclaration())
        body = self._child(ctx.actionBody())
        if not isinstance(declaration, AcceptNodeDeclaration) or not isinstance(body, ActionBody):
            raise ValueError("state accept action requires declaration and body")
        self._store(ctx, AcceptActionUsage(declaration=declaration, body=body))

    def exitStateSendActionUsage(self, ctx: SysMLv2Parser.StateSendActionUsageContext) -> None:
        """Assemble a state send action declaration and body."""
        declaration = self._child(ctx.sendNodeDeclaration())
        body = self._child(ctx.actionBody())
        if not isinstance(declaration, SendNodeDeclaration) or not isinstance(body, ActionBody):
            raise ValueError("state send action requires declaration and body")
        self._store(ctx, SendActionUsage(declaration=declaration, body=body))

    def exitStateAssignmentActionUsage(
        self, ctx: SysMLv2Parser.StateAssignmentActionUsageContext
    ) -> None:
        """Assemble a state assignment action declaration and body."""
        declaration = self._child(ctx.assignmentNodeDeclaration())
        body = self._child(ctx.actionBody())
        if not isinstance(declaration, AssignmentNodeDeclaration) or not isinstance(
            body, ActionBody
        ):
            raise ValueError("state assignment action requires declaration and body")
        self._store(ctx, AssignmentActionUsage(declaration=declaration, body=body))

    def exitPayloadParameter(self, ctx: SysMLv2Parser.PayloadParameterContext) -> None:
        """Assemble payload feature or trigger-value alternatives."""
        feature = self._child(ctx.payloadFeature()) if ctx.payloadFeature() else None
        identification = self._child(ctx.identification()) if ctx.identification() else None
        specialization = (
            self._child(ctx.payloadFeatureSpecializationPart())
            if ctx.payloadFeatureSpecializationPart()
            else None
        )
        trigger = self._child(ctx.triggerValuePart()) if ctx.triggerValuePart() else None
        self._store(
            ctx,
            PayloadParameter(
                payload_feature=feature if isinstance(feature, PayloadFeature) else None,
                identification=identification
                if isinstance(identification, Identification)
                else None,
                specialization=(
                    specialization
                    if isinstance(specialization, FeatureSpecializationPart)
                    else None
                ),
                trigger_expression=trigger if isinstance(trigger, Expression) else None,
            ),
        )

    def exitPayloadParameterMember(self, ctx: SysMLv2Parser.PayloadParameterMemberContext) -> None:
        """Pass payload parameter through its wrapper."""
        self._pass(ctx, ctx.payloadParameter())

    def exitPayloadFeatureMember(self, ctx: SysMLv2Parser.PayloadFeatureMemberContext) -> None:
        """Pass payload feature through its one-child grammar wrapper."""
        self._pass(ctx, ctx.payloadFeature())

    def exitPayloadFeature(self, ctx: SysMLv2Parser.PayloadFeatureContext) -> None:
        """Assemble every structured ``payloadFeature`` alternative."""
        owned_typing = self._child(ctx.ownedFeatureTyping()) if ctx.ownedFeatureTyping() else None
        identification = self._child(ctx.identification()) if ctx.identification() else None
        specialization = (
            self._child(ctx.payloadFeatureSpecializationPart())
            if ctx.payloadFeatureSpecializationPart()
            else None
        )
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        multiplicity = (
            self._text(ctx.ownedMultiplicity()).strip() if ctx.ownedMultiplicity() else None
        )
        if (
            not isinstance(owned_typing, OwnedFeatureTyping)
            and not isinstance(identification, Identification)
            and not isinstance(specialization, FeatureSpecializationPart)
            and not multiplicity
        ):
            raise ValueError("payloadFeature has no assembled alternative")
        self._store(
            ctx,
            PayloadFeature(
                identification=identification
                if isinstance(identification, Identification)
                else None,
                specialization=specialization
                if isinstance(specialization, FeatureSpecializationPart)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
                owned_feature_typing=owned_typing
                if isinstance(owned_typing, OwnedFeatureTyping)
                else None,
                multiplicity_text=multiplicity,
            ),
        )

    def exitPayloadFeatureSpecializationPart(
        self, ctx: SysMLv2Parser.PayloadFeatureSpecializationPartContext
    ) -> None:
        """Preserve payload specialization structure as a feature part."""
        specializations = [self._child(item) for item in ctx.featureSpecialization()]
        multiplicity = (
            self._text(ctx.multiplicityPart()).strip() if ctx.multiplicityPart() else None
        )
        self._store(
            ctx,
            FeatureSpecializationPart(
                specializations=[
                    item for item in specializations if isinstance(item, FeatureSpecialization)
                ],
                multiplicity_text=multiplicity,
            ),
        )

    def exitNodeParameter(self, ctx: SysMLv2Parser.NodeParameterContext) -> None:
        """Assemble one node parameter from its feature binding expression."""
        expression = self._child(ctx.featureBinding())
        if not isinstance(expression, Expression):
            raise ValueError("nodeParameter requires an Expression")
        self._store(ctx, NodeParameter(expression))

    def exitFeatureBinding(self, ctx: SysMLv2Parser.FeatureBindingContext) -> None:
        """Pass a bound expression through its grammar wrapper."""
        self._pass(ctx, ctx.ownedExpression())

    def exitNodeParameterMember(self, ctx: SysMLv2Parser.NodeParameterMemberContext) -> None:
        """Pass node parameter through its wrapper."""
        self._pass(ctx, ctx.nodeParameter())

    def exitAcceptParameterPart(self, ctx: SysMLv2Parser.AcceptParameterPartContext) -> None:
        """Assemble payload and optional ``via`` node parameter."""
        payload = self._child(ctx.payloadParameterMember())
        via = self._child(ctx.nodeParameterMember()) if ctx.nodeParameterMember() else None
        if not isinstance(payload, PayloadParameter):
            raise ValueError("acceptParameterPart requires payloadParameter")
        if ctx.nodeParameterMember() is not None and not isinstance(via, NodeParameter):
            raise ValueError("acceptParameterPart via requires nodeParameter")
        self._store(
            ctx,
            AcceptParameterPart(
                payload=payload,
                via_parameter=via,
            ),
        )

    def exitTriggerExpression(self, ctx: SysMLv2Parser.TriggerExpressionContext) -> None:
        """Assemble ``at``, ``after`` and ``when`` trigger expressions."""
        argument = self._child(ctx.argumentMember() or ctx.argumentExpressionMember())
        if not isinstance(argument, Expression):
            raise ValueError("triggerExpression requires an Expression argument")
        operator = "at" if ctx.AT() is not None else "after" if ctx.AFTER() is not None else "when"
        self._store(ctx, TriggerExpression(operator, argument))

    def exitTriggerValuePart(self, ctx: SysMLv2Parser.TriggerValuePartContext) -> None:
        """Pass trigger feature value through its one-child wrapper."""
        self._pass(ctx, ctx.triggerFeatureValue())

    def exitTriggerFeatureValue(self, ctx: SysMLv2Parser.TriggerFeatureValueContext) -> None:
        """Pass trigger expression through its one-child wrapper."""
        self._pass(ctx, ctx.triggerExpression())

    def exitAcceptNodeDeclaration(self, ctx: SysMLv2Parser.AcceptNodeDeclarationContext) -> None:
        """Assemble an accept declaration's optional action usage and payload."""
        action_decl = (
            self._child(ctx.actionNodeUsageDeclaration())
            if ctx.actionNodeUsageDeclaration()
            else None
        )
        params = self._child(ctx.acceptParameterPart())
        if not isinstance(params, AcceptParameterPart):
            raise ValueError("acceptNodeDeclaration requires acceptParameterPart")
        self._store(
            ctx,
            AcceptNodeDeclaration(
                accept_parameter_part=params,
                action_node_usage_declaration=action_decl
                if isinstance(action_decl, ActionNodeUsageDeclaration)
                else None,
            ),
        )

    def exitActionNodeUsageDeclaration(
        self, ctx: SysMLv2Parser.ActionNodeUsageDeclarationContext
    ) -> None:
        """Assemble an optional action-node usage declaration."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        self._store(
            ctx,
            ActionNodeUsageDeclaration(
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
            ),
        )

    def exitSenderReceiverPart(self, ctx: SysMLv2Parser.SenderReceiverPartContext) -> None:
        """Assemble explicit sender/receiver node parameters."""
        parameters = [self._child(item) for item in ctx.nodeParameterMember()]
        self._store(
            ctx,
            SenderReceiverPart(
                via_parameter=parameters[0]
                if parameters and isinstance(parameters[0], NodeParameter) and ctx.VIA()
                else None,
                to_parameter=parameters[-1]
                if parameters and isinstance(parameters[-1], NodeParameter) and ctx.TO()
                else None,
            ),
        )

    def exitSendNodeDeclaration(self, ctx: SysMLv2Parser.SendNodeDeclarationContext) -> None:
        """Assemble a send declaration and its optional routing fields."""
        action_decl = (
            self._child(ctx.actionNodeUsageDeclaration())
            if ctx.actionNodeUsageDeclaration()
            else None
        )
        parameter = self._child(ctx.nodeParameterMember()) if ctx.nodeParameterMember() else None
        if not isinstance(parameter, NodeParameter):
            raise ValueError("sendNodeDeclaration requires nodeParameter")
        if action_decl is not None and not isinstance(action_decl, ActionNodeUsageDeclaration):
            raise ValueError("sendNodeDeclaration action declaration was not assembled")
        sender = self._child(ctx.senderReceiverPart()) if ctx.senderReceiverPart() else None
        if sender is not None and not isinstance(sender, SenderReceiverPart):
            raise ValueError("sendNodeDeclaration sender/receiver was not assembled")
        self._store(
            ctx,
            SendNodeDeclaration(
                send_parameter=parameter,
                action_node_usage_declaration=action_decl,
                sender_receiver_part=sender,
            ),
        )

    def exitAssignmentNodeDeclaration(
        self, ctx: SysMLv2Parser.AssignmentNodeDeclarationContext
    ) -> None:
        """Preserve assignment target and value fields for node assembly."""
        target_binding = self._child(ctx.assignmentTargetMember())
        target = self._child(ctx.featureChainMember())
        value = self._child(ctx.nodeParameterMember())
        action_decl = (
            self._child(ctx.actionNodeUsageDeclaration())
            if ctx.actionNodeUsageDeclaration()
            else None
        )
        if not isinstance(target, FeatureChain) or not isinstance(value, NodeParameter):
            raise ValueError("assignmentNodeDeclaration requires target and value")
        if target_binding is not None and not isinstance(target_binding, Expression):
            raise ValueError("assignmentNodeDeclaration target binding was not an expression")
        self._store(
            ctx,
            AssignmentNodeDeclaration(
                target=target,
                value=value,
                action_node_usage_declaration=action_decl
                if isinstance(action_decl, ActionNodeUsageDeclaration)
                else None,
                assignment_target_binding=(
                    target_binding if isinstance(target_binding, Expression) else None
                ),
            ),
        )

    def exitActionUsage(self, ctx: SysMLv2Parser.ActionUsageContext) -> None:
        """Assemble a top-level ``action`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.actionUsageDeclaration())
        body = self._child(ctx.actionBody())
        # The SysML examples use ``action stop terminate;`` as a declaration-
        # only action usage.  The compatibility grammar exposes that form
        # without an ``actionBody`` child, so materialize the required
        # semicolon body here instead of dropping it during AST assembly.
        is_terminate = ctx.TERMINATE() is not None
        if body is None and is_terminate and ctx.SEMI() is not None:
            body = ActionBody(declaration_only=True)
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, ActionUsageDeclaration)
            or not isinstance(body, ActionBody)
        ):
            raise ValueError("actionUsage has incomplete required fields")
        self._store(
            ctx,
            ActionUsage(
                occurrence_usage_prefix=prefix,
                declaration=declaration,
                body=body,
                is_terminate=is_terminate,
            ),
        )

    def exitPerformActionUsage(self, ctx: SysMLv2Parser.PerformActionUsageContext) -> None:
        """Assemble a top-level ``perform`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.performActionUsageDeclaration())
        body = self._child(ctx.actionBody())
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, PerformActionUsageDeclaration)
            or not isinstance(body, ActionBody)
        ):
            raise ValueError("performActionUsage has incomplete required fields")
        self._store(
            ctx,
            PerformActionUsage(
                occurrence_usage_prefix=prefix,
                declaration=declaration,
                body=body,
            ),
        )

    def exitActionDefinition(self, ctx: SysMLv2Parser.ActionDefinitionContext) -> None:
        """Assemble an ``action def`` and its structured action body."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        declaration = self._child(ctx.definitionDeclaration())
        body = self._child(ctx.actionBody())
        if (
            not isinstance(prefix, OccurrenceDefinitionPrefix)
            or not isinstance(declaration, DefinitionDeclaration)
            or not isinstance(body, ActionBody)
        ):
            raise ValueError("actionDefinition has incomplete required fields")
        self._store(ctx, ActionDefinition(prefix, declaration, body))

    # ------------------------------------------------------------------
    # State and transition productions
    # ------------------------------------------------------------------

    def exitEntryActionMember(self, ctx: SysMLv2Parser.EntryActionMemberContext) -> None:
        """Assemble an entry action and any attached entry transitions."""
        action = self._child(ctx.stateActionUsage())
        if not isinstance(action, ActionUsageNode):
            raise ValueError("entryActionMember requires stateActionUsage")
        self._store(
            ctx,
            EntryActionMember(
                state_action_usage=action,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitDoActionMember(self, ctx: SysMLv2Parser.DoActionMemberContext) -> None:
        """Assemble a do action member."""
        action = self._child(ctx.stateActionUsage())
        if not isinstance(action, ActionUsageNode):
            raise ValueError("doActionMember requires stateActionUsage")
        self._store(ctx, DoActionMember(action, self._member_prefix(ctx.memberPrefix())))

    def exitExitActionMember(self, ctx: SysMLv2Parser.ExitActionMemberContext) -> None:
        """Assemble an exit action member."""
        action = self._child(ctx.stateActionUsage())
        if not isinstance(action, ActionUsageNode):
            raise ValueError("exitActionMember requires stateActionUsage")
        self._store(ctx, ExitActionMember(action, self._member_prefix(ctx.memberPrefix())))

    def exitEntryTransitionMember(self, ctx: SysMLv2Parser.EntryTransitionMemberContext) -> None:
        """Assemble a guarded or ordinary entry transition member."""
        guard_expression = None
        succession = None
        if ctx.guardedTargetSuccession():
            guarded = ctx.guardedTargetSuccession()
            guard_expression = self._child(guarded.guardExpressionMember())
            succession = self._child(guarded.transitionSuccessionMember())
        else:
            succession = self._child(ctx.transitionSuccessionMember())
        if not isinstance(succession, TransitionSuccession):
            raise ValueError("entryTransitionMember requires transitionSuccession")
        if guard_expression is not None and not isinstance(guard_expression, GuardExpressionMember):
            raise ValueError("guarded entryTransitionMember requires guardExpressionMember")
        self._store(
            ctx,
            EntryTransitionMember(
                target=succession,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
                guard=guard_expression.owned_expression if guard_expression else None,
            ),
        )

    def exitTriggerAction(self, ctx: SysMLv2Parser.TriggerActionContext) -> None:
        """Pass the accept parameter part through the trigger wrapper."""
        self._pass(ctx, ctx.acceptParameterPart())

    def exitTriggerActionMember(self, ctx: SysMLv2Parser.TriggerActionMemberContext) -> None:
        """Assemble the concrete ``accept`` trigger member."""
        trigger = self._child(ctx.triggerAction())
        if not isinstance(trigger, AcceptParameterPart):
            raise ValueError("triggerActionMember requires acceptParameterPart")
        self._store(ctx, TriggerActionMember(trigger))

    def exitGuardExpressionMember(self, ctx: SysMLv2Parser.GuardExpressionMemberContext) -> None:
        """Assemble a guard around the structured owned expression."""
        expression = self._child(ctx.ownedExpression())
        if not isinstance(expression, Expression):
            raise ValueError("guardExpressionMember requires ownedExpression")
        self._store(ctx, GuardExpressionMember(expression))

    def exitEffectBehaviorMember(self, ctx: SysMLv2Parser.EffectBehaviorMemberContext) -> None:
        """Assemble an effect around its concrete action usage alternative."""
        effect = self._child(ctx.effectBehaviorUsage())
        if not isinstance(effect, ActionUsageNode):
            raise ValueError("effectBehaviorMember requires effectBehaviorUsage")
        self._store(ctx, EffectBehaviorMember(effect))

    def exitEffectBehaviorUsage(self, ctx: SysMLv2Parser.EffectBehaviorUsageContext) -> None:
        """Pass the selected transition effect action variant."""
        child = (
            ctx.emptyActionUsage_()
            or ctx.transitionPerformActionUsage()
            or ctx.transitionAcceptActionUsage()
            or ctx.transitionSendActionUsage()
            or ctx.transitionAssignmentActionUsage()
        )
        if child is None:
            raise ValueError("effectBehaviorUsage has no alternative")
        if ctx.emptyActionUsage_():
            self._store(ctx, EmptyActionUsage())
        else:
            self._pass(ctx, child)

    def exitTransitionPerformActionUsage(
        self, ctx: SysMLv2Parser.TransitionPerformActionUsageContext
    ) -> None:
        """Assemble a transition perform effect and optional action body."""
        declaration = self._child(ctx.performActionUsageDeclaration())
        if not isinstance(declaration, PerformActionUsageDeclaration):
            raise ValueError("transitionPerformActionUsage requires declaration")
        body = (
            ActionBody(items=self._source_items(ctx.actionBodyItem()))
            if ctx.LBRACE()
            else ActionBody(declaration_only=True)
            if ctx.SEMI()
            else None
        )
        self._store(ctx, TransitionPerformActionUsage(declaration=declaration, body=body))

    def exitTransitionAcceptActionUsage(
        self, ctx: SysMLv2Parser.TransitionAcceptActionUsageContext
    ) -> None:
        """Assemble a transition accept effect and optional action body."""
        declaration = self._child(ctx.acceptNodeDeclaration())
        if not isinstance(declaration, AcceptNodeDeclaration):
            raise ValueError("transitionAcceptActionUsage requires declaration")
        body = (
            ActionBody(items=self._source_items(ctx.actionBodyItem()))
            if ctx.LBRACE()
            else ActionBody(declaration_only=True)
            if ctx.SEMI()
            else None
        )
        self._store(ctx, AcceptActionUsage(declaration=declaration, body=body))

    def exitTransitionSendActionUsage(
        self, ctx: SysMLv2Parser.TransitionSendActionUsageContext
    ) -> None:
        """Assemble a transition send effect and optional action body."""
        declaration = self._child(ctx.sendNodeDeclaration())
        if not isinstance(declaration, SendNodeDeclaration):
            raise ValueError("transitionSendActionUsage requires declaration")
        body = (
            ActionBody(items=self._source_items(ctx.actionBodyItem()))
            if ctx.LBRACE()
            else ActionBody(declaration_only=True)
            if ctx.SEMI()
            else None
        )
        self._store(ctx, SendActionUsage(declaration=declaration, body=body))

    def exitTransitionAssignmentActionUsage(
        self, ctx: SysMLv2Parser.TransitionAssignmentActionUsageContext
    ) -> None:
        """Assemble a transition assignment effect and optional action body."""
        declaration = self._child(ctx.assignmentNodeDeclaration())
        if not isinstance(declaration, AssignmentNodeDeclaration):
            raise ValueError("transitionAssignmentActionUsage requires declaration")
        body = (
            ActionBody(items=self._source_items(ctx.actionBodyItem()))
            if ctx.LBRACE()
            else ActionBody(declaration_only=True)
            if ctx.SEMI()
            else None
        )
        self._store(ctx, AssignmentActionUsage(declaration=declaration, body=body))

    def exitTransitionSuccession(self, ctx: SysMLv2Parser.TransitionSuccessionContext) -> None:
        """Assemble the target connector-end reference."""
        connector = self._child(ctx.connectorEndMember())
        if isinstance(connector, ConnectorEnd):
            connector = connector.reference
        if not self._is_reference(connector):
            raise ValueError("transitionSuccession requires connectorEndMember")
        self._store(ctx, TransitionSuccession(connector))

    def exitConnectorEndMember(self, ctx: SysMLv2Parser.ConnectorEndMemberContext) -> None:
        """Pass connector-end syntax through its one-child wrapper."""
        self._pass(ctx, ctx.connectorEnd())

    def exitConnectorEnd(self, ctx: SysMLv2Parser.ConnectorEndContext) -> None:
        """Assemble endpoint reference, multiplicity, and relation fields."""
        reference = self._child(ctx.ownedReferenceSubsetting())
        if not self._is_reference(reference):
            raise ValueError("connectorEnd requires ownedReferenceSubsetting")
        self._store(
            ctx,
            ConnectorEnd(
                reference=reference,
                cross_multiplicity=(
                    self._text(ctx.ownedCrossMultiplicityMember()).strip()
                    if ctx.ownedCrossMultiplicityMember()
                    else None
                ),
                name=self._name_value(ctx.name()) if ctx.name() else None,
                name_operator=(
                    self._token_text(ctx.COLON_COLON_GT())
                    if ctx.COLON_COLON_GT()
                    else self._token_text(ctx.REFERENCES())
                    if ctx.REFERENCES()
                    else None
                ),
            ),
        )

    def exitConnectorPart(self, ctx: SysMLv2Parser.ConnectorPartContext) -> None:
        """Pass the selected binary or n-ary connector-part alternative."""
        child = ctx.binaryConnectorPart() or ctx.naryConnectorPart()
        if child is None:
            raise ValueError("connectorPart has no alternative")
        self._pass(ctx, child)

    def exitBinaryConnectorPart(self, ctx: SysMLv2Parser.BinaryConnectorPartContext) -> None:
        """Assemble two connector ends joined by ``to``."""
        ends = [self._child(item) for item in ctx.connectorEndMember()]
        if len(ends) != 2 or not all(isinstance(item, ConnectorEnd) for item in ends):
            raise ValueError("binaryConnectorPart requires two ConnectorEnd nodes")
        self._store(ctx, BinaryConnectorPart(ends[0], ends[1]))

    def exitNaryConnectorPart(self, ctx: SysMLv2Parser.NaryConnectorPartContext) -> None:
        """Assemble the ordered connector ends in an n-ary part."""
        ends = [self._child(item) for item in ctx.connectorEndMember()]
        if len(ends) < 2 or not all(isinstance(item, ConnectorEnd) for item in ends):
            raise ValueError("naryConnectorPart requires at least two ConnectorEnd nodes")
        self._store(
            ctx,
            NaryConnectorPart([item for item in ends if isinstance(item, ConnectorEnd)]),
        )

    def exitConnectionDefinition(self, ctx: SysMLv2Parser.ConnectionDefinitionContext) -> None:
        """Assemble ``connection def`` from its occurrence prefix and definition."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        definition = self._child(ctx.definition())
        if not isinstance(prefix, OccurrenceDefinitionPrefix) or not isinstance(
            definition, Definition
        ):
            raise ValueError("connectionDefinition has incomplete required fields")
        self._store(ctx, ConnectionDefinition(prefix, definition))

    def exitConnectionUsage(self, ctx: SysMLv2Parser.ConnectionUsageContext) -> None:
        """Assemble named and shorthand connection usages."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        body = self._child(ctx.usageBody())
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        connector = self._child(ctx.connectorPart()) if ctx.connectorPart() else None
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(body, DefinitionBody):
            raise ValueError("connectionUsage has incomplete required fields")
        if declaration is not None and not isinstance(declaration, UsageDeclaration):
            raise ValueError("connectionUsage declaration was not assembled")
        if value is not None and not isinstance(value, ValuePart):
            raise ValueError("connectionUsage value was not assembled")
        if connector is not None and not isinstance(connector, ConnectorPart):
            raise ValueError("connectionUsage connector part was not assembled")
        self._store(
            ctx,
            ConnectionUsage(
                occurrence_usage_prefix=prefix,
                usage_body=body,
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
                connector_part=connector if isinstance(connector, ConnectorPart) else None,
                has_connection_keyword=ctx.CONNECTION() is not None,
            ),
        )

    def exitInterfaceEnd(self, ctx: SysMLv2Parser.InterfaceEndContext) -> None:
        """Assemble interface endpoint reference and concrete modifiers."""
        reference = self._child(ctx.ownedReferenceSubsetting())
        if not self._is_reference(reference):
            raise ValueError("interfaceEnd requires ownedReferenceSubsetting")
        self._store(
            ctx,
            InterfaceEnd(
                reference=reference,
                cross_multiplicity=(
                    self._text(ctx.ownedCrossMultiplicityMember()).strip()
                    if ctx.ownedCrossMultiplicityMember()
                    else None
                ),
                name=self._name_value(ctx.name()) if ctx.name() else None,
                name_operator=(
                    self._token_text(ctx.COLON_COLON_GT())
                    if ctx.COLON_COLON_GT()
                    else self._token_text(ctx.REFERENCES())
                    if ctx.REFERENCES()
                    else None
                ),
            ),
        )

    def exitInterfaceEndMember(self, ctx: SysMLv2Parser.InterfaceEndMemberContext) -> None:
        """Pass an interface end through its one-child grammar wrapper."""
        self._pass(ctx, ctx.interfaceEnd())

    def exitInterfacePart(self, ctx: SysMLv2Parser.InterfacePartContext) -> None:
        """Pass the selected binary or n-ary interface-part alternative."""
        child = ctx.binaryInterfacePart() or ctx.naryInterfacePart()
        if child is None:
            raise ValueError("interfacePart has no alternative")
        self._pass(ctx, child)

    def exitBinaryInterfacePart(self, ctx: SysMLv2Parser.BinaryInterfacePartContext) -> None:
        """Assemble two interface ends joined by ``to``."""
        ends = [self._child(item) for item in ctx.interfaceEndMember()]
        if len(ends) != 2 or not all(isinstance(item, InterfaceEnd) for item in ends):
            raise ValueError("binaryInterfacePart requires two InterfaceEnd nodes")
        self._store(ctx, BinaryInterfacePart(ends[0], ends[1]))

    def exitNaryInterfacePart(self, ctx: SysMLv2Parser.NaryInterfacePartContext) -> None:
        """Assemble the ordered interface ends in an n-ary part."""
        ends = [self._child(item) for item in ctx.interfaceEndMember()]
        if len(ends) < 2 or not all(isinstance(item, InterfaceEnd) for item in ends):
            raise ValueError("naryInterfacePart requires at least two InterfaceEnd nodes")
        self._store(
            ctx,
            NaryInterfacePart([item for item in ends if isinstance(item, InterfaceEnd)]),
        )

    def exitInterfaceBody(self, ctx: SysMLv2Parser.InterfaceBodyContext) -> None:
        """Assemble a semicolon or ordered interface-body member list."""
        if ctx.SEMI() is not None:
            self._store(ctx, InterfaceBody(declaration_only=True))
            return
        items = [self._child(item) for item in ctx.interfaceBodyItem()]
        if not all(isinstance(item, SourceElement) for item in items):
            raise ValueError("interfaceBody contains an unassembled item")
        self._store(
            ctx,
            InterfaceBody(items=[item for item in items if isinstance(item, SourceElement)]),
        )

    def exitInterfaceBodyItem(self, ctx: SysMLv2Parser.InterfaceBodyItemContext) -> None:
        """Assemble interface-body alternatives and preserve source succession."""
        if ctx.definitionMember() is not None:
            self._pass(ctx, ctx.definitionMember())
            return
        if ctx.variantUsageMember() is not None:
            self._pass(ctx, ctx.variantUsageMember())
            return
        if ctx.interfaceNonOccurrenceUsageMember() is not None:
            self._pass(ctx, ctx.interfaceNonOccurrenceUsageMember())
            return
        if ctx.interfaceOccurrenceUsageMember() is not None:
            occurrence = self._child(ctx.interfaceOccurrenceUsageMember())
            if not isinstance(occurrence, InterfaceOccurrenceUsageMember):
                raise ValueError("interfaceBodyItem requires occurrence member")
            source = (
                self._child(ctx.sourceSuccessionMember()) if ctx.sourceSuccessionMember() else None
            )
            if source is None:
                self._pass(ctx, ctx.interfaceOccurrenceUsageMember())
                return
            if not isinstance(source, SourceSuccession):
                raise ValueError("interfaceBodyItem source succession was not assembled")
            self._store(
                ctx,
                InterfaceOccurrenceUsageMember(
                    usage=occurrence.usage,
                    member_prefix=occurrence.member_prefix,
                    source_succession=source,
                ),
            )
            return
        if ctx.aliasMember() is not None:
            self._pass(ctx, ctx.aliasMember())
            return
        if ctx.importRule() is not None:
            self._pass(ctx, ctx.importRule())
            return
        raise ValueError("interfaceBodyItem has no alternative")

    def exitInterfaceNonOccurrenceUsageMember(
        self, ctx: SysMLv2Parser.InterfaceNonOccurrenceUsageMemberContext
    ) -> None:
        """Assemble an interface non-occurrence member and visibility."""
        usage = self._child(ctx.interfaceNonOccurrenceUsageElement())
        if not isinstance(usage, SourceElement):
            raise ValueError("interfaceNonOccurrenceUsageMember requires typed usage")
        self._store(
            ctx,
            InterfaceNonOccurrenceUsageMember(
                usage=usage,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitInterfaceNonOccurrenceUsageElement(
        self, ctx: SysMLv2Parser.InterfaceNonOccurrenceUsageElementContext
    ) -> None:
        """Pass typed interface non-occurrence alternatives or retain an unimplemented one."""
        child = (
            ctx.referenceUsage()
            or ctx.attributeUsage()
            or ctx.enumerationUsage()
            or ctx.bindingConnectorAsUsage()
            or ctx.successionAsUsage()
        )
        if child is not None and self._child(child) is not None:
            self._pass(ctx, child)
            return
        self._raw_store(ctx)

    def exitInterfaceOccurrenceUsageMember(
        self, ctx: SysMLv2Parser.InterfaceOccurrenceUsageMemberContext
    ) -> None:
        """Assemble an interface occurrence member and visibility."""
        usage = self._child(ctx.interfaceOccurrenceUsageElement())
        if not isinstance(usage, SourceElement):
            raise ValueError("interfaceOccurrenceUsageMember requires typed usage")
        self._store(
            ctx,
            InterfaceOccurrenceUsageMember(
                usage=usage,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitInterfaceOccurrenceUsageElement(
        self, ctx: SysMLv2Parser.InterfaceOccurrenceUsageElementContext
    ) -> None:
        """Pass default end, end occurrence, structure, or behavior usage."""
        child = (
            ctx.defaultInterfaceEnd()
            or ctx.endOccurrenceUsageElement()
            or ctx.structureUsageElement()
            or ctx.behaviorUsageElement()
        )
        if child is None:
            raise ValueError("interfaceOccurrenceUsageElement has no alternative")
        if self._child(child) is not None:
            self._pass(ctx, child)
            return
        self._raw_store(ctx)

    def exitDefaultInterfaceEnd(self, ctx: SysMLv2Parser.DefaultInterfaceEndContext) -> None:
        """Assemble ``end`` with its structured interface-end usage."""
        usage = self._child(ctx.usage())
        if not isinstance(usage, Usage):
            raise ValueError("defaultInterfaceEnd requires Usage")
        self._store(ctx, DefaultInterfaceEnd(usage))

    def exitInterfaceUsageDeclaration(
        self, ctx: SysMLv2Parser.InterfaceUsageDeclarationContext
    ) -> None:
        """Assemble interface declaration/value and optional connection part."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        part = self._child(ctx.interfacePart()) if ctx.interfacePart() else None
        if declaration is not None and not isinstance(declaration, UsageDeclaration):
            raise ValueError("interfaceUsageDeclaration declaration was not assembled")
        if value is not None and not isinstance(value, ValuePart):
            raise ValueError("interfaceUsageDeclaration value was not assembled")
        if part is not None and not isinstance(part, InterfacePart):
            raise ValueError("interfaceUsageDeclaration part was not assembled")
        self._store(
            ctx,
            InterfaceUsageDeclaration(
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
                interface_part=part if isinstance(part, InterfacePart) else None,
                has_connect_keyword=ctx.CONNECT() is not None,
            ),
        )

    def exitInterfaceDefinition(self, ctx: SysMLv2Parser.InterfaceDefinitionContext) -> None:
        """Assemble ``interface def`` with its dedicated declaration/body nodes."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        declaration = self._child(ctx.definitionDeclaration())
        body = self._child(ctx.interfaceBody())
        if not isinstance(prefix, OccurrenceDefinitionPrefix):
            raise ValueError("interfaceDefinition requires occurrence prefix")
        if not isinstance(declaration, DefinitionDeclaration):
            raise ValueError("interfaceDefinition requires definition declaration")
        if not isinstance(body, InterfaceBody):
            raise ValueError("interfaceDefinition requires interface body")
        self._store(ctx, InterfaceDefinition(prefix, declaration, body))

    def exitInterfaceUsage(self, ctx: SysMLv2Parser.InterfaceUsageContext) -> None:
        """Assemble ``interface`` usage with declaration and body."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.interfaceUsageDeclaration())
        body = self._child(ctx.interfaceBody())
        if not isinstance(prefix, OccurrenceUsagePrefix):
            raise ValueError("interfaceUsage requires occurrence prefix")
        if not isinstance(declaration, InterfaceUsageDeclaration):
            raise ValueError("interfaceUsage requires interface usage declaration")
        if not isinstance(body, InterfaceBody):
            raise ValueError("interfaceUsage requires interface body")
        self._store(ctx, InterfaceUsage(prefix, declaration, body))

    def exitTransitionSuccessionMember(
        self, ctx: SysMLv2Parser.TransitionSuccessionMemberContext
    ) -> None:
        """Pass the semantic transition succession through its wrapper."""
        self._pass(ctx, ctx.transitionSuccession())

    def exitTransitionUsage(self, ctx: SysMLv2Parser.TransitionUsageContext) -> None:
        """Assemble a complete transition usage from concrete grammar fields."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        source = self._child(ctx.featureChainMember())
        succession = self._child(ctx.transitionSuccessionMember())
        body = self._child(ctx.actionBody())
        trigger_ctx = ctx.triggerActionMember()
        guard_ctx = ctx.guardExpressionMember()
        trigger = self._child(trigger_ctx) if trigger_ctx else None
        guard = self._child(guard_ctx) if guard_ctx else None
        effect = self._child(ctx.effectBehaviorMember()) if ctx.effectBehaviorMember() else None
        if (
            not isinstance(source, FeatureChain)
            or not isinstance(succession, TransitionSuccession)
            or not isinstance(body, ActionBody)
        ):
            raise ValueError("transitionUsage has incomplete required fields")
        self._store(
            ctx,
            TransitionUsage(
                source_feature_chain=source,
                transition_succession_member=succession,
                action_body=body,
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                is_first=ctx.FIRST() is not None,
                input_parameter_count=len(ctx.emptyParameterMember()),
                trigger_action_member=trigger if isinstance(trigger, TriggerActionMember) else None,
                guard_expression_member=guard if isinstance(guard, GuardExpressionMember) else None,
                effect_behavior_member=effect if isinstance(effect, EffectBehaviorMember) else None,
                guard_before_trigger=(
                    trigger is not None
                    and guard is not None
                    and guard_ctx.start.tokenIndex < trigger_ctx.start.tokenIndex
                ),
            ),
        )

    def exitTransitionUsageMember(self, ctx: SysMLv2Parser.TransitionUsageMemberContext) -> None:
        """Preserve a transition member's visibility prefix beside the child."""
        child = self._child(ctx.transitionUsage())
        if not isinstance(child, TransitionUsage):
            raise ValueError("transitionUsageMember requires transitionUsage")
        self._store(ctx, TransitionUsageMember(child, self._member_prefix(ctx.memberPrefix())))

    def exitTargetTransitionUsage(self, ctx: SysMLv2Parser.TargetTransitionUsageContext) -> None:
        """Assemble abbreviated target-transition alternatives."""
        succession = self._child(ctx.transitionSuccessionMember())
        body = self._child(ctx.actionBody())
        if not isinstance(succession, TransitionSuccession) or not isinstance(body, ActionBody):
            raise ValueError("targetTransitionUsage has incomplete required fields")
        trigger_ctx = ctx.triggerActionMember()
        guard_ctx = ctx.guardExpressionMember()
        trigger = self._child(trigger_ctx) if trigger_ctx else None
        guard = self._child(guard_ctx) if guard_ctx else None
        effect = self._child(ctx.effectBehaviorMember()) if ctx.effectBehaviorMember() else None
        form = TargetTransitionForm.BARE
        if ctx.TRANSITION():
            form = TargetTransitionForm.TRANSITION
        self._store(
            ctx,
            TargetTransitionUsage(
                transition_succession_member=succession,
                action_body=body,
                form=form,
                input_parameter_count=len(ctx.emptyParameterMember()),
                trigger_action_member=trigger if isinstance(trigger, TriggerActionMember) else None,
                guard_expression_member=guard if isinstance(guard, GuardExpressionMember) else None,
                effect_behavior_member=effect if isinstance(effect, EffectBehaviorMember) else None,
            ),
        )

    def exitTargetTransitionUsageMember(
        self, ctx: SysMLv2Parser.TargetTransitionUsageMemberContext
    ) -> None:
        """Preserve a target-transition member visibility prefix."""
        child = self._child(ctx.targetTransitionUsage())
        if not isinstance(child, TargetTransitionUsage):
            raise ValueError("targetTransitionUsageMember requires targetTransitionUsage")
        self._store(
            ctx, TargetTransitionUsageMember(child, self._member_prefix(ctx.memberPrefix()))
        )

    def exitBehaviorUsageElement(self, ctx: SysMLv2Parser.BehaviorUsageElementContext) -> None:
        """Pass every typed behavior-usage alternative."""
        child = (
            ctx.actionUsage()
            or ctx.calculationUsage()
            or ctx.stateUsage()
            or ctx.constraintUsage()
            or ctx.requirementUsage()
            or ctx.concernUsage()
            or ctx.caseUsage()
            or ctx.analysisCaseUsage()
            or ctx.verificationCaseUsage()
            or ctx.useCaseUsage()
            or ctx.viewpointUsage()
            or ctx.performActionUsage()
            or ctx.exhibitStateUsage()
            or ctx.includeUseCaseUsage()
            or ctx.assertConstraintUsage()
            or ctx.satisfyRequirementUsage()
        )
        if child is not None:
            self._pass(ctx, child)
        else:
            self._raw_store(ctx)

    def exitBehaviorUsageMember(self, ctx: SysMLv2Parser.BehaviorUsageMemberContext) -> None:
        """Assemble an optional source succession and behavior usage member."""
        behavior = self._child(ctx.behaviorUsageElement())
        if not isinstance(behavior, SourceElement):
            raise ValueError("behaviorUsageMember requires behaviorUsageElement")
        self._store(
            ctx,
            BehaviorUsageMember(
                behavior_usage=behavior,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitSourceSuccessionMember(self, ctx: SysMLv2Parser.SourceSuccessionMemberContext) -> None:
        """Retain a source-succession marker for its enclosing member."""
        self._store(ctx, SourceSuccession())

    def exitSourceSuccession(self, ctx: SysMLv2Parser.SourceSuccessionContext) -> None:
        """Retain the epsilon source succession marker."""
        self._store(ctx, SourceSuccession())

    def exitStateBodyItem(self, ctx: SysMLv2Parser.StateBodyItemContext) -> None:
        """Assemble state-body alternatives without a redundant item wrapper."""
        if ctx.nonBehaviorBodyItem():
            self._pass(ctx, ctx.nonBehaviorBodyItem())
            return
        if ctx.transitionUsageMember():
            self._pass(ctx, ctx.transitionUsageMember())
            return
        if ctx.entryActionMember():
            entry = self._child(ctx.entryActionMember())
            if not isinstance(entry, EntryActionMember):
                raise ValueError("entry state-body member is incomplete")
            transitions = [self._child(item) for item in ctx.entryTransitionMember()]
            self._store(
                ctx,
                EntryActionMember(
                    state_action_usage=entry.state_action_usage,
                    member_prefix=entry.member_prefix,
                    entry_transition_members=[
                        item for item in transitions if isinstance(item, EntryTransitionMember)
                    ],
                ),
            )
            return
        if ctx.doActionMember():
            self._pass(ctx, ctx.doActionMember())
            return
        if ctx.exitActionMember():
            self._pass(ctx, ctx.exitActionMember())
            return
        behavior = self._child(ctx.behaviorUsageMember()) if ctx.behaviorUsageMember() else None
        if not isinstance(behavior, BehaviorUsageMember):
            raise ValueError("stateBodyItem behavior alternative is incomplete")
        source = self._child(ctx.sourceSuccessionMember()) if ctx.sourceSuccessionMember() else None
        targets = [self._child(item) for item in ctx.targetTransitionUsageMember()]
        self._store(
            ctx,
            BehaviorUsageStateMember(
                behavior_usage_member=behavior,
                source_succession=source if isinstance(source, SourceSuccession) else None,
                target_transition_members=[
                    item for item in targets if isinstance(item, TargetTransitionUsageMember)
                ],
            ),
        )

    def _state_body(self, ctx: Any) -> SourceElement:
        """Build either a state-definition or state-usage body explicitly."""
        members = [self._child(item) for item in ctx.stateBodyItem()]
        values = [item for item in members if isinstance(item, SourceElement)]
        if isinstance(ctx, SysMLv2Parser.StateDefBodyContext):
            return StateDefBody(
                is_parallel=ctx.PARALLEL() is not None,
                is_declaration_only=ctx.SEMI() is not None,
                state_body_members=values,
            )
        return StateUsageBody(
            is_parallel=ctx.PARALLEL() is not None,
            is_declaration_only=ctx.SEMI() is not None,
            state_body_members=values,
        )

    def exitStateDefBody(self, ctx: SysMLv2Parser.StateDefBodyContext) -> None:
        """Assemble a state-definition body."""
        self._store(ctx, self._state_body(ctx))

    def exitStateUsageBody(self, ctx: SysMLv2Parser.StateUsageBodyContext) -> None:
        """Assemble a state-usage body."""
        self._store(ctx, self._state_body(ctx))

    def exitStateDefinition(self, ctx: SysMLv2Parser.StateDefinitionContext) -> None:
        """Assemble ``state def`` with explicit prefix, declaration, and body."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        declaration = self._child(ctx.definitionDeclaration())
        body = self._child(ctx.stateDefBody())
        if (
            not isinstance(prefix, OccurrenceDefinitionPrefix)
            or not isinstance(declaration, DefinitionDeclaration)
            or not isinstance(body, StateDefBody)
        ):
            raise ValueError("stateDefinition has incomplete required fields")
        self._store(ctx, StateDefinition(prefix, declaration, body))

    def exitStateUsage(self, ctx: SysMLv2Parser.StateUsageContext) -> None:
        """Assemble ``state`` usage with explicit declaration and body."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.actionUsageDeclaration())
        body = self._child(ctx.stateUsageBody())
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, ActionUsageDeclaration)
            or not isinstance(body, StateUsageBody)
        ):
            raise ValueError("stateUsage has incomplete required fields")
        self._store(ctx, StateUsage(prefix, declaration, body))

    def exitExhibitStateUsage(self, ctx: SysMLv2Parser.ExhibitStateUsageContext) -> None:
        """Assemble an exhibit-state usage and its selected declaration form."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        reference = (
            self._child(ctx.ownedReferenceSubsetting()) if ctx.ownedReferenceSubsetting() else None
        )
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        body = self._child(ctx.stateUsageBody())
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(body, StateUsageBody):
            raise ValueError("exhibitStateUsage has incomplete required fields")
        self._store(
            ctx,
            ExhibitStateUsage(
                occurrence_usage_prefix=prefix,
                owned_reference_subsetting=reference if self._is_reference(reference) else None,
                feature_specialization_part=specialization
                if isinstance(specialization, FeatureSpecializationPart)
                else None,
                state_usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
                state_usage_body=body,
            ),
        )

    # ------------------------------------------------------------------
    # Generic definition/usage containment
    # ------------------------------------------------------------------

    def exitDependency(self, ctx: SysMLv2Parser.DependencyContext) -> None:
        """Assemble dependency endpoints as structured qualified references."""
        names = [self._child(item) for item in ctx.qualifiedName()]
        references = [item for item in names if isinstance(item, QualifiedReference)]
        if ctx.dependencyDeclaration() is not None:
            declaration = ctx.dependencyDeclaration()
            names = [self._child(item) for item in declaration.qualifiedName()]
            references = [item for item in names if isinstance(item, QualifiedReference)]
            identification = None
            if declaration.identification() is not None:
                identification = self._child(declaration.identification())
            source_count = len(references) // 2
            source_references = references[:source_count]
            target_references = references[source_count:]
        else:
            identification = self._child(ctx.identification()) if ctx.identification() else None
            to_index = ctx.TO().symbol.tokenIndex if ctx.TO() is not None else -1
            source_references = [
                item for item in references if item.span is None or item.span.line >= 0
            ]
            # The grammar's endpoint names occur in source order.  The last
            # ``to`` token is the only stable boundary needed here.
            source_references = [
                item for item in references if item.span is None or item.span.line >= 0
            ]
            if to_index >= 0:
                qualified_contexts = ctx.qualifiedName()
                split = next(
                    (
                        index
                        for index, child in enumerate(qualified_contexts)
                        if child.start.tokenIndex > to_index
                    ),
                    len(qualified_contexts),
                )
                source_references = [
                    self._child(item)
                    for item in qualified_contexts[:split]
                    if isinstance(self._child(item), QualifiedReference)
                ]
                target_references = [
                    self._child(item)
                    for item in qualified_contexts[split:]
                    if isinstance(self._child(item), QualifiedReference)
                ]
            else:
                target_references = []
        body = self._child(ctx.relationshipBody())
        if not isinstance(body, RelationshipBody):
            raise ValueError("dependency requires relationshipBody")
        if not isinstance(identification, Identification):
            identification = None
        if not source_references or not target_references:
            # Recovery and declaration shorthand still get a typed node.  The
            # relationship body keeps the exact fragment until linking expands
            # endpoint alternatives further.
            source_references = source_references or references[:1]
            target_references = target_references or references[1:]
        self._store(
            ctx,
            Dependency(
                source_references=source_references,
                target_references=target_references,
                relationship_body=body,
                identification=identification,
                prefix_metadata=[
                    self._text(item).strip() for item in ctx.prefixMetadataAnnotation()
                ],
            ),
        )

    def exitEnumerationDefinition(self, ctx: SysMLv2Parser.EnumerationDefinitionContext) -> None:
        """Assemble an ``enum def`` with explicit body members."""
        declaration = self._child(ctx.definitionDeclaration())
        body = self._child(ctx.enumerationBody())
        if not isinstance(declaration, DefinitionDeclaration) or not isinstance(
            body, EnumerationBody
        ):
            raise ValueError("enumerationDefinition has incomplete required fields")
        self._store(
            ctx,
            EnumerationDefinition(
                definition_declaration=declaration,
                enumeration_body=body,
                extension_keywords=[
                    self._text(item).strip() for item in ctx.definitionExtensionKeyword()
                ],
            ),
        )

    def exitAllocationDefinition(self, ctx: SysMLv2Parser.AllocationDefinitionContext) -> None:
        """Assemble an ``allocation def``."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        definition = self._child(ctx.definition())
        if not isinstance(prefix, OccurrenceDefinitionPrefix) or not isinstance(
            definition, Definition
        ):
            raise ValueError("allocationDefinition has incomplete required fields")
        self._store(ctx, AllocationDefinition(prefix, definition))

    def exitFlowDefinition(self, ctx: SysMLv2Parser.FlowDefinitionContext) -> None:
        """Assemble a ``flow def``."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        definition = self._child(ctx.definition())
        if not isinstance(prefix, OccurrenceDefinitionPrefix) or not isinstance(
            definition, Definition
        ):
            raise ValueError("flowDefinition has incomplete required fields")
        self._store(ctx, FlowDefinition(prefix, definition))

    def exitRenderingDefinition(self, ctx: SysMLv2Parser.RenderingDefinitionContext) -> None:
        """Assemble a ``rendering def``."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        definition = self._child(ctx.definition())
        if not isinstance(prefix, OccurrenceDefinitionPrefix) or not isinstance(
            definition, Definition
        ):
            raise ValueError("renderingDefinition has incomplete required fields")
        self._store(ctx, RenderingDefinition(prefix, definition))

    def exitMetadataDefinition(self, ctx: SysMLv2Parser.MetadataDefinitionContext) -> None:
        """Assemble a ``metadata def``."""
        definition = self._child(ctx.definition())
        if not isinstance(definition, Definition):
            raise ValueError("metadataDefinition has incomplete required fields")
        self._store(
            ctx,
            MetadataDefinition(
                definition=definition,
                is_abstract=ctx.ABSTRACT() is not None,
                extension_keywords=[
                    self._text(item).strip() for item in ctx.definitionExtensionKeyword()
                ],
            ),
        )

    def exitExtendedDefinition(self, ctx: SysMLv2Parser.ExtendedDefinitionContext) -> None:
        """Assemble an extension-keyword definition."""
        definition = self._child(ctx.definition())
        if not isinstance(definition, Definition):
            raise ValueError("extendedDefinition has incomplete required fields")
        basic = (
            self._text(ctx.basicDefinitionPrefix()).strip() if ctx.basicDefinitionPrefix() else None
        )
        self._store(
            ctx,
            ExtendedDefinition(
                definition_prefix=DefinitionPrefix(
                    basic_definition_keyword=basic,
                    extension_keywords=[
                        self._text(item).strip() for item in ctx.definitionExtensionKeyword()
                    ],
                ),
                definition=definition,
            ),
        )

    def _definition_with_body(self, ctx: Any, body_rule: Any, node_type: Any) -> None:
        """Build one occurrence definition with its explicit body node."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        declaration = self._child(ctx.definitionDeclaration())
        body = self._child(body_rule)
        if not isinstance(prefix, OccurrenceDefinitionPrefix):
            raise ValueError("definition requires occurrenceDefinitionPrefix")
        if not isinstance(declaration, DefinitionDeclaration) or not isinstance(
            body, SourceElement
        ):
            raise ValueError("definition requires definitionDeclaration and body")
        self._store(ctx, node_type(prefix, declaration, body))

    def exitCalculationDefinition(self, ctx: SysMLv2Parser.CalculationDefinitionContext) -> None:
        """Assemble a ``calc def``."""
        self._definition_with_body(ctx, ctx.calculationBody(), CalculationDefinition)

    def exitConstraintDefinition(self, ctx: SysMLv2Parser.ConstraintDefinitionContext) -> None:
        """Assemble a ``constraint def``."""
        self._definition_with_body(ctx, ctx.calculationBody(), ConstraintDefinition)

    def exitRequirementDefinition(self, ctx: SysMLv2Parser.RequirementDefinitionContext) -> None:
        """Assemble a ``requirement def``."""
        self._definition_with_body(ctx, ctx.requirementBody(), RequirementDefinition)

    def exitConcernDefinition(self, ctx: SysMLv2Parser.ConcernDefinitionContext) -> None:
        """Assemble a ``concern def``."""
        self._definition_with_body(ctx, ctx.requirementBody(), ConcernDefinition)

    def exitCaseDefinition(self, ctx: SysMLv2Parser.CaseDefinitionContext) -> None:
        """Assemble a ``case def``."""
        self._definition_with_body(ctx, ctx.caseBody(), CaseDefinition)

    def exitAnalysisCaseDefinition(self, ctx: SysMLv2Parser.AnalysisCaseDefinitionContext) -> None:
        """Assemble an ``analysis def``."""
        self._definition_with_body(ctx, ctx.caseBody(), AnalysisCaseDefinition)

    def exitVerificationCaseDefinition(
        self, ctx: SysMLv2Parser.VerificationCaseDefinitionContext
    ) -> None:
        """Assemble a ``verification def``."""
        self._definition_with_body(ctx, ctx.caseBody(), VerificationCaseDefinition)

    def exitUseCaseDefinition(self, ctx: SysMLv2Parser.UseCaseDefinitionContext) -> None:
        """Assemble a ``use case def``."""
        self._definition_with_body(ctx, ctx.caseBody(), UseCaseDefinition)

    def exitViewDefinition(self, ctx: SysMLv2Parser.ViewDefinitionContext) -> None:
        """Assemble a ``view def``."""
        self._definition_with_body(ctx, ctx.viewDefinitionBody(), ViewDefinition)

    def exitViewpointDefinition(self, ctx: SysMLv2Parser.ViewpointDefinitionContext) -> None:
        """Assemble a ``viewpoint def``."""
        self._definition_with_body(ctx, ctx.requirementBody(), ViewpointDefinition)

    def exitFlowEnd(self, ctx: SysMLv2Parser.FlowEndContext) -> None:
        """Assemble a flow endpoint as a qualified reference."""
        names = [self._child(item) for item in ctx.qualifiedName()]
        references = [item for item in names if isinstance(item, QualifiedReference)]
        if not references:
            raise ValueError("flowEnd requires qualifiedName")
        self._pass(ctx, ctx.qualifiedName()[0]) if len(references) == 1 else self._store(
            ctx, DottedQualifiedReference(references)
        )

    def exitFlowEndMember(self, ctx: SysMLv2Parser.FlowEndMemberContext) -> None:
        """Pass the flow endpoint through its one-child wrapper."""
        self._pass(ctx, ctx.flowEnd())

    def exitFlowPayloadFeature(self, ctx: SysMLv2Parser.FlowPayloadFeatureContext) -> None:
        """Pass the structured payload feature through its wrapper."""
        self._pass(ctx, ctx.payloadFeature())

    def exitFlowPayloadFeatureMember(
        self, ctx: SysMLv2Parser.FlowPayloadFeatureMemberContext
    ) -> None:
        """Pass the payload feature member through its wrapper."""
        self._pass(ctx, ctx.flowPayloadFeature())

    def exitFlowDeclaration(self, ctx: SysMLv2Parser.FlowDeclarationContext) -> None:
        """Assemble flow declaration fields without flattening endpoints."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        feature_declaration = (
            self._child(ctx.featureDeclaration()) if ctx.featureDeclaration() else None
        )
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        payload = (
            self._child(ctx.flowPayloadFeatureMember()) if ctx.flowPayloadFeatureMember() else None
        )
        ends = [self._child(item) for item in ctx.flowEndMember()]
        references = [
            item
            for item in ends
            if isinstance(item, (QualifiedReference, DottedQualifiedReference))
        ]
        self._store(
            ctx,
            FlowDeclaration(
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                feature_declaration=(
                    feature_declaration
                    if isinstance(feature_declaration, FeatureDeclaration)
                    else None
                ),
                value_part=value if isinstance(value, ValuePart) else None,
                payload_feature=payload if isinstance(payload, SourceElement) else None,
                source_end=references[0] if references else None,
                target_end=references[1] if len(references) > 1 else None,
                all_ends=ctx.ALL() is not None,
            ),
        )

    def exitMessageEvent(self, ctx: SysMLv2Parser.MessageEventContext) -> None:
        """Pass a message event's owned reference."""
        self._pass(ctx, ctx.ownedReferenceSubsetting())

    def exitMessageEventMember(self, ctx: SysMLv2Parser.MessageEventMemberContext) -> None:
        """Pass a message event through its one-child wrapper."""
        self._pass(ctx, ctx.messageEvent())

    def exitMessageDeclaration(self, ctx: SysMLv2Parser.MessageDeclarationContext) -> None:
        """Assemble message declaration and optional event endpoints."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        payload = (
            self._child(ctx.flowPayloadFeatureMember()) if ctx.flowPayloadFeatureMember() else None
        )
        events = [self._child(item) for item in ctx.messageEventMember()]
        references = [
            item
            for item in events
            if isinstance(item, (QualifiedReference, DottedQualifiedReference))
        ]
        self._store(
            ctx,
            MessageDeclaration(
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
                payload_feature=payload if isinstance(payload, SourceElement) else None,
                source_event=references[0] if references else None,
                target_event=references[1] if len(references) > 1 else None,
            ),
        )

    def exitAllocationUsageDeclaration(
        self, ctx: SysMLv2Parser.AllocationUsageDeclarationContext
    ) -> None:
        """Assemble allocation/allocate declaration alternatives."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        connector = self._child(ctx.connectorPart()) if ctx.connectorPart() else None
        self._store(
            ctx,
            AllocationUsageDeclaration(
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                connector_part=connector if isinstance(connector, ConnectorPart) else None,
                has_allocation_keyword=ctx.ALLOCATION() is not None,
            ),
        )

    def exitConstraintUsageDeclaration(
        self, ctx: SysMLv2Parser.ConstraintUsageDeclarationContext
    ) -> None:
        """Assemble constraint usage declaration and optional value."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        self._store(
            ctx,
            ConstraintUsageDeclaration(
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
            ),
        )

    def _usage_with_body(
        self, ctx: Any, declaration_rule: Any, body_rule: Any, node_type: Any
    ) -> None:
        """Build one occurrence usage with an explicit declaration and body."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(declaration_rule) if declaration_rule is not None else None
        body = self._child(body_rule)
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(body, SourceElement):
            raise ValueError("usage requires occurrenceUsagePrefix and body")
        if declaration is None:
            raise ValueError("usage requires declaration")
        self._store(ctx, node_type(prefix, declaration, body))

    def exitCalculationUsage(self, ctx: SysMLv2Parser.CalculationUsageContext) -> None:
        """Assemble a ``calc`` usage."""
        declaration = self._child(ctx.actionUsageDeclaration())
        body = self._child(ctx.calculationBody())
        prefix = self._child(ctx.occurrenceUsagePrefix())
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, ActionUsageDeclaration)
            or not isinstance(body, CalculationBody)
        ):
            raise ValueError("calculationUsage has incomplete required fields")
        self._store(ctx, CalculationUsage(prefix, declaration, body))

    def exitConstraintUsage(self, ctx: SysMLv2Parser.ConstraintUsageContext) -> None:
        """Assemble a ``constraint`` usage."""
        declaration = self._child(ctx.constraintUsageDeclaration())
        body = self._child(ctx.calculationBody())
        prefix = self._child(ctx.occurrenceUsagePrefix())
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, ConstraintUsageDeclaration)
            or not isinstance(body, CalculationBody)
        ):
            raise ValueError("constraintUsage has incomplete required fields")
        self._store(ctx, ConstraintUsage(prefix, declaration, body))

    def exitRequirementUsage(self, ctx: SysMLv2Parser.RequirementUsageContext) -> None:
        """Assemble a ``requirement`` usage."""
        self._usage_with_body(
            ctx, ctx.constraintUsageDeclaration(), ctx.requirementBody(), RequirementUsage
        )

    def exitConcernUsage(self, ctx: SysMLv2Parser.ConcernUsageContext) -> None:
        """Assemble a ``concern`` usage."""
        self._usage_with_body(
            ctx, ctx.constraintUsageDeclaration(), ctx.requirementBody(), ConcernUsage
        )

    def exitCaseUsage(self, ctx: SysMLv2Parser.CaseUsageContext) -> None:
        """Assemble a ``case`` usage."""
        self._usage_with_body(ctx, ctx.constraintUsageDeclaration(), ctx.caseBody(), CaseUsage)

    def exitAnalysisCaseUsage(self, ctx: SysMLv2Parser.AnalysisCaseUsageContext) -> None:
        """Assemble an ``analysis`` usage."""
        self._usage_with_body(
            ctx, ctx.constraintUsageDeclaration(), ctx.caseBody(), AnalysisCaseUsage
        )

    def exitVerificationCaseUsage(self, ctx: SysMLv2Parser.VerificationCaseUsageContext) -> None:
        """Assemble a ``verification`` usage."""
        self._usage_with_body(
            ctx, ctx.constraintUsageDeclaration(), ctx.caseBody(), VerificationCaseUsage
        )

    def exitUseCaseUsage(self, ctx: SysMLv2Parser.UseCaseUsageContext) -> None:
        """Assemble a ``use case`` usage."""
        self._usage_with_body(ctx, ctx.constraintUsageDeclaration(), ctx.caseBody(), UseCaseUsage)

    def exitViewpointUsage(self, ctx: SysMLv2Parser.ViewpointUsageContext) -> None:
        """Assemble a ``viewpoint`` usage."""
        self._usage_with_body(
            ctx, ctx.constraintUsageDeclaration(), ctx.requirementBody(), ViewpointUsage
        )

    def exitViewUsage(self, ctx: SysMLv2Parser.ViewUsageContext) -> None:
        """Assemble a ``view`` usage and its dedicated view body."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        body = self._child(ctx.viewBody())
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(body, ViewBody):
            raise ValueError("viewUsage has incomplete required fields")
        self._store(
            ctx,
            ViewUsage(
                occurrence_usage_prefix=prefix,
                view_body=body,
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
            ),
        )

    def exitViewRenderingUsage(self, ctx: SysMLv2Parser.ViewRenderingUsageContext) -> None:
        """Assemble a view rendering target and its usage body."""
        reference = (
            self._child(ctx.ownedReferenceSubsetting()) if ctx.ownedReferenceSubsetting() else None
        )
        usage = self._child(ctx.usage()) if ctx.usage() else None
        body = self._child(ctx.usageBody()) if ctx.usageBody() else None
        if body is None and isinstance(usage, Usage):
            body = usage.body
        if not isinstance(body, DefinitionBody):
            raise ValueError("viewRenderingUsage requires usage body")
        self._store(
            ctx,
            ViewRenderingUsage(
                body=body,
                reference=reference
                if isinstance(reference, (QualifiedReference, DottedQualifiedReference))
                else None,
                usage=usage if isinstance(usage, Usage) else None,
            ),
        )

    def exitRenderingUsage(self, ctx: SysMLv2Parser.RenderingUsageContext) -> None:
        """Assemble a ``rendering`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        usage = self._child(ctx.usage())
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(usage, Usage):
            raise ValueError("renderingUsage has incomplete required fields")
        self._store(ctx, RenderingUsage(prefix, usage))

    def exitAllocationUsage(self, ctx: SysMLv2Parser.AllocationUsageContext) -> None:
        """Assemble an ``allocation`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.allocationUsageDeclaration())
        body = self._child(ctx.usageBody())
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, AllocationUsageDeclaration)
            or not isinstance(body, DefinitionBody)
        ):
            raise ValueError("allocationUsage has incomplete required fields")
        self._store(ctx, AllocationUsage(prefix, declaration, body))

    def exitMessage(self, ctx: SysMLv2Parser.MessageContext) -> None:
        """Assemble a ``message`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.messageDeclaration())
        body = self._child(ctx.definitionBody())
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, MessageDeclaration)
            or not isinstance(body, DefinitionBody)
        ):
            raise ValueError("message has incomplete required fields")
        self._store(ctx, Message(prefix, declaration, body))

    def exitFlowUsage(self, ctx: SysMLv2Parser.FlowUsageContext) -> None:
        """Assemble a ``flow`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.flowDeclaration())
        body = self._child(ctx.definitionBody())
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, FlowDeclaration)
            or not isinstance(body, DefinitionBody)
        ):
            raise ValueError("flowUsage has incomplete required fields")
        self._store(ctx, FlowUsage(prefix, declaration, body))

    def exitSuccessionFlowUsage(self, ctx: SysMLv2Parser.SuccessionFlowUsageContext) -> None:
        """Assemble a ``succession flow`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        declaration = self._child(ctx.flowDeclaration())
        body = self._child(ctx.definitionBody())
        if (
            not isinstance(prefix, OccurrenceUsagePrefix)
            or not isinstance(declaration, FlowDeclaration)
            or not isinstance(body, DefinitionBody)
        ):
            raise ValueError("successionFlowUsage has incomplete required fields")
        self._store(ctx, SuccessionFlowUsage(prefix, declaration, body))

    def exitIncludeUseCaseUsage(self, ctx: SysMLv2Parser.IncludeUseCaseUsageContext) -> None:
        """Assemble an ``include use case`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        body = self._child(ctx.caseBody())
        reference = (
            self._child(ctx.ownedReferenceSubsetting()) if ctx.ownedReferenceSubsetting() else None
        )
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(body, CaseBody):
            raise ValueError("includeUseCaseUsage has incomplete required fields")
        self._store(
            ctx,
            IncludeUseCaseUsage(
                occurrence_usage_prefix=prefix,
                case_body=body,
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
                owned_reference_subsetting=reference
                if isinstance(reference, (QualifiedReference, DottedQualifiedReference))
                else None,
                feature_specialization_part=specialization
                if isinstance(specialization, FeatureSpecializationPart)
                else None,
            ),
        )

    def exitAssertConstraintUsage(self, ctx: SysMLv2Parser.AssertConstraintUsageContext) -> None:
        """Assemble an ``assert constraint`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        body = self._child(ctx.calculationBody())
        reference = (
            self._child(ctx.ownedReferenceSubsetting()) if ctx.ownedReferenceSubsetting() else None
        )
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        declaration = (
            self._child(ctx.constraintUsageDeclaration())
            if ctx.constraintUsageDeclaration()
            else None
        )
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(body, CalculationBody):
            raise ValueError("assertConstraintUsage has incomplete required fields")
        self._store(
            ctx,
            AssertConstraintUsage(
                occurrence_usage_prefix=prefix,
                calculation_body=body,
                constraint_usage_declaration=declaration
                if isinstance(declaration, ConstraintUsageDeclaration)
                else None,
                owned_reference_subsetting=reference
                if isinstance(reference, (QualifiedReference, DottedQualifiedReference))
                else None,
                feature_specialization_part=specialization
                if isinstance(specialization, FeatureSpecializationPart)
                else None,
                is_not=ctx.NOT() is not None,
            ),
        )

    def exitSatisfyRequirementUsage(
        self, ctx: SysMLv2Parser.SatisfyRequirementUsageContext
    ) -> None:
        """Assemble a ``satisfy requirement`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        body = self._child(ctx.requirementBody())
        reference = (
            self._child(ctx.ownedReferenceSubsetting()) if ctx.ownedReferenceSubsetting() else None
        )
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(body, RequirementBody):
            raise ValueError("satisfyRequirementUsage has incomplete required fields")
        self._store(
            ctx,
            SatisfyRequirementUsage(
                occurrence_usage_prefix=prefix,
                requirement_body=body,
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
                value_part=value if isinstance(value, ValuePart) else None,
                owned_reference_subsetting=reference
                if isinstance(reference, (QualifiedReference, DottedQualifiedReference))
                else None,
                feature_specialization_part=specialization
                if isinstance(specialization, FeatureSpecializationPart)
                else None,
                is_assert=ctx.ASSERT() is not None,
                is_not=ctx.NOT() is not None,
            ),
        )

    def exitUsageBody(self, ctx: SysMLv2Parser.UsageBodyContext) -> None:
        """Pass a generic usage body through to its definition body."""
        self._pass(ctx, ctx.definitionBody())

    def exitDefinitionBodyItemContent(
        self, ctx: SysMLv2Parser.DefinitionBodyItemContentContext
    ) -> None:
        """Pass the selected generic definition-body content alternative."""
        if ctx.ALIAS() is not None:
            self._store(ctx, self._alias_node(ctx))
            return
        if ctx.VARIANT() is not None:
            element = self._child(ctx.variantUsageElement())
            if not isinstance(element, SourceElement):
                raise ValueError("variant definition body item has no assembled element")
            self._store(ctx, VariantUsage(element))
            return
        child = ctx.definitionElement() or ctx.nonOccurrenceUsageElement()
        if child is None:
            self._raw_store(ctx)
            return
        self._pass(ctx, child)

    def exitVariantUsageElement(self, ctx: SysMLv2Parser.VariantUsageElementContext) -> None:
        """Pass a typed variant usage or retain an unimplemented non-state choice."""
        children = (
            ctx.attributeUsage(),
            ctx.itemUsage(),
            ctx.partUsage(),
            ctx.portUsage(),
            ctx.viewUsage(),
            ctx.renderingUsage(),
            ctx.allocationUsage(),
            ctx.message(),
            ctx.flowUsage(),
            ctx.successionFlowUsage(),
            ctx.occurrenceUsage(),
            ctx.individualUsage(),
            ctx.portionUsage(),
            ctx.eventOccurrenceUsage(),
            ctx.connectionUsage(),
            ctx.interfaceUsage(),
            ctx.behaviorUsageElement(),
        )
        for child in children:
            if child is not None and self._child(child) is not None:
                self._pass(ctx, child)
                return
        self._raw_store(ctx)

    def exitNonOccurrenceUsageMember(
        self, ctx: SysMLv2Parser.NonOccurrenceUsageMemberContext
    ) -> None:
        """Assemble a non-occurrence usage member and retain visibility."""
        usage = self._child(ctx.nonOccurrenceUsageElement())
        if not isinstance(usage, SourceElement):
            raise ValueError("nonOccurrenceUsageMember requires a typed usage")
        self._store(
            ctx,
            NonOccurrenceUsageMember(
                usage=usage,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitDefinitionBodyItem(self, ctx: SysMLv2Parser.DefinitionBodyItemContext) -> None:
        """Assemble a generic body item with its owned source/visibility fields."""
        if ctx.importRule():
            import_rule = self._child(ctx.importRule())
            if not isinstance(import_rule, ImportRule):
                raise ValueError("definitionBodyItem import requires ImportRule")
            self._store(
                ctx,
                DefinitionBodyItem(
                    element=import_rule,
                    member_prefix=None,
                    source_succession=None,
                ),
            )
            return
        source = self._child(ctx.sourceSuccessionMember()) if ctx.sourceSuccessionMember() else None
        member_prefix = self._member_prefix(ctx.memberPrefix()) if ctx.memberPrefix() else None
        child_ctx = (
            ctx.definitionBodyItemContent()
            or ctx.endOccurrenceUsageElement()
            or ctx.occurrenceUsageElement()
        )
        child = self._child(child_ctx)
        if not isinstance(child, SourceElement):
            raise ValueError("definitionBodyItem has no assembled element")
        self._store(
            ctx,
            DefinitionBodyItem(
                element=child,
                member_prefix=member_prefix,
                source_succession=source if isinstance(source, SourceSuccession) else None,
            ),
        )

    def exitDefinitionBody(self, ctx: SysMLv2Parser.DefinitionBodyContext) -> None:
        """Assemble a generic definition body and preserve ordered members."""
        if ctx.SEMI():
            self._store(ctx, DefinitionBody(declaration_only=True))
            return
        items = [self._child(item) for item in ctx.definitionBodyItem()]
        if not all(isinstance(item, DefinitionBodyItem) for item in items):
            raise ValueError("definitionBody contains an unassembled item")
        self._store(
            ctx,
            DefinitionBody(items=[item for item in items if isinstance(item, DefinitionBodyItem)]),
        )

    def exitDefinition(self, ctx: SysMLv2Parser.DefinitionContext) -> None:
        """Assemble a generic definition declaration and body."""
        declaration = self._child(ctx.definitionDeclaration())
        body = self._child(ctx.definitionBody())
        if not isinstance(declaration, DefinitionDeclaration) or not isinstance(
            body, DefinitionBody
        ):
            raise ValueError("definition has incomplete required fields")
        self._store(ctx, Definition(declaration=declaration, body=body))

    def exitPartDefinition(self, ctx: SysMLv2Parser.PartDefinitionContext) -> None:
        """Assemble a structured ``part def``."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        definition = self._child(ctx.definition())
        if not isinstance(prefix, OccurrenceDefinitionPrefix) or not isinstance(
            definition, Definition
        ):
            raise ValueError("partDefinition has incomplete required fields")
        self._store(ctx, PartDefinition(prefix, definition))

    def exitOccurrenceDefinition(self, ctx: SysMLv2Parser.OccurrenceDefinitionContext) -> None:
        """Assemble the generic ``occurrence def`` production."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        definition = self._child(ctx.definition())
        if not isinstance(prefix, OccurrenceDefinitionPrefix) or not isinstance(
            definition, Definition
        ):
            raise ValueError("occurrenceDefinition has incomplete required fields")
        self._store(ctx, OccurrenceDefinition(prefix, definition))

    def exitIndividualDefinition(self, ctx: SysMLv2Parser.IndividualDefinitionContext) -> None:
        """Assemble the distinct ``individual ... def`` alternative."""
        definition = self._child(ctx.definition())
        if not isinstance(definition, Definition):
            raise ValueError("individualDefinition has incomplete required fields")
        self._store(
            ctx,
            IndividualDefinition(
                basic_definition_keyword=(
                    self._text(ctx.basicDefinitionPrefix()).strip()
                    if ctx.basicDefinitionPrefix()
                    else None
                ),
                extension_keywords=[
                    self._text(item).strip() for item in ctx.definitionExtensionKeyword()
                ],
                definition=definition,
            ),
        )

    def exitItemDefinition(self, ctx: SysMLv2Parser.ItemDefinitionContext) -> None:
        """Assemble an ``item def`` from its explicit grammar children."""
        prefix = self._child(ctx.occurrenceDefinitionPrefix())
        definition = self._child(ctx.definition())
        if not isinstance(prefix, OccurrenceDefinitionPrefix) or not isinstance(
            definition, Definition
        ):
            raise ValueError("itemDefinition has incomplete required fields")
        self._store(ctx, ItemDefinition(prefix, definition))

    def exitAttributeDefinition(self, ctx: SysMLv2Parser.AttributeDefinitionContext) -> None:
        """Assemble an ``attribute def`` with its non-occurrence prefix."""
        prefix = self._child(ctx.definitionPrefix())
        definition = self._child(ctx.definition())
        if not isinstance(prefix, DefinitionPrefix) or not isinstance(definition, Definition):
            raise ValueError("attributeDefinition has incomplete required fields")
        self._store(ctx, AttributeDefinition(prefix, definition))

    def exitAttributeUsage(self, ctx: SysMLv2Parser.AttributeUsageContext) -> None:
        """Assemble an ``attribute`` usage from prefix and generic completion."""
        prefix = self._child(ctx.usagePrefix())
        usage = self._child(ctx.usage())
        if not isinstance(prefix, UsagePrefix) or not isinstance(usage, Usage):
            raise ValueError("attributeUsage has incomplete required fields")
        self._store(ctx, AttributeUsage(prefix, usage))

    def exitEnumerationUsage(self, ctx: SysMLv2Parser.EnumerationUsageContext) -> None:
        """Assemble an ``enum`` usage from prefix and generic completion."""
        prefix = self._child(ctx.usagePrefix())
        usage = self._child(ctx.usage())
        if not isinstance(prefix, UsagePrefix) or not isinstance(usage, Usage):
            raise ValueError("enumerationUsage has incomplete required fields")
        self._store(ctx, EnumerationUsage(prefix, usage))

    def _usage_prefix_from_ref_prefix(self, ctx: Any) -> UsagePrefix:
        """Convert a ``refPrefix`` context into the shared typed prefix node."""
        ref = ctx.refPrefix() if ctx is not None and hasattr(ctx, "refPrefix") else ctx
        if not hasattr(ref, "featureDirection"):
            return UsagePrefix(extension_keywords=[self._text(ctx).strip()])
        return UsagePrefix(
            feature_direction=(
                self._text(ref.featureDirection()).strip()
                if ref is not None and ref.featureDirection()
                else None
            ),
            is_derived=bool(ref is not None and ref.DERIVED()),
            is_abstract=bool(ref is not None and ref.ABSTRACT()),
            is_variation=bool(ref is not None and ref.VARIATION()),
            is_constant=bool(ref is not None and ref.CONSTANT()),
        )

    def exitReferenceUsage(self, ctx: SysMLv2Parser.ReferenceUsageContext) -> None:
        """Assemble an explicit ``ref`` usage instead of a raw fragment."""
        usage = self._child(ctx.usage())
        prefix_context = ctx.refPrefix() or ctx.endUsagePrefix()
        if not isinstance(usage, Usage) or prefix_context is None:
            raise ValueError("referenceUsage has incomplete required fields")
        self._store(ctx, ReferenceUsage(self._usage_prefix_from_ref_prefix(prefix_context), usage))

    def exitDefaultReferenceUsage(self, ctx: SysMLv2Parser.DefaultReferenceUsageContext) -> None:
        """Assemble a default reference usage without a second ``ref`` token."""
        usage = self._child(ctx.usage())
        prefix = ctx.refPrefix()
        if not isinstance(usage, Usage) or prefix is None:
            raise ValueError("defaultReferenceUsage has incomplete required fields")
        self._store(
            ctx,
            ReferenceUsage(self._usage_prefix_from_ref_prefix(prefix), usage, False),
        )

    def exitConjugatedPortDefinitionMember(
        self, ctx: SysMLv2Parser.ConjugatedPortDefinitionMemberContext
    ) -> None:
        """Pass the optional conjugated-port definition suffix."""
        if (
            ctx.conjugatedPortDefinition() is not None
            and self._child(ctx.conjugatedPortDefinition()) is not None
        ):
            self._pass(ctx, ctx.conjugatedPortDefinition())

    def exitConjugatedPortDefinition(
        self, ctx: SysMLv2Parser.ConjugatedPortDefinitionContext
    ) -> None:
        """Pass the concrete conjugated-port definition marker."""
        if ctx.portConjugation() is not None and self._child(ctx.portConjugation()) is not None:
            self._pass(ctx, ctx.portConjugation())

    def exitPortDefinition(self, ctx: SysMLv2Parser.PortDefinitionContext) -> None:
        """Assemble a ``port def`` and preserve its conjugation suffix."""
        prefix = self._child(ctx.definitionPrefix())
        definition = self._child(ctx.definition())
        conjugation = self._child(ctx.conjugatedPortDefinitionMember())
        if not isinstance(prefix, DefinitionPrefix) or not isinstance(definition, Definition):
            raise ValueError("portDefinition has incomplete required fields")
        self._store(
            ctx,
            PortDefinition(
                definition_prefix=prefix,
                definition=definition,
                conjugated_port_definition=conjugation
                if isinstance(conjugation, ConjugatedPortTyping)
                else None,
            ),
        )

    def exitUsage(self, ctx: SysMLv2Parser.UsageContext) -> None:
        """Assemble a generic usage declaration and completion body."""
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        completion = self._child(ctx.usageCompletion())
        if not isinstance(completion, Usage):
            raise ValueError("usage completion was not assembled")
        self._store(
            ctx,
            Usage(
                body=completion.body,
                declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else completion.declaration,
                value_part=completion.value_part,
            ),
        )

    def exitUsageCompletion(self, ctx: SysMLv2Parser.UsageCompletionContext) -> None:
        """Assemble generic usage value and body before the outer declaration."""
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        body = self._child(ctx.usageBody())
        if not isinstance(body, DefinitionBody):
            raise ValueError("usageCompletion requires definition body")
        self._store(
            ctx,
            Usage(
                body=body,
                value_part=value if isinstance(value, ValuePart) else None,
            ),
        )

    def exitPartUsage(self, ctx: SysMLv2Parser.PartUsageContext) -> None:
        """Assemble a structured ``part`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        usage = self._child(ctx.usage())
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(usage, Usage):
            raise ValueError("partUsage has incomplete required fields")
        self._store(ctx, PartUsage(prefix, usage))

    def exitOccurrenceUsage(self, ctx: SysMLv2Parser.OccurrenceUsageContext) -> None:
        """Assemble the generic ``occurrence`` usage alternative."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        usage = self._child(ctx.usage())
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(usage, Usage):
            raise ValueError("occurrenceUsage has incomplete required fields")
        self._store(ctx, OccurrenceUsage(prefix, usage))

    def exitIndividualUsage(self, ctx: SysMLv2Parser.IndividualUsageContext) -> None:
        """Assemble the distinct ``individual`` usage alternative."""
        usage = self._child(ctx.usage())
        if not isinstance(usage, Usage):
            raise ValueError("individualUsage has incomplete required fields")
        basic = ctx.basicUsagePrefix()
        ref = basic.refPrefix() if basic and basic.refPrefix() else None
        prefix = UsagePrefix(
            feature_direction=(
                self._text(ref.featureDirection()).strip()
                if ref and ref.featureDirection()
                else None
            ),
            is_derived=bool(ref and ref.DERIVED()),
            is_abstract=bool(ref and ref.ABSTRACT()),
            is_variation=bool(ref and ref.VARIATION()),
            is_constant=bool(ref and ref.CONSTANT()),
            is_reference=bool(basic and basic.REF()),
        )
        self._store(
            ctx,
            IndividualUsage(
                basic_usage_prefix=prefix,
                extension_keywords=[
                    self._text(item).strip() for item in ctx.usageExtensionKeyword()
                ],
                usage=usage,
            ),
        )

    def exitPortionUsage(self, ctx: SysMLv2Parser.PortionUsageContext) -> None:
        """Assemble a ``snapshot`` or ``timeslice`` occurrence usage."""
        usage = self._child(ctx.usage())
        if not isinstance(usage, Usage):
            raise ValueError("portionUsage has incomplete required fields")
        basic = ctx.basicUsagePrefix()
        ref = basic.refPrefix() if basic and basic.refPrefix() else None
        prefix = OccurrenceUsagePrefix(
            feature_direction=(
                self._text(ref.featureDirection()).strip()
                if ref and ref.featureDirection()
                else None
            ),
            is_derived=bool(ref and ref.DERIVED()),
            is_abstract=bool(ref and ref.ABSTRACT()),
            is_variation=bool(ref and ref.VARIATION()),
            is_constant=bool(ref and ref.CONSTANT()),
            is_reference=bool(basic and basic.REF()),
            is_individual=ctx.INDIVIDUAL() is not None,
            portion_kind=self._text(ctx.portionKind()).strip(),
            extension_keywords=[self._text(item).strip() for item in ctx.usageExtensionKeyword()],
        )
        self._store(ctx, PortionUsage(prefix, usage))

    def exitEventOccurrenceUsage(self, ctx: SysMLv2Parser.EventOccurrenceUsageContext) -> None:
        """Assemble the named and shorthand ``event`` occurrence forms."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        completion = self._child(ctx.usageCompletion())
        reference = (
            self._child(ctx.ownedReferenceSubsetting()) if ctx.ownedReferenceSubsetting() else None
        )
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        declaration = self._child(ctx.usageDeclaration()) if ctx.usageDeclaration() else None
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(completion, Usage):
            raise ValueError("eventOccurrenceUsage has incomplete required fields")
        self._store(
            ctx,
            EventOccurrenceUsage(
                occurrence_usage_prefix=prefix,
                usage=completion,
                owned_reference_subsetting=reference if self._is_reference(reference) else None,
                feature_specialization_part=(
                    specialization
                    if isinstance(specialization, FeatureSpecializationPart)
                    else None
                ),
                occurrence=ctx.OCCURRENCE() is not None,
                usage_declaration=declaration
                if isinstance(declaration, UsageDeclaration)
                else None,
            ),
        )

    def exitPortUsage(self, ctx: SysMLv2Parser.PortUsageContext) -> None:
        """Assemble a structured ``port`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        usage = self._child(ctx.usage())
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(usage, Usage):
            raise ValueError("portUsage has incomplete required fields")
        self._store(ctx, PortUsage(prefix, usage))

    def exitItemUsage(self, ctx: SysMLv2Parser.ItemUsageContext) -> None:
        """Assemble a structured ``item`` usage."""
        prefix = self._child(ctx.occurrenceUsagePrefix())
        usage = self._child(ctx.usage())
        if not isinstance(prefix, OccurrenceUsagePrefix) or not isinstance(usage, Usage):
            raise ValueError("itemUsage has incomplete required fields")
        self._store(ctx, ItemUsage(prefix, usage))

    def exitEndOccurrenceUsageElement(
        self, ctx: SysMLv2Parser.EndOccurrenceUsageElementContext
    ) -> None:
        """Assemble an ``end`` occurrence usage with owned concrete modifiers."""
        usage = self._child(ctx.occurrenceUsageElement())
        if not isinstance(usage, SourceElement):
            raise ValueError("endOccurrenceUsageElement requires occurrenceUsageElement")
        self._store(
            ctx,
            EndOccurrenceUsageElement(
                occurrence_usage=usage,
                name=self._name_value(ctx.name()) if ctx.name() else None,
                cross_multiplicity_text=(
                    self._text(ctx.ownedCrossMultiplicityMember()).strip()
                    if ctx.ownedCrossMultiplicityMember()
                    else None
                ),
                is_nonunique=ctx.NONUNIQUE() is not None,
            ),
        )

    def exitStructureUsageElement(self, ctx: SysMLv2Parser.StructureUsageElementContext) -> None:
        """Pass every typed structure-usage alternative."""
        child = (
            ctx.occurrenceUsage()
            or ctx.individualUsage()
            or ctx.portionUsage()
            or ctx.eventOccurrenceUsage()
            or ctx.itemUsage()
            or ctx.partUsage()
            or ctx.viewUsage()
            or ctx.renderingUsage()
            or ctx.portUsage()
            or ctx.connectionUsage()
            or ctx.interfaceUsage()
            or ctx.allocationUsage()
            or ctx.message()
            or ctx.flowUsage()
            or ctx.successionFlowUsage()
        )
        if child is not None:
            self._pass(ctx, child)
            return
        self._raw_store(ctx)

    def exitStructureUsageMember(self, ctx: SysMLv2Parser.StructureUsageMemberContext) -> None:
        """Assemble a structural usage member from its actual production."""
        child = self._child(ctx.structureUsageElement())
        if not isinstance(child, SourceElement):
            raise ValueError("structureUsageMember requires structureUsageElement")
        self._store(
            ctx,
            StructureUsageMember(
                structure_usage=child,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    # ------------------------------------------------------------------
    # Package/document containment
    # ------------------------------------------------------------------

    def exitMetadataFeatureDeclaration(
        self, ctx: SysMLv2Parser.MetadataFeatureDeclarationContext
    ) -> None:
        """Assemble metadata identification, typing operator, and type."""
        identification = self._child(ctx.identification()) if ctx.identification() else None
        owned_feature_typing = self._child(ctx.ownedFeatureTyping())
        if not isinstance(owned_feature_typing, OwnedFeatureTyping):
            raise ValueError("metadataFeatureDeclaration requires ownedFeatureTyping")
        operator = None
        if ctx.COLON() is not None:
            operator = ":"
        elif ctx.TYPED() is not None:
            operator = "typed by"
        if identification is not None and not isinstance(identification, Identification):
            raise ValueError("metadataFeatureDeclaration identification was not assembled")
        self._store(
            ctx,
            MetadataFeatureDeclaration(
                owned_feature_typing=owned_feature_typing,
                identification=identification
                if isinstance(identification, Identification)
                else None,
                operator=operator,
            ),
        )

    def exitMetadataBody(self, ctx: SysMLv2Parser.MetadataBodyContext) -> None:
        """Assemble a metadata semicolon or ordered brace body."""
        if ctx.SEMI() is not None:
            self._store(ctx, MetadataBody(declaration_only=True))
            return
        expected_count = sum(
            len(contexts)
            for contexts in (
                ctx.metadataBodyElement(),
                ctx.definitionMember(),
                ctx.metadataBodyUsageMember(),
                ctx.aliasMember(),
                ctx.importRule(),
            )
        )
        items = self._direct_source_items(ctx)
        if len(items) != expected_count:
            raise ValueError("metadataBody contains an unassembled member")
        self._store(ctx, MetadataBody(items=items))

    def exitMetadataBodyElement(self, ctx: SysMLv2Parser.MetadataBodyElementContext) -> None:
        """Pass one metadata body element alternative."""
        child = (
            ctx.nonFeatureMember()
            or ctx.metadataBodyFeatureMember()
            or ctx.aliasMember()
            or ctx.importRule()
        )
        if child is None:
            raise ValueError("metadataBodyElement has no alternative")
        self._pass(ctx, child)

    def exitMetadataBodyFeatureMember(
        self, ctx: SysMLv2Parser.MetadataBodyFeatureMemberContext
    ) -> None:
        """Pass the concrete metadata body feature through its wrapper."""
        self._pass(ctx, ctx.metadataBodyFeature())

    def exitMetadataBodyFeature(self, ctx: SysMLv2Parser.MetadataBodyFeatureContext) -> None:
        """Assemble a metadata feature with typed specialization and value fields."""
        owned_redefinition = self._child(ctx.ownedRedefinition())
        body = self._child(ctx.metadataBody())
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        if not self._is_reference(owned_redefinition) or not isinstance(body, MetadataBody):
            raise ValueError("metadataBodyFeature has incomplete required fields")
        if specialization is not None and not isinstance(specialization, FeatureSpecializationPart):
            raise ValueError("metadataBodyFeature specialization was not assembled")
        if value is not None and not isinstance(value, ValuePart):
            raise ValueError("metadataBodyFeature value was not assembled")
        self._store(
            ctx,
            MetadataBodyFeature(
                owned_redefinition=owned_redefinition,
                body=body,
                is_feature=ctx.FEATURE() is not None,
                redefinition_operator=(
                    ":>>"
                    if ctx.COLON_GT_GT() is not None
                    else "redefines"
                    if ctx.REDEFINES() is not None
                    else None
                ),
                feature_specialization_part=(
                    specialization
                    if isinstance(specialization, FeatureSpecializationPart)
                    else None
                ),
                value_part=value if isinstance(value, ValuePart) else None,
            ),
        )

    def exitMetadataBodyUsageMember(
        self, ctx: SysMLv2Parser.MetadataBodyUsageMemberContext
    ) -> None:
        """Pass the concrete metadata body usage through its wrapper."""
        self._pass(ctx, ctx.metadataBodyUsage())

    def exitMetadataBodyUsage(self, ctx: SysMLv2Parser.MetadataBodyUsageContext) -> None:
        """Assemble a metadata usage with typed specialization and value fields."""
        owned_redefinition = self._child(ctx.ownedRedefinition())
        body = self._child(ctx.metadataBody())
        specialization = (
            self._child(ctx.featureSpecializationPart())
            if ctx.featureSpecializationPart()
            else None
        )
        value = self._child(ctx.valuePart()) if ctx.valuePart() else None
        if not self._is_reference(owned_redefinition) or not isinstance(body, MetadataBody):
            raise ValueError("metadataBodyUsage has incomplete required fields")
        if specialization is not None and not isinstance(specialization, FeatureSpecializationPart):
            raise ValueError("metadataBodyUsage specialization was not assembled")
        if value is not None and not isinstance(value, ValuePart):
            raise ValueError("metadataBodyUsage value was not assembled")
        self._store(
            ctx,
            MetadataBodyUsage(
                owned_redefinition=owned_redefinition,
                body=body,
                is_ref=ctx.REF() is not None,
                redefinition_operator=(
                    ":>>"
                    if ctx.COLON_GT_GT() is not None
                    else "redefines"
                    if ctx.REDEFINES() is not None
                    else None
                ),
                feature_specialization_part=(
                    specialization
                    if isinstance(specialization, FeatureSpecializationPart)
                    else None
                ),
                value_part=value if isinstance(value, ValuePart) else None,
            ),
        )

    def exitMetadataFeature(self, ctx: SysMLv2Parser.MetadataFeatureContext) -> None:
        """Assemble a model-owned metadata annotation from explicit children."""
        declaration = self._child(ctx.metadataFeatureDeclaration())
        body = self._child(ctx.metadataBody())
        prefixes = [self._child(item) for item in ctx.prefixMetadataMember()]
        about = [self._child(item) for item in ctx.annotation()]
        if not isinstance(declaration, MetadataFeatureDeclaration) or not isinstance(
            body, MetadataBody
        ):
            raise ValueError("metadataFeature has incomplete required fields")
        if not all(isinstance(item, OwnedFeatureTyping) for item in prefixes):
            raise ValueError("metadataFeature prefix metadata was not assembled")
        if not all(isinstance(item, QualifiedReference) for item in about):
            raise ValueError("metadataFeature about annotation was not assembled")
        self._store(
            ctx,
            MetadataFeature(
                declaration=declaration,
                body=body,
                keyword="@" if ctx.AT_SIGN() is not None else "metadata",
                about=[item for item in about if isinstance(item, QualifiedReference)],
                prefix_metadata=[item for item in prefixes if isinstance(item, OwnedFeatureTyping)],
            ),
        )

    def exitPackageDeclaration(self, ctx: SysMLv2Parser.PackageDeclarationContext) -> None:
        """Pass package identification through the keyword wrapper."""
        if ctx.identification():
            self._pass(ctx, ctx.identification())
        else:
            self.parts[ctx] = None

    def exitAnnotation(self, ctx: SysMLv2Parser.AnnotationContext) -> None:
        """Pass comment ``about`` targets as typed qualified references."""
        self._pass(ctx, ctx.qualifiedName())

    def exitComment(self, ctx: SysMLv2Parser.CommentContext) -> None:
        """Assemble model-owned comment syntax and regular-comment text."""
        identification = self._child(ctx.identification()) if ctx.identification() else None
        locale = self._text(ctx.DOUBLE_STRING()).strip() if ctx.DOUBLE_STRING() else None
        about = [self._child(item) for item in ctx.annotation()]
        self._store(
            ctx,
            Comment(
                is_comment=ctx.COMMENT() is not None,
                declaration=identification if isinstance(identification, Identification) else None,
                locale=locale,
                body=_relative_source(self._text(ctx.REGULAR_COMMENT())),
                about=[item for item in about if isinstance(item, QualifiedReference)],
            ),
        )

    def exitDocumentation(self, ctx: SysMLv2Parser.DocumentationContext) -> None:
        """Assemble model-owned documentation syntax."""
        identification = self._child(ctx.identification()) if ctx.identification() else None
        locale = self._text(ctx.DOUBLE_STRING()).strip() if ctx.DOUBLE_STRING() else None
        self._store(
            ctx,
            Documentation(
                identification=identification
                if isinstance(identification, Identification)
                else None,
                locale=locale,
                body=_relative_source(self._text(ctx.REGULAR_COMMENT())),
            ),
        )

    def exitAnnotatingElement(self, ctx: SysMLv2Parser.AnnotatingElementContext) -> None:
        """Pass comment/documentation annotations or retain unrelated metadata."""
        child = ctx.comment() or ctx.documentation() or ctx.metadataFeature()
        if child is not None:
            self._pass(ctx, child)
        else:
            self._raw_store(ctx)

    def exitDefinitionElement(self, ctx: SysMLv2Parser.DefinitionElementContext) -> None:
        """Pass every concrete SysML definition alternative."""
        child = (
            ctx.stateDefinition()
            or ctx.partDefinition()
            or ctx.itemDefinition()
            or ctx.occurrenceDefinition()
            or ctx.individualDefinition()
            or ctx.attributeDefinition()
            or ctx.dependency()
            or ctx.enumerationDefinition()
            or ctx.portDefinition()
            or ctx.connectionDefinition()
            or ctx.flowDefinition()
            or ctx.interfaceDefinition()
            or ctx.actionDefinition()
            or ctx.calculationDefinition()
            or ctx.constraintDefinition()
            or ctx.requirementDefinition()
            or ctx.concernDefinition()
            or ctx.caseDefinition()
            or ctx.analysisCaseDefinition()
            or ctx.verificationCaseDefinition()
            or ctx.useCaseDefinition()
            or ctx.viewDefinition()
            or ctx.viewpointDefinition()
            or ctx.renderingDefinition()
            or ctx.metadataDefinition()
            or ctx.allocationDefinition()
            or ctx.extendedDefinition()
            or ctx.package()
            or ctx.libraryPackage()
            or ctx.annotatingElement()
        )
        if child is not None:
            self._pass(ctx, child)
        else:
            self._raw_store(ctx)

    def exitNonOccurrenceUsageElement(
        self, ctx: SysMLv2Parser.NonOccurrenceUsageElementContext
    ) -> None:
        """Preserve non-occurrence usage syntax at the compatibility boundary."""
        child = (
            ctx.referenceUsage()
            or ctx.endFeatureUsage()
            or ctx.defaultReferenceUsage()
            or ctx.attributeUsage()
            or ctx.enumerationUsage()
        )
        if child is not None:
            if self._child(child) is not None:
                self._pass(ctx, child)
            else:
                self._raw_store(ctx)
            return
        self._raw_store(ctx)

    def exitUsageElement(self, ctx: SysMLv2Parser.UsageElementContext) -> None:
        """Pass occurrence/behavior state usage alternatives."""
        child = ctx.occurrenceUsageElement() or ctx.nonOccurrenceUsageElement()
        if child is None:
            raise ValueError("usageElement has no alternative")
        self._pass(ctx, child)

    def exitOccurrenceUsageElement(self, ctx: SysMLv2Parser.OccurrenceUsageElementContext) -> None:
        """Pass behavior usages and retain unrelated occurrence syntax."""
        child = ctx.structureUsageElement() or ctx.behaviorUsageElement()
        if child is not None:
            self._pass(ctx, child)
        else:
            self._raw_store(ctx)

    def exitDefinitionMember(self, ctx: SysMLv2Parser.DefinitionMemberContext) -> None:
        """Assemble a nested definition member and preserve visibility."""
        child = self._child(ctx.definitionElement())
        if not isinstance(child, SourceElement):
            raise ValueError("definitionMember requires definitionElement")
        self._store(
            ctx,
            DefinitionBodyItem(
                element=child,
                member_prefix=self._member_prefix(ctx.memberPrefix()),
            ),
        )

    def exitNonBehaviorBodyItem(self, ctx: SysMLv2Parser.NonBehaviorBodyItemContext) -> None:
        """Pass nested definitions or preserve non-state body syntax."""
        if ctx.importRule():
            self._pass(ctx, ctx.importRule())
        elif ctx.aliasMember():
            self._pass(ctx, ctx.aliasMember())
        elif ctx.definitionMember():
            self._pass(ctx, ctx.definitionMember())
        elif ctx.structureUsageMember():
            self._pass(ctx, ctx.structureUsageMember())
        elif ctx.nonOccurrenceUsageMember():
            self._pass(ctx, ctx.nonOccurrenceUsageMember())
        else:
            self._raw_store(ctx)

    def exitPackageMember(self, ctx: SysMLv2Parser.PackageMemberContext) -> None:
        """Assemble a package member without mutating its child node."""
        child_ctx = ctx.definitionElement() or ctx.usageElement()
        child = self._child(child_ctx)
        if not isinstance(child, SourceElement):
            raise ValueError("packageMember has no assembled element")
        self._store(
            ctx,
            PackageMember(element=child, member_prefix=self._member_prefix(ctx.memberPrefix())),
        )

    def exitPackageBodyElement(self, ctx: SysMLv2Parser.PackageBodyElementContext) -> None:
        """Pass package members or retain unrelated package syntax."""
        child = (
            ctx.packageMember()
            or ctx.elementFilterMember()
            or ctx.aliasMember()
            or ctx.importRule()
        )
        if child is None:
            raise ValueError("packageBodyElement has no alternative")
        if self._child(child) is not None:
            self._pass(ctx, child)
        else:
            # Parser recovery can expose an incomplete dispatcher context;
            # retain that malformed fragment without affecting valid typed
            # package members.
            self._raw_store(ctx)

    def exitPackageBody(self, ctx: SysMLv2Parser.PackageBodyContext) -> None:
        """Collect ordered package members in a listener-local body record."""
        if ctx.SEMI():
            self.parts[ctx] = (True, [])
        else:
            self.parts[ctx] = (
                False,
                [
                    self._child(item)
                    for item in ctx.packageBodyElement()
                    if isinstance(self._child(item), SourceElement)
                ],
            )

    def _build_package(self, ctx: Any, is_library: bool) -> None:
        """Build one package variant from its declaration and local body record."""
        declaration_ctx = ctx.packageDeclaration()
        identification = (
            self._child(declaration_ctx)
            if declaration_ctx and declaration_ctx.identification()
            else None
        )
        body_decl_only, members = self.parts.get(ctx.packageBody(), (False, []))
        self._store(
            ctx,
            Package(
                identification=identification
                if isinstance(identification, Identification)
                else None,
                members=[item for item in members if isinstance(item, SourceElement)],
                is_library=is_library,
                is_standard=bool(is_library and ctx.STANDARD() is not None),
                declaration_only=body_decl_only,
                prefix_metadata=[self._text(item).strip() for item in ctx.prefixMetadataMember()],
            ),
        )

    def exitPackage(self, ctx: SysMLv2Parser.PackageContext) -> None:
        """Build an ordinary package."""
        self._build_package(ctx, False)

    def exitLibraryPackage(self, ctx: SysMLv2Parser.LibraryPackageContext) -> None:
        """Build a library package and preserve its standard marker."""
        self._build_package(ctx, True)

    def exitRootNamespace(self, ctx: SysMLv2Parser.RootNamespaceContext) -> None:
        """Build the ordered SysML document-root model."""
        members = [self._child(item) for item in ctx.packageBodyElement()]
        self._store(
            ctx, Model(members=[item for item in members if isinstance(item, SourceElement)])
        )


__all__ = ["SysMLAstListener"]
