"""Explicit source-AST nodes for the SysML v2 textual notation.

This module is the concrete-syntax side of the package.  It follows the
OMG SysML 2.0 separation between textual concrete syntax and the later
abstract/semantic model: a node records what the parser saw, while the
``semantic`` and ``workspace`` packages are responsible for linking names,
deriving relationships, and checking the normative constraints.

The classes are deliberately handwritten.  A grammar rule is retained as a
public node only when it carries syntax or model meaning.  Rules that merely
wrap one child (for example ``StateBodyItem``, ``TransitionSuccessionMember``
and ``EmptyParameterMember``) are passed through by the listener.  Conversely,
expressions and action statements are represented at operator/statement
granularity instead of being collapsed into a source-text field.

The public type hierarchy is intentional: ``ASTNode`` carries provenance,
``SourceElement`` marks exportable syntax, ``Expression`` marks every
structured expression, ``Statement`` marks executable action-body content,
``ActionNode`` marks the action-node grammar family, and
``ActionUsageNode`` marks action usages that can be effects or subactions.
Concrete fields use the narrowest useful class in that hierarchy (or an
explicit union of grammar alternatives); callers never have to accept an
arbitrary ``ASTNode`` and guess what it means.  A grammar-required child is a
required dataclass argument.  ``Optional`` and defaults are used only for
grammar alternatives that are actually optional.  The listener attaches
``span`` after construction; :class:`SourceSpan` carries the optional source
path, so direct construction still allows provenance to be absent without
weakening required syntax fields.

The exported ``RawElement`` lossless compatibility node is audited in
``docs/research/raw_element_compatibility_ledger.json``.  Each entry names the
grammar production, listener callback, regression test, and follow-up typed
node.  It is a controlled syntax escape hatch, not a semantic-model API and
not a license for a normal expression, action, state, transition, import,
alias, filter, connection, or interface path to become opaque.

The AST is intentionally not the linked SysML semantic model.  Qualified
names, feature chains, transition endpoints, and action references remain
source-level objects until a workspace/linker layer resolves them.  This
keeps source spans meaningful and prevents parser recovery from inventing
semantic identity.  The listener is the sole assembler and uses explicit
``exit<GrammarRule>`` callbacks; generated parser contexts are never converted
through reflection or a generic text scanner.  ``RawElement`` is restricted
to explicit deferred-production and parser-recovery fragments while coverage
is staged; it must not appear on ordinary expression, action, transition, or
state paths.  The class remains importable from ``pysysmlv2.syntax`` so syntax
clients can recognize and reject this boundary explicitly; semantic code must
never treat it as a resolved model element.

Every concrete node owns its exporter.  ``str(node)`` and ``to_sysml()`` build
canonical, parseable SysML text from the node's named fields.  ``source_path``
is represented only inside :class:`SourceSpan`, which is the sole field shared
by all nodes; provenance is not semantic identity or a generic
traversal/rendering mechanism.

.. list-table:: AST module roadmap
   :header-rows: 1

   * - Area
     - Public nodes
     - Boundary
   * - Provenance
     - :class:`SourceSpan`, :class:`ASTNode`
     - Source location only; no generic children or renderer.
   * - Names and declarations
     - :class:`Identification`, :class:`QualifiedReference`,
       :class:`FeatureChain`, :class:`DefinitionDeclaration`,
       :class:`UsageDeclaration`
     - Unresolved syntax names; workspace linking is deferred.
   * - Namespace membership
     - :class:`AliasMember`, :class:`ImportRule`, :class:`MembershipImport`,
       :class:`NamespaceImport`, :class:`FilterPackage`,
       :class:`ElementFilterMember`
     - Import, alias, and package-filter syntax; name resolution is deferred.
   * - Expressions
     - :class:`BooleanLiteral`, :class:`UnaryExpression`, :class:`BinaryExpression`,
       :class:`ConditionalExpression`, :class:`InvocationExpression`,
       :class:`FeatureChainExpression`, and related nodes
     - Operator tree and argument structure, not opaque text.
   * - State/action syntax
     - :class:`StateDefinition`, :class:`StateUsage`,
       :class:`StateSubactionMembership`, :class:`TransitionUsage`,
       :class:`TargetTransitionUsage`, :class:`ActionBody`,
       :class:`ActionNode`, :class:`ControlNode`
     - Concrete state-machine forms from SysML 2.0 section 8.2.2.18.
   * - Connection/interface syntax
     - :class:`ConnectionDefinition`, :class:`ConnectionUsage`,
       :class:`InterfaceDefinition`, :class:`InterfaceUsage`,
       :class:`ConnectorEnd`, :class:`InterfaceEnd`
     - Explicit connector endpoints, binary/n-ary parts, and interface body
       members; workspace linking is deferred.
   * - Document roots
     - :class:`Package`, :class:`Model`, :class:`Comment`,
       :class:`Documentation`
     - Ordered source members and model-owned textual elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, List, Optional, Sequence, Union


@dataclass(frozen=True)
class SourceSpan:
    """Represent a one-based, half-open source range.

    :param line: One-based start line.
    :type line: int
    :param column: One-based start column.
    :type column: int
    :param end_line: One-based exclusive end line.
    :type end_line: int
    :param end_column: One-based exclusive end column.
    :type end_column: int
    :param source_path: Original document path or URI, if known.
    :type source_path: str, optional
    :ivar line: One-based start line.
    :vartype line: int
    :ivar column: One-based start column.
    :vartype column: int
    :ivar end_line: One-based exclusive end line.
    :vartype end_line: int
    :ivar end_column: One-based exclusive end column.
    :vartype end_column: int
    :ivar source_path: Original document path or URI, if known.
    :vartype source_path: str, optional

    Example::

        >>> SourceSpan(1, 1, 1, 8).contains(SourceSpan(1, 2, 1, 4))
        True
    """

    line: int
    column: int
    end_line: int
    end_column: int
    source_path: Optional[str] = None

    def contains(self, other: "SourceSpan") -> bool:
        """Return whether ``other`` is wholly contained by this range.

        When both spans identify a source document, containment also requires
        those paths to match.  An absent path means that the caller has no
        document identity to compare, so the positional check is retained as
        the useful conservative result for partially annotated ASTs.

        :param other: Candidate nested source range.
        :type other: :class:`pysysmlv2.syntax.ast.SourceSpan`
        :return: ``True`` when both boundaries are contained.
        :rtype: bool
        """
        if (
            self.source_path is not None
            and other.source_path is not None
            and self.source_path != other.source_path
        ):
            return False
        return (self.line, self.column) <= (other.line, other.column) and (
            other.end_line,
            other.end_column,
        ) <= (self.end_line, self.end_column)


@dataclass
class ASTNode:
    """Store only source provenance shared by concrete AST dataclasses.

    This is intentionally a plain dataclass.  It has no child collection,
    visitor, renderer, semantic identifier, or reflection helper.  Concrete
    nodes declare their own fields and implement their own round-trip method.

    :param span: Source range occupied by the node, if known.
    :type span: :class:`pysysmlv2.syntax.ast.SourceSpan`, optional
    :ivar span: Source range occupied by the node.
    :vartype span: :class:`pysysmlv2.syntax.ast.SourceSpan`, optional

    Example::

        >>> ASTNode().span is None
        True
    """

    span: Optional[SourceSpan] = field(
        default=None,
        init=False,
        compare=False,
        repr=False,
    )

    def to_sysml(self) -> str:
        """Render this node as canonical SysML source.

        Concrete source nodes own their rendering rules.  Keeping the base
        method explicit prevents a missing production from silently turning
        into an empty or misleading source fragment.

        :raises NotImplementedError: Always, for the abstract source node.
        """
        raise NotImplementedError("concrete AST nodes must implement to_sysml")

    def __str__(self) -> str:
        """Return the canonical SysML rendering supplied by ``to_sysml``."""
        return self.to_sysml()


@dataclass
class SourceElement(ASTNode):
    """Base class for concrete source elements that can be emitted as SysML."""


@dataclass
class FunctionBodyItem(SourceElement):
    """Base class for an item retained in a structured function body.

    Function bodies permit declaration items, type-body members, return
    feature members, and an optional result expression.  This narrow marker
    prevents :class:`BodyExpression` from accepting an arbitrary source node.

    Example::

        >>> isinstance(FunctionBodyItem(), SourceElement)
        True
    """


@dataclass
class Expression(SourceElement):
    """Base class for every structured ``ownedExpression`` AST node."""


@dataclass
class Statement(SourceElement):
    """Base class for executable action-body statements."""


@dataclass
class ActionNode(Statement):
    """Base class for the grammar's executable ``actionNode`` family."""


@dataclass
class ControlNode(ActionNode):
    """Base class for merge, decision, join, and fork control nodes."""


@dataclass
class ActionUsageNode(Statement):
    """Base class for action usages used as statements or effects."""


def _join(parts: Sequence[str], separator: str = " ") -> str:
    """Join non-empty canonical fragments without introducing empty spacing."""
    return separator.join(part for part in parts if part)


def _indent(text: str, prefix: str = "    ") -> str:
    """Indent every non-empty line in a child rendering."""
    return "\n".join(prefix + line if line else line for line in text.splitlines())


def _render_block(items: Sequence[SourceElement], *, declaration_only: bool) -> str:
    """Render a brace/semicolon body from its ordered child nodes."""
    if declaration_only:
        return ";"
    rendered = [str(item) for item in items if str(item)]
    if not rendered:
        return "{ }"
    return "{\n" + "\n".join(_indent(item) for item in rendered) + "\n}"


def _append_body(prefix: str, body: str) -> str:
    """Attach a canonical ``;`` or brace body without stray spaces."""
    if not prefix:
        return body
    if body.startswith(";"):
        return prefix + body
    if body.startswith("{"):
        return prefix + " " + body
    return _join([prefix, body])


_BINARY_PRECEDENCE = {
    "??": 2,
    "implies": 3,
    "or": 4,
    "and": 5,
    "xor": 6,
    "|": 7,
    "&": 8,
    "==": 9,
    "!=": 9,
    "===": 9,
    "!==": 9,
    "<": 10,
    ">": 10,
    "<=": 10,
    ">=": 10,
    "..": 11,
    "+": 12,
    "-": 12,
    "*": 13,
    "/": 13,
    "%": 13,
    "**": 14,
    "^": 14,
}


def _expression_precedence(expression: "Expression") -> int:
    """Return the precedence used by canonical expression output."""
    if isinstance(expression, BinaryExpression):
        return _BINARY_PRECEDENCE.get(expression.operator, 1)
    if isinstance(expression, CoalesceExpression):
        return _BINARY_PRECEDENCE["??"]
    if isinstance(expression, ConditionalExpression):
        return 1
    return 100


def _render_expression_child(
    expression: "Expression", parent_precedence: int, operator: str, side: str
) -> str:
    """Render one child with parentheses when its AST grouping needs them."""
    rendered = str(expression)
    # The SysML ``ownedExpression`` grammar admits a conditional expression as
    # either operand of a binary expression.  Parenthesizing it here would
    # create a different concrete ``ParenthesizedExpression`` node on the next
    # parse even though the grammar assigns the same grouping without it.
    if isinstance(expression, ConditionalExpression):
        return rendered
    child_precedence = _expression_precedence(expression)
    needs_parentheses = child_precedence < parent_precedence
    if child_precedence == parent_precedence:
        needs_parentheses = side == ("left" if operator in ("**", "^") else "right")
    return "(" + rendered + ")" if needs_parentheses else rendered


def _relative_source(text: str) -> str:
    """Normalize a retained source fragment to its own indentation level."""
    # Raw compatibility fragments may contain tabs from the official examples.
    # Expand them before calculating the relative indentation so an exported
    # fragment has one stable representation after reparsing.
    lines = text.expandtabs(4).strip().splitlines()
    indents = [len(line) - len(line.lstrip(" \t")) for line in lines[1:] if line.strip()]
    if not indents:
        return "\n".join(line.rstrip() for line in lines)
    base_indent = min(indents)
    normalized = [lines[0]]
    for line in lines[1:]:
        prefix = line[:base_indent]
        normalized.append((line[base_indent:] if prefix.isspace() else line).rstrip())
    return "\n".join(normalized)


class LiteralKind(str, Enum):
    """Kinds of literals accepted by the SysML expression grammar."""

    BOOLEAN = "boolean"
    STRING = "string"
    INTEGER = "integer"
    REAL = "real"
    INFINITY = "infinity"
    NULL = "null"
    COMMENT = "comment"


class StateSubactionKind(str, Enum):
    """OMG ``StateSubactionKind`` literal values."""

    ENTRY = "entry"
    DO = "do"
    EXIT = "exit"


class TransitionFeatureKind(str, Enum):
    """OMG ``TransitionFeatureKind`` literal values."""

    TRIGGER = "trigger"
    GUARD = "guard"
    EFFECT = "effect"


class TargetTransitionForm(str, Enum):
    """Concrete keyword alternatives of ``TargetTransitionUsage``."""

    BARE = "bare"
    TRANSITION = "transition"


@dataclass
class Identification(SourceElement):
    """Represent an optional short name and declared name.

    :param short_name: Name between ``<`` and ``>`` when present.
    :type short_name: str, optional
    :param declared_name: Ordinary declared name when present.
    :type declared_name: str, optional

    Example::

        >>> str(Identification(short_name="s", declared_name="State"))
        '<s> State'
    """

    short_name: Optional[str] = None
    declared_name: Optional[str] = None

    def to_sysml(self) -> str:
        """Render the identification from its two grammar name fields."""
        if self.short_name is not None and self.declared_name is not None:
            return "<{}> {}".format(self.short_name, self.declared_name)
        if self.short_name is not None:
            return "<{}>".format(self.short_name)
        return self.declared_name or ""

    def __str__(self) -> str:
        """Return canonical identification text."""
        return self.to_sysml()


@dataclass
class QualifiedReference(SourceElement):
    """Represent an unresolved ``qualifiedName``.

    :param segments: Name segments from namespace to member.
    :type segments: list[str]
    :param is_absolute: Whether the source starts with ``$::``.
    :type is_absolute: bool

    Example::

        >>> str(QualifiedReference(segments=["Demo", "Idle"]))
        'Demo::Idle'
    """

    segments: List[str] = field(default_factory=list)
    is_absolute: bool = False
    separator: str = "::"

    def to_sysml(self) -> str:
        """Render the unresolved qualified name."""
        return ("$::" if self.is_absolute else "") + self.separator.join(self.segments)

    def __str__(self) -> str:
        """Return canonical qualified-name text."""
        return self.to_sysml()


@dataclass
class DottedQualifiedReference(SourceElement):
    """Represent ``qualifiedName ( DOT qualifiedName )*`` without flattening names.

    Each child remains a complete :class:`QualifiedReference`, preserving its
    own namespace separator and optional absolute-name marker.  This matters
    for forms such as ``A::B.C::D``: the dot belongs to the enclosing grammar
    production, while ``::`` belongs to each qualified-name child.

    :param qualified_names: Ordered qualified-name children joined by grammar
        dot tokens.
    :type qualified_names: list[pysysmlv2.syntax.ast.QualifiedReference]
    :ivar qualified_names: Ordered qualified-name children.
    :vartype qualified_names: list[pysysmlv2.syntax.ast.QualifiedReference]

    Example::

        >>> str(DottedQualifiedReference([
        ...     QualifiedReference(["A", "B"]),
        ...     QualifiedReference(["C", "D"]),
        ... ]))
        'A::B.C::D'
    """

    qualified_names: List[QualifiedReference]

    def to_sysml(self) -> str:
        """Render the child qualified names with their explicit dot relations."""
        return ".".join(str(item) for item in self.qualified_names)

    def __str__(self) -> str:
        """Return canonical dotted-qualified-reference source."""
        return self.to_sysml()


Reference = Union[QualifiedReference, DottedQualifiedReference]


@dataclass
class OwnedFeatureTyping(SourceElement):
    """Represent the concrete ``ownedFeatureTyping`` relationship.

    The relation is intentionally retained as concrete syntax rather than
    lowered to an already-linked type.  A later semantic layer resolves the
    reference and derives the appropriate model relationship.

    :param reference: One or more qualified-name children separated by ``.``.
    :type reference: :class:`pysysmlv2.syntax.ast.DottedQualifiedReference`
    :ivar reference: Unresolved concrete feature-typing reference.
    :vartype reference: :class:`pysysmlv2.syntax.ast.DottedQualifiedReference`

    Example::

        >>> str(OwnedFeatureTyping(DottedQualifiedReference([
        ...     QualifiedReference(["A", "B"]),
        ...     QualifiedReference(["C"]),
        ... ])))
        'A::B.C'
    """

    reference: DottedQualifiedReference

    def to_sysml(self) -> str:
        """Render the dotted qualified reference owned by the relation."""
        return str(self.reference)

    def __str__(self) -> str:
        """Return canonical owned-feature-typing source."""
        return self.to_sysml()


@dataclass
class ConjugatedPortTyping(SourceElement):
    """Represent the concrete ``conjugatedPortTyping`` alternative.

    This is distinct from an owned feature typing because the leading ``~``
    denotes a conjugated port type.  Resolving the referenced port type is a
    workspace concern, while the source AST must retain the choice exactly.

    :param reference: Unresolved conjugated port type reference.
    :type reference: :class:`pysysmlv2.syntax.ast.QualifiedReference`
    :ivar reference: Unresolved conjugated port type reference.
    :vartype reference: :class:`pysysmlv2.syntax.ast.QualifiedReference`

    Example::

        >>> str(ConjugatedPortTyping(QualifiedReference(["FuelPort"])))
        '~FuelPort'
    """

    reference: QualifiedReference

    def to_sysml(self) -> str:
        """Render the conjugation marker and unresolved port type reference."""
        return "~" + str(self.reference)

    def __str__(self) -> str:
        """Return canonical conjugated-port-typing source."""
        return self.to_sysml()


@dataclass
class DeclaredFeatureTyping(SourceElement):
    """Represent the declaration form of the ``featureTyping`` production.

    The grammar distinguishes a named specialization relationship from an
    owned typing and from a conjugated port typing.  The source AST keeps both
    participating unresolved references and the relationship body, leaving
    semantic ownership and resolution to the later workspace layer.

    :param typed_feature: Feature being declared as typed.
    :type typed_feature: :class:`pysysmlv2.syntax.ast.QualifiedReference`
    :param operator: Concrete ``:`` or ``typed by`` operator.
    :type operator: str
    :param general_type: Referenced general type.
    :type general_type: :class:`pysysmlv2.syntax.ast.Reference`
    :param relationship_body: Required relationship body after the type.
    :type relationship_body: :class:`pysysmlv2.syntax.ast.RelationshipBody`
    :param is_specialization: Whether the optional ``specialization`` keyword
        is present, defaults to ``False``.
    :type is_specialization: bool, optional
    :param identification: Optional relationship identification, defaults to
        ``None``.
    :type identification: :class:`pysysmlv2.syntax.ast.Identification`, optional
    :ivar typed_feature: Feature being declared as typed.
    :vartype typed_feature: :class:`pysysmlv2.syntax.ast.QualifiedReference`
    :ivar operator: Concrete typing operator.
    :vartype operator: str
    :ivar general_type: Referenced general type.
    :vartype general_type: :class:`pysysmlv2.syntax.ast.Reference`
    :ivar relationship_body: Required relationship body.
    :vartype relationship_body: :class:`pysysmlv2.syntax.ast.RelationshipBody`
    :ivar is_specialization: Whether the optional specialization keyword is present.
    :vartype is_specialization: bool
    :ivar identification: Optional relationship identification.
    :vartype identification: :class:`pysysmlv2.syntax.ast.Identification`, optional

    Example::

        >>> body = RelationshipBody(";")
        >>> str(DeclaredFeatureTyping(
        ...     QualifiedReference(["f"]),
        ...     ":",
        ...     QualifiedReference(["T"]),
        ...     body,
        ... ))
        'typing f : T;'
    """

    typed_feature: QualifiedReference
    operator: str
    general_type: Reference
    relationship_body: "RelationshipBody"
    is_specialization: bool = False
    identification: Optional[Identification] = None

    def to_sysml(self) -> str:
        """Render the declared relation in grammar-field order."""
        prefix = _join(
            [
                "specialization" if self.is_specialization else "",
                str(self.identification) if self.identification else "",
                "typing",
                str(self.typed_feature),
                self.operator,
                str(self.general_type),
            ]
        )
        return _append_body(prefix, str(self.relationship_body))

    def __str__(self) -> str:
        """Return canonical declared-feature-typing source."""
        return self.to_sysml()


