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
``source_path`` and ``span`` after construction, so direct construction still
allows provenance to be absent without weakening required syntax fields.

The AST is intentionally not the linked SysML semantic model.  Qualified
names, feature chains, transition endpoints, and action references remain
source-level objects until a workspace/linker layer resolves them.  This
keeps source spans meaningful and prevents parser recovery from inventing
semantic identity.  The listener is the sole assembler and uses explicit
``exit<GrammarRule>`` callbacks; generated parser contexts are never converted
through reflection or a generic text scanner.  ``RawElement`` is restricted
to an explicit non-state compatibility boundary while coverage is staged; it
must not appear on ordinary expression, action, transition, or state paths.

Every concrete node owns its exporter.  ``str(node)`` and ``to_sysml()`` build
canonical, parseable SysML text from the node's named fields.  ``source_path``
and ``span`` are the only fields shared by all nodes; they are provenance, not
semantic identity or a generic traversal/rendering mechanism.

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
   * - Expressions
     - :class:`BooleanLiteral`, :class:`UnaryExpression`, :class:`BinaryExpression`,
       :class:`ConditionalExpression`, :class:`InvocationExpression`,
       :class:`FeatureAccessExpression`, and related nodes
     - Operator tree and argument structure, not opaque text.
   * - State/action syntax
     - :class:`StateDefinition`, :class:`StateUsage`,
       :class:`StateSubactionMembership`, :class:`TransitionUsage`,
       :class:`TargetTransitionUsage`, :class:`ActionBody`,
       :class:`ActionNode`, :class:`ControlNode`
     - Concrete state-machine forms from SysML 2.0 section 8.2.2.18.
   * - Document roots
     - :class:`Package`, :class:`Model`, :class:`Comment`,
       :class:`Documentation`
     - Ordered source members and model-owned textual elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence, Union


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

        :param other: Candidate nested source range.
        :type other: :class:`pysysmlv2.syntax.ast.SourceSpan`
        :return: ``True`` when both boundaries are contained.
        :rtype: bool
        """
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

    :param source_path: Original document path or URI, if known.
    :type source_path: str, optional
    :param span: Source range occupied by the node, if known.
    :type span: :class:`pysysmlv2.syntax.ast.SourceSpan`, optional
    :ivar source_path: Original document path or URI.
    :vartype source_path: str, optional
    :ivar span: Source range occupied by the node.
    :vartype span: :class:`pysysmlv2.syntax.ast.SourceSpan`, optional

    Example::

        >>> ASTNode(source_path="demo.sysml").source_path
        'demo.sysml'
    """

    source_path: Optional[str] = field(default=None, init=False)
    span: Optional[SourceSpan] = field(default=None, init=False)

    def __init__(
        self, source_path: Optional[str] = None, span: Optional[SourceSpan] = None
    ) -> None:
        """Initialize provenance for a directly-created base node.

        Concrete dataclass nodes intentionally omit these fields from their
        generated constructor so grammar-required fields remain required.
        Their generated ``__init__`` invokes :meth:`__post_init__`.
        """
        self.source_path = source_path
        self.span = span

    def __post_init__(self) -> None:
        """Initialize omitted provenance fields on concrete dataclass nodes."""
        if not hasattr(self, "source_path"):
            self.source_path = None
        if not hasattr(self, "span"):
            self.span = None

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
    """Concrete alternatives of ``TargetTransitionUsage``."""

    BARE = "bare"
    TRANSITION = "transition"
    TRIGGER = "trigger"
    GUARD = "guard"


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

    def to_sysml(self) -> str:
        """Render the unresolved qualified name."""
        return ("$::" if self.is_absolute else "") + "::".join(self.segments)

    def __str__(self) -> str:
        """Return canonical qualified-name text."""
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
    :param references: Ordered unresolved references in this specialization.
    :type references: list[pysysmlv2.syntax.ast.QualifiedReference]
    """

    operator: str
    references: List[QualifiedReference] = field(default_factory=list)

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
    :param has_empty_multiplicity: Whether ``individual`` carries the empty
        multiplicity production.
    :type has_empty_multiplicity: bool
    :param extension_keywords: Prefix metadata/extension spellings retained in
        source order.
    :type extension_keywords: list[str]
    """

    basic_definition_keyword: Optional[str] = None
    is_individual: bool = False
    has_empty_multiplicity: bool = False
    extension_keywords: List[str] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the occurrence-definition prefix."""
        parts = []
        if self.basic_definition_keyword:
            parts.append(self.basic_definition_keyword)
        if self.is_individual:
            parts.append("individual")
        if self.has_empty_multiplicity:
            parts.append("[]")
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
        return "{} {} {}".format(
            str(self.left),
            self.operator,
            str(self.right),
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
            str(self.left),
            str(self.right),
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
            self.condition,
            self.then_expression,
            self.else_expression,
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
    """Represent ``ownedExpression [ sequenceExpressionList? ]``."""

    target: Expression
    indices: Optional[SequenceExpression] = None

    def to_sysml(self) -> str:
        """Render target and bracketed index sequence."""
        return "{}[{}]".format(
            str(self.target),
            str(self.indices) if self.indices else "",
        )

    def __str__(self) -> str:
        """Return canonical index-expression text."""
        return self.to_sysml()


@dataclass
class FeatureAccessExpression(Expression):
    """Represent ``ownedExpression . qualifiedName`` member access."""

    target: Expression
    member: QualifiedReference

    def to_sysml(self) -> str:
        """Render dotted member access."""
        return "{}.{}".format(self.target, self.member)

    def __str__(self) -> str:
        """Return canonical feature-access text."""
        return self.to_sysml()


@dataclass
class BodyAccessExpression(Expression):
    """Represent the ``ownedExpression .? bodyExpression`` alternative."""

    target: Expression
    body_expression: BodyExpression

    def to_sysml(self) -> str:
        """Render safe access to a body expression."""
        return "{}.?{}".format(
            self.target,
            self.body_expression,
        )

    def __str__(self) -> str:
        """Return canonical body-access text."""
        return self.to_sysml()


@dataclass
class ArrowExpression(Expression):
    """Represent ``ownedExpression -> qualifiedName (body|arguments)``."""

    target: Expression
    member: QualifiedReference
    result: Union[BodyExpression, ArgumentList]

    def to_sysml(self) -> str:
        """Render arrow target, member, and result node."""
        return "{} -> {}{}".format(
            self.target,
            self.member,
            self.result,
        )

    def __str__(self) -> str:
        """Return canonical arrow-expression text."""
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
    :type items: list[pysysmlv2.syntax.ast.SourceElement]
    """

    items: List[SourceElement] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Render the body expression and its statement items."""
        return _render_block(self.items, declaration_only=False)

    def __str__(self) -> str:
        """Return canonical body-expression text."""
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
class RawElement(SourceElement):
    """Preserve an unsupported non-state grammar element losslessly.

    This is a deliberately narrow compatibility boundary for package/action
    productions that have not yet received a handwritten node.  It is not used
    for expressions, state bodies, transitions, or action statements covered
    by the listener.  Unlike the old opaque node it has no grammar-name field:
    the only retained value is explicitly the source fragment itself.

    :param source_text: Parseable source fragment for the unsupported element.
    :type source_text: str
    :param member_prefix: Optional visibility/member prefix.
    :type member_prefix: str
    """

    source_text: str
    member_prefix: str = ""

    def to_sysml(self) -> str:
        """Render the retained source fragment."""
        return _join([self.member_prefix, self.source_text.strip()])

    def __str__(self) -> str:
        """Return the retained parseable fragment."""
        return self.to_sysml()


@dataclass
class DefinitionBodyItem(SourceElement):
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


@dataclass
class PartDefinition(SourceElement):
    """Represent a ``part def`` backed by a structured definition body."""

    occurrence_definition_prefix: OccurrenceDefinitionPrefix
    definition: Definition

    def to_sysml(self) -> str:
        """Render part-definition prefix, keyword, and nested definition."""
        return _join(
            [
                str(self.occurrence_definition_prefix),
                "part def",
                str(self.definition),
            ]
        )

    def __str__(self) -> str:
        """Return canonical part-definition text."""
        return self.to_sysml()


@dataclass
class PartUsage(SourceElement):
    """Represent a ``part`` usage backed by a structured usage body."""

    occurrence_usage_prefix: OccurrenceUsagePrefix
    usage: Usage

    def to_sysml(self) -> str:
        """Render part-usage prefix, keyword, and nested usage."""
        return _join([str(self.occurrence_usage_prefix), "part", str(self.usage)])

    def __str__(self) -> str:
        """Return canonical part-usage text."""
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
    """Represent the explicit ``via``/``to`` sender-receiver relationship."""

    via_parameter: Optional[NodeParameter] = None
    to_parameter: Optional[NodeParameter] = None
    has_empty_parameter: bool = False

    def to_sysml(self) -> str:
        """Render sender/receiver keywords and structured node parameters."""
        if self.has_empty_parameter:
            source = "()"
        else:
            source = _join(["via", str(self.via_parameter) if self.via_parameter else ""])
        return _join([source, "to", str(self.to_parameter) if self.to_parameter else ""])

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
    has_empty_parameter: bool = False

    def to_sysml(self) -> str:
        """Render full send-node declaration alternatives."""
        parameter = (
            "()"
            if self.has_empty_parameter
            else str(self.send_parameter)
            if self.send_parameter
            else ""
        )
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

    def to_sysml(self) -> str:
        """Render optional action declaration, assignment target, and value."""
        return _join(
            [
                str(self.action_node_usage_declaration)
                if self.action_node_usage_declaration
                else "",
                "assign",
                str(self.target),
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
    """Represent a ``while`` or ``loop ()`` action node."""

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
            header = _join([str(self.action_node_prefix), "loop", "()"])
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

    referenced_feature: Optional[QualifiedReference] = None
    action_usage_declaration: Optional[UsageDeclaration] = None
    specialization: Optional[FeatureSpecializationPart] = None
    value_part: Optional[ValuePart] = None

    def to_sysml(self) -> str:
        """Render reference/action declaration, specialization, and value."""
        first = self.referenced_feature or self.action_usage_declaration
        return _join(
            [
                str(first) if first else "",
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
    feature_reference: Optional[QualifiedReference] = None
    multiplicity_text: Optional[str] = None

    def to_sysml(self) -> str:
        """Render payload feature declaration, typing, and value fields."""
        return _join(
            [
                str(self.identification) if self.identification else "",
                str(self.feature_reference) if self.feature_reference else "",
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

    def to_sysml(self) -> str:
        """Render prefix, keyword, declaration, and body."""
        prefix = _join(
            [
                str(self.occurrence_usage_prefix) if self.occurrence_usage_prefix else "",
                "action",
                str(self.declaration),
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
        return _join([self.kind.value, str(self.action) if self.action else ";"])

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
    """Represent a structural usage member and its optional source prefix."""

    structure_usage: SourceElement
    member_prefix: Optional[str] = None
    source_succession: Optional[SourceSuccession] = None

    def to_sysml(self) -> str:
        """Render source succession, visibility, and structural usage."""
        return _join(
            [
                str(self.source_succession) if self.source_succession else "",
                self.member_prefix or "",
                str(self.structure_usage),
            ]
        )

    def __str__(self) -> str:
        """Return canonical structure-usage-member text."""
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

    connector_end: QualifiedReference

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
    input_parameter_count: int = 0
    trigger_action_member: Optional[TriggerActionMember] = None
    guard_expression_member: Optional[GuardExpressionMember] = None
    effect_behavior_member: Optional[EffectBehaviorMember] = None

    def to_sysml(self) -> str:
        """Render each grammar field in its normative source order."""
        declaration = _join(
            [
                str(self.usage_declaration) if self.usage_declaration else "",
                "first" if self.is_first else "",
            ]
        )
        prefix = _join(
            [
                "transition",
                declaration,
                str(self.source_feature_chain),
                str(self.trigger_action_member) if self.trigger_action_member else "",
                str(self.guard_expression_member) if self.guard_expression_member else "",
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
    """Represent all concrete alternatives of ``TargetTransitionUsage``."""

    transition_succession_member: TransitionSuccession
    action_body: ActionBody
    form: TargetTransitionForm = TargetTransitionForm.BARE
    input_parameter_count: int = 0
    trigger_action_member: Optional[TriggerActionMember] = None
    guard_expression_member: Optional[GuardExpressionMember] = None
    effect_behavior_member: Optional[EffectBehaviorMember] = None

    def to_sysml(self) -> str:
        """Render selected shorthand alternative and each child field."""
        transition_keyword = "transition" if self.form is not TargetTransitionForm.BARE else ""
        prefix = _join(
            [
                transition_keyword,
                str(self.trigger_action_member) if self.trigger_action_member else "",
                str(self.guard_expression_member) if self.guard_expression_member else "",
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
    owned_reference_subsetting: Optional[QualifiedReference] = None
    feature_specialization_part: Optional[FeatureSpecializationPart] = None
    state_usage_declaration: Optional[UsageDeclaration] = None
    value_part: Optional[ValuePart] = None
    state_usage_body: Optional[StateUsageBody] = None

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
        body = str(self.state_usage_body) if self.state_usage_body else ";"
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

    declaration: Optional[Identification] = None
    locale: Optional[str] = None
    body: str = ""

    def to_sysml(self) -> str:
        """Render comment declaration, locale, and regular-comment body."""
        return (
            _join(
                [
                    "comment" if self.declaration is not None else "",
                    str(self.declaration) if self.declaration else "",
                    "locale " + self.locale if self.locale else "",
                    self.body,
                ]
            )
            or self.body
        )

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
                self.body,
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
    "AcceptNodeDeclaration",
    "ArgumentList",
    "ArrowExpression",
    "AssignmentActionUsage",
    "AssignmentNode",
    "BinaryExpression",
    "BodyExpression",
    "BodyAccessExpression",
    "CastExpression",
    "Comment",
    "CommentExpression",
    "ControlNode",
    "ControlNodePrefix",
    "ConditionalExpression",
    "ConstructorExpression",
    "CoalesceExpression",
    "DecisionNode",
    "DefaultTargetSuccession",
    "DoActionMember",
    "Definition",
    "DefinitionDeclaration",
    "DefinitionBody",
    "DefinitionBodyItem",
    "Documentation",
    "EmptyActionUsage",
    "EffectBehaviorMember",
    "EntryActionMember",
    "EntryTransitionMember",
    "ExhibitStateUsage",
    "FeatureAccessExpression",
    "FeatureChain",
    "FeatureReferenceExpression",
    "FeatureSpecialization",
    "FeatureSpecializationPart",
    "ForkNode",
    "Expression",
    "ForLoopNode",
    "GuardedSuccession",
    "GuardedSuccessionMember",
    "GuardedTargetSuccession",
    "Identification",
    "InfinityLiteral",
    "IfNode",
    "InitialNodeMember",
    "IndexExpression",
    "IntegerLiteral",
    "LiteralKind",
    "MetadataAccessExpression",
    "MetadataCastExpression",
    "MergeNode",
    "Model",
    "NamedArgument",
    "NodeParameter",
    "NullExpression",
    "OccurrenceDefinitionPrefix",
    "OccurrenceUsagePrefix",
    "Package",
    "PackageMember",
    "PartDefinition",
    "PartUsage",
    "ParenthesizedExpression",
    "PayloadFeature",
    "PayloadParameter",
    "PerformActionUsage",
    "PerformActionUsageDeclaration",
    "QualifiedReference",
    "RawElement",
    "RealLiteral",
    "RelationshipBody",
    "SequenceExpression",
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
    "ValuePart",
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
