"""Build the source AST by walking an ANTLR parse tree.

This module deliberately contains no SysML text scanner. The parser owns
syntax recognition and :class:`pysysmlv2.syntax.listener.SysMLAstListener`
owns context-to-node assembly; this function only connects the two through
ANTLR's standard :class:`antlr4.ParseTreeWalker`.

.. list-table:: AST builder roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`build_ast`
     - Walk a parse tree and return its fully assembled root node.
"""

from __future__ import annotations

from typing import Optional

from antlr4 import ParseTreeWalker

from .ast import Model, SourceElement
from .listener import SysMLAstListener


def build_ast_node(text: str, source_path: Optional[str], parse_tree) -> SourceElement:
    """Walk an ANTLR context and return its explicitly typed AST node.

    This is the shared builder for complete documents and local grammar-entry
    parsing.  The caller is responsible for selecting a parser rule; this
    function only performs the listener walk and attaches the entry context's
    source provenance to the returned root node.

    :param text: Source text consumed by ``parse_tree``.
    :type text: str
    :param source_path: Original path or URI, or ``None`` when unavailable.
    :type source_path: str, optional
    :param parse_tree: ANTLR parser context to walk.
    :type parse_tree: object
    :return: Concrete source AST node mapped for ``parse_tree``.
    :rtype: :class:`pysysmlv2.syntax.ast.SourceElement`
    :raises TypeError: If the listener does not produce a source AST node.

    Example::

        >>> from antlr4 import CommonTokenStream, InputStream
        >>> from pysysmlv2.syntax.generated.SysMLv2Lexer import SysMLv2Lexer
        >>> from pysysmlv2.syntax.generated.SysMLv2Parser import SysMLv2Parser
        >>> source = "true"
        >>> parser = SysMLv2Parser(CommonTokenStream(SysMLv2Lexer(InputStream(source))))
        >>> node = build_ast_node(source, None, parser.ownedExpression())
        >>> str(node)
        'true'
    """
    listener = SysMLAstListener(text, source_path)
    ParseTreeWalker().walk(listener, parse_tree)
    node = listener.node_for(parse_tree)
    if not isinstance(node, SourceElement):
        raise TypeError(
            "{} did not produce a SourceElement AST node".format(type(parse_tree).__name__)
        )
    node.span = listener._span(parse_tree)
    return node


def build_ast(text: str, source_path: Optional[str], parse_tree) -> Model:
    """Walk a validated ANTLR tree and return the listener-built model root.

    :param text: Complete SysML v2 source text supplied to the parser.
    :type text: str
    :param source_path: Original path or URI, or ``None`` when unavailable.
    :type source_path: str, optional
    :param parse_tree: ANTLR ``rootNamespace`` parse context.
    :type parse_tree: object
    :return: Root AST node containing explicit handwritten source nodes.
    :rtype: :class:`pysysmlv2.syntax.ast.Model`
    :raises TypeError: If the supplied tree is not the root namespace context.

    Example::

        >>> from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
        >>> from pysysmlv2.syntax.generated.SysMLv2Lexer import SysMLv2Lexer
        >>> from pysysmlv2.syntax.generated.SysMLv2Parser import SysMLv2Parser
        >>> source = "package Demo { }"
        >>> parser = SysMLv2Parser(CommonTokenStream(SysMLv2Lexer(InputStream(source))))
        >>> tree = parser.rootNamespace()
        >>> str(build_ast(source, None, tree))
        'package Demo { }'
    """
    root = build_ast_node(text, source_path, parse_tree)
    if not isinstance(root, Model):
        raise TypeError("rootNamespace did not produce the Model AST node")
    return root


__all__ = ["build_ast", "build_ast_node"]
