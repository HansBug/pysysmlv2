"""Formatting boundaries for canonical and future source-preserving output.

The current :func:`pysysmlv2.formatter.format_ast` entry point exports the
model-level AST representation. It intentionally does not make lexical trivia
part of the AST contract; a later formatter can add source-preserving behavior
without changing syntax node ownership.

.. list-table:: Formatter roadmap
   :header-rows: 1

   * - Export
     - Responsibility
   * - :func:`pysysmlv2.formatter.format_ast`
     - Render parseable canonical SysML from an AST node.
"""

from .formatter import format_ast

__all__ = ["format_ast"]
