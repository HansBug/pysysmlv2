"""Placeholder semantic model boundary for future SysML v2 linking.

The semantic model will eventually own symbol identity, imports, references,
and semantic diagnostics. It currently wraps the syntax AST without pretending
that linking or model checking is implemented.

.. list-table:: Semantic module roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :class:`SemanticModel`
     - Stable holder for syntax and future resolved semantic data.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SemanticModel:
    """Wrap syntax while the full SysML v2 semantic layer is staged.

    This boundary deliberately does not claim symbol resolution or semantic
    validation. Those facilities will be added without changing the syntax
    AST contract consumed by downstream analyzers.

    :param syntax: Syntax AST associated with this semantic view.
    :type syntax: object
    :ivar syntax: Syntax AST associated with this semantic view.
    :vartype syntax: object

    Example::

        >>> from pysysmlv2.syntax.ast import Model
        >>> SemanticModel(Model()).syntax.members
        []
    """

    syntax: Any
