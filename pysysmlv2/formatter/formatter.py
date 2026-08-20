"""AST formatting without making trivia part of the AST contract.

The formatter is the output boundary for canonical model text. It delegates
to AST ``__str__``/``to_sysml`` methods today and leaves room for a separate
trivia-preserving formatter later.

.. list-table:: Formatter module roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`format_ast`
     - Render canonical parseable SysML from an AST node.
"""

from ..syntax.ast import ASTNode


def format_ast(node: ASTNode) -> str:
    """Render an AST node in canonical SysML form.

    The formatter intentionally operates on the AST contract and does not
    promise preservation of lexical trivia such as ordinary comments or
    whitespace. Model-owned documentation nodes remain part of the result.

    :param node: AST node to render.
    :type node: :class:`pysysmlv2.syntax.ast.ASTNode`
    :return: Canonical parseable SysML text.
    :rtype: str

    Example::

        >>> from pysysmlv2 import parse
        >>> format_ast(parse("package Demo { }").ast)
        'package Demo { }'
    """
    return str(node)
