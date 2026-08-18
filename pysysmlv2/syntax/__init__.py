"""Syntax parsing, diagnostics, and source AST APIs.

This is the foundation's source-facing layer. :func:`pysysmlv2.syntax.parse`
invokes the generated ANTLR4 lexer/parser, converts the result into the
source-aware AST, and returns structured diagnostics. AST nodes retain model
documentation and source provenance, and ``str(node)`` exports parseable
canonical SysML text. Generated modules are implementation details and must be
regenerated through the repository tooling.

.. list-table:: Syntax roadmap
   :header-rows: 1

   * - Export
     - Responsibility
   * - :func:`pysysmlv2.syntax.parse`
     - Parse text and return :class:`pysysmlv2.syntax.ParseResult`.
   * - :class:`pysysmlv2.syntax.Model`
     - Root source AST with round-trip export.
   * - :class:`pysysmlv2.syntax.SourceSpan`
     - One-based source provenance range.
   * - :class:`pysysmlv2.syntax.Diagnostic`
     - Structured lexer/parser problem.
"""

from .ast import ASTNode, Comment, Documentation, Model, SourceSpan
from .parser import Diagnostic, ParseResult, parse

__all__ = [
    "ASTNode",
    "Comment",
    "Diagnostic",
    "Documentation",
    "Model",
    "ParseResult",
    "SourceSpan",
    "parse",
]
