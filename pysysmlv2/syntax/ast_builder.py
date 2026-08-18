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

from .ast import Model
from .listener import SysMLAstListener


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
    listener = SysMLAstListener(text, source_path)
    ParseTreeWalker().walk(listener, parse_tree)
    root = listener.node_for(parse_tree)
    if not isinstance(root, Model):
        raise TypeError("rootNamespace did not produce the Model AST node")
    return root


__all__ = ["build_ast"]
