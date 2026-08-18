"""Semantic model extension points.

The semantic layer is deliberately separate from :mod:`pysysmlv2.syntax`.
It will own identity, symbol tables, imports, and resolved relationships while
the syntax AST continues to own source structure and round-trip export.

.. list-table:: Semantic roadmap
   :header-rows: 1

   * - Export
     - Responsibility
   * - :class:`pysysmlv2.semantic.SemanticModel`
     - Temporary wrapper for the syntax AST and future resolved model.
"""

from .model import SemanticModel

__all__ = ["SemanticModel"]