@dataclass
class NonFeatureMember(FunctionBodyItem):
    """Represent a ``nonFeatureMember`` containing owned feature typing.

    The grammar-owned member prefix remains attached to this node.  Other
    non-feature alternatives receive their own typed member nodes as their
    parser mappings are introduced; they must not be converted into opaque
    source text.

    :param owned_feature_typing: Structured non-feature relationship.
    :type owned_feature_typing: :class:`pysysmlv2.syntax.ast.OwnedFeatureTyping`
    :param member_prefix: Optional visibility prefix, defaults to ``None``.
    :type member_prefix: str, optional
    :ivar owned_feature_typing: Structured non-feature relationship.
    :vartype owned_feature_typing: :class:`pysysmlv2.syntax.ast.OwnedFeatureTyping`
    :ivar member_prefix: Optional visibility prefix.
    :vartype member_prefix: str, optional

    Example::

        >>> str(NonFeatureMember(OwnedFeatureTyping(QualifiedReference(["T"]))))
        'T'
    """

    owned_feature_typing: OwnedFeatureTyping
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render the optional member prefix and owned typing relation."""
        return _join([self.member_prefix or "", str(self.owned_feature_typing)])

    def __str__(self) -> str:
        """Return canonical non-feature-member source."""
        return self.to_sysml()


@dataclass
class FeatureChain(SourceElement):
    """Represent the ordered ``featureChainMember`` qualified names.

    :param qualified_names: Qualified names separated by ``.``.
    :type qualified_names: list[pysysmlv2.syntax.ast.QualifiedReference]

    Example::

        >>> str(FeatureChain(qualified_names=[QualifiedReference(segments=["Idle"])]))
        'Idle'
    """

    qualified_names: List[QualifiedReference] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the dotted feature chain."""
        return ".".join(str(item) for item in self.qualified_names)

    def __str__(self) -> str:
        """Return canonical feature-chain text."""
        return self.to_sysml()


@dataclass
class FeatureRelationshipPart(SourceElement):
    """Base class for structured ``featureRelationshipPart`` alternatives.

    The grammar rule is a dispatcher.  Its concrete alternatives are retained
    as typed subclasses below so a feature declaration never has to expose an
    opaque relationship spelling.

    Example::

        >>> isinstance(ChainingPart(DottedQualifiedReference([QualifiedReference(["B"])])), FeatureRelationshipPart)
        True
    """


@dataclass
class TypeRelationshipPart(FeatureRelationshipPart):
    """Base class for the ``typeRelationshipPart`` alternatives."""


@dataclass
class ConjugationPart(SourceElement):
    """Represent a concrete ``conjugationPart``.

    :param operator: ``~`` or ``conjugates`` spelling.
    :type operator: str
    :param owned_conjugation: Dotted unresolved conjugated type reference.
    :type owned_conjugation: :class:`pysysmlv2.syntax.ast.DottedQualifiedReference`

    Example::

        >>> str(ConjugationPart("~", DottedQualifiedReference([QualifiedReference(["Port"])])))
        '~ Port'
    """

    operator: str
    owned_conjugation: DottedQualifiedReference

    def to_sysml(self) -> str:
        """Render the conjugation operator and its unresolved target."""
        return _join([self.operator, str(self.owned_conjugation)])

    def __str__(self) -> str:
        """Return canonical conjugation-part source."""
        return self.to_sysml()


@dataclass
class ChainingPart(FeatureRelationshipPart):
    """Represent ``chains`` and its dotted feature references.

    :param chained_features: Ordered qualified names joined by dots.
    :type chained_features: list[pysysmlv2.syntax.ast.QualifiedReference]
    """

    chained_features: List[QualifiedReference]

    def to_sysml(self) -> str:
        """Render the ``chains`` relationship."""
        return _join(["chains", ".".join(str(item) for item in self.chained_features)])

    def __str__(self) -> str:
        """Return canonical chaining-part source."""
        return self.to_sysml()


@dataclass
class InvertingPart(FeatureRelationshipPart):
    """Represent ``inverse of`` and its dotted feature reference.

    :param owned_feature_inverting: Dotted unresolved feature reference.
    :type owned_feature_inverting: :class:`pysysmlv2.syntax.ast.DottedQualifiedReference`
    """

    owned_feature_inverting: DottedQualifiedReference

    def to_sysml(self) -> str:
        """Render the ``inverse of`` relationship."""
        return _join(["inverse", "of", str(self.owned_feature_inverting)])

    def __str__(self) -> str:
        """Return canonical inverting-part source."""
        return self.to_sysml()


@dataclass
class TypeFeaturingPart(FeatureRelationshipPart):
    """Represent ``featured by`` and its owned type references.

    :param featured_types: Ordered type references after ``featured by``.
    :type featured_types: list[pysysmlv2.syntax.ast.QualifiedReference]
    """

    featured_types: List[QualifiedReference]

    def to_sysml(self) -> str:
        """Render the ``featured by`` relationship."""
        return _join(["featured by", ", ".join(str(item) for item in self.featured_types)])

    def __str__(self) -> str:
        """Return canonical type-featuring-part source."""
        return self.to_sysml()


@dataclass
class DisjoiningPart(TypeRelationshipPart):
    """Represent ``disjoint from`` and its owned type references."""

    disjoined_types: List[DottedQualifiedReference]

    def to_sysml(self) -> str:
        """Render the ``disjoint from`` relationship."""
        return _join(["disjoint from", ", ".join(str(item) for item in self.disjoined_types)])

    def __str__(self) -> str:
        """Return canonical disjoining-part source."""
        return self.to_sysml()


@dataclass
class UnioningPart(TypeRelationshipPart):
    """Represent ``unions`` and its owned type references."""

    unioned_types: List[DottedQualifiedReference]

    def to_sysml(self) -> str:
        """Render the ``unions`` relationship."""
        return _join(["unions", ", ".join(str(item) for item in self.unioned_types)])

    def __str__(self) -> str:
        """Return canonical unioning-part source."""
        return self.to_sysml()


@dataclass
class IntersectingPart(TypeRelationshipPart):
    """Represent ``intersects`` and its owned type references."""

    intersected_types: List[DottedQualifiedReference]

    def to_sysml(self) -> str:
        """Render the ``intersects`` relationship."""
        return _join(["intersects", ", ".join(str(item) for item in self.intersected_types)])

    def __str__(self) -> str:
        """Return canonical intersecting-part source."""
        return self.to_sysml()


@dataclass
class DifferencingPart(TypeRelationshipPart):
    """Represent ``differences`` and its owned type references."""

    differenced_types: List[DottedQualifiedReference]

    def to_sysml(self) -> str:
        """Render the ``differences`` relationship."""
        return _join(["differences", ", ".join(str(item) for item in self.differenced_types)])

    def __str__(self) -> str:
        """Return canonical differencing-part source."""
        return self.to_sysml()


@dataclass
class SubclassificationPart(SourceElement):
    """Represent a definition ``subclassificationPart``.

    :param operator: ``:>`` or ``specializes`` spelling.
    :type operator: str
    :param supertype_references: Ordered unresolved superclass references.
    :type supertype_references: list[pysysmlv2.syntax.ast.QualifiedReference]

    Example::

        >>> str(SubclassificationPart(operator=":>", supertype_references=[QualifiedReference(segments=["Base"])]))
        ':> Base'
    """

    operator: str
    supertype_references: List[QualifiedReference] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the subclassification operator and references."""
        return _join([self.operator, ", ".join(str(item) for item in self.supertype_references)])

    def __str__(self) -> str:
        """Return canonical subclassification text."""
        return self.to_sysml()


@dataclass
class FeatureSpecialization(SourceElement):
    """Represent one explicit feature-specialization operator.

    The full SysML specialization family is resolved later by the semantic
    layer.  Keeping the operator and references separately still preserves the
    concrete grammar alternatives without pretending that a reference is
    already linked.

    :param operator: Grammar operator such as ``:>``, ``:>>`` or ``crosses``.
    :type operator: str
    :param references: Ordered structured targets in this specialization.
    :type references: list[Union[pysysmlv2.syntax.ast.Reference,
        pysysmlv2.syntax.ast.OwnedFeatureTyping,
        pysysmlv2.syntax.ast.ConjugatedPortTyping,
        pysysmlv2.syntax.ast.DeclaredFeatureTyping]]
    """

    operator: str
    references: List[
        Union[
            Reference,
            OwnedFeatureTyping,
            ConjugatedPortTyping,
            DeclaredFeatureTyping,
        ]
    ] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render this feature-specialization alternative."""
        return _join([self.operator, ", ".join(str(item) for item in self.references)])

    def __str__(self) -> str:
        """Return canonical feature-specialization text."""
        return self.to_sysml()


@dataclass
class FeatureSpecializationPart(SourceElement):
    """Represent ordered feature specializations and optional multiplicity.

    :param specializations: Ordered grammar-level specialization alternatives.
    :type specializations: list[pysysmlv2.syntax.ast.FeatureSpecialization]
    :param multiplicity_text: Parsed multiplicity part, if present.
    :type multiplicity_text: str, optional

    ``multiplicity_text`` is deliberately limited to the multiplicity grammar
    boundary.  Its bounds are not expression text: the parser keeps the
    multiplicity production intact, while the semantic layer can later lower
    its bound expressions into the same expression nodes used elsewhere.
    """

    specializations: List[FeatureSpecialization] = field(default_factory=list)
    multiplicity_text: Optional[str] = None

    def to_sysml(self) -> str:
        """Render specializations in source order."""
        parts = [str(item) for item in self.specializations]
        if self.multiplicity_text:
            parts.append(self.multiplicity_text)
        return _join(parts)

    def __str__(self) -> str:
        """Return canonical feature-specialization-part text."""
        return self.to_sysml()


