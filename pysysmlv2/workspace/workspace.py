"""Request-local SysML document workspace placeholder.

The workspace is the ownership boundary for multiple documents in one parse
request. It currently stores :class:`pysysmlv2.syntax.parser.ParseResult`
objects and exposes a no-op ``link`` hook; future implementations will add
imports, symbol tables, and semantic diagnostics here.

.. list-table:: Workspace module roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :class:`Workspace`
     - Add documents and expose the linking lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from ..syntax.parser import ParseResult, parse


@dataclass
class Workspace:
    """Collect request-local documents and expose the linking boundary.

    :param documents: Mapping from source path to parse result.
    :type documents: dict[str, pysysmlv2.syntax.parser.ParseResult], optional
    :ivar documents: Parsed documents keyed by their caller-provided paths.
    :vartype documents: dict[str, pysysmlv2.syntax.parser.ParseResult]

    Example::

        >>> workspace = Workspace()
        >>> result = workspace.add_text("demo.sysml", "package Demo { }")
        >>> result.ok
        True
    """

    documents: Dict[str, ParseResult] = field(default_factory=dict)

    def add_text(self, source_path: str, text: str) -> ParseResult:
        """Parse and add one source document to this workspace.

        :param source_path: Stable path or URI for the document.
        :type source_path: str
        :param text: Complete SysML source text.
        :type text: str
        :return: Parse result stored under ``source_path``.
        :rtype: :class:`pysysmlv2.syntax.parser.ParseResult`

        Example::

            >>> Workspace().add_text("demo.sysml", "package Demo { }").ok
            True
        """
        result = parse(text, source_path)
        self.documents[source_path] = result
        return result

    def link(self) -> None:
        """Run workspace linking when semantic resolution is available.

        Linking is currently a stable no-op placeholder. The method exists so
        callers can adopt a request-local workspace without coupling themselves
        to a future resolver implementation.

        :return: ``None`` until workspace linking is implemented.
        :rtype: None

        Example::

            >>> Workspace().link() is None
            True
        """
        return None
