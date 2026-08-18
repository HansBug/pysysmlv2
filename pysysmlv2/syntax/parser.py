"""ANTLR parser adapter and structured syntax diagnostics.

This module is the syntax boundary between generated ANTLR classes and the
public package. :func:`parse` installs quiet lexer/parser listeners, retains
structured source ranges, builds the public AST, and returns the optional raw
parse tree for advanced callers. Generated classes remain an implementation
detail under :mod:`pysysmlv2.syntax.generated`.

.. list-table:: Parser module roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :class:`Diagnostic`
     - Stable lexer/parser diagnostic DTO.
   * - :class:`ParseResult`
     - AST, diagnostics, parse tree, and ``ok`` status.
   * - :func:`parse`
     - Parse one SysML v2 document.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from .ast import Model


@dataclass(frozen=True)
class Diagnostic:
    """Describe one lexer or parser problem with a source location.

    :param severity: Diagnostic severity, currently ``"error"`` for parser
        and lexer failures.
    :type severity: str
    :param message: Human-readable diagnostic message.
    :type message: str
    :param line: One-based start line.
    :type line: int
    :param column: One-based start column.
    :type column: int
    :param end_line: One-based exclusive end line.
    :type end_line: int
    :param end_column: One-based exclusive end column.
    :type end_column: int
    :param source_path: Optional source path or URI, defaults to ``None``.
    :type source_path: str, optional
    :param code: Optional machine-readable diagnostic code, defaults to ``None``.
    :type code: str, optional
    :ivar severity: Diagnostic severity.
    :vartype severity: str
    :ivar message: Human-readable diagnostic message.
    :vartype message: str

    Example::

        >>> Diagnostic("error", "bad token", 1, 1, 1, 2).severity
        'error'
    """

    severity: str
    message: str
    line: int
    column: int
    end_line: int
    end_column: int
    source_path: Optional[str] = None
    code: Optional[str] = None


class _DiagnosticListener(ErrorListener):
    """Collect ANTLR lexer/parser errors without printing to stderr."""

    def __init__(self, source_path: Optional[str]) -> None:
        super().__init__()
        self.source_path = source_path
        self.items: List[Diagnostic] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """Record one ANTLR error without writing to standard error.

        :param recognizer: ANTLR lexer or parser that reported the error.
        :type recognizer: object
        :param offendingSymbol: Token associated with the error, if available.
        :type offendingSymbol: object
        :param line: One-based error line supplied by ANTLR.
        :type line: int
        :param column: Zero-based error column supplied by ANTLR.
        :type column: int
        :param msg: Human-readable ANTLR message.
        :type msg: str
        :param e: Optional ANTLR exception, if supplied.
        :type e: BaseException, optional
        :return: ``None``.
        :rtype: None
        """
        end_column = column + 1
        if offendingSymbol is not None and getattr(offendingSymbol, "text", None):
            end_column = column + len(offendingSymbol.text)
        self.items.append(
            Diagnostic("error", msg, line, column + 1, line, end_column, self.source_path)
        )


@dataclass
class ParseResult:
    """Hold the syntax AST, diagnostics, and optional ANTLR parse tree.

    :param ast: Source AST built from the parser result.
    :type ast: :class:`pysysmlv2.syntax.ast.Model`
    :param diagnostics: Lexer and parser diagnostics in source order.
    :type diagnostics: list[pysysmlv2.syntax.parser.Diagnostic]
    :param parse_tree: Original ANTLR parse tree, defaults to ``None``.
    :type parse_tree: object, optional
    :param source_path: Source path or URI, defaults to ``None``.
    :type source_path: str, optional
    :ivar ast: Source AST for the document.
    :vartype ast: :class:`pysysmlv2.syntax.ast.Model`
    :ivar diagnostics: Structured parser diagnostics.
    :vartype diagnostics: list[pysysmlv2.syntax.parser.Diagnostic]

    Example::

        >>> result = parse("package Demo { }")
        >>> result.ok
        True
    """

    ast: Model
    diagnostics: List[Diagnostic]
    parse_tree: Any = None
    source_path: Optional[str] = None

    @property
    def ok(self) -> bool:
        """Return whether no lexer or parser errors were reported.

        :return: ``True`` when every diagnostic is non-error or no diagnostic
            was emitted.
        :rtype: bool

        Example::

            >>> parse("package Demo { }").ok
            True
        """
        return not any(item.severity == "error" for item in self.diagnostics)


def parse(text: str, source_path: Optional[str] = None) -> ParseResult:
    """Parse SysML text with the generated ANTLR lexer/parser.

    :param text: SysML v2 textual notation.
    :param source_path: Optional source path or URI for diagnostics.
    :return: Parse result containing AST, diagnostics, and parse tree.
    :rtype: ParseResult

    Example::

        >>> result = parse("package Demo { part def Vehicle; }")
        >>> result.ok
        True
    """
    from .ast_builder import build_ast
    from .generated.SysMLv2Lexer import SysMLv2Lexer
    from .generated.SysMLv2Parser import SysMLv2Parser

    lexer_errors = _DiagnosticListener(source_path)
    parser_errors = _DiagnosticListener(source_path)
    lexer = SysMLv2Lexer(InputStream(text))
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexer_errors)
    token_stream = CommonTokenStream(lexer)
    parser = SysMLv2Parser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(parser_errors)
    tree = parser.rootNamespace()
    diagnostics = lexer_errors.items + parser_errors.items
    ast = build_ast(text, source_path, tree)
    return ParseResult(ast, diagnostics, tree, source_path)