@dataclass
class DefinitionDeclaration(SourceElement):
    """Represent a definition declaration and its subclassification.

    :param identification: Optional declared identification.
    :type identification: :class:`pysysmlv2.syntax.ast.Identification`, optional
    :param subclassification: Optional explicit superclass relationship.
    :type subclassification: :class:`pysysmlv2.syntax.ast.SubclassificationPart`, optional
    """

    identification: Optional[Identification] = None
    subclassification: Optional[SubclassificationPart] = None

    def to_sysml(self) -> str:
        """Render identification followed by subclassification."""
        return _join(
            [
                str(self.identification) if self.identification else "",
                str(self.subclassification) if self.subclassification else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical definition-declaration text."""
        return self.to_sysml()


@dataclass
class UsageDeclaration(SourceElement):
    """Represent a usage identification and feature specialization.

    :param identification: Optional usage identification.
    :type identification: :class:`pysysmlv2.syntax.ast.Identification`, optional
    :param specialization: Optional explicit feature-specialization part.
    :type specialization: :class:`pysysmlv2.syntax.ast.FeatureSpecializationPart`, optional
    """

    identification: Optional[Identification] = None
    specialization: Optional[FeatureSpecializationPart] = None

    def to_sysml(self) -> str:
        """Render the usage declaration fields."""
        return _join(
            [
                str(self.identification) if self.identification else "",
                str(self.specialization) if self.specialization else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical usage-declaration text."""
        return self.to_sysml()


@dataclass
class OccurrenceDefinitionPrefix(SourceElement):
    """Represent the named fields of ``occurrenceDefinitionPrefix``.

    :param basic_definition_keyword: ``abstract`` or ``variation``.
    :type basic_definition_keyword: str, optional
    :param is_individual: Whether the ``individual`` keyword is present.
    :type is_individual: bool
    :param extension_keywords: Prefix metadata/extension spellings retained in
        source order.
    :type extension_keywords: list[str]
    """

    basic_definition_keyword: Optional[str] = None
    is_individual: bool = False
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the occurrence-definition prefix."""
        parts = []
        if self.basic_definition_keyword:
            parts.append(self.basic_definition_keyword)
        if self.is_individual:
            parts.append("individual")
        parts.extend(self.extension_keywords)
        return _join(parts)

    def __str__(self) -> str:
        """Return canonical occurrence-definition-prefix text."""
        return self.to_sysml()


@dataclass
class OccurrenceUsagePrefix(SourceElement):
    """Represent the named fields of ``occurrenceUsagePrefix``.

    :param feature_direction: ``in``, ``out`` or ``inout`` when present.
    :type feature_direction: str, optional
    :param is_derived: Whether ``derived`` is present.
    :type is_derived: bool
    :param is_abstract: Whether ``abstract`` is present.
    :type is_abstract: bool
    :param is_variation: Whether ``variation`` is present.
    :type is_variation: bool
    :param is_constant: Whether ``const`` is present.
    :type is_constant: bool
    :param is_reference: Whether ``ref`` is present.
    :type is_reference: bool
    :param is_individual: Whether ``individual`` is present.
    :type is_individual: bool
    :param portion_kind: ``snapshot`` or ``timeslice`` when present.
    :type portion_kind: str, optional
    :param extension_keywords: Usage-extension spellings in source order.
    :type extension_keywords: list[str]
    """

    feature_direction: Optional[str] = None
    is_derived: bool = False
    is_abstract: bool = False
    is_variation: bool = False
    is_constant: bool = False
    is_reference: bool = False
    is_individual: bool = False
    portion_kind: Optional[str] = None
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the occurrence-usage prefix."""
        parts = []
        if self.feature_direction:
            parts.append(self.feature_direction)
        if self.is_derived:
            parts.append("derived")
        if self.is_abstract:
            parts.append("abstract")
        if self.is_variation:
            parts.append("variation")
        if self.is_constant:
            parts.append("constant")
        if self.is_reference:
            parts.append("ref")
        if self.is_individual:
            parts.append("individual")
        if self.portion_kind:
            parts.append(self.portion_kind)
        parts.extend(self.extension_keywords)
        return _join(parts)

    def __str__(self) -> str:
        """Return canonical occurrence-usage-prefix text."""
        return self.to_sysml()


@dataclass
class DefinitionPrefix(SourceElement):
    """Represent the shared ``definitionPrefix`` grammar production.

    ``definitionPrefix`` is used by non-occurrence definitions such as
    ``attribute def`` and ``port def``.  It is kept separate from
    :class:`OccurrenceDefinitionPrefix` because the two productions own
    different keyword sets in the SysML grammar.

    :param basic_definition_keyword: Optional ``abstract`` or ``variation``
        keyword, defaults to ``None``.
    :type basic_definition_keyword: str, optional
    :param extension_keywords: Prefix metadata/extension spellings in source
        order, defaults to an empty list.
    :type extension_keywords: list[str], optional

    Example::

        >>> str(DefinitionPrefix("abstract"))
        'abstract'
    """

    basic_definition_keyword: Optional[str] = None
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the optional basic and extension prefix fields."""
        return _join([self.basic_definition_keyword or "", *self.extension_keywords])

    def __str__(self) -> str:
        """Return canonical definition-prefix text."""
        return self.to_sysml()


@dataclass
class UsagePrefix(SourceElement):
    """Represent the shared ``usagePrefix`` grammar production.

    The prefix is intentionally not collapsed into an occurrence prefix:
    generic usages such as attributes and references have a distinct grammar
    production and therefore a distinct source AST contract.

    :param feature_direction: Optional ``in``, ``out`` or ``inout`` keyword.
    :type feature_direction: str, optional
    :param is_derived: Whether ``derived`` is present, defaults to ``False``.
    :type is_derived: bool, optional
    :param is_abstract: Whether ``abstract`` is present, defaults to ``False``.
    :type is_abstract: bool, optional
    :param is_variation: Whether ``variation`` is present, defaults to
        ``False``.
    :type is_variation: bool, optional
    :param is_constant: Whether ``constant`` is present, defaults to ``False``.
    :type is_constant: bool, optional
    :param is_reference: Whether ``ref`` is present, defaults to ``False``.
    :type is_reference: bool, optional
    :param extension_keywords: Usage-extension spellings in source order,
        defaults to an empty list.
    :type extension_keywords: list[str], optional

    Example::

        >>> str(UsagePrefix(feature_direction="in"))
        'in'
    """

    feature_direction: Optional[str] = None
    is_derived: bool = False
    is_abstract: bool = False
    is_variation: bool = False
    is_constant: bool = False
    is_reference: bool = False
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render usage modifiers in their grammar-defined order."""
        parts: List[str] = []
        if self.feature_direction:
            parts.append(self.feature_direction)
        if self.is_derived:
            parts.append("derived")
        if self.is_abstract:
            parts.append("abstract")
        if self.is_variation:
            parts.append("variation")
        if self.is_constant:
            parts.append("constant")
        if self.is_reference:
            parts.append("ref")
        parts.extend(self.extension_keywords)
        return _join(parts)

    def __str__(self) -> str:
        """Return canonical usage-prefix text."""
        return self.to_sysml()


@dataclass
class ControlNodePrefix(SourceElement):
    """Represent the concrete ``controlNodePrefix`` grammar fields.

    A control node uses ``refPrefix`` rather than the broader occurrence-usage
    prefix.  Keeping this separate prevents a control node from accidentally
    acquiring a ``ref`` or other usage-only token during export.
    """

    feature_direction: Optional[str] = None
    is_derived: bool = False
    is_abstract: bool = False
    is_variation: bool = False
    is_constant: bool = False
    is_individual: bool = False
    portion_kind: Optional[str] = None
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the control-node prefix in grammar order."""
        parts: List[str] = []
        if self.feature_direction:
            parts.append(self.feature_direction)
        if self.is_derived:
            parts.append("derived")
        if self.is_abstract:
            parts.append("abstract")
        if self.is_variation:
            parts.append("variation")
        if self.is_constant:
            parts.append("constant")
        if self.is_individual:
            parts.append("individual")
        if self.portion_kind:
            parts.append(self.portion_kind)
        parts.extend(self.extension_keywords)
        return _join(parts)

    def __str__(self) -> str:
        """Return canonical control-node-prefix text."""
        return self.to_sysml()


@dataclass
class ActionNodePrefix(SourceElement):
    """Represent ``actionNodePrefix`` and its optional action declaration."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    action_node_usage_declaration: Optional["ActionNodeUsageDeclaration"] = None

    def to_sysml(self) -> str:
        """Render the occurrence prefix and optional ``action`` declaration."""
        return _join(
            [
                str(self.occurrence_usage_prefix),
                str(self.action_node_usage_declaration)
                if self.action_node_usage_declaration
                else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical action-node-prefix text."""
        return self.to_sysml()


@dataclass
class ValuePart(SourceElement):
    """Represent a ``valuePart`` operator and structured expression."""

    operator: str
    expression: Expression

    def to_sysml(self) -> str:
        """Render the value operator and expression."""
        return _join([self.operator, str(self.expression)])

    def __str__(self) -> str:
        """Return canonical value-part text."""
        return self.to_sysml()


@dataclass
class MetadataFeatureDeclaration(SourceElement):
    """Represent the declaration portion of a ``metadataFeature``.

    :param owned_feature_typing: Required metadata type or feature reference.
    :type owned_feature_typing: :class:`pysysmlv2.syntax.ast.OwnedFeatureTyping`
    :param identification: Optional metadata feature identification.
    :type identification: :class:`pysysmlv2.syntax.ast.Identification`, optional
    :param operator: Optional ``:`` or ``typed by`` spelling, defaults to ``None``.
    :type operator: str, optional

    Example::

        >>> declaration = MetadataFeatureDeclaration(
        ...     OwnedFeatureTyping(DottedQualifiedReference([QualifiedReference(["Tool"])])),
        ... )
        >>> str(declaration)
        'Tool'
    """

    owned_feature_typing: OwnedFeatureTyping
    identification: Optional[Identification] = None
    operator: Optional[str] = None

    def to_sysml(self) -> str:
        """Render identification, optional typing operator, and owned typing."""
        return _join(
            [
                str(self.identification) if self.identification else "",
                self.operator or "",
                str(self.owned_feature_typing),
            ]
        )

    def __str__(self) -> str:
        """Return canonical metadata-feature-declaration text."""
        return self.to_sysml()


@dataclass
class MetadataBody(SourceElement):
    """Represent a metadata body and its ordered typed members.

    :param declaration_only: Whether the grammar selected the terminating
        semicolon form, defaults to ``False``.
    :type declaration_only: bool, optional
    :param items: Ordered metadata body members.
    :type items: list[pysysmlv2.syntax.ast.SourceElement]

    Example::

        >>> str(MetadataBody(declaration_only=True))
        ';'
    """

    declaration_only: bool = False
    items: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the metadata body's semicolon or brace form."""
        return _render_block(self.items, declaration_only=self.declaration_only)

    def __str__(self) -> str:
        """Return canonical metadata-body text."""
        return self.to_sysml()


@dataclass
class MetadataBodyFeature(SourceElement):
    """Represent one metadata body feature and its optional value/body.

    :param owned_redefinition: Required feature name being declared or
        redefined.
    :type owned_redefinition: :class:`pysysmlv2.syntax.ast.Reference`
    :param body: Required nested metadata body.
    :type body: :class:`pysysmlv2.syntax.ast.MetadataBody`
    :param is_feature: Whether the optional ``feature`` keyword is present,
        defaults to ``False``.
    :type is_feature: bool, optional
    :param redefinition_operator: Optional ``:>>`` or ``redefines`` spelling.
    :type redefinition_operator: str, optional
    :param feature_specialization_part: Optional specialization fields.
    :type feature_specialization_part: :class:`pysysmlv2.syntax.ast.FeatureSpecializationPart`, optional
    :param value_part: Optional value assignment.
    :type value_part: :class:`pysysmlv2.syntax.ast.ValuePart`, optional

    Example::

        >>> feature = MetadataBodyFeature(
        ...     QualifiedReference(["toolName"]),
        ...     MetadataBody(declaration_only=True),
        ...     value_part=ValuePart("=", StringLiteral('"x"')),
        ... )
        >>> str(feature)
        'toolName = "x";'
    """

    owned_redefinition: Reference
    body: MetadataBody
    is_feature: bool = False
    redefinition_operator: Optional[str] = None
    feature_specialization_part: Optional[FeatureSpecializationPart] = None
    value_part: Optional[ValuePart] = None

    def to_sysml(self) -> str:
        """Render keyword, redefinition, specialization, value, and body."""
        return _append_body(
            _join(
                [
                    "feature" if self.is_feature else "",
                    self.redefinition_operator or "",
                    str(self.owned_redefinition),
                    str(self.feature_specialization_part)
                    if self.feature_specialization_part
                    else "",
                    str(self.value_part) if self.value_part else "",
                ]
            ),
            str(self.body),
        )

    def __str__(self) -> str:
        """Return canonical metadata-body-feature text."""
        return self.to_sysml()


@dataclass
class MetadataBodyUsage(SourceElement):
    """Represent one metadata body usage and its optional value/body.

    :param owned_redefinition: Required referenced metadata feature name.
    :type owned_redefinition: :class:`pysysmlv2.syntax.ast.Reference`
    :param body: Required nested metadata body.
    :type body: :class:`pysysmlv2.syntax.ast.MetadataBody`
    :param is_ref: Whether the optional ``ref`` keyword is present, defaults
        to ``False``.
    :type is_ref: bool, optional
    :param redefinition_operator: Optional ``:>>`` or ``redefines`` spelling.
    :type redefinition_operator: str, optional
    :param feature_specialization_part: Optional specialization fields.
    :type feature_specialization_part: :class:`pysysmlv2.syntax.ast.FeatureSpecializationPart`, optional
    :param value_part: Optional value assignment.
    :type value_part: :class:`pysysmlv2.syntax.ast.ValuePart`, optional

    Example::

        >>> usage = MetadataBodyUsage(
        ...     QualifiedReference(["toolName"]),
        ...     MetadataBody(declaration_only=True),
        ...     is_ref=True,
        ... )
        >>> str(usage)
        'ref toolName;'
    """

    owned_redefinition: Reference
    body: MetadataBody
    is_ref: bool = False
    redefinition_operator: Optional[str] = None
    feature_specialization_part: Optional[FeatureSpecializationPart] = None
    value_part: Optional[ValuePart] = None

    def to_sysml(self) -> str:
        """Render reference marker, redefinition, value, and nested body."""
        return _append_body(
            _join(
                [
                    "ref" if self.is_ref else "",
                    self.redefinition_operator or "",
                    str(self.owned_redefinition),
                    str(self.feature_specialization_part)
                    if self.feature_specialization_part
                    else "",
                    str(self.value_part) if self.value_part else "",
                ]
            ),
            str(self.body),
        )

    def __str__(self) -> str:
        """Return canonical metadata-body-usage text."""
        return self.to_sysml()


@dataclass
class MetadataFeature(SourceElement):
    """Represent a model-owned ``metadata`` or ``@`` annotation.

    :param declaration: Required metadata feature declaration.
    :type declaration: :class:`pysysmlv2.syntax.ast.MetadataFeatureDeclaration`
    :param body: Required metadata body.
    :type body: :class:`pysysmlv2.syntax.ast.MetadataBody`
    :param keyword: Concrete ``metadata`` or ``@`` marker.
    :type keyword: str
    :param about: Ordered annotation targets after optional ``about``.
    :type about: list[pysysmlv2.syntax.ast.QualifiedReference]
    :param prefix_metadata: Ordered ``#`` metadata prefixes, defaults to an
        empty list.
    :type prefix_metadata: list[pysysmlv2.syntax.ast.OwnedFeatureTyping], optional

    Example::

        >>> node = MetadataFeature(
        ...     MetadataFeatureDeclaration(
        ...         OwnedFeatureTyping(DottedQualifiedReference([QualifiedReference(["Tool"])]))
        ...     ),
        ...     MetadataBody(declaration_only=True),
        ...     keyword="metadata",
        ... )
        >>> str(node)
        'metadata Tool;'
    """

    declaration: MetadataFeatureDeclaration
    body: MetadataBody
    keyword: str
    about: List[QualifiedReference] = field(default_factory=list)
    prefix_metadata: List[OwnedFeatureTyping] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render prefixes, marker, declaration, targets, and body."""
        about = ""
        if self.about:
            about = "about " + ", ".join(str(item) for item in self.about)
        prefix = _join(
            [
                *[("#" + str(item)) for item in self.prefix_metadata],
                self.keyword,
                str(self.declaration),
                about,
            ]
        )
        return _append_body(prefix, str(self.body))

    def __str__(self) -> str:
        """Return canonical metadata-feature text."""
        return self.to_sysml()


@dataclass
class BooleanLiteral(Expression):
    """Represent the ``literalBoolean`` parser alternative."""

    raw_lexeme: str

    def to_sysml(self) -> str:
        """Render the boolean token spelling."""
        return self.raw_lexeme

    def __str__(self) -> str:
        """Return canonical boolean-literal text."""
        return self.to_sysml()


@dataclass
class StringLiteral(Expression):
    """Represent the ``literalString`` parser alternative."""

    raw_lexeme: str

    def to_sysml(self) -> str:
        """Render the quoted string token spelling."""
        return self.raw_lexeme

    def __str__(self) -> str:
        """Return canonical string-literal text."""
        return self.to_sysml()


@dataclass
class IntegerLiteral(Expression):
    """Represent the ``literalInteger`` parser alternative."""

    raw_lexeme: str

    def to_sysml(self) -> str:
        """Render the integer token spelling."""
        return self.raw_lexeme

    def __str__(self) -> str:
        """Return canonical integer-literal text."""
        return self.to_sysml()


@dataclass
class RealLiteral(Expression):
    """Represent the ``literalReal`` parser alternative."""

    raw_lexeme: str

    def to_sysml(self) -> str:
        """Render the real-number token spelling."""
        return self.raw_lexeme

    def __str__(self) -> str:
        """Return canonical real-literal text."""
        return self.to_sysml()


@dataclass
class InfinityLiteral(Expression):
    """Represent the ``literalInfinity`` ``*`` alternative."""

    def to_sysml(self) -> str:
        """Render the infinity token."""
        return "*"

    def __str__(self) -> str:
        """Return canonical infinity-literal text."""
        return self.to_sysml()


@dataclass
class NullExpression(Expression):
    """Represent the ``nullExpression`` alternative."""

    parenthesized: bool = False

    def to_sysml(self) -> str:
        """Render ``null`` or the empty ``()`` form."""
        return "()" if self.parenthesized else "null"

    def __str__(self) -> str:
        """Return canonical null-expression text."""
        return self.to_sysml()


@dataclass
class FeatureReferenceExpression(Expression):
    """Represent a ``featureReferenceExpression`` qualified name."""

    reference: QualifiedReference

    def to_sysml(self) -> str:
        """Render the unresolved feature reference."""
        return str(self.reference)

    def __str__(self) -> str:
        """Return canonical feature-reference text."""
        return self.to_sysml()


@dataclass
class UnaryExpression(Expression):
    """Represent a prefix unary ``ownedExpression`` alternative."""

    operator: str
    operand: Expression

    def to_sysml(self) -> str:
        """Render the unary operator and operand."""
        return self.operator + str(self.operand)

    def __str__(self) -> str:
        """Return canonical unary-expression text."""
        return self.to_sysml()


@dataclass
class BinaryExpression(Expression):
    """Represent a binary ``ownedExpression`` operator and two operands."""

    left: Expression
    operator: str
    right: Expression

    def to_sysml(self) -> str:
        """Render the binary expression with explicit operand grouping."""
        precedence = _BINARY_PRECEDENCE.get(self.operator, 1)
        return "{} {} {}".format(
            _render_expression_child(self.left, precedence, self.operator, "left"),
            self.operator,
            _render_expression_child(self.right, precedence, self.operator, "right"),
        ).strip()

    def __str__(self) -> str:
        """Return canonical binary-expression text."""
        return self.to_sysml()


@dataclass
class CoalesceExpression(Expression):
    """Represent the dedicated ``ownedExpression ?? ownedExpression`` rule."""

    left: Expression
    right: Expression

    def to_sysml(self) -> str:
        """Render the null-coalescing operands."""
        return "{} ?? {}".format(
            _render_expression_child(self.left, _BINARY_PRECEDENCE["??"], "??", "left"),
            _render_expression_child(self.right, _BINARY_PRECEDENCE["??"], "??", "right"),
        ).strip()

    def __str__(self) -> str:
        """Return canonical coalescing-expression text."""
        return self.to_sysml()


@dataclass
class ConditionalExpression(Expression):
    """Represent ``if condition ? then_expression else else_expression``."""

    condition: Expression
    then_expression: Expression
    else_expression: Expression

    def to_sysml(self) -> str:
        """Render all three conditional operands."""
        return "if {} ? {} else {}".format(
            _render_expression_child(self.condition, 1, "if", "left"),
            _render_expression_child(self.then_expression, 1, "if", "right"),
            _render_expression_child(self.else_expression, 1, "if", "right"),
        )

    def __str__(self) -> str:
        """Return canonical conditional-expression text."""
        return self.to_sysml()


@dataclass
class TypeOperationExpression(Expression):
    """Represent a prefix or infix type operation.

    :param operator: ``@``, ``@@``, ``istype``, ``hastype`` or ``meta``.
    :type operator: str
    :param type_reference: Unresolved type reference.
    :type type_reference: :class:`pysysmlv2.syntax.ast.QualifiedReference`
    :param operand: Infix operand; ``None`` for prefix operations.
    :type operand: :class:`pysysmlv2.syntax.ast.Expression`, optional
    """

    operator: str
    type_reference: QualifiedReference
    operand: Optional[Expression] = None

    def to_sysml(self) -> str:
        """Render the prefix/infix type operation."""
        if self.operand is None:
            return "{}{}".format(self.operator, self.type_reference)
        return "{} {} {}".format(self.operand, self.operator, self.type_reference)

    def __str__(self) -> str:
        """Return canonical type-operation text."""
        return self.to_sysml()


@dataclass
class CastExpression(Expression):
    """Represent the ``ownedExpression AS typeReference`` alternative."""

    operand: Expression
    type_reference: QualifiedReference

    def to_sysml(self) -> str:
        """Render the cast expression."""
        return "{} as {}".format(self.operand, self.type_reference).strip()

    def __str__(self) -> str:
        """Return canonical cast-expression text."""
        return self.to_sysml()


@dataclass
class SequenceExpression(Expression):
    """Represent an expression sequence inside brackets or parentheses."""

    elements: List[Expression] = field(default_factory=list)
    delimiter: str = ", "

    def to_sysml(self) -> str:
        """Render the ordered expression elements."""
        return self.delimiter.join(str(item) for item in self.elements)

    def __str__(self) -> str:
        """Return canonical sequence-expression text."""
        return self.to_sysml()


@dataclass
class ParenthesizedExpression(Expression):
    """Preserve explicit grouping from ``( sequenceExpressionList? )``."""

    sequence: Optional[SequenceExpression] = None

    def to_sysml(self) -> str:
        """Render the parenthesized sequence, including empty ``()``."""
        return "(" + (str(self.sequence) if self.sequence else "") + ")"

    def __str__(self) -> str:
        """Return canonical parenthesized-expression text."""
        return self.to_sysml()


@dataclass
class NamedArgument(SourceElement):
    """Represent one ``qualifiedName = ownedExpression`` argument."""

    name: QualifiedReference
    expression: Expression

    def to_sysml(self) -> str:
        """Render the named argument."""
        return "{} = {}".format(self.name, self.expression).strip()

    def __str__(self) -> str:
        """Return canonical named-argument text."""
        return self.to_sysml()


@dataclass
class ArgumentList(SourceElement):
    """Represent positional/named arguments between parentheses."""

    positional_arguments: List[Expression] = field(default_factory=list)
    named_arguments: List[NamedArgument] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the argument list including delimiters."""
        values = [str(item) for item in self.positional_arguments]
        values.extend(str(item) for item in self.named_arguments)
        return "(" + ", ".join(values) + ")"

    def __str__(self) -> str:
        """Return canonical argument-list text."""
        return self.to_sysml()


@dataclass
class InvocationExpression(Expression):
    """Represent ``ownedExpression argumentList`` invocation."""

    target: Expression
    arguments: ArgumentList

    def to_sysml(self) -> str:
        """Render the invocation target and arguments."""
        return str(self.target) + str(self.arguments)

    def __str__(self) -> str:
        """Return canonical invocation-expression text."""
        return self.to_sysml()


@dataclass
class IndexExpression(Expression):
    """Represent the OMG ``IndexExpression`` ``ownedExpression#(...)`` form.

    :param target: Expression receiving the hash invocation.
    :type target: :class:`pysysmlv2.syntax.ast.Expression`
    :param arguments: Parenthesized argument sequence.
    :type arguments: :class:`pysysmlv2.syntax.ast.ArgumentList`

    Example::

        >>> str(IndexExpression(BooleanLiteral("x"), ArgumentList()))
        'x#()'
    """

    target: Expression
    arguments: ArgumentList

    def to_sysml(self) -> str:
        """Render the hash index operator without losing its token."""
        return "{}#{}".format(self.target, self.arguments)

    def __str__(self) -> str:
        """Return canonical index-expression text."""
        return self.to_sysml()


@dataclass
class BracketExpression(Expression):
    """Represent the OMG ``BracketExpression`` ``ownedExpression[...]`` form."""

    target: Expression
    indices: Optional[SequenceExpression] = None

    def to_sysml(self) -> str:
        """Render target and bracketed expression sequence."""
        return "{}[{}]".format(
            str(self.target),
            str(self.indices) if self.indices else "",
        )

    def __str__(self) -> str:
        """Return canonical bracket-expression text."""
        return self.to_sysml()


@dataclass
class FeatureChainExpression(Expression):
    """Represent the OMG ``FeatureChainExpression`` dotted member form."""

    target: Expression
    member: QualifiedReference

    def to_sysml(self) -> str:
        """Render dotted feature-chain access."""
        return "{}.{}".format(self.target, self.member)

    def __str__(self) -> str:
        """Return canonical feature-chain-expression text."""
        return self.to_sysml()


@dataclass
class SelectExpression(Expression):
    """Represent the OMG ``SelectExpression`` ``ownedExpression.?{...}`` form."""

    target: Expression
    body_expression: BodyExpression

    def to_sysml(self) -> str:
        """Render selection access to a body expression."""
        return "{}.?{}".format(
            self.target,
            self.body_expression,
        )

    def __str__(self) -> str:
        """Return canonical select-expression text."""
        return self.to_sysml()


@dataclass
class FunctionOperationExpression(Expression):
    """Represent the OMG ``FunctionOperationExpression`` arrow form.

    :param target: Expression on the left of the arrow.
    :type target: :class:`pysysmlv2.syntax.ast.Expression`
    :param member: Referenced function on the right of the arrow.
    :type member: :class:`pysysmlv2.syntax.ast.QualifiedReference`
    :param result: A body expression or parenthesized argument list.
    :type result: :class:`pysysmlv2.syntax.ast.BodyExpression` or :class:`pysysmlv2.syntax.ast.ArgumentList`

    Example::

        >>> str(FunctionOperationExpression(
        ...     FeatureReferenceExpression(QualifiedReference(["x"])),
        ...     QualifiedReference(["collect"]),
        ...     ArgumentList(positional_arguments=[IntegerLiteral("1")]),
        ... ))
        'x -> collect(1)'
    """

    target: Expression
    member: QualifiedReference
    result: Union[BodyExpression, ArgumentList]

    def to_sysml(self) -> str:
        """Render arrow target, function reference, and result node."""
        separator = " " if isinstance(self.result, BodyExpression) else ""
        return "{} -> {}{}{}".format(
            self.target,
            self.member,
            separator,
            self.result,
        )

    def __str__(self) -> str:
        """Return canonical function-operation-expression text."""
        return self.to_sysml()


@dataclass
class ConstructorExpression(Expression):
    """Represent ``new qualifiedName argumentList``."""

    type_reference: QualifiedReference
    arguments: ArgumentList

    def to_sysml(self) -> str:
        """Render constructor keyword, type, and arguments."""
        return "new {}{}".format(self.type_reference, self.arguments)

    def __str__(self) -> str:
        """Return canonical constructor-expression text."""
        return self.to_sysml()


@dataclass
class MetadataAccessExpression(Expression):
    """Represent ``qualifiedName . metadata`` access."""

    target: QualifiedReference

    def to_sysml(self) -> str:
        """Render metadata access."""
        return str(self.target) + ".metadata"

    def __str__(self) -> str:
        """Return canonical metadata-access text."""
        return self.to_sysml()


@dataclass
class MetadataCastExpression(Expression):
    """Represent the concrete ``(as MetadataType)`` expression."""

    type_reference: QualifiedReference

    def to_sysml(self) -> str:
        """Render metadata-cast syntax."""
        return "(as {})".format(self.type_reference)

    def __str__(self) -> str:
        """Return canonical metadata-cast text."""
        return self.to_sysml()


@dataclass
class AllExpression(Expression):
    """Represent ``all typeReference``."""

    type_reference: QualifiedReference

    def to_sysml(self) -> str:
        """Render the ``all`` expression."""
        return "all " + str(self.type_reference)

    def __str__(self) -> str:
        """Return canonical all-expression text."""
        return self.to_sysml()


@dataclass
class BodyExpression(Expression):
    """Represent a brace-delimited expression body.

    :param items: Parsed function-body items in source order.
    :type items: list[pysysmlv2.syntax.ast.FunctionBodyItem]
    """

    items: List[FunctionBodyItem] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the body expression and its statement items."""
        return _render_block(self.items, declaration_only=False)

    def __str__(self) -> str:
        """Return canonical body-expression text."""
        return self.to_sysml()


@dataclass
class ResultExpressionMember(FunctionBodyItem):
    """Represent a function-body result expression and its visibility prefix.

    :param expression: Structured expression owned by the result member.
    :type expression: :class:`pysysmlv2.syntax.ast.Expression`
    :param member_prefix: Optional visibility spelling, defaults to ``None``.
    :type member_prefix: str, optional

    Example::

        >>> str(ResultExpressionMember(BooleanLiteral("true")))
        'true'
    """

    expression: Expression
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render the optional prefix and result expression."""
        return _join([self.member_prefix or "", str(self.expression)])

    def __str__(self) -> str:
        """Return canonical result-expression-member text."""
        return self.to_sysml()


@dataclass
class ReturnFeatureMember(FunctionBodyItem):
    """Represent a ``return`` feature retained in a function body.

    The returned feature is preserved by the explicit source-syntax bridge
    while the generic feature family is introduced. Keeping the ``return``
    relationship as its own AST node preserves its keyword and member-prefix
    ownership without treating the enclosing function body as text.

    :param feature_element: Lossless feature element owned by ``return``.
    :type feature_element: :class:`pysysmlv2.syntax.ast.RawElement`
    :param member_prefix: Optional member visibility, defaults to ``None``.
    :type member_prefix: str, optional

    Example::

        >>> str(ReturnFeatureMember(RawElement(": Boolean;")))
        'return : Boolean;'
    """

    feature_element: "RawElement"
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render the return keyword and its owned feature element."""
        return _join([self.member_prefix or "", "return", str(self.feature_element)])

    def __str__(self) -> str:
        """Return canonical return-feature-member text."""
        return self.to_sysml()


@dataclass
class ReturnParameterMember(SourceElement):
    """Represent a calculation/case ``return`` parameter member."""

    usage_element: SourceElement
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility, ``return``, and the nested usage element."""
        return _join([self.member_prefix or "", "return", str(self.usage_element)])

    def __str__(self) -> str:
        """Return canonical return-parameter-member text."""
        return self.to_sysml()


@dataclass
class CommentExpression(Expression):
    """Represent a parser-accepted regular comment expression placeholder."""

    comment_text: str

    def to_sysml(self) -> str:
        """Render the comment lexeme."""
        return self.comment_text

    def __str__(self) -> str:
        """Return canonical comment-expression text."""
        return self.to_sysml()


@dataclass
class RawElement(FunctionBodyItem):
    """Preserve an unsupported grammar fragment losslessly.

    This exported class is a deliberately narrow syntax compatibility
    boundary for deferred productions and parser-recovery fragments that have
    not yet received a handwritten node.  It may occur in a function body
    because that grammar admits type-body members, but it is never a semantic
    model element and must not be used for expressions, state bodies,
    transitions, or action statements.  The only retained value is the
    explicitly parseable source fragment itself; downstream code must
    recognize this type and reject or account for it rather than silently
    treating it as typed syntax.

    :param source_text: Parseable source fragment for the unsupported element.
    :type source_text: str
    :param member_prefix: Optional visibility/member prefix.
    :type member_prefix: str
    """

    source_text: str
    member_prefix: str = ""

    def to_sysml(self) -> str:
        """Render the retained source fragment."""
        return _join([self.member_prefix, _relative_source(self.source_text)])

    def __str__(self) -> str:
        """Return the retained parseable fragment."""
        return self.to_sysml()


@dataclass
class DefinitionBodyItem(FunctionBodyItem):
    """Represent one generic ``definitionBodyItem`` with owned prefixes.

    The wrapper is retained because ``memberPrefix`` and an optional source
    succession belong to this production rather than to the nested usage or
    definition.  It is therefore meaningful source structure, unlike a
    one-child dispatcher.
    """

    element: SourceElement
    member_prefix: Optional[str] = None
    source_succession: Optional["SourceSuccession"] = None

    def to_sysml(self) -> str:
        """Render succession, visibility, and the nested body element."""
        return _join(
            [
                str(self.source_succession) if self.source_succession else "",
                self.member_prefix or "",
                str(self.element),
            ]
        )

    def __str__(self) -> str:
        """Return canonical definition-body-item text."""
        return self.to_sysml()


@dataclass
class VariantUsage(SourceElement):
    """Represent the ``variant`` keyword and its selected usage element.

    ``variantUsageElement`` accepts multiple structure and behavior families.
    The wrapper is retained because the variant relationship is concrete source
    syntax and future semantic linking must distinguish it from an ordinary
    nested usage.

    :param element: Concrete usage selected by the variant declaration.
    :type element: :class:`pysysmlv2.syntax.ast.SourceElement`
    :ivar element: Concrete usage selected by the variant declaration.
    :vartype element: :class:`pysysmlv2.syntax.ast.SourceElement`

    Example::

        >>> str(VariantUsage(RawElement("part Variant;")))
        'variant part Variant;'
    """

    element: SourceElement

    def to_sysml(self) -> str:
        """Render the variant keyword followed by its selected usage."""
        return _join(["variant", str(self.element)])

    def __str__(self) -> str:
        """Return canonical variant-usage text."""
        return self.to_sysml()


@dataclass
class DefinitionBody(SourceElement):
    """Represent a generic ``definitionBody`` with ordered child elements."""

    declaration_only: bool = False
    items: List[DefinitionBodyItem] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the generic definition body."""
        return _render_block(self.items, declaration_only=self.declaration_only)

    def __str__(self) -> str:
        """Return canonical definition-body text."""
        return self.to_sysml()


@dataclass
class Definition(SourceElement):
    """Represent the reusable ``definition`` production."""

    declaration: DefinitionDeclaration
    body: DefinitionBody

    def to_sysml(self) -> str:
        """Render the declaration and generic definition body."""
        return _append_body(str(self.declaration), str(self.body))

    def __str__(self) -> str:
        """Return canonical definition text."""
        return self.to_sysml()


@dataclass
class Usage(SourceElement):
    """Represent the reusable ``usage`` production.

    ``usage`` is intentionally distinct from :class:`ActionUsageDeclaration`:
    it owns the completion body and is used by generic part/feature usages.
    """

    body: DefinitionBody
    declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None

    def to_sysml(self) -> str:
        """Render usage declaration, value, and completion body."""
        return _append_body(
            _join(
                [
                    str(self.declaration) if self.declaration else "",
                    str(self.value_part) if self.value_part else "",
                ]
            ),
            str(self.body),
        )

    def __str__(self) -> str:
        """Return canonical usage text."""
        return self.to_sysml()


class _OccurrenceDefinitionWithDefinition(SourceElement):
    """Render occurrence definitions whose body is the shared ``definition``."""

    keyword: ClassVar[str]

    def to_sysml(self) -> str:
        """Render the explicit occurrence prefix, keyword, and definition."""
        return _append_body(
            _join([str(self.occurrence_definition_prefix), self.keyword, "def"]),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical occurrence-definition text."""
        return self.to_sysml()


class _OccurrenceDefinitionWithBody(SourceElement):
    """Render occurrence definitions with a dedicated grammar body."""

    keyword: ClassVar[str]

    def to_sysml(self) -> str:
        """Render the explicit occurrence prefix, declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.occurrence_definition_prefix),
                    self.keyword,
                    "def",
                    str(self.definition_declaration),
                ]
            ),
            str(self.body),
        )

    def __str__(self) -> str:
        """Return canonical occurrence-definition text."""
        return self.to_sysml()


class _UsageWithBody(SourceElement):
    """Render occurrence usages with a dedicated grammar body."""

    keyword: ClassVar[str]

    def to_sysml(self) -> str:
        """Render the explicit occurrence prefix, declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.occurrence_usage_prefix),
                    self.keyword,
                    str(self.declaration),
                ]
            ),
            str(self.body),
        )

    def __str__(self) -> str:
        """Return canonical occurrence-usage text."""
        return self.to_sysml()


