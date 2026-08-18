"""Document container types reserved for workspace linking.

This module keeps immutable source identity and text separate from parsed AST
and semantic state. The workspace can later attach parse/link snapshots without
changing this small value object.

.. list-table:: Document module roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :class:`Document`
     - Immutable source-path and text pair.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """Represent one immutable source document in a workspace.

    :param source_path: Stable path or URI used to identify the document.
    :type source_path: str
    :param text: Complete SysML source text.
    :type text: str
    :ivar source_path: Stable document identity.
    :vartype source_path: str
    :ivar text: Complete source text.
    :vartype text: str

    Example::

        >>> Document("demo.sysml", "package Demo { }").source_path
        'demo.sysml'
    """

    source_path: str
    text: str
