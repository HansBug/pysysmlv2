"""Round-trippable syntax AST nodes for the SysML v2 textual notation.

The AST intentionally owns syntax structure and model-level documentation but
does not own workspace identity or resolved references. Every concrete node
exports parseable SysML text through ``str(node)``. Source provenance is kept
to the original path and source span; deeper trace maps belong to the workspace
layer.

.. list-table:: AST module roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :class:`SourceSpan`
     - Source provenance range.
   * - :class:`ASTNode`
     - Round-trip export base class.
   * - :class:`Package` / :class:`Model`
     - Typed package and document roots.
   * - :class:`RawElement`
     - Loss-minimizing placeholder for unmapped valid syntax.
   * - :class:`Documentation` / :class:`Comment`
     - Model-owned textual elements preserved by export.
   * - :func:`structural_text`
     - Canonical structural export helper.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SourceSpan:
    """Represent a one-based, half-open source range.

    :param line: One-based starting line.
    :param column: One-based starting column.
    :param end_line: One-based exclusive ending line.
    :param end_column: One-based exclusive ending column.
    :type line: int
    :type column: int
    :type end_line: int
    :type end_column: int
    :ivar line: One-based starting line.
    :vartype line: int
    :ivar column: One-based starting column.
    :vartype column: int
    :ivar end_line: One-based exclusive ending line.
    :vartype end_line: int
    :ivar end_column: One-based exclusive ending column.
    :vartype end_column: int

    Example::

        >>> SourceSpan(1, 1, 1, 8).contains(SourceSpan(1, 2, 1, 4))
        True
    """

    line: int
    column: int
    end_line: int
    end_column: int

    def contains(self, other: "SourceSpan") -> bool:
        """Return whether another span is fully contained by this span.

        :param other: Candidate child span.
        :type other: :class:`pysysmlv2.syntax.ast.SourceSpan`
        :return: ``True`` when both boundaries are inside this span.
        :rtype: bool

        Example::

            >>> SourceSpan(1, 1, 1, 8).contains(SourceSpan(1, 2, 1, 4))
            True
        """
        start_ok = (self.line, self.column) <= (other.line, other.column)
        end_ok = (other.end_line, other.end_column) <= (self.end_line, self.end_column)
        return start_ok and end_ok


@dataclass
class ASTNode:
    """Base class for syntax AST nodes.

    :param source_path: Original document path or URI, if known.
    :type source_path: str, optional
    :param span: Source range occupied by this node, if known.
    :type span: :class:`pysysmlv2.syntax.ast.SourceSpan`, optional
    :ivar source_path: Original document path or URI.
    :vartype source_path: str, optional
    :ivar span: Source range occupied by this node.
    :vartype span: :class:`pysysmlv2.syntax.ast.SourceSpan`, optional

    Example::

        >>> str(ASTNode())
        ''
    """

    source_path: Optional[str] = None
    span: Optional[SourceSpan] = None

    def to_sysml(self) -> str:
        """Return canonical SysML text for this node.

        :return: Parseable canonical SysML text.
        :rtype: str

        Example::

            >>> ASTNode().to_sysml()
            ''
        """
        return ""

    def __str__(self) -> str:
        """Export this node as parseable canonical SysML text.

        :return: Canonical SysML representation.
        :rtype: str
        """
        return self.to_sysml()


@dataclass
class Documentation(ASTNode):
    """Store model-level documentation that must survive AST export.

    :param text: Documentation body without comment delimiters.
    :type text: str
    :ivar text: Documentation body.
    :vartype text: str

    Example::

        >>> str(Documentation(text="A demo"))
        '/**\\n * A demo\\n */'
    """

    text: str = ""

    def to_sysml(self) -> str:
        """Return the SysML documentation form.

        :return: Canonical documentation comment.
        :rtype: str
        """
        lines = self.text.splitlines() or [""]
        body = "\n".join(" * " + line for line in lines)
        return "/**\n" + body + "\n */"


@dataclass
class Comment(ASTNode):
    """Store a model-owned comment distinct from formatting trivia.

    :param text: Comment body without delimiters.
    :type text: str
    :ivar text: Comment body.
    :vartype text: str

    Example::

        >>> str(Comment(text="A note"))
        '/* A note */'
    """

    text: str = ""

    def to_sysml(self) -> str:
        """Return the canonical block comment representation.

        :return: Canonical block comment.
        :rtype: str
        """
        return "/* " + self.text.replace("*/", "* /") + " */"


@dataclass
class RawElement(ASTNode):
    """Preserve a valid element not yet mapped to a typed AST class.

    :param text: Source text for the unmapped element.
    :type text: str
    :ivar text: Source text retained for loss-minimizing export.
    :vartype text: str

    Example::

        >>> str(RawElement(text="part def Vehicle;"))
        'part def Vehicle;'
    """

    text: str = ""

    def to_sysml(self) -> str:
        """Return the captured source text.

        :return: Trimmed source text.
        :rtype: str
        """
        return self.text.strip()


@dataclass
class Package(ASTNode):
    """Represent a SysML package with nested model elements.

    :param name: Package name, or ``None`` for an anonymous package.
    :type name: str, optional
    :param members: Nested syntax nodes, defaults to an empty list.
    :type members: list[pysysmlv2.syntax.ast.ASTNode], optional
    :param documentation: Model documentation nodes, defaults to an empty list.
    :type documentation: list[pysysmlv2.syntax.ast.Documentation], optional
    :ivar name: Package name.
    :vartype name: str, optional
    :ivar members: Nested syntax nodes.
    :vartype members: list[pysysmlv2.syntax.ast.ASTNode]
    :ivar documentation: Documentation attached to this package.
    :vartype documentation: list[pysysmlv2.syntax.ast.Documentation]

    Example::

        >>> str(Package(name="Demo"))
        'package Demo {}'
    """

    name: Optional[str] = None
    members: List[ASTNode] = field(default_factory=list)
    documentation: List[Documentation] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Return a canonical package declaration.

        :return: Parseable package source.
        :rtype: str
        """
        prefix = "\n".join(str(item) for item in self.documentation)
        title = "package" + ((" " + self.name) if self.name else "")
        body = "\n".join(_indent(str(item)) for item in self.members if str(item))
        rendered = title + " {"
        if body:
            rendered += "\n" + body + "\n"
        rendered += "}"
        return (prefix + "\n" if prefix else "") + rendered


@dataclass
class Model(ASTNode):
    """Represent the root AST for one SysML document.

    :param members: Top-level syntax nodes, defaults to an empty list.
    :type members: list[pysysmlv2.syntax.ast.ASTNode], optional
    :ivar members: Top-level syntax nodes.
    :vartype members: list[pysysmlv2.syntax.ast.ASTNode]

    Example::

        >>> str(Model(members=[Package(name="Demo")]))
        'package Demo {}'
    """

    members: List[ASTNode] = field(default_factory=list)

    def to_sysml(self) -> str:
        """Return canonical SysML text for all document members.

        :return: Parseable canonical document source.
        :rtype: str
        """
        return "\n\n".join(str(item) for item in self.members if str(item))


def _indent(text: str, prefix: str = "    ") -> str:
    """Indent every line of a rendered child node."""
    return "\n".join(prefix + line if line else line for line in text.splitlines())


def structural_text(node: ASTNode) -> str:
    """Return export text for structural round-trip comparisons.

    :param node: AST node to export.
    :return: Canonical SysML text.
    :rtype: str

    Example::

        >>> structural_text(Model(members=[Package(name="Demo")]))
        'package Demo {}'
    """
    return str(node)