class _UsageWithDefinitionBody(SourceElement):
    """Render occurrence usages backed by the shared ``definitionBody``."""

    keyword: ClassVar[str]

    def to_sysml(self) -> str:
        """Render the explicit prefix, declaration, and generic body."""
        return _append_body(
            _join(
                [
                    str(self.occurrence_usage_prefix),
                    self.keyword,
                    str(self.declaration),
                ]
            ),
            str(self.body),
        )

    def __str__(self) -> str:
        """Return canonical occurrence-usage text."""
        return self.to_sysml()


@dataclass
class Dependency(SourceElement):
    """Represent a concrete ``dependency`` relationship."""

    source_references: List[QualifiedReference]
    target_references: List[QualifiedReference]
    relationship_body: RelationshipBody
    identification: Optional[Identification] = None
    prefix_metadata: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render dependency identification, endpoints, and body."""
        declaration = _join(
            [
                str(self.identification) if self.identification else "",
                "from" if self.identification else "",
                ", ".join(str(item) for item in self.source_references),
                "to",
                ", ".join(str(item) for item in self.target_references),
            ]
        )
        return _append_body(
            _join([*self.prefix_metadata, "dependency", declaration]),
            str(self.relationship_body),
        )

    def __str__(self) -> str:
        """Return canonical dependency text."""
        return self.to_sysml()


@dataclass
class EnumerationDefinition(SourceElement):
    """Represent an ``enum def`` with its declaration and body."""

    definition_declaration: DefinitionDeclaration
    enumeration_body: "EnumerationBody"
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render extension metadata, declaration, and enumeration body."""
        return _append_body(
            _join([*self.extension_keywords, "enum def", str(self.definition_declaration)]),
            str(self.enumeration_body),
        )

    def __str__(self) -> str:
        """Return canonical enumeration-definition text."""
        return self.to_sysml()


@dataclass
class AllocationDefinition(_OccurrenceDefinitionWithDefinition):
    """Represent an ``allocation def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition: Definition
    keyword: ClassVar[str] = "allocation"


@dataclass
class FlowDefinition(_OccurrenceDefinitionWithDefinition):
    """Represent a ``flow def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition: Definition
    keyword: ClassVar[str] = "flow"


