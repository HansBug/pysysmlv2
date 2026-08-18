"""Workspace and document abstractions.

The workspace owns request-local document identity and is the future home for
cross-file imports, linking, and symbol resolution. It deliberately does not
change AST ownership: syntax nodes keep source paths and spans, while resolved
relationships belong above them.

.. list-table:: Workspace roadmap
   :header-rows: 1

   * - Export
     - Responsibility
   * - :class:`pysysmlv2.workspace.Workspace`
     - Collect parsed documents and expose the linking boundary.
   * - :class:`pysysmlv2.workspace.document.Document`
     - Immutable source-path and text container.
"""

from .workspace import Workspace

__all__ = ["Workspace"]
