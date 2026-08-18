"""Public namespace for the pysysmlv2 SysML v2 foundation library.

The package exposes stable version metadata and the primary syntax/workspace
entry points. Downstream state-machine tooling should depend on these APIs
instead of importing generated ANTLR classes directly.

The package roadmap is intentionally visible here so users can choose the
right abstraction layer:

.. list-table:: Package roadmap
   :header-rows: 1

   * - Module
     - Responsibility
   * - :mod:`pysysmlv2.syntax`
     - ANTLR parsing, structured diagnostics, source spans, and round-trippable AST nodes.
   * - :mod:`pysysmlv2.workspace`
     - Request-local document storage and the future cross-file linking boundary.
   * - :mod:`pysysmlv2.semantic`
     - Semantic-model wrapper reserved for symbol resolution and validation.
   * - :mod:`pysysmlv2.formatter`
     - Canonical AST export, kept separate from trivia-preserving formatting.
   * - :mod:`pysysmlv2.entry`
     - Click command-line inspection, validation, and formatting commands.
   * - :mod:`pysysmlv2.query`
     - Extension point for downstream semantic and state-machine queries.

.. list-table:: Main exports
   :header-rows: 1

   * - Export
     - Purpose
   * - :data:`__version__`
     - Package release version.
   * - :class:`~pysysmlv2.syntax.ast.Model`
     - Syntax AST root with SysML round-trip export.
   * - :class:`~pysysmlv2.syntax.parser.ParseResult`
     - Parser output with diagnostics and AST.
   * - :class:`~pysysmlv2.workspace.Workspace`
     - Request-local document and linking workspace.

Example::

    >>> import pysysmlv2
    >>> isinstance(pysysmlv2.__version__, str)
    True
"""

from .config.meta import __VERSION__ as __version__
from .syntax.ast import ASTNode, Model
from .syntax.parser import Diagnostic, ParseResult, parse
from .workspace.workspace import Workspace

__all__ = [
    "ASTNode",
    "Diagnostic",
    "Model",
    "ParseResult",
    "Workspace",
    "__version__",
    "parse",
]