@dataclass
class RenderingDefinition(_OccurrenceDefinitionWithDefinition):
    """Represent a ``rendering def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition: Definition
    keyword: ClassVar[str] = "rendering"


@dataclass
class MetadataDefinition(SourceElement):
    """Represent a ``metadata def``."""

    definition: Definition
    is_abstract: bool = False
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the metadata prefix, keyword, and shared definition."""
        return _append_body(
            _join(
                [
                    "abstract" if self.is_abstract else "",
                    *self.extension_keywords,
                    "metadata def",
                ]
            ),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical metadata-definition text."""
        return self.to_sysml()


@dataclass
class ExtendedDefinition(_OccurrenceDefinitionWithDefinition):
    """Represent an extension-keyword ``... def`` production."""

    definition_prefix: DefinitionPrefix
    definition: Definition
    keyword: ClassVar[str] = ""

    def to_sysml(self) -> str:
        """Render the basic/extension prefix followed by ``def``."""
        return _append_body(
            _join([str(self.definition_prefix), "def"]),
            str(self.definition),
        )


@dataclass
class PartDefinition(SourceElement):
    """Represent a ``part def`` backed by a structured definition body."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition: Definition

    def to_sysml(self) -> str:
        """Render part-definition prefix, keyword, and nested definition."""
        return _append_body(
            _join([str(self.occurrence_definition_prefix), "part def"]),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical part-definition text."""
        return self.to_sysml()


@dataclass
class OccurrenceDefinition(SourceElement):
    """Represent an ``occurrence def`` with its concrete prefix and body.

    The occurrence family is distinct from ``part`` and ``item`` even though
    all three use the same definition completion.  Keeping the keyword in a
    dedicated node prevents the generic dispatcher from losing the semantic
    distinction needed by later workspace extraction.
    """

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition: Definition

    def to_sysml(self) -> str:
        """Render the occurrence-definition prefix and definition."""
        return _append_body(
            _join([str(self.occurrence_definition_prefix), "occurrence def"]),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical occurrence-definition text."""
        return self.to_sysml()


@dataclass
class IndividualDefinition(SourceElement):
    """Represent the separate ``individual ... def`` grammar alternative."""

    basic_definition_keyword: Optional[str]
    extension_keywords: List[str]
    definition: Definition

    def to_sysml(self) -> str:
        """Render the individual-definition prefix and completion."""
        return _append_body(
            _join(
                [
                    self.basic_definition_keyword or "",
                    "individual",
                    *self.extension_keywords,
                    "def",
                ]
            ),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical individual-definition text."""
        return self.to_sysml()


@dataclass
class PartUsage(SourceElement):
    """Represent a ``part`` usage backed by a structured usage body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render part-usage prefix, keyword, and nested usage."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), "part"]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical part-usage text."""
        return self.to_sysml()


@dataclass
class ItemUsage(SourceElement):
    """Represent a structured ``item`` usage.

    ``itemUsage`` is distinct from :class:`PartUsage` because its concrete
    keyword is meaningful for later semantic mapping, while it shares the
    common occurrence prefix and generic usage completion structure.

    :param occurrence_usage_prefix: Concrete occurrence-usage modifiers.
    :type occurrence_usage_prefix: :class:`pysysmlv2.syntax.ast.OccurrenceUsagePrefix`
    :param usage: Shared structured usage declaration and completion.
    :type usage: :class:`pysysmlv2.syntax.ast.Usage`
    :ivar occurrence_usage_prefix: Concrete occurrence-usage modifiers.
    :vartype occurrence_usage_prefix: :class:`pysysmlv2.syntax.ast.OccurrenceUsagePrefix`
    :ivar usage: Shared structured usage declaration and completion.
    :vartype usage: :class:`pysysmlv2.syntax.ast.Usage`

    Example::

        >>> str(ItemUsage(OccurrenceUsagePrefix(), Usage(DefinitionBody(True))))
        'item;'
    """

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render occurrence modifiers, ``item``, and the usage completion."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), "item"]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical item-usage text."""
        return self.to_sysml()


@dataclass
class OccurrenceUsage(SourceElement):
    """Represent an ``occurrence`` usage and its completion."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render occurrence modifiers, keyword, and usage completion."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), "occurrence"]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical occurrence-usage text."""
        return self.to_sysml()


@dataclass
class IndividualUsage(SourceElement):
    """Represent the ``individual`` usage alternative."""

    basic_usage_prefix: UsagePrefix
    usage: Usage
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the individual usage prefix and completion."""
        return _append_body(
            _join([str(self.basic_usage_prefix), "individual", *self.extension_keywords]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical individual-usage text."""
        return self.to_sysml()


@dataclass
class PortionUsage(SourceElement):
    """Represent a ``snapshot`` or ``timeslice`` usage alternative."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render the portion prefix and usage completion."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix)]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical portion-usage text."""
        return self.to_sysml()


@dataclass
class EventOccurrenceUsage(SourceElement):
    """Represent either concrete ``event`` occurrence grammar alternative.

    Exactly one of ``owned_reference_subsetting`` or ``occurrence`` is
    normally populated.  The parser keeps both fields explicit so semantic
    linking can distinguish the shorthand ``event occ1`` from the named
    ``event occurrence evt`` form without reparsing source text.
    """

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage: Usage
    owned_reference_subsetting: Optional[Reference] = None
    feature_specialization_part: Optional[FeatureSpecializationPart] = None
    occurrence: bool = False
    usage_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render the selected event-occurrence alternative."""
        if self.owned_reference_subsetting is not None:
            head = _join(
                [
                    str(self.occurrence_usage_prefix),
                    "event",
                    str(self.owned_reference_subsetting),
                    str(self.feature_specialization_part)
                    if self.feature_specialization_part
                    else "",
                ]
            )
        else:
            head = _join(
                [
                    str(self.occurrence_usage_prefix),
                    "event",
                    "occurrence" if self.occurrence else "",
                    str(self.usage_declaration) if self.usage_declaration else "",
                ]
            )
        completion = str(self.usage)
        if completion.startswith(";"):
            return head + completion
        if completion.startswith("{"):
            return head + " " + completion
        return _join([head, completion])

    def __str__(self) -> str:
        """Return canonical event-occurrence-usage text."""
        return self.to_sysml()


@dataclass
class ItemDefinition(SourceElement):
    """Represent an ``item def`` with its explicit definition fields.

    :param occurrence_definition_prefix: Modifiers owned by the occurrence
        definition prefix.
    :type occurrence_definition_prefix: :class:`pysysmlv2.syntax.ast.OccurrenceDefinitionPrefix`
    :param definition: Identification, specialization, and body owned by the
        shared ``definition`` production.
    :type definition: :class:`pysysmlv2.syntax.ast.Definition`

    Example::

        >>> str(ItemDefinition(OccurrenceDefinitionPrefix(), Definition(DefinitionDeclaration(), DefinitionBody(True))))
        'item def;'
    """

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition: Definition

    def to_sysml(self) -> str:
        """Render occurrence modifiers, ``item def``, and the definition."""
        return _append_body(
            _join([str(self.occurrence_definition_prefix), "item def"]),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical item-definition text."""
        return self.to_sysml()


@dataclass
class AttributeDefinition(SourceElement):
    """Represent an ``attribute def`` with explicit prefix and definition."""

    definition_prefix: DefinitionPrefix
    definition: Definition

    def to_sysml(self) -> str:
        """Render the definition prefix and attribute definition."""
        return _append_body(
            _join([str(self.definition_prefix), "attribute def"]),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical attribute-definition text."""
        return self.to_sysml()


@dataclass
class AttributeUsage(SourceElement):
    """Represent an ``attribute`` usage with its generic usage completion."""

    usage_prefix: UsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render usage modifiers, the attribute keyword, and its usage."""
        return _append_body(
            _join([str(self.usage_prefix), "attribute"]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical attribute-usage text."""
        return self.to_sysml()


@dataclass
class ReferenceUsage(SourceElement):
    """Represent ``referenceUsage`` and ``defaultReferenceUsage`` explicitly."""

    usage_prefix: UsagePrefix
    usage: Usage
    has_ref_keyword: bool = True

    def to_sysml(self) -> str:
        """Render the prefix, optional ``ref`` keyword, and completion."""
        head = _join([str(self.usage_prefix), "ref" if self.has_ref_keyword else ""])
        return _append_body(head, str(self.usage))

    def __str__(self) -> str:
        """Return canonical reference-usage text."""
        return self.to_sysml()


@dataclass
class PortDefinition(SourceElement):
    """Represent a ``port def`` and its derived conjugation marker.

    The grammar's ``portConjugation`` production is an epsilon production:
    the conjugate port definition is derived by SysML and is not written as
    source text.  The optional field is retained for compatibility with the
    syntax production, but it must never append a ``~`` fragment to exported
    source.
    """

    definition_prefix: DefinitionPrefix
    definition: Definition
    conjugated_port_definition: Optional[ConjugatedPortTyping] = None

    def to_sysml(self) -> str:
        """Render the source-owned port definition only."""
        return _append_body(
            _join([str(self.definition_prefix), "port def"]),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical port-definition text."""
        return self.to_sysml()


@dataclass
class PortUsage(SourceElement):
    """Represent a ``port`` usage with its occurrence prefix and completion."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render occurrence modifiers, ``port``, and its usage."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), "port"]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical port-usage text."""
        return self.to_sysml()


@dataclass
class EndOccurrenceUsageElement(SourceElement):
    """Represent an ``end`` occurrence usage and its concrete modifiers.

    The child is a :class:`SourceElement` because the grammar accepts every
    structured and behavioral occurrence-usage alternative.  This node retains
    every token owned by the ``endOccurrenceUsageElement`` production while
    those alternatives are progressively narrowed to their concrete classes.

    :param occurrence_usage: Concrete occurrence usage owned by this end.
    :type occurrence_usage: :class:`pysysmlv2.syntax.ast.SourceElement`
    :param name: Optional end name, defaults to ``None``.
    :type name: str, optional
    :param cross_multiplicity_text: Optional cross multiplicity source,
        defaults to ``None``.
    :type cross_multiplicity_text: str, optional
    :param is_nonunique: Whether the ``nonunique`` modifier is present,
        defaults to ``False``.
    :type is_nonunique: bool, optional
    :ivar occurrence_usage: Concrete occurrence usage owned by this end.
    :vartype occurrence_usage: :class:`pysysmlv2.syntax.ast.SourceElement`
    :ivar name: Optional end name.
    :vartype name: str, optional
    :ivar cross_multiplicity_text: Optional cross multiplicity source.
    :vartype cross_multiplicity_text: str, optional
    :ivar is_nonunique: Whether the ``nonunique`` modifier is present.
    :vartype is_nonunique: bool

    Example::

        >>> str(EndOccurrenceUsageElement(ItemUsage(OccurrenceUsagePrefix(), Usage(DefinitionBody(True)))))
        'end item;'
    """

    occurrence_usage: SourceElement
    name: Optional[str] = None
    cross_multiplicity_text: Optional[str] = None
    is_nonunique: bool = False

    def to_sysml(self) -> str:
        """Render end-owned modifiers before the nested occurrence usage."""
        return _append_body(
            _join(
                [
                    "end",
                    self.name or "",
                    self.cross_multiplicity_text or "",
                    "nonunique" if self.is_nonunique else "",
                ]
            ),
            str(self.occurrence_usage),
        )

    def __str__(self) -> str:
        """Return canonical end-occurrence-usage text."""
        return self.to_sysml()


@dataclass
class FeatureIdentification(SourceElement):
    """Represent the name-bearing alternative of ``featureIdentification``.

    This node is kept distinct from :class:`Identification` because the
    grammar uses it inside a feature declaration, where a short name is
    introduced with ``<`` and ``>`` but the surrounding declaration may have
    no ordinary usage identifier.

    :param short_name: Optional short feature name, defaults to ``None``.
    :type short_name: str, optional
    :param declared_name: Optional declared feature name, defaults to ``None``.
    :type declared_name: str, optional

    Example::

        >>> str(FeatureIdentification(declared_name="source"))
        'source'
    """

    short_name: Optional[str] = None
    declared_name: Optional[str] = None

    def to_sysml(self) -> str:
        """Render the feature's optional short and declared names."""
        if self.short_name is not None and self.declared_name is not None:
            return "<{}> {}".format(self.short_name, self.declared_name)
        if self.short_name is not None:
            return "<{}>".format(self.short_name)
        return self.declared_name or ""

    def __str__(self) -> str:
        """Return canonical feature-identification text."""
        return self.to_sysml()


@dataclass
class FeatureDeclaration(SourceElement):
    """Represent a structured ``featureDeclaration``.

    The feature relationship productions are retained in source order as
    explicit concrete nodes while the name, specialization, and conjugation
    choices remain separate typed fields.  The semantic layer can later map
    those relationship productions without reparsing this declaration.

    :param identification: Optional feature name, defaults to ``None``.
    :type identification: :class:`pysysmlv2.syntax.ast.FeatureIdentification`, optional
    :param specialization: Optional feature specialization, defaults to ``None``.
    :type specialization: :class:`pysysmlv2.syntax.ast.FeatureSpecializationPart`, optional
    :param is_all: Whether the ``all`` modifier is present, defaults to ``False``.
    :type is_all: bool, optional
    :param conjugation_part: Optional concrete conjugation part, defaults to
        ``None``.
    :type conjugation_part: :class:`pysysmlv2.syntax.ast.ConjugationPart`, optional
    :param relationship_parts: Ordered concrete feature relationship parts,
        defaults to ``[]``.
    :type relationship_parts: list[pysysmlv2.syntax.ast.FeatureRelationshipPart], optional

    Example::

        >>> declaration = FeatureDeclaration(
        ...     identification=FeatureIdentification(declared_name="a"),
        ... )
        >>> str(declaration)
        'a'
    """

    identification: Optional[FeatureIdentification] = None
    specialization: Optional[FeatureSpecializationPart] = None
    is_all: bool = False
    conjugation_part: Optional[ConjugationPart] = None
    relationship_parts: List[FeatureRelationshipPart] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render feature declaration fields in grammar order."""
        return _join(
            [
                "all" if self.is_all else "",
                str(self.identification) if self.identification else "",
                str(self.specialization) if self.specialization else "",
                str(self.conjugation_part) if self.conjugation_part else "",
                *(str(item) for item in self.relationship_parts),
            ]
        )

    def __str__(self) -> str:
        """Return canonical feature-declaration text."""
        return self.to_sysml()


@dataclass
class OwnedCrossFeature(SourceElement):
    """Represent one ``ownedCrossFeature`` alternative.

    Exactly one of the feature and usage alternatives is normally populated
    by the parser.  Keeping the alternatives explicit preserves the ``end``
    prefix relationship used by connection and interface endpoints.

    :param basic_feature_prefix: Optional feature-prefix spelling.
    :type basic_feature_prefix: str, optional
    :param feature_declaration: Optional nested feature declaration.
    :type feature_declaration: :class:`pysysmlv2.syntax.ast.FeatureDeclaration`, optional
    :param basic_usage_prefix: Optional usage-prefix node.
    :type basic_usage_prefix: :class:`pysysmlv2.syntax.ast.UsagePrefix`, optional
    :param usage_declaration: Optional nested usage declaration.
    :type usage_declaration: :class:`pysysmlv2.syntax.ast.UsageDeclaration`, optional

    Example::

        >>> str(OwnedCrossFeature(basic_usage_prefix=UsagePrefix()))
        ''
    """

    basic_feature_prefix: Optional[str] = None
    feature_declaration: Optional[FeatureDeclaration] = None
    basic_usage_prefix: Optional[UsagePrefix] = None
    usage_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render the selected owned-cross-feature alternative."""
        return _join(
            [
                self.basic_feature_prefix or "",
                str(self.feature_declaration) if self.feature_declaration else "",
                str(self.basic_usage_prefix) if self.basic_usage_prefix else "",
                str(self.usage_declaration) if self.usage_declaration else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical owned-cross-feature text."""
        return self.to_sysml()


@dataclass
class EndUsagePrefix(SourceElement):
    """Represent the ``end`` keyword and its owned cross feature."""

    owned_cross_feature: OwnedCrossFeature

    def to_sysml(self) -> str:
        """Render ``end`` and its required cross-feature child."""
        return _join(["end", str(self.owned_cross_feature)])

    def __str__(self) -> str:
        """Return canonical end-usage-prefix text."""
        return self.to_sysml()


@dataclass
class EndFeatureUsage(SourceElement):
    """Represent a connection/interface end feature usage.

    :param end_usage_prefix: Explicit ``end`` prefix and cross-feature.
    :type end_usage_prefix: :class:`pysysmlv2.syntax.ast.EndUsagePrefix`
    :param feature_declaration: Declared end feature and specialization.
    :type feature_declaration: :class:`pysysmlv2.syntax.ast.FeatureDeclaration`
    :param usage: Optional value/body completion owned by the end feature.
    :type usage: :class:`pysysmlv2.syntax.ast.Usage`

    Example::

        >>> end = EndFeatureUsage(
        ...     EndUsagePrefix(OwnedCrossFeature(basic_usage_prefix=UsagePrefix())),
        ...     FeatureDeclaration(FeatureIdentification(declared_name="a")),
        ...     Usage(DefinitionBody(declaration_only=True)),
        ... )
        >>> str(end)
        'end a;'
    """

    end_usage_prefix: EndUsagePrefix
    feature_declaration: FeatureDeclaration
    usage: Usage

    def to_sysml(self) -> str:
        """Render end prefix, declaration, and completion body."""
        return _append_body(
            _join([str(self.end_usage_prefix), str(self.feature_declaration)]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical end-feature-usage text."""
        return self.to_sysml()


def _render_connection_end(
    reference: Reference,
    cross_multiplicity: Optional[str],
    name: Optional[str],
    name_operator: Optional[str],
) -> str:
    """Render the common endpoint grammar shared by connector/interface ends."""
    return _join(
        [
            cross_multiplicity or "",
            name or "",
            name_operator or "",
            str(reference),
        ]
    )


@dataclass
class ConnectorEnd(SourceElement):
    """Represent one concrete ``connectorEnd``.

    :param reference: Unresolved endpoint reference.
    :type reference: :class:`pysysmlv2.syntax.ast.Reference`
    :param cross_multiplicity: Optional endpoint multiplicity spelling.
    :type cross_multiplicity: str, optional
    :param name: Optional endpoint name before ``::>``/``references``.
    :type name: str, optional
    :param name_operator: Optional endpoint relation operator.
    :type name_operator: str, optional

    Example::

        >>> str(ConnectorEnd(QualifiedReference(["hub"]), "[1]"))
        '[1] hub'
    """

    reference: Reference
    cross_multiplicity: Optional[str] = None
    name: Optional[str] = None
    name_operator: Optional[str] = None

    def to_sysml(self) -> str:
        """Render endpoint modifiers and its unresolved reference."""
        return _render_connection_end(
            self.reference,
            self.cross_multiplicity,
            self.name,
            self.name_operator,
        )

    def __str__(self) -> str:
        """Return canonical connector-end text."""
        return self.to_sysml()


@dataclass
class ConnectorPart(SourceElement):
    """Base class for binary and n-ary connector-part alternatives."""


@dataclass
class BinaryConnectorPart(ConnectorPart):
    """Represent the binary ``connectorEnd to connectorEnd`` alternative."""

    source: ConnectorEnd
    target: ConnectorEnd

    def to_sysml(self) -> str:
        """Render the two connector ends and their ``to`` relation."""
        return _join([str(self.source), "to", str(self.target)])

    def __str__(self) -> str:
        """Return canonical binary connector-part text."""
        return self.to_sysml()


@dataclass
class NaryConnectorPart(ConnectorPart):
    """Represent the parenthesized n-ary connector-part alternative."""

    ends: List[ConnectorEnd]

    def to_sysml(self) -> str:
        """Render the ordered n-ary connector ends."""
        return "(" + ", ".join(str(item) for item in self.ends) + ")"

    def __str__(self) -> str:
        """Return canonical n-ary connector-part text."""
        return self.to_sysml()


@dataclass
class ConnectionDefinition(SourceElement):
    """Represent a concrete ``connection def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition: Definition

    def to_sysml(self) -> str:
        """Render prefix, ``connection def``, declaration, and body."""
        return _append_body(
            _join([str(self.occurrence_definition_prefix), "connection def"]),
            str(self.definition),
        )

    def __str__(self) -> str:
        """Return canonical connection-definition text."""
        return self.to_sysml()


@dataclass
class ConnectionUsage(SourceElement):
    """Represent a concrete ``connectionUsage``.

    ``has_connection_keyword`` distinguishes the named ``connection`` form
    from the generic ``connect`` shorthand.  The endpoint part remains a
    typed binary or n-ary grammar alternative.
    """

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage_body: DefinitionBody
    usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None
    connector_part: Optional[ConnectorPart] = None
    has_connection_keyword: bool = True

    def to_sysml(self) -> str:
        """Render connection declaration, connector part, and body."""
        head = _join(
            [
                str(self.occurrence_usage_prefix),
                "connection" if self.has_connection_keyword else "",
                str(self.usage_declaration) if self.usage_declaration else "",
                str(self.value_part) if self.value_part else "",
                "connect" if self.connector_part is not None else "",
                str(self.connector_part) if self.connector_part else "",
            ]
        )
        if not self.has_connection_keyword and self.connector_part is not None:
            head = _join(
                [
                    str(self.occurrence_usage_prefix),
                    "connect",
                    str(self.connector_part),
                ]
            )
        return _append_body(head, str(self.usage_body))

    def __str__(self) -> str:
        """Return canonical connection-usage text."""
        return self.to_sysml()


@dataclass
class BindingConnectorAsUsage(SourceElement):
    """Represent the concrete ``bindingConnectorAsUsage`` production.

    The grammar distinguishes the full ``binding`` form from the shorthand
    ``bind`` form. Both forms retain the required usage prefix, two ordered
    connector ends, and the usage body as explicit fields; name resolution of
    the endpoints is deferred to the workspace layer.

    :param usage_prefix: Required generic usage prefix.
    :type usage_prefix: :class:`pysysmlv2.syntax.ast.UsagePrefix`
    :param source: First connector end on the left side of ``=``.
    :type source: :class:`pysysmlv2.syntax.ast.ConnectorEnd`
    :param target: Second connector end on the right side of ``=``.
    :type target: :class:`pysysmlv2.syntax.ast.ConnectorEnd`
    :param usage_body: Required semicolon or brace usage body.
    :type usage_body: :class:`pysysmlv2.syntax.ast.DefinitionBody`
    :param usage_declaration: Optional declaration owned by ``binding``.
    :type usage_declaration: :class:`pysysmlv2.syntax.ast.UsageDeclaration`, optional
    :param has_binding_keyword: Whether the optional ``binding`` keyword is
        present, defaults to ``False``.
    :type has_binding_keyword: bool, optional

    Example::

        >>> binding = BindingConnectorAsUsage(
        ...     UsagePrefix(),
        ...     ConnectorEnd(QualifiedReference(["a"])),
        ...     ConnectorEnd(QualifiedReference(["b"])),
        ...     DefinitionBody(declaration_only=True),
        ... )
        >>> str(binding)
        'bind a = b;'
    """

    usage_prefix: UsagePrefix
    source: ConnectorEnd
    target: ConnectorEnd
    usage_body: DefinitionBody
    usage_declaration: Optional[UsageDeclaration] = None
    has_binding_keyword: bool = False

    def to_sysml(self) -> str:
        """Render the binding form, endpoints, and usage body."""
        prefix = _join(
            [
                str(self.usage_prefix),
                "binding" if self.has_binding_keyword else "",
                str(self.usage_declaration) if self.usage_declaration else "",
                "bind",
                str(self.source),
                "=",
                str(self.target),
            ]
        )
        return _append_body(prefix, str(self.usage_body))

    def __str__(self) -> str:
        """Return canonical binding-connector-usage text."""
        return self.to_sysml()


@dataclass
class SuccessionAsUsage(SourceElement):
    """Represent the concrete ``successionAsUsage`` production.

    The full ``succession`` form and the shorthand ``first`` form share the
    same ordered source/target connector ends. The optional declaration is
    owned by the full form; the source AST preserves that distinction without
    resolving either endpoint.

    :param usage_prefix: Required generic usage prefix.
    :type usage_prefix: :class:`pysysmlv2.syntax.ast.UsagePrefix`
    :param source: First connector end after ``first``.
    :type source: :class:`pysysmlv2.syntax.ast.ConnectorEnd`
    :param target: Second connector end after ``then``.
    :type target: :class:`pysysmlv2.syntax.ast.ConnectorEnd`
    :param usage_body: Required semicolon or brace usage body.
    :type usage_body: :class:`pysysmlv2.syntax.ast.DefinitionBody`
    :param usage_declaration: Optional declaration owned by ``succession``.
    :type usage_declaration: :class:`pysysmlv2.syntax.ast.UsageDeclaration`, optional
    :param has_succession_keyword: Whether the optional ``succession`` keyword
        is present, defaults to ``False``.
    :type has_succession_keyword: bool, optional

    Example::

        >>> succession = SuccessionAsUsage(
        ...     UsagePrefix(),
        ...     ConnectorEnd(QualifiedReference(["a"])),
        ...     ConnectorEnd(QualifiedReference(["b"])),
        ...     DefinitionBody(declaration_only=True),
        ... )
        >>> str(succession)
        'first a then b;'
    """

    usage_prefix: UsagePrefix
    source: ConnectorEnd
    target: ConnectorEnd
    usage_body: DefinitionBody
    usage_declaration: Optional[UsageDeclaration] = None
    has_succession_keyword: bool = False

    def to_sysml(self) -> str:
        """Render the succession form, endpoints, and usage body."""
        prefix = _join(
            [
                str(self.usage_prefix),
                "succession" if self.has_succession_keyword else "",
                str(self.usage_declaration) if self.usage_declaration else "",
                "first",
                str(self.source),
                "then",
                str(self.target),
            ]
        )
        return _append_body(prefix, str(self.usage_body))

    def __str__(self) -> str:
        """Return canonical succession-usage text."""
        return self.to_sysml()


@dataclass
class InterfaceEnd(SourceElement):
    """Represent one concrete ``interfaceEnd`` endpoint."""

    reference: Reference
    cross_multiplicity: Optional[str] = None
    name: Optional[str] = None
    name_operator: Optional[str] = None

    def to_sysml(self) -> str:
        """Render interface endpoint modifiers and reference."""
        return _render_connection_end(
            self.reference,
            self.cross_multiplicity,
            self.name,
            self.name_operator,
        )

    def __str__(self) -> str:
        """Return canonical interface-end text."""
        return self.to_sysml()


@dataclass
class InterfacePart(SourceElement):
    """Base class for binary and n-ary interface-part alternatives."""


@dataclass
class BinaryInterfacePart(InterfacePart):
    """Represent the binary ``interfaceEnd to interfaceEnd`` alternative."""

    source: InterfaceEnd
    target: InterfaceEnd

    def to_sysml(self) -> str:
        """Render the two interface ends and their ``to`` relation."""
        return _join([str(self.source), "to", str(self.target)])

    def __str__(self) -> str:
        """Return canonical binary interface-part text."""
        return self.to_sysml()


@dataclass
class NaryInterfacePart(InterfacePart):
    """Represent the parenthesized n-ary interface-part alternative."""

    ends: List[InterfaceEnd]

    def to_sysml(self) -> str:
        """Render the ordered n-ary interface ends."""
        return "(" + ", ".join(str(item) for item in self.ends) + ")"

    def __str__(self) -> str:
        """Return canonical n-ary interface-part text."""
        return self.to_sysml()


@dataclass
class InterfaceBody(SourceElement):
    """Represent a semicolon or ordered ``interfaceBody`` member list."""

    declaration_only: bool = False
    items: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the interface body and its ordered members."""
        return _render_block(self.items, declaration_only=self.declaration_only)

    def __str__(self) -> str:
        """Return canonical interface-body text."""
        return self.to_sysml()


@dataclass
class DefaultInterfaceEnd(SourceElement):
    """Represent the ``defaultInterfaceEnd`` ``end`` usage alternative."""

    usage: Usage

    def to_sysml(self) -> str:
        """Render ``end`` and its structured usage completion."""
        return _append_body("end", str(self.usage))

    def __str__(self) -> str:
        """Return canonical default-interface-end text."""
        return self.to_sysml()


@dataclass
class InterfaceNonOccurrenceUsageMember(SourceElement):
    """Represent an interface non-occurrence member and visibility prefix."""

    usage: SourceElement
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility and the nested non-occurrence usage."""
        return _join([self.member_prefix or "", str(self.usage)])

    def __str__(self) -> str:
        """Return canonical interface non-occurrence member text."""
        return self.to_sysml()


@dataclass
class InterfaceOccurrenceUsageMember(SourceElement):
    """Represent an interface occurrence member and optional source succession."""

    usage: SourceElement
    member_prefix: Optional[str] = None
    source_succession: Optional[SourceSuccession] = None

    def to_sysml(self) -> str:
        """Render source succession, visibility, and nested occurrence usage."""
        return _join(
            [
                str(self.source_succession) if self.source_succession else "",
                self.member_prefix or "",
                str(self.usage),
            ]
        )

    def __str__(self) -> str:
        """Return canonical interface occurrence member text."""
        return self.to_sysml()


@dataclass
class VariantUsageMember(SourceElement):
    """Represent a visibility-prefixed ``variant`` interface member."""

    element: SourceElement
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility, ``variant``, and its selected element."""
        return _join([self.member_prefix or "", "variant", str(self.element)])

    def __str__(self) -> str:
        """Return canonical variant-usage-member text."""
        return self.to_sysml()


@dataclass
class InterfaceUsageDeclaration(SourceElement):
    """Represent the two alternatives of ``interfaceUsageDeclaration``."""

    usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None
    interface_part: Optional[InterfacePart] = None
    has_connect_keyword: bool = False

    def to_sysml(self) -> str:
        """Render declaration/value and optional interface connection part."""
        if self.interface_part is not None and not self.has_connect_keyword:
            return str(self.interface_part)
        return _join(
            [
                str(self.usage_declaration) if self.usage_declaration else "",
                str(self.value_part) if self.value_part else "",
                "connect" if self.interface_part is not None else "",
                str(self.interface_part) if self.interface_part else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical interface-usage-declaration text."""
        return self.to_sysml()


@dataclass
class InterfaceDefinition(SourceElement):
    """Represent a concrete ``interface def`` and its interface body."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    interface_body: InterfaceBody

    def to_sysml(self) -> str:
        """Render interface definition prefix, declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.occurrence_definition_prefix),
                    "interface def",
                    str(self.definition_declaration),
                ]
            ),
            str(self.interface_body),
        )

    def __str__(self) -> str:
        """Return canonical interface-definition text."""
        return self.to_sysml()


@dataclass
class InterfaceUsage(SourceElement):
    """Represent a concrete ``interface`` usage and its body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    interface_usage_declaration: InterfaceUsageDeclaration
    interface_body: InterfaceBody

    def to_sysml(self) -> str:
        """Render interface usage prefix, declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.occurrence_usage_prefix),
                    "interface",
                    str(self.interface_usage_declaration),
                ]
            ),
            str(self.interface_body),
        )

    def __str__(self) -> str:
        """Return canonical interface-usage text."""
        return self.to_sysml()


@dataclass
class ActionDefinition(SourceElement):
    """Represent an ``action def`` with a structured action body."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    action_body: ActionBody

    def to_sysml(self) -> str:
        """Render action-definition prefix, declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.occurrence_definition_prefix),
                    "action def",
                    str(self.definition_declaration),
                ]
            ),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical action-definition text."""
        return self.to_sysml()


@dataclass
class ActionBody(SourceElement):
    """Represent ``ActionBody`` as a semicolon or ordered statements."""

    declaration_only: bool = False
    items: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the action body from its explicit statement list."""
        return _render_block(self.items, declaration_only=self.declaration_only)

    def __str__(self) -> str:
        """Return canonical action-body text."""
        return self.to_sysml()


@dataclass
class CalculationBody(ActionBody):
    """Represent ``calculationBody`` and its optional result member."""

    result_expression_member: Optional[ResultExpressionMember] = None

    def to_sysml(self) -> str:
        """Render calculation statements and the optional result expression."""
        if self.declaration_only:
            return ";"
        items = [*self.items]
        if self.result_expression_member is not None:
            items.append(self.result_expression_member)
        return _render_block(items, declaration_only=False)

    def __str__(self) -> str:
        """Return canonical calculation-body text."""
        return self.to_sysml()


@dataclass
class CaseBody(CalculationBody):
    """Represent ``caseBody`` with action items and an optional result."""


@dataclass
class RequirementBody(SourceElement):
    """Represent ``requirementBody`` and its ordered members."""

    declaration_only: bool = False
    items: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render requirement members in source order."""
        return _render_block(self.items, declaration_only=self.declaration_only)

    def __str__(self) -> str:
        """Return canonical requirement-body text."""
        return self.to_sysml()


@dataclass
class ViewDefinitionBody(DefinitionBody):
    """Represent the dedicated ``viewDefinitionBody`` production."""


@dataclass
class ViewBody(DefinitionBody):
    """Represent the dedicated ``viewBody`` production."""


@dataclass
class EnumerationBody(SourceElement):
    """Represent an enumeration's semicolon or ordered value members."""

    declaration_only: bool = False
    items: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render enumeration members in source order."""
        return _render_block(self.items, declaration_only=self.declaration_only)

    def __str__(self) -> str:
        """Return canonical enumeration-body text."""
        return self.to_sysml()


@dataclass
class EnumeratedValue(SourceElement):
    """Represent one ``enumeratedValue`` usage."""

    usage: Usage
    is_enum: bool = False

    def to_sysml(self) -> str:
        """Render the optional ``enum`` marker and usage."""
        return _join(["enum" if self.is_enum else "", str(self.usage)])

    def __str__(self) -> str:
        """Return canonical enumerated-value text."""
        return self.to_sysml()


@dataclass
class EnumerationUsageMember(SourceElement):
    """Represent visibility, metadata, and one enumerated value."""

    enumerated_value: EnumeratedValue
    member_prefix: Optional[str] = None
    prefix_metadata: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render metadata, visibility, and enumerated value."""
        return _join([*self.prefix_metadata, self.member_prefix or "", str(self.enumerated_value)])

    def __str__(self) -> str:
        """Return canonical enumeration-member text."""
        return self.to_sysml()


@dataclass
class EnumerationUsage(SourceElement):
    """Represent an ``enum`` usage in a non-occurrence usage position."""

    usage_prefix: UsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render the usage prefix, ``enum`` keyword, and completion."""
        return _append_body(_join([str(self.usage_prefix), "enum"]), str(self.usage))

    def __str__(self) -> str:
        """Return canonical enumeration-usage text."""
        return self.to_sysml()


@dataclass
class FlowDeclaration(SourceElement):
    """Represent the structured declaration alternatives of a flow."""

    usage_declaration: Optional[UsageDeclaration] = None
    feature_declaration: Optional[FeatureDeclaration] = None
    value_part: Optional[ValuePart] = None
    payload_feature: Optional[SourceElement] = None
    source_end: Optional[QualifiedReference] = None
    target_end: Optional[QualifiedReference] = None
    all_ends: bool = False

    def to_sysml(self) -> str:
        """Render declaration, payload, and optional source/target endpoints."""
        declaration = str(self.feature_declaration or self.usage_declaration or "")
        endpoints = ""
        if self.source_end is not None and self.target_end is not None:
            endpoints = _join(
                ["all" if self.all_ends else "", str(self.source_end), "to", str(self.target_end)]
            )
        return _join(
            [
                declaration,
                str(self.value_part) if self.value_part else "",
                "of" if self.payload_feature else "",
                str(self.payload_feature) if self.payload_feature else "",
                "from" if endpoints and not self.all_ends else "",
                endpoints,
            ]
        )

    def __str__(self) -> str:
        """Return canonical flow-declaration text."""
        return self.to_sysml()


@dataclass
class MessageDeclaration(SourceElement):
    """Represent a message declaration and optional event endpoints."""

    usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None
    payload_feature: Optional[SourceElement] = None
    source_event: Optional[QualifiedReference] = None
    target_event: Optional[QualifiedReference] = None

    def to_sysml(self) -> str:
        """Render message declaration fields in grammar order."""
        endpoints = (
            _join(["from", str(self.source_event), "to", str(self.target_event)])
            if self.source_event is not None and self.target_event is not None
            else ""
        )
        return _join(
            [
                str(self.usage_declaration) if self.usage_declaration else "",
                str(self.value_part) if self.value_part else "",
                "of" if self.payload_feature else "",
                str(self.payload_feature) if self.payload_feature else "",
                endpoints,
            ]
        )

    def __str__(self) -> str:
        """Return canonical message-declaration text."""
        return self.to_sysml()


@dataclass
class AllocationUsageDeclaration(SourceElement):
    """Represent ``allocationUsageDeclaration`` alternatives."""

    usage_declaration: Optional[UsageDeclaration] = None
    connector_part: Optional[ConnectorPart] = None
    has_allocation_keyword: bool = True

    def to_sysml(self) -> str:
        """Render allocation declaration and optional ``allocate`` relation."""
        if not self.has_allocation_keyword:
            return _join(["allocate", str(self.connector_part) if self.connector_part else ""])
        return _join(
            [
                "allocation",
                str(self.usage_declaration) if self.usage_declaration else "",
                "allocate" if self.connector_part else "",
                str(self.connector_part) if self.connector_part else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical allocation-declaration text."""
        return self.to_sysml()


@dataclass
class ConstraintUsageDeclaration(SourceElement):
    """Represent a constraint usage declaration and optional value."""

    usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None

    def to_sysml(self) -> str:
        """Render declaration and value fields."""
        return _join(
            [
                str(self.usage_declaration) if self.usage_declaration else "",
                str(self.value_part) if self.value_part else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical constraint-usage-declaration text."""
        return self.to_sysml()


@dataclass
class CalculationDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``calc def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: CalculationBody
    keyword: ClassVar[str] = "calc"


@dataclass
class ConstraintDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``constraint def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: CalculationBody
    keyword: ClassVar[str] = "constraint"


@dataclass
class RequirementDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``requirement def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: RequirementBody
    keyword: ClassVar[str] = "requirement"


@dataclass
class ConcernDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``concern def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: RequirementBody
    keyword: ClassVar[str] = "concern"


@dataclass
class CaseDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``case def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: CaseBody
    keyword: ClassVar[str] = "case"


@dataclass
class AnalysisCaseDefinition(_OccurrenceDefinitionWithBody):
    """Represent an ``analysis def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: CaseBody
    keyword: ClassVar[str] = "analysis"


@dataclass
class VerificationCaseDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``verification def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: CaseBody
    keyword: ClassVar[str] = "verification"


@dataclass
class UseCaseDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``use case def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: CaseBody
    keyword: ClassVar[str] = "use case"


@dataclass
class ViewDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``view def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: ViewDefinitionBody
    keyword: ClassVar[str] = "view"


@dataclass
class ViewpointDefinition(_OccurrenceDefinitionWithBody):
    """Represent a ``viewpoint def``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    body: RequirementBody
    keyword: ClassVar[str] = "viewpoint"


@dataclass
class ActionUsageDeclaration(SourceElement):
    """Represent an action usage declaration and optional value part."""

    usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None

    def to_sysml(self) -> str:
        """Render declaration and value fields."""
        return _join(
            [
                str(self.usage_declaration) if self.usage_declaration else "",
                str(self.value_part) if self.value_part else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical action-usage-declaration text."""
        return self.to_sysml()


@dataclass
class CalculationUsage(_UsageWithBody):
    """Represent a ``calc`` usage with a calculation body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ActionUsageDeclaration
    body: CalculationBody
    keyword: ClassVar[str] = "calc"


@dataclass
class ConstraintUsage(_UsageWithBody):
    """Represent a ``constraint`` usage with a calculation body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ConstraintUsageDeclaration
    body: CalculationBody
    keyword: ClassVar[str] = "constraint"


@dataclass
class RequirementUsage(_UsageWithBody):
    """Represent a ``requirement`` usage with a requirement body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ConstraintUsageDeclaration
    body: RequirementBody
    keyword: ClassVar[str] = "requirement"


@dataclass
class ConcernUsage(_UsageWithBody):
    """Represent a ``concern`` usage with a requirement body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ConstraintUsageDeclaration
    body: RequirementBody
    keyword: ClassVar[str] = "concern"


@dataclass
class CaseUsage(_UsageWithBody):
    """Represent a ``case`` usage with a case body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ConstraintUsageDeclaration
    body: CaseBody
    keyword: ClassVar[str] = "case"


@dataclass
class AnalysisCaseUsage(_UsageWithBody):
    """Represent an ``analysis`` usage with a case body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ConstraintUsageDeclaration
    body: CaseBody
    keyword: ClassVar[str] = "analysis"


@dataclass
class VerificationCaseUsage(_UsageWithBody):
    """Represent a ``verification`` usage with a case body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ConstraintUsageDeclaration
    body: CaseBody
    keyword: ClassVar[str] = "verification"


@dataclass
class UseCaseUsage(_UsageWithBody):
    """Represent a ``use case`` usage with a case body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ConstraintUsageDeclaration
    body: CaseBody
    keyword: ClassVar[str] = "use case"


@dataclass
class ViewpointUsage(_UsageWithBody):
    """Represent a ``viewpoint`` usage with a requirement body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ConstraintUsageDeclaration
    body: RequirementBody
    keyword: ClassVar[str] = "viewpoint"


@dataclass
class ViewUsage(SourceElement):
    """Represent a ``view`` usage and its dedicated view body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    view_body: ViewBody
    usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None

    def to_sysml(self) -> str:
        """Render view declaration, value, and body."""
        return _append_body(
            _join(
                [
                    str(self.occurrence_usage_prefix),
                    "view",
                    str(self.usage_declaration) if self.usage_declaration else "",
                    str(self.value_part) if self.value_part else "",
                ]
            ),
            str(self.view_body),
        )

    def __str__(self) -> str:
        """Return canonical view-usage text."""
        return self.to_sysml()


@dataclass
class ViewRenderingUsage(SourceElement):
    """Represent a view's ``render`` member target."""

    body: DefinitionBody
    reference: Optional[Reference] = None
    usage: Optional[Usage] = None

    def to_sysml(self) -> str:
        """Render the selected rendering target and body."""
        return _append_body(
            _join(
                [
                    "rendering" if self.usage is not None else "",
                    str(self.reference) if self.reference else "",
                    str(self.usage) if self.usage else "",
                ]
            ),
            str(self.body),
        )

    def __str__(self) -> str:
        """Return canonical view-rendering usage text."""
        return self.to_sysml()


@dataclass
class RenderingUsage(SourceElement):
    """Represent a ``rendering`` usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render the rendering keyword and generic usage completion."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), "rendering"]),
            str(self.usage),
        )

    def __str__(self) -> str:
        """Return canonical rendering-usage text."""
        return self.to_sysml()


@dataclass
class AllocationUsage(_UsageWithDefinitionBody):
    """Represent an ``allocation`` usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: AllocationUsageDeclaration
    body: DefinitionBody
    keyword: ClassVar[str] = ""

    def to_sysml(self) -> str:
        """Render the allocation declaration and usage body."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), str(self.declaration)]),
            str(self.body),
        )


@dataclass
class Message(_UsageWithDefinitionBody):
    """Represent a ``message`` usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: MessageDeclaration
    body: DefinitionBody
    keyword: ClassVar[str] = "message"


@dataclass
class FlowUsage(_UsageWithDefinitionBody):
    """Represent a ``flow`` usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: FlowDeclaration
    body: DefinitionBody
    keyword: ClassVar[str] = "flow"


@dataclass
class SuccessionFlowUsage(_UsageWithDefinitionBody):
    """Represent a ``succession flow`` usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: FlowDeclaration
    body: DefinitionBody
    keyword: ClassVar[str] = "succession flow"


@dataclass
class IncludeUseCaseUsage(SourceElement):
    """Represent an ``include use case`` usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    case_body: CaseBody
    usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None
    owned_reference_subsetting: Optional[Reference] = None
    feature_specialization_part: Optional[FeatureSpecializationPart] = None

    def to_sysml(self) -> str:
        """Render target/declaration, value, and case body."""
        target = (
            _join(
                [
                    str(self.owned_reference_subsetting),
                    str(self.feature_specialization_part)
                    if self.feature_specialization_part
                    else "",
                ]
            )
            if self.owned_reference_subsetting
            else _join(
                [
                    "use case",
                    str(self.usage_declaration) if self.usage_declaration else "",
                ]
            )
        )
        return _append_body(
            _join(
                [
                    str(self.occurrence_usage_prefix),
                    "include",
                    target,
                    str(self.value_part) if self.value_part else "",
                ]
            ),
            str(self.case_body),
        )

    def __str__(self) -> str:
        """Return canonical include-use-case text."""
        return self.to_sysml()


@dataclass
class AssertConstraintUsage(SourceElement):
    """Represent an ``assert constraint`` usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    calculation_body: CalculationBody
    constraint_usage_declaration: Optional[ConstraintUsageDeclaration] = None
    owned_reference_subsetting: Optional[Reference] = None
    feature_specialization_part: Optional[FeatureSpecializationPart] = None
    is_not: bool = False

    def to_sysml(self) -> str:
        """Render assertion target and calculation body."""
        target = (
            _join(
                [
                    str(self.owned_reference_subsetting),
                    str(self.feature_specialization_part)
                    if self.feature_specialization_part
                    else "",
                ]
            )
            if self.owned_reference_subsetting
            else _join(
                [
                    "constraint",
                    str(self.constraint_usage_declaration)
                    if self.constraint_usage_declaration
                    else "",
                ]
            )
        )
        return _append_body(
            _join(
                [str(self.occurrence_usage_prefix), "assert", "not" if self.is_not else "", target]
            ),
            str(self.calculation_body),
        )

    def __str__(self) -> str:
        """Return canonical assert-constraint text."""
        return self.to_sysml()


@dataclass
class SatisfyRequirementUsage(SourceElement):
    """Represent a ``satisfy requirement`` usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    requirement_body: RequirementBody
    usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None
    owned_reference_subsetting: Optional[Reference] = None
    feature_specialization_part: Optional[FeatureSpecializationPart] = None
    is_assert: bool = False
    is_not: bool = False

    def to_sysml(self) -> str:
        """Render satisfaction target, value, and requirement body."""
        target = (
            _join(
                [
                    str(self.owned_reference_subsetting),
                    str(self.feature_specialization_part)
                    if self.feature_specialization_part
                    else "",
                ]
            )
            if self.owned_reference_subsetting
            else _join(
                [
                    "requirement",
                    str(self.usage_declaration) if self.usage_declaration else "",
                ]
            )
        )
        return _append_body(
            _join(
                [
                    str(self.occurrence_usage_prefix),
                    "assert" if self.is_assert else "",
                    "not" if self.is_not else "",
                    "satisfy",
                    target,
                    str(self.value_part) if self.value_part else "",
                ]
            ),
            str(self.requirement_body),
        )

    def __str__(self) -> str:
        """Return canonical satisfy-requirement text."""
        return self.to_sysml()


@dataclass
class ActionNodeUsageDeclaration(SourceElement):
    """Represent ``actionNodeUsageDeclaration`` and its optional name."""

    usage_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render the optional ``action`` keyword and usage declaration."""
        return _join(["action", str(self.usage_declaration) if self.usage_declaration else ""])

    def __str__(self) -> str:
        """Return canonical action-node declaration text."""
        return self.to_sysml()


@dataclass
class AcceptNodeDeclaration(SourceElement):
    """Represent ``acceptNodeDeclaration`` including its payload fields."""

    accept_parameter_part: AcceptParameterPart
    action_node_usage_declaration: Optional[ActionNodeUsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render optional action declaration, ``accept``, and payload."""
        return _join(
            [
                str(self.action_node_usage_declaration)
                if self.action_node_usage_declaration
                else "",
                "accept",
                str(self.accept_parameter_part),
            ]
        )

    def __str__(self) -> str:
        """Return canonical accept-node declaration text."""
        return self.to_sysml()


@dataclass
class SenderReceiverPart(SourceElement):
    """Represent the explicit ``via``/``to`` sender-receiver relationship.

    ``emptyParameterMember`` is an epsilon production, so it never becomes a
    literal ``()`` during canonical rendering.  A missing ``via`` parameter
    with a present ``to`` parameter already identifies that grammar choice.
    """

    via_parameter: Optional[NodeParameter] = None
    to_parameter: Optional[NodeParameter] = None

    def to_sysml(self) -> str:
        """Render sender/receiver keywords and structured node parameters."""
        parts = []
        if self.via_parameter is not None:
            parts.extend(["via", str(self.via_parameter)])
        if self.to_parameter is not None:
            parts.extend(["to", str(self.to_parameter)])
        return _join(parts)

    def __str__(self) -> str:
        """Return canonical sender-receiver text."""
        return self.to_sysml()


@dataclass
class SendNodeDeclaration(SourceElement):
    """Represent ``sendNodeDeclaration`` with structured parameters."""

    send_parameter: NodeParameter
    action_node_usage_declaration: Optional[ActionNodeUsageDeclaration] = None
    sender_receiver_part: Optional[SenderReceiverPart] = None

    def to_sysml(self) -> str:
        """Render optional action declaration, send parameter, and routing."""
        return _join(
            [
                str(self.action_node_usage_declaration)
                if self.action_node_usage_declaration
                else "",
                "send",
                str(self.send_parameter),
                str(self.sender_receiver_part) if self.sender_receiver_part else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical send-node declaration text."""
        return self.to_sysml()


@dataclass
class SendNodeUsageDeclaration(SourceElement):
    """Represent the broader declaration alternatives of ``sendNode``."""

    send_parameter: Optional[NodeParameter] = None
    action_node_usage_declaration: Optional[ActionNodeUsageDeclaration] = None
    action_usage_declaration: Optional[ActionUsageDeclaration] = None
    sender_receiver_part: Optional[SenderReceiverPart] = None

    def to_sysml(self) -> str:
        """Render full send-node declaration alternatives."""
        parameter = str(self.send_parameter) if self.send_parameter else ""
        return _join(
            [
                str(self.action_node_usage_declaration)
                if self.action_node_usage_declaration
                else str(self.action_usage_declaration)
                if self.action_usage_declaration
                else "",
                "send",
                parameter,
                str(self.sender_receiver_part) if self.sender_receiver_part else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical full send-node declaration text."""
        return self.to_sysml()


@dataclass
class AssignmentNodeDeclaration(SourceElement):
    """Represent ``assignmentNodeDeclaration`` with target and value."""

    target: FeatureChain
    value: NodeParameter
    action_node_usage_declaration: Optional[ActionNodeUsageDeclaration] = None
    assignment_target_binding: Optional[Expression] = None

    def to_sysml(self) -> str:
        """Render optional action declaration, assignment target, and value."""
        target = (
            "{}.{}".format(self.assignment_target_binding, self.target)
            if self.assignment_target_binding is not None
            else str(self.target)
        )
        return _join(
            [
                str(self.action_node_usage_declaration)
                if self.action_node_usage_declaration
                else "",
                "assign",
                target,
                ":=",
                str(self.value),
            ]
        )

    def __str__(self) -> str:
        """Return canonical assignment-node declaration text."""
        return self.to_sysml()


@dataclass
class MergeNode(ControlNode):
    """Represent a concrete ``mergeNode`` action statement."""

    control_node_prefix: ControlNodePrefix
    action_body: ActionBody
    usage_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render the merge keyword, optional declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.control_node_prefix),
                    "merge",
                    str(self.usage_declaration) if self.usage_declaration else "",
                ]
            ),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical merge-node text."""
        return self.to_sysml()


@dataclass
class DecisionNode(ControlNode):
    """Represent a concrete ``decisionNode`` action statement."""

    control_node_prefix: ControlNodePrefix
    action_body: ActionBody
    usage_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render the decision keyword, optional declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.control_node_prefix),
                    "decide",
                    str(self.usage_declaration) if self.usage_declaration else "",
                ]
            ),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical decision-node text."""
        return self.to_sysml()


@dataclass
class JoinNode(ControlNode):
    """Represent a concrete ``joinNode`` action statement."""

    control_node_prefix: ControlNodePrefix
    action_body: ActionBody
    usage_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render the join keyword, optional declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.control_node_prefix),
                    "join",
                    str(self.usage_declaration) if self.usage_declaration else "",
                ]
            ),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical join-node text."""
        return self.to_sysml()


@dataclass
class ForkNode(ControlNode):
    """Represent a concrete ``forkNode`` action statement."""

    control_node_prefix: ControlNodePrefix
    action_body: ActionBody
    usage_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render the fork keyword, optional declaration, and body."""
        return _append_body(
            _join(
                [
                    str(self.control_node_prefix),
                    "fork",
                    str(self.usage_declaration) if self.usage_declaration else "",
                ]
            ),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical fork-node text."""
        return self.to_sysml()


@dataclass
class ActionBodyParameter(SourceElement):
    """Represent a brace-delimited action body used by control flow nodes."""

    items: List[SourceElement] = field(default_factory=list)
    action_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render optional ``action`` marker and ordered nested statements."""
        prefix = _join(
            [
                "action" if self.action_declaration is not None else "",
                str(self.action_declaration) if self.action_declaration else "",
            ]
        )
        body = _render_block(self.items, declaration_only=False)
        return _join([prefix, body])

    def __str__(self) -> str:
        """Return canonical action-body-parameter text."""
        return self.to_sysml()


@dataclass
class ActionNodeMember(Statement):
    """Represent an action-node member and its optional visibility prefix."""

    action_node: ActionNode
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility and the nested action node."""
        return _join([self.member_prefix or "", str(self.action_node)])

    def __str__(self) -> str:
        """Return canonical action-node-member text."""
        return self.to_sysml()


@dataclass
class RelationshipBody(SourceElement):
    """Preserve a structured relationship body outside the state core."""

    source_text: str

    def to_sysml(self) -> str:
        """Render the relationship body's canonical source fragment."""
        return self.source_text

    def __str__(self) -> str:
        """Return canonical relationship-body text."""
        return self.to_sysml()


@dataclass
class ImportDeclaration(SourceElement):
    """Base class for the concrete ``importDeclaration`` alternatives.

    The grammar wrapper itself is a one-child dispatch rule and is therefore
    passed through by the listener.  This marker gives all retained import
    alternatives a precise field type without exposing a generic AST node.
    """


@dataclass
class MembershipImport(ImportDeclaration):
    """Represent a membership import target and optional member wildcard.

    :param target: Unresolved namespace/member name being imported.
    :type target: :class:`pysysmlv2.syntax.ast.QualifiedReference`
    :param is_all_members: Whether the concrete ``::*`` suffix is present.
    :type is_all_members: bool
    """

    target: QualifiedReference
    is_all_members: bool = False

    def to_sysml(self) -> str:
        """Render the target and optional membership wildcard."""
        return str(self.target) + ("::**" if self.is_all_members else "")

    def __str__(self) -> str:
        """Return canonical membership-import text."""
        return self.to_sysml()


@dataclass
class NamespaceImport(ImportDeclaration):
    """Represent a namespace wildcard import.

    :param target: Namespace selected by the required qualified name.
    :type target: :class:`pysysmlv2.syntax.ast.QualifiedReference`
    :param is_recursive: Whether the optional trailing ``::**`` is present.
    :type is_recursive: bool
    """

    target: QualifiedReference
    is_recursive: bool = False

    def to_sysml(self) -> str:
        """Render namespace wildcard and optional recursive wildcard."""
        suffix = "::*" + ("::**" if self.is_recursive else "")
        return str(self.target) + suffix

    def __str__(self) -> str:
        """Return canonical namespace-import text."""
        return self.to_sysml()


@dataclass
class FilterPackage(ImportDeclaration):
    """Represent a filtered import and its ordered filter expressions.

    ``filterPackage`` is an import declaration alternative, not a package
    declaration.  Its base declaration is either a membership import or the
    direct namespace wildcard form; each bracket expression remains a typed
    :class:`Expression` for downstream model queries.

    :param import_declaration: Unfiltered import selected by the grammar.
    :type import_declaration: :class:`pysysmlv2.syntax.ast.ImportDeclaration`
    :param filters: Ordered expressions enclosed in ``[...]``.
    :type filters: list[pysysmlv2.syntax.ast.Expression]
    """

    import_declaration: ImportDeclaration
    filters: List[Expression] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the base import followed by each bracketed expression."""
        return str(self.import_declaration) + "".join(
            "[{}]".format(expression) for expression in self.filters
        )

    def __str__(self) -> str:
        """Return canonical filtered-import text."""
        return self.to_sysml()


@dataclass
class ImportRule(SourceElement):
    """Represent an ``import`` declaration and its relationship body.

    :param import_declaration: Typed membership, namespace, or filtered import.
    :type import_declaration: :class:`pysysmlv2.syntax.ast.ImportDeclaration`
    :param relationship_body: Required terminating relationship body.
    :type relationship_body: :class:`pysysmlv2.syntax.ast.RelationshipBody`
    :param visibility: Optional visibility indicator owned by the import rule.
    :type visibility: str, optional
    :param is_all: Whether the optional ``all`` keyword follows ``import``.
    :type is_all: bool
    """

    import_declaration: ImportDeclaration
    relationship_body: RelationshipBody
    visibility: Optional[str] = None
    is_all: bool = False

    def to_sysml(self) -> str:
        """Render visibility, import keyword, declaration, and body."""
        prefix = _join(
            [
                self.visibility or "",
                "import",
                "all" if self.is_all else "",
                str(self.import_declaration),
            ]
        )
        return _append_body(prefix, str(self.relationship_body))

    def __str__(self) -> str:
        """Return canonical import-rule text."""
        return self.to_sysml()


@dataclass
class AliasMember(SourceElement):
    """Represent an alias member with explicit names and target relation.

    :param target: Unresolved qualified name after ``for``.
    :type target: :class:`pysysmlv2.syntax.ast.QualifiedReference`
    :param relationship_body: Required alias relationship body.
    :type relationship_body: :class:`pysysmlv2.syntax.ast.RelationshipBody`
    :param identification: Optional ``<short> name`` alias identification.
    :type identification: :class:`pysysmlv2.syntax.ast.Identification`, optional
    :param member_prefix: Optional visibility indicator.
    :type member_prefix: str, optional
    """

    target: QualifiedReference
    relationship_body: RelationshipBody
    identification: Optional[Identification] = None
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility, alias identification, target, and body."""
        prefix = _join(
            [
                self.member_prefix or "",
                "alias",
                str(self.identification) if self.identification else "",
                "for",
                str(self.target),
            ]
        )
        return _append_body(prefix, str(self.relationship_body))

    def __str__(self) -> str:
        """Return canonical alias-member text."""
        return self.to_sysml()


@dataclass
class ElementFilterMember(SourceElement):
    """Represent a package ``filter`` member and its typed expression.

    :param expression: Structured filter predicate expression.
    :type expression: :class:`pysysmlv2.syntax.ast.Expression`
    :param member_prefix: Optional visibility indicator.
    :type member_prefix: str, optional
    """

    expression: Expression
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility, filter keyword, expression, and semicolon."""
        return _join([self.member_prefix or "", "filter", str(self.expression)]) + ";"

    def __str__(self) -> str:
        """Return canonical element-filter-member text."""
        return self.to_sysml()


@dataclass
class InitialNodeMember(Statement):
    """Represent an action body's ``first`` initial-node member."""

    target: QualifiedReference
    relationship_body: RelationshipBody
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility, ``first``, target, and relationship body."""
        return _append_body(
            _join([self.member_prefix or "", "first", str(self.target)]),
            str(self.relationship_body),
        )

    def __str__(self) -> str:
        """Return canonical initial-node-member text."""
        return self.to_sysml()


@dataclass
class TargetSuccession(SourceElement):
    """Represent an ordinary action target succession."""

    target: TransitionSuccession
    source_end_text: Optional[str] = None

    def to_sysml(self) -> str:
        """Render optional source end, ``then``, and target connector."""
        return _join([self.source_end_text or "", "then", str(self.target)])

    def __str__(self) -> str:
        """Return canonical target-succession text."""
        return self.to_sysml()


@dataclass
class GuardedTargetSuccession(SourceElement):
    """Represent a guarded action target succession."""

    guard: GuardExpressionMember
    target: TransitionSuccession

    def to_sysml(self) -> str:
        """Render guard, ``then``, and target connector."""
        return _join([str(self.guard), "then", str(self.target)])

    def __str__(self) -> str:
        """Return canonical guarded-target-succession text."""
        return self.to_sysml()


@dataclass
class DefaultTargetSuccession(SourceElement):
    """Represent an ``else`` action target succession."""

    target: TransitionSuccession

    def to_sysml(self) -> str:
        """Render ``else`` and its target connector."""
        return _join(["else", str(self.target)])

    def __str__(self) -> str:
        """Return canonical default-target-succession text."""
        return self.to_sysml()


@dataclass
class ActionTargetSuccession(SourceElement):
    """Represent a target succession and its following usage body."""

    succession: Union[TargetSuccession, GuardedTargetSuccession, DefaultTargetSuccession]
    body: DefinitionBody

    def to_sysml(self) -> str:
        """Render succession followed by the structured usage body."""
        return _append_body(str(self.succession), str(self.body))

    def __str__(self) -> str:
        """Return canonical action-target-succession text."""
        return self.to_sysml()


@dataclass
class ActionTargetSuccessionMember(Statement):
    """Represent an action target succession with member visibility."""

    target_succession: ActionTargetSuccession
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility and nested action target succession."""
        return _join([self.member_prefix or "", str(self.target_succession)])

    def __str__(self) -> str:
        """Return canonical action-target-succession-member text."""
        return self.to_sysml()


@dataclass
class GuardedSuccession(SourceElement):
    """Represent a ``guardedSuccession`` action-body construct."""

    source: FeatureChain
    guard: GuardExpressionMember
    target: TransitionSuccession
    body: DefinitionBody
    usage_declaration: Optional[UsageDeclaration] = None
    has_succession_keyword: bool = False

    def to_sysml(self) -> str:
        """Render optional succession declaration, source, guard, target, body."""
        prefix = _join(
            [
                "succession" if self.has_succession_keyword else "",
                str(self.usage_declaration) if self.usage_declaration else "",
                "first",
                str(self.source),
                str(self.guard),
                "then",
                str(self.target),
            ]
        )
        return _append_body(prefix, str(self.body))

    def __str__(self) -> str:
        """Return canonical guarded-succession text."""
        return self.to_sysml()


@dataclass
class GuardedSuccessionMember(Statement):
    """Represent a guarded succession with member visibility."""

    succession: GuardedSuccession
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility and guarded succession."""
        return _join([self.member_prefix or "", str(self.succession)])

    def __str__(self) -> str:
        """Return canonical guarded-succession-member text."""
        return self.to_sysml()


@dataclass
class AcceptNode(ActionNode):
    """Represent an ``acceptNode`` action statement."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: AcceptNodeDeclaration
    action_body: ActionBody

    def to_sysml(self) -> str:
        """Render occurrence prefix, accept declaration, and body."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), str(self.declaration)]),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical accept-node text."""
        return self.to_sysml()


@dataclass
class SendNode(ActionNode):
    """Represent a ``sendNode`` action statement."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: SendNodeUsageDeclaration
    action_body: ActionBody

    def to_sysml(self) -> str:
        """Render send declaration and action body."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), str(self.declaration)]),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical send-node text."""
        return self.to_sysml()


@dataclass
class AssignmentNode(ActionNode):
    """Represent an ``assignmentNode`` action statement."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: AssignmentNodeDeclaration
    action_body: ActionBody

    def to_sysml(self) -> str:
        """Render assignment declaration and action body."""
        return _append_body(
            _join([str(self.occurrence_usage_prefix), str(self.declaration)]),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical assignment-node text."""
        return self.to_sysml()


@dataclass
class TerminateNode(ActionNode):
    """Represent a ``terminateNode`` action statement."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    action_body: ActionBody
    action_node_usage_declaration: Optional[ActionNodeUsageDeclaration] = None
    node_parameter: Optional[NodeParameter] = None

    def to_sysml(self) -> str:
        """Render optional declaration/parameter and terminate body."""
        return _append_body(
            _join(
                [
                    str(self.occurrence_usage_prefix),
                    str(self.action_node_usage_declaration)
                    if self.action_node_usage_declaration
                    else "",
                    "terminate",
                    str(self.node_parameter) if self.node_parameter else "",
                ]
            ),
            str(self.action_body),
        )

    def __str__(self) -> str:
        """Return canonical terminate-node text."""
        return self.to_sysml()


@dataclass
class IfNode(ActionNode):
    """Represent an ``ifNode`` and its optional else branch."""

    action_node_prefix: ActionNodePrefix
    condition: Expression
    then_body: ActionBodyParameter
    else_body: Optional[Union[ActionBodyParameter, "IfNode"]] = None

    def to_sysml(self) -> str:
        """Render condition, then body, and optional else branch."""
        result = _join(
            [
                str(self.action_node_prefix),
                "if",
                str(self.condition),
                str(self.then_body),
            ]
        )
        if self.else_body is not None:
            result = _join([result, "else", str(self.else_body)])
        return result

    def __str__(self) -> str:
        """Return canonical if-node text."""
        return self.to_sysml()


@dataclass
class WhileLoopNode(ActionNode):
    """Represent a ``while`` or bare ``loop`` action node."""

    action_node_prefix: ActionNodePrefix
    loop_kind: str
    body: ActionBodyParameter
    condition: Optional[Expression] = None
    until_condition: Optional[Expression] = None

    def to_sysml(self) -> str:
        """Render loop mode, body, and optional terminating condition."""
        if self.loop_kind == "while":
            header = _join([str(self.action_node_prefix), "while", str(self.condition)])
        else:
            header = _join([str(self.action_node_prefix), "loop"])
        result = _join([header, str(self.body)])
        if self.until_condition is not None:
            result = _join([result, "until", str(self.until_condition)]) + ";"
        return result

    def __str__(self) -> str:
        """Return canonical while/loop-node text."""
        return self.to_sysml()


@dataclass
class ForLoopNode(ActionNode):
    """Represent a ``for`` action node."""

    action_node_prefix: ActionNodePrefix
    collection: NodeParameter
    body: ActionBodyParameter
    variable_declaration: Optional[UsageDeclaration] = None

    def to_sysml(self) -> str:
        """Render loop variable, collection, and body."""
        return _join(
            [
                str(self.action_node_prefix),
                "for",
                str(self.variable_declaration) if self.variable_declaration else "",
                "in",
                str(self.collection),
                str(self.body),
            ]
        )

    def __str__(self) -> str:
        """Return canonical for-loop-node text."""
        return self.to_sysml()


@dataclass
class PerformActionUsageDeclaration(SourceElement):
    """Represent the two alternatives of ``performActionUsageDeclaration``."""

    referenced_feature: Optional[Reference] = None
    action_usage_declaration: Optional[UsageDeclaration] = None
    specialization: Optional[FeatureSpecializationPart] = None
    value_part: Optional[ValuePart] = None
    is_action: bool = False

    def to_sysml(self) -> str:
        """Render reference/action declaration, specialization, and value."""
        if self.referenced_feature is not None:
            first = str(self.referenced_feature)
        elif self.is_action:
            first = _join(
                [
                    "action",
                    str(self.action_usage_declaration) if self.action_usage_declaration else "",
                ]
            )
        else:
            first = str(self.action_usage_declaration) if self.action_usage_declaration else ""
        return _join(
            [
                first,
                str(self.specialization) if self.specialization else "",
                str(self.value_part) if self.value_part else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical perform-declaration text."""
        return self.to_sysml()


@dataclass
class PayloadFeature(SourceElement):
    """Represent the structured alternatives of ``payloadFeature``."""

    identification: Optional[Identification] = None
    specialization: Optional[FeatureSpecializationPart] = None
    value_part: Optional[ValuePart] = None
    owned_feature_typing: Optional[OwnedFeatureTyping] = None
    multiplicity_text: Optional[str] = None

    def to_sysml(self) -> str:
        """Render payload feature declaration, typing, and value fields."""
        return _join(
            [
                str(self.identification) if self.identification else "",
                str(self.owned_feature_typing) if self.owned_feature_typing else "",
                str(self.specialization) if self.specialization else "",
                self.multiplicity_text or "",
                str(self.value_part) if self.value_part else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical payload-feature text."""
        return self.to_sysml()


@dataclass
class PayloadParameter(SourceElement):
    """Represent a trigger payload parameter.

    The payload grammar has feature and trigger-value alternatives.  The
    fields retain those alternatives separately so semantic linking can later
    distinguish a payload feature from a timing/event expression.
    """

    payload_feature: Optional[PayloadFeature] = None
    identification: Optional[Identification] = None
    specialization: Optional[FeatureSpecializationPart] = None
    trigger_expression: Optional[Expression] = None

    def __post_init__(self) -> None:
        """Reject a direct construction with neither grammar alternative."""
        if self.payload_feature is None and self.trigger_expression is None:
            raise ValueError("payloadParameter requires a payload feature or trigger expression")

    def to_sysml(self) -> str:
        """Render the selected payload alternative."""
        return _join(
            [
                str(self.payload_feature) if self.payload_feature else "",
                str(self.identification) if self.identification else "",
                str(self.specialization) if self.specialization else "",
                str(self.trigger_expression) if self.trigger_expression else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical payload-parameter text."""
        return self.to_sysml()


@dataclass
class NodeParameter(SourceElement):
    """Represent a node parameter containing one structured expression."""

    expression: Expression

    def to_sysml(self) -> str:
        """Render the node parameter expression."""
        return str(self.expression)

    def __str__(self) -> str:
        """Return canonical node-parameter text."""
        return self.to_sysml()


@dataclass
class AcceptParameterPart(SourceElement):
    """Represent an accept payload and optional ``via`` node parameter."""

    payload: PayloadParameter
    via_parameter: Optional[NodeParameter] = None

    def to_sysml(self) -> str:
        """Render payload and optional via parameter."""
        return _join(
            [
                str(self.payload),
                _join(["via", str(self.via_parameter)]) if self.via_parameter is not None else "",
            ]
        )

    def __str__(self) -> str:
        """Return canonical accept-parameter text."""
        return self.to_sysml()


@dataclass
class TriggerExpression(Expression):
    """Represent ``at``, ``after`` or ``when`` trigger expressions."""

    operator: str
    argument: Expression

    def to_sysml(self) -> str:
        """Render trigger operator and argument."""
        return _join([self.operator, str(self.argument)])

    def __str__(self) -> str:
        """Return canonical trigger-expression text."""
        return self.to_sysml()


@dataclass
class EmptyActionUsage(ActionUsageNode):
    """Represent the explicit empty action ``;`` alternative."""

    def to_sysml(self) -> str:
        """Render the empty action terminator."""
        return ";"

    def __str__(self) -> str:
        """Return the empty action text."""
        return self.to_sysml()


@dataclass
class ActionUsage(ActionUsageNode):
    """Represent the concrete ``action`` usage form."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: ActionUsageDeclaration
    body: ActionBody
    is_terminate: bool = False

    def to_sysml(self) -> str:
        """Render prefix, keyword, declaration, and body."""
        prefix = _join(
            [
                str(self.occurrence_usage_prefix) if self.occurrence_usage_prefix else "",
                "action",
                str(self.declaration),
                "terminate" if self.is_terminate else "",
            ]
        )
        return _append_body(prefix, str(self.body))

    def __str__(self) -> str:
        """Return canonical action-usage text."""
        return self.to_sysml()


@dataclass
class PerformActionUsage(ActionUsageNode):
    """Represent a ``perform`` action usage."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    declaration: PerformActionUsageDeclaration
    body: ActionBody

    def to_sysml(self) -> str:
        """Render perform prefix, declaration, and body."""
        prefix = _join(
            [
                str(self.occurrence_usage_prefix) if self.occurrence_usage_prefix else "",
                "perform",
                str(self.declaration),
            ]
        )
        return _append_body(prefix, str(self.body))

    def __str__(self) -> str:
        """Return canonical perform-action text."""
        return self.to_sysml()


@dataclass
class StatePerformActionUsage(ActionUsageNode):
    """Represent the state-only perform action without a ``perform`` token.

    ``statePerformActionUsage`` is nested below ``entry``, ``do`` or
    ``exit``.  Its grammar starts directly with
    ``performActionUsageDeclaration``; adding a literal ``perform`` during
    rendering would therefore change the source form.
    """

    declaration: PerformActionUsageDeclaration
    body: ActionBody

    def to_sysml(self) -> str:
        """Render declaration and action body in state-subaction position."""
        return _append_body(str(self.declaration), str(self.body))

    def __str__(self) -> str:
        """Return canonical state perform-action text."""
        return self.to_sysml()


@dataclass
class TransitionPerformActionUsage(ActionUsageNode):
    """Represent a transition effect's perform declaration.

    The ``transitionPerformActionUsage`` grammar does not contain a
    ``perform`` keyword.  It is therefore distinct from
    :class:`PerformActionUsage`, even though both carry the same declaration
    production.
    """

    declaration: PerformActionUsageDeclaration
    body: Optional[ActionBody] = None

    def to_sysml(self) -> str:
        """Render declaration and optional transition-effect body."""
        if self.body is None:
            return str(self.declaration)
        if self.body.declaration_only:
            return str(self.declaration) + ";"
        return _append_body(str(self.declaration), str(self.body))

    def __str__(self) -> str:
        """Return canonical transition-perform-effect text."""
        return self.to_sysml()


@dataclass
class AcceptActionUsage(ActionUsageNode):
    """Represent an ``accept`` action usage."""

    declaration: AcceptNodeDeclaration
    body: Optional[ActionBody] = None

    def to_sysml(self) -> str:
        """Render accept declaration and body."""
        prefix = str(self.declaration)
        return _append_body(prefix, str(self.body)) if self.body else prefix

    def __str__(self) -> str:
        """Return canonical accept-action text."""
        return self.to_sysml()


@dataclass
class SendActionUsage(ActionUsageNode):
    """Represent a ``send`` action usage."""

    declaration: SendNodeDeclaration
    body: Optional[ActionBody] = None

    def to_sysml(self) -> str:
        """Render send declaration and body."""
        prefix = str(self.declaration)
        return _append_body(prefix, str(self.body)) if self.body else prefix

    def __str__(self) -> str:
        """Return canonical send-action text."""
        return self.to_sysml()


@dataclass
class AssignmentActionUsage(ActionUsageNode):
    """Represent an ``assign`` action usage."""

    declaration: AssignmentNodeDeclaration
    body: Optional[ActionBody] = None

    def to_sysml(self) -> str:
        """Render assignment declaration and body."""
        prefix = str(self.declaration)
        return _append_body(prefix, str(self.body)) if self.body else prefix

    def __str__(self) -> str:
        """Return canonical assignment-action text."""
        return self.to_sysml()


@dataclass
class StateSubactionMembership(SourceElement):
    """Represent the semantic shape synthesized by an entry/do/exit member.

    The parser normally exposes the more concrete :class:`EntryActionMember`,
    :class:`DoActionMember`, and :class:`ExitActionMember` nodes below.  This
    class remains available for the later semantic projection, where the OMG
    ``StateSubactionMembership`` kind/action relationship is materialized.
    """

    kind: StateSubactionKind
    action: Optional[ActionUsageNode] = None

    def to_sysml(self) -> str:
        """Render the semantic membership in its concrete keyword form."""
        return _append_body(self.kind.value, str(self.action) if self.action else ";")

    def __str__(self) -> str:
        """Return canonical state-subaction text."""
        return self.to_sysml()


@dataclass
class EntryTransitionMember(SourceElement):
    """Represent one concrete ``entryTransitionMember``."""

    target: TransitionSuccession
    member_prefix: Optional[str] = None
    guard: Optional[Expression] = None

    def to_sysml(self) -> str:
        """Render optional visibility, guard, target, and semicolon."""
        return (
            _join(
                [
                    self.member_prefix or "",
                    "if " + str(self.guard) if self.guard else "",
                    "then",
                    str(self.target),
                ]
            )
            + ";"
        )

    def __str__(self) -> str:
        """Return canonical entry-transition-member text."""
        return self.to_sysml()


@dataclass
class EntryActionMember(SourceElement):
    """Represent the concrete ``entryActionMember`` grammar rule."""

    state_action_usage: ActionUsageNode
    member_prefix: Optional[str] = None
    entry_transition_members: List[EntryTransitionMember] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render entry keyword, state action, and attached transitions."""
        prefix = _join([self.member_prefix or "", "entry"])
        rendered = _append_body(prefix, str(self.state_action_usage))
        return rendered + (
            " " + " ".join(str(item) for item in self.entry_transition_members)
            if self.entry_transition_members
            else ""
        )

    def __str__(self) -> str:
        """Return canonical entry-action-member text."""
        return self.to_sysml()


@dataclass
class DoActionMember(SourceElement):
    """Represent the concrete ``doActionMember`` grammar rule."""

    state_action_usage: ActionUsageNode
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render do keyword and state action."""
        return _append_body(_join([self.member_prefix or "", "do"]), str(self.state_action_usage))

    def __str__(self) -> str:
        """Return canonical do-action-member text."""
        return self.to_sysml()


@dataclass
class ExitActionMember(SourceElement):
    """Represent the concrete ``exitActionMember`` grammar rule."""

    state_action_usage: ActionUsageNode
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render exit keyword and state action."""
        return _append_body(_join([self.member_prefix or "", "exit"]), str(self.state_action_usage))

    def __str__(self) -> str:
        """Return canonical exit-action-member text."""
        return self.to_sysml()


@dataclass
class SourceSuccession(SourceElement):
    """Represent the concrete ``then`` source-succession marker."""

    keyword: str = "then"

    def to_sysml(self) -> str:
        """Render the leading ``then`` source succession."""
        return self.keyword

    def __str__(self) -> str:
        """Return canonical source-succession text."""
        return self.to_sysml()


@dataclass
class BehaviorUsageMember(SourceElement):
    """Represent a behavior usage with its member prefix."""

    behavior_usage: SourceElement
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render prefix and nested behavior usage."""
        return _join([self.member_prefix or "", str(self.behavior_usage)])

    def __str__(self) -> str:
        """Return canonical behavior-usage-member text."""
        return self.to_sysml()


@dataclass
class StructureUsageMember(SourceElement):
    """Represent the grammar-owned prefix and structural usage element.

    ``structureUsageMember`` is deliberately distinct from
    :class:`DefinitionBodyItem`: its grammar production owns a
    ``memberPrefix`` but does not permit a source-succession prefix.

    :param structure_usage: Structured usage emitted by the member.
    :type structure_usage: :class:`pysysmlv2.syntax.ast.SourceElement`
    :param member_prefix: Optional visibility/member prefix, defaults to
        ``None``.
    :type member_prefix: str, optional

    Example::

        >>> str(StructureUsageMember(RawElement("part p;")))
        'part p;'
    """

    structure_usage: SourceElement
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render the member prefix and structural usage."""
        return _join([self.member_prefix or "", str(self.structure_usage)])

    def __str__(self) -> str:
        """Return canonical structure-usage-member text."""
        return self.to_sysml()


@dataclass
class NonOccurrenceUsageMember(SourceElement):
    """Represent a non-occurrence usage with its member visibility prefix."""

    usage: SourceElement
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility followed by the non-occurrence usage."""
        return _join([self.member_prefix or "", str(self.usage)])

    def __str__(self) -> str:
        """Return canonical non-occurrence-usage-member text."""
        return self.to_sysml()


@dataclass
class TargetTransitionUsageMember(SourceElement):
    """Represent a target-transition member attached to a behavior usage."""

    target_transition_usage: TargetTransitionUsage
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render prefix and target transition."""
        return _join([self.member_prefix or "", str(self.target_transition_usage)])

    def __str__(self) -> str:
        """Return canonical target-transition-member text."""
        return self.to_sysml()


@dataclass
class BehaviorUsageStateMember(SourceElement):
    """Represent the multi-child state-body behavior-usage alternative."""

    behavior_usage_member: BehaviorUsageMember
    source_succession: Optional[SourceSuccession] = None
    target_transition_members: List[TargetTransitionUsageMember] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render optional source, behavior, and target-transition members."""
        return " ".join(
            str(item)
            for item in [
                self.source_succession,
                self.behavior_usage_member,
                *self.target_transition_members,
            ]
            if item is not None
        )

    def __str__(self) -> str:
        """Return canonical behavior-usage-state-member text."""
        return self.to_sysml()


@dataclass
class TransitionSuccession(SourceElement):
    """Represent ``TransitionSuccession`` with explicit connector end."""

    connector_end: Reference

    def to_sysml(self) -> str:
        """Render the target connector end."""
        return str(self.connector_end)

    def __str__(self) -> str:
        """Return canonical transition-succession text."""
        return self.to_sysml()


@dataclass
class TransitionUsageMember(SourceElement):
    """Represent the concrete ``transitionUsageMember`` wrapper."""

    transition_usage: TransitionUsage
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render prefix and transition usage."""
        return _join([self.member_prefix or "", str(self.transition_usage)])

    def __str__(self) -> str:
        """Return canonical transition-usage-member text."""
        return self.to_sysml()


@dataclass
class TriggerActionMember(SourceElement):
    """Represent ``TriggerActionMember`` and its accept parameter."""

    trigger_action: AcceptParameterPart

    def to_sysml(self) -> str:
        """Render ``accept`` and structured payload parameter."""
        return _join(["accept", str(self.trigger_action)])

    def __str__(self) -> str:
        """Return canonical trigger-action-member text."""
        return self.to_sysml()


@dataclass
class GuardExpressionMember(SourceElement):
    """Represent ``GuardExpressionMember`` with a structured expression."""

    owned_expression: Expression

    def to_sysml(self) -> str:
        """Render ``if`` and the owned expression."""
        return _join(["if", str(self.owned_expression)])

    def __str__(self) -> str:
        """Return canonical guard-expression-member text."""
        return self.to_sysml()


@dataclass
class EffectBehaviorMember(SourceElement):
    """Represent ``EffectBehaviorMember`` with an explicit action variant."""

    effect_behavior_usage: ActionUsageNode

    def to_sysml(self) -> str:
        """Render ``do`` and effect action usage."""
        return _join(["do", str(self.effect_behavior_usage) if self.effect_behavior_usage else ""])

    def __str__(self) -> str:
        """Return canonical effect-behavior-member text."""
        return self.to_sysml()


@dataclass
class TransitionUsage(SourceElement):
    """Represent the complete concrete ``TransitionUsage`` grammar rule."""

    source_feature_chain: FeatureChain
    transition_succession_member: TransitionSuccession
    action_body: ActionBody
    usage_declaration: Optional[UsageDeclaration] = None
    is_first: bool = False
    trigger_action_member: Optional[TriggerActionMember] = None
    guard_expression_member: Optional[GuardExpressionMember] = None
    effect_behavior_member: Optional[EffectBehaviorMember] = None
    guard_before_trigger: bool = False

    def to_sysml(self) -> str:
        """Render each grammar field in its normative source order."""
        declaration = _join(
            [
                str(self.usage_declaration) if self.usage_declaration else "",
                "first" if self.is_first else "",
            ]
        )
        trigger = str(self.trigger_action_member) if self.trigger_action_member else ""
        guard = str(self.guard_expression_member) if self.guard_expression_member else ""
        conditionals = [guard, trigger] if self.guard_before_trigger else [trigger, guard]
        prefix = _join(
            [
                "transition",
                declaration,
                str(self.source_feature_chain),
                *conditionals,
                str(self.effect_behavior_member) if self.effect_behavior_member else "",
                "then",
                str(self.transition_succession_member),
            ]
        )
        return _append_body(prefix, str(self.action_body))

    def __str__(self) -> str:
        """Return canonical transition-usage text."""
        return self.to_sysml()


@dataclass
class TargetTransitionUsage(SourceElement):
    """Represent the normative concrete alternatives of ``TargetTransitionUsage``.

    Target shorthand permits trigger-before-guard or guard-only forms.  A
    guard-before-trigger ordering belongs to the complete ``TransitionUsage``
    rule and is intentionally not represented here.
    """

    transition_succession_member: TransitionSuccession
    action_body: ActionBody
    form: TargetTransitionForm = TargetTransitionForm.BARE
    trigger_action_member: Optional[TriggerActionMember] = None
    guard_expression_member: Optional[GuardExpressionMember] = None
    effect_behavior_member: Optional[EffectBehaviorMember] = None

    def to_sysml(self) -> str:
        """Render selected shorthand alternative and each child field."""
        transition_keyword = "transition" if self.form is TargetTransitionForm.TRANSITION else ""
        trigger = str(self.trigger_action_member) if self.trigger_action_member else ""
        guard = str(self.guard_expression_member) if self.guard_expression_member else ""
        conditionals = [trigger, guard]
        prefix = _join(
            [
                transition_keyword,
                *conditionals,
                str(self.effect_behavior_member) if self.effect_behavior_member else "",
                "then",
                str(self.transition_succession_member),
            ]
        )
        return _append_body(prefix, str(self.action_body))

    def __str__(self) -> str:
        """Return canonical target-transition-usage text."""
        return self.to_sysml()


@dataclass
class StateDefBody(SourceElement):
    """Represent the distinct ``stateDefBody`` grammar production."""

    is_parallel: bool = False
    is_declaration_only: bool = False
    state_body_members: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render parallel flag and ordered state body members."""
        body = _render_block(self.state_body_members, declaration_only=self.is_declaration_only)
        return (
            body if self.is_declaration_only else (("parallel " if self.is_parallel else "") + body)
        )

    def __str__(self) -> str:
        """Return canonical state-definition-body text."""
        return self.to_sysml()


@dataclass
class StateUsageBody(SourceElement):
    """Represent the distinct ``stateUsageBody`` grammar production."""

    is_parallel: bool = False
    is_declaration_only: bool = False
    state_body_members: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render parallel flag and ordered state body members."""
        body = _render_block(self.state_body_members, declaration_only=self.is_declaration_only)
        return (
            body if self.is_declaration_only else (("parallel " if self.is_parallel else "") + body)
        )

    def __str__(self) -> str:
        """Return canonical state-usage-body text."""
        return self.to_sysml()


@dataclass
class StateDefinition(SourceElement):
    """Represent the concrete syntax of OMG ``StateDefinition``."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition_declaration: DefinitionDeclaration
    state_def_body: StateDefBody

    def to_sysml(self) -> str:
        """Render prefix, ``state def``, declaration, and body."""
        prefix = _join(
            [
                str(self.occurrence_definition_prefix),
                "state def",
                str(self.definition_declaration),
            ]
        )
        return _append_body(prefix, str(self.state_def_body))

    def __str__(self) -> str:
        """Return canonical state-definition text."""
        return self.to_sysml()


@dataclass
class StateUsage(SourceElement):
    """Represent the concrete syntax of OMG ``StateUsage``."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    action_usage_declaration: ActionUsageDeclaration
    state_usage_body: StateUsageBody

    def to_sysml(self) -> str:
        """Render prefix, ``state``, declaration, and body."""
        prefix = _join(
            [
                str(self.occurrence_usage_prefix),
                "state",
                str(self.action_usage_declaration),
            ]
        )
        return _append_body(prefix, str(self.state_usage_body))

    def __str__(self) -> str:
        """Return canonical state-usage text."""
        return self.to_sysml()


@dataclass
class ExhibitStateUsage(SourceElement):
    """Represent the concrete ``exhibitStateUsage`` grammar production."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    state_usage_body: StateUsageBody
    owned_reference_subsetting: Optional[Reference] = None
    feature_specialization_part: Optional[FeatureSpecializationPart] = None
    state_usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None

    def to_sysml(self) -> str:
        """Render reference/state alternative, value, and body."""
        if self.owned_reference_subsetting is not None:
            target = _join(
                [
                    str(self.owned_reference_subsetting),
                    str(self.feature_specialization_part)
                    if self.feature_specialization_part
                    else "",
                ]
            )
        else:
            target = _join(
                ["state", str(self.state_usage_declaration) if self.state_usage_declaration else ""]
            )
        body = str(self.state_usage_body)
        return _append_body(
            _join(
                [
                    str(self.occurrence_usage_prefix),
                    "exhibit",
                    target,
                    str(self.value_part) if self.value_part else "",
                ]
            ),
            body,
        )

    def __str__(self) -> str:
        """Return canonical exhibit-state-usage text."""
        return self.to_sysml()


@dataclass
class Package(SourceElement):
    """Represent a package with ordered model-owned members."""

    identification: Optional[Identification] = None
    members: List[SourceElement] = field(default_factory=list)
    is_library: bool = False
    is_standard: bool = False
    declaration_only: bool = False
    prefix_metadata: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render package prefix, declaration, and ordered body members."""
        keyword = "library package" if self.is_library else "package"
        if self.is_standard and self.is_library:
            keyword = "standard " + keyword
        heading = _join(
            self.prefix_metadata
            + [keyword, str(self.identification) if self.identification else ""]
        )
        return _append_body(
            heading, _render_block(self.members, declaration_only=self.declaration_only)
        )

    def __str__(self) -> str:
        """Return canonical package text."""
        return self.to_sysml()


@dataclass
class PackageMember(SourceElement):
    """Represent a package member and its optional visibility prefix.

    ``packageMember`` is not a meaningless one-child dispatcher: its
    ``member_prefix`` carries the concrete visibility token.  Keeping that
    token beside the child avoids mutating the child node after construction
    and preserves the grammar-level ownership of the prefix.

    :param element: Concrete package definition or usage node.
    :type element: :class:`pysysmlv2.syntax.ast.ASTNode`
    :param member_prefix: Optional ``public``, ``private`` or ``protected``
        spelling, defaults to ``None``.
    :type member_prefix: str, optional
    """

    element: SourceElement
    member_prefix: Optional[str] = None

    def to_sysml(self) -> str:
        """Render visibility followed by the owned package element."""
        return _join([self.member_prefix or "", str(self.element)])

    def __str__(self) -> str:
        """Return canonical package-member text."""
        return self.to_sysml()


@dataclass
class Comment(SourceElement):
    """Represent model-owned ``comment`` syntax."""

    is_comment: bool = False
    declaration: Optional[Identification] = None
    about: List[QualifiedReference] = field(default_factory=list)
    locale: Optional[str] = None
    body: str = ""

    def to_sysml(self) -> str:
        """Render comment declaration, locale, and regular-comment body."""
        return _join(
            [
                "comment" if self.is_comment or self.declaration or self.about else "",
                str(self.declaration) if self.declaration else "",
                "about " + ", ".join(str(item) for item in self.about) if self.about else "",
                "locale " + self.locale if self.locale else "",
                _relative_source(self.body),
            ]
        ) or _relative_source(self.body)

    def __str__(self) -> str:
        """Return canonical comment text."""
        return self.to_sysml()


@dataclass
class Documentation(SourceElement):
    """Represent model-owned ``doc`` syntax."""

    identification: Optional[Identification] = None
    locale: Optional[str] = None
    body: str = ""

    def to_sysml(self) -> str:
        """Render documentation declaration, locale, and body."""
        return _join(
            [
                "doc",
                str(self.identification) if self.identification else "",
                "locale " + self.locale if self.locale else "",
                _relative_source(self.body),
            ]
        )

    def __str__(self) -> str:
        """Return canonical documentation text."""
        return self.to_sysml()


@dataclass
class Model(SourceElement):
    """Represent one complete SysML source document."""

    members: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render ordered top-level elements separated by blank lines."""
        return "\n\n".join(str(item) for item in self.members if str(item))

    def __str__(self) -> str:
        """Return canonical complete-document text."""
        return self.to_sysml()


def structural_text(node: ASTNode) -> str:
    """Return canonical SysML text for a concrete AST node.

    :param node: Concrete source AST node.
    :type node: :class:`pysysmlv2.syntax.ast.ASTNode`
    :return: Parseable SysML text.
    :rtype: str
    """
    return str(node)


__all__ = [
    "ASTNode",
    "ActionDefinition",
    "ActionNode",
    "ActionNodeMember",
    "ActionNodePrefix",
    "ActionUsageNode",
    "AcceptActionUsage",
    "AcceptParameterPart",
    "ActionBody",
    "ActionNodeUsageDeclaration",
    "ActionUsage",
    "ActionUsageDeclaration",
    "AllExpression",
    "AttributeDefinition",
    "AttributeUsage",
    "AcceptNodeDeclaration",
    "ArgumentList",
    "BracketExpression",
    "AssignmentActionUsage",
    "AssignmentNode",
    "BinaryExpression",
    "BinaryConnectorPart",
    "BindingConnectorAsUsage",
    "BinaryInterfacePart",
    "BodyExpression",
    "CastExpression",
    "Comment",
    "CommentExpression",
    "ConjugatedPortTyping",
    "ConnectionDefinition",
    "ConnectionUsage",
    "ConnectorEnd",
    "ConnectorPart",
    "ControlNode",
    "ControlNodePrefix",
    "ConditionalExpression",
    "ConstructorExpression",
    "CoalesceExpression",
    "DecisionNode",
    "DeclaredFeatureTyping",
    "DefaultTargetSuccession",
    "DefaultInterfaceEnd",
    "DoActionMember",
    "Definition",
    "DefinitionDeclaration",
    "DefinitionBody",
    "DefinitionBodyItem",
    "DefinitionPrefix",
    "Documentation",
    "EmptyActionUsage",
    "EffectBehaviorMember",
    "EntryActionMember",
    "EntryTransitionMember",
    "EventOccurrenceUsage",
    "EndOccurrenceUsageElement",
    "EndFeatureUsage",
    "EndUsagePrefix",
    "ExhibitStateUsage",
    "FeatureChain",
    "FeatureChainExpression",
    "FeatureDeclaration",
    "FeatureIdentification",
    "FeatureRelationshipPart",
    "FeatureReferenceExpression",
    "FeatureSpecialization",
    "FeatureSpecializationPart",
    "ConjugationPart",
    "ChainingPart",
    "InvertingPart",
    "TypeFeaturingPart",
    "TypeRelationshipPart",
    "DisjoiningPart",
    "UnioningPart",
    "IntersectingPart",
    "DifferencingPart",
    "ForkNode",
    "Expression",
    "FunctionBodyItem",
    "FunctionOperationExpression",
    "ForLoopNode",
    "GuardedSuccession",
    "GuardedSuccessionMember",
    "GuardedTargetSuccession",
    "Identification",
    "InterfaceBody",
    "InterfaceDefinition",
    "InterfaceEnd",
    "InterfaceNonOccurrenceUsageMember",
    "InterfaceOccurrenceUsageMember",
    "InterfacePart",
    "InterfaceUsage",
    "InterfaceUsageDeclaration",
    "IndividualDefinition",
    "IndividualUsage",
    "InfinityLiteral",
    "IfNode",
    "ItemDefinition",
    "ItemUsage",
    "InitialNodeMember",
    "IndexExpression",
    "IntegerLiteral",
    "InvocationExpression",
    "LiteralKind",
    "MetadataAccessExpression",
    "MetadataBody",
    "MetadataBodyFeature",
    "MetadataBodyUsage",
    "MetadataFeature",
    "MetadataFeatureDeclaration",
    "MetadataCastExpression",
    "MergeNode",
    "Model",
    "NamedArgument",
    "NaryConnectorPart",
    "NaryInterfacePart",
    "NodeParameter",
    "NonFeatureMember",
    "NonOccurrenceUsageMember",
    "NullExpression",
    "OccurrenceDefinition",
    "OccurrenceDefinitionPrefix",
    "OccurrenceUsage",
    "OccurrenceUsagePrefix",
    "OwnedCrossFeature",
    "OwnedFeatureTyping",
    "Package",
    "PackageMember",
    "PartDefinition",
    "PartUsage",
    "PortionUsage",
    "PortDefinition",
    "PortUsage",
    "ParenthesizedExpression",
    "PayloadFeature",
    "PayloadParameter",
    "PerformActionUsage",
    "PerformActionUsageDeclaration",
    "QualifiedReference",
    "Reference",
    "ReferenceUsage",
    "DottedQualifiedReference",
    "ElementFilterMember",
    "RawElement",
    "RealLiteral",
    "RelationshipBody",
    "ImportDeclaration",
    "MembershipImport",
    "NamespaceImport",
    "FilterPackage",
    "ImportRule",
    "AliasMember",
    "ReturnFeatureMember",
    "ResultExpressionMember",
    "SequenceExpression",
    "SelectExpression",
    "SendNode",
    "SendNodeDeclaration",
    "SendNodeUsageDeclaration",
    "SenderReceiverPart",
    "SendActionUsage",
    "SourceSpan",
    "StateDefinition",
    "StateDefBody",
    "StatePerformActionUsage",
    "StateSubactionKind",
    "StateSubactionMembership",
    "StateUsageBody",
    "StateUsage",
    "StructureUsageMember",
    "SubclassificationPart",
    "SuccessionAsUsage",
    "StringLiteral",
    "TargetTransitionForm",
    "TargetTransitionUsage",
    "TargetTransitionUsageMember",
    "TargetSuccession",
    "TerminateNode",
    "TransitionFeatureKind",
    "TransitionSuccession",
    "TransitionPerformActionUsage",
    "TransitionUsageMember",
    "TransitionUsage",
    "TriggerActionMember",
    "TriggerExpression",
    "UnaryExpression",
    "UsageDeclaration",
    "UsagePrefix",
    "ValuePart",
    "VariantUsage",
    "DoActionMember",
    "ExitActionMember",
    "GuardExpressionMember",
    "BehaviorUsageMember",
    "BehaviorUsageStateMember",
    "SourceSuccession",
    "SourceElement",
    "Statement",
    "TypeOperationExpression",
    "AssignmentNodeDeclaration",
    "ActionBodyParameter",
    "ActionTargetSuccession",
    "ActionTargetSuccessionMember",
    "AcceptNode",
    "AcceptNodeDeclaration",
    "WhileLoopNode",
    "JoinNode",
    "NodeParameter",
    "Usage",
    "BooleanLiteral",
    "structural_text",
]
