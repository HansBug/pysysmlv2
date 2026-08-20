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
from typing import Any, Callable, Dict, List, Optional

from antlr4 import CommonTokenStream, InputStream, Token
from antlr4.error.ErrorListener import ErrorListener

from .ast import Model, SourceElement


class ASTParseError(SyntaxError):
    """Report a failed local grammar-entry parse with structured diagnostics.

    :param message: Human-readable summary of the parse failure.
    :type message: str
    :param diagnostics: Structured lexer/parser diagnostics, defaults to ``()``.
    :type diagnostics: list[pysysmlv2.syntax.parser.Diagnostic], optional
    :ivar diagnostics: Structured diagnostics associated with the failure.
    :vartype diagnostics: list[pysysmlv2.syntax.parser.Diagnostic]

    Example::

        >>> error = ASTParseError("bad", [])
        >>> error.diagnostics
        []
    """

    def __init__(self, message: str, diagnostics: Optional[List["Diagnostic"]] = None):
        super().__init__(message)
        self.diagnostics = list(diagnostics or [])


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
        start_column = column + 1
        end_column = start_column
        token_text = getattr(offendingSymbol, "text", None)
        if not token_text and e is not None:
            start_index = getattr(e, "startIndex", -1)
            input_stream = getattr(recognizer, "inputStream", None)
            source_text = getattr(input_stream, "strdata", None)
            current_index = getattr(input_stream, "index", -1)
            if (
                isinstance(source_text, str)
                and isinstance(start_index, int)
                and isinstance(current_index, int)
                and 0 <= start_index <= current_index <= len(source_text)
            ):
                token_text = source_text[start_index:current_index]
        if token_text and token_text != "<EOF>":
            normalized_text = token_text.replace("\r\n", "\n").replace("\r", "\n")
            lines = normalized_text.split("\n")
            if len(lines) == 1:
                end_column = start_column + len(lines[0])
                end_line = line
            else:
                end_line = line + len(lines) - 1
                end_column = len(lines[-1]) + 1
        else:
            end_line = line
        self.items.append(
            Diagnostic("error", msg, line, start_column, end_line, end_column, self.source_path)
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


def _ordered_diagnostics(*groups: List[Diagnostic]) -> List[Diagnostic]:
    """Merge diagnostic groups into stable source order.

    ANTLR reports lexer and parser failures through separate listeners. A
    simple listener concatenation can therefore place a later lexical failure
    before an earlier parser failure. Sorting the combined records by their
    source range preserves the public :class:`ParseResult` contract while the
    final group/sequence keys keep ties deterministic.

    :param groups: Diagnostic lists collected by independent listeners.
    :type groups: list[pysysmlv2.syntax.parser.Diagnostic]
    :return: Combined diagnostics ordered by source position.
    :rtype: list[pysysmlv2.syntax.parser.Diagnostic]

    Example::

        >>> late = Diagnostic("error", "late", 2, 1, 2, 2)
        >>> early = Diagnostic("error", "early", 1, 3, 1, 4)
        >>> [item.message for item in _ordered_diagnostics([late], [early])]
        ['early', 'late']
    """
    indexed = []
    for group_index, group in enumerate(groups):
        indexed.extend((item, group_index, item_index) for item_index, item in enumerate(group))
    return [
        item
        for item, _, _ in sorted(
            indexed,
            key=lambda entry: (
                entry[0].line,
                entry[0].column,
                entry[0].end_line,
                entry[0].end_column,
                entry[1],
                entry[2],
            ),
        )
    ]


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
    diagnostics = _ordered_diagnostics(lexer_errors.items, parser_errors.items)
    if diagnostics:
        ast = Model()
    else:
        ast = build_ast(text, source_path, tree)
    return ParseResult(ast, diagnostics, tree, source_path)


def _grammar_entry_rules() -> Dict[str, Callable[..., Any]]:
    """Return the explicit public parser-entry mapping.

    The mapping is intentionally handwritten.  The generated parser exposes
    hundreds of helper productions, while only productions with a listener
    mapping to a concrete :class:`SourceElement` are safe public AST entries.
    Keeping this list explicit prevents a spelling mistake or an unsupported
    grammar rule from silently returning an untyped value.
    """
    from .generated.SysMLv2Parser import SysMLv2Parser

    return {
        "rootNamespace": SysMLv2Parser.rootNamespace,
        "package": SysMLv2Parser.package,
        "libraryPackage": SysMLv2Parser.libraryPackage,
        "packageMember": SysMLv2Parser.packageMember,
        "packageBodyElement": SysMLv2Parser.packageBodyElement,
        "elementFilterMember": SysMLv2Parser.elementFilterMember,
        "aliasMember": SysMLv2Parser.aliasMember,
        "importRule": SysMLv2Parser.importRule,
        "importDeclaration": SysMLv2Parser.importDeclaration,
        "membershipImport": SysMLv2Parser.membershipImport,
        "namespaceImport": SysMLv2Parser.namespaceImport,
        "filterPackage": SysMLv2Parser.filterPackage,
        "definitionElement": SysMLv2Parser.definitionElement,
        "usageElement": SysMLv2Parser.usageElement,
        "occurrenceUsageElement": SysMLv2Parser.occurrenceUsageElement,
        "definition": SysMLv2Parser.definition,
        "definitionBody": SysMLv2Parser.definitionBody,
        "definitionBodyItem": SysMLv2Parser.definitionBodyItem,
        "partDefinition": SysMLv2Parser.partDefinition,
        "partUsage": SysMLv2Parser.partUsage,
        "itemUsage": SysMLv2Parser.itemUsage,
        "endOccurrenceUsageElement": SysMLv2Parser.endOccurrenceUsageElement,
        "actionDefinition": SysMLv2Parser.actionDefinition,
        "actionUsage": SysMLv2Parser.actionUsage,
        "performActionUsage": SysMLv2Parser.performActionUsage,
        "actionBody": SysMLv2Parser.actionBody,
        "actionNode": SysMLv2Parser.actionNode,
        "stateDefinition": SysMLv2Parser.stateDefinition,
        "stateUsage": SysMLv2Parser.stateUsage,
        "exhibitStateUsage": SysMLv2Parser.exhibitStateUsage,
        "stateDefBody": SysMLv2Parser.stateDefBody,
        "stateUsageBody": SysMLv2Parser.stateUsageBody,
        "stateBodyItem": SysMLv2Parser.stateBodyItem,
        "transitionUsage": SysMLv2Parser.transitionUsage,
        "transitionUsageMember": SysMLv2Parser.transitionUsageMember,
        "targetTransitionUsage": SysMLv2Parser.targetTransitionUsage,
        "targetTransitionUsageMember": SysMLv2Parser.targetTransitionUsageMember,
        "ownedExpression": SysMLv2Parser.ownedExpression,
        "baseExpression": SysMLv2Parser.baseExpression,
        "literalExpression": SysMLv2Parser.literalExpression,
        "nullExpression": SysMLv2Parser.nullExpression,
        "featureReferenceExpression": SysMLv2Parser.featureReferenceExpression,
        "featureTyping": SysMLv2Parser.featureTyping,
        "constructorExpression": SysMLv2Parser.constructorExpression,
        "bodyExpression": SysMLv2Parser.bodyExpression,
        "sequenceExpressionList": SysMLv2Parser.sequenceExpressionList,
        "argumentList": SysMLv2Parser.argumentList,
        "namedArgument": SysMLv2Parser.namedArgument,
        "qualifiedName": SysMLv2Parser.qualifiedName,
        "typeReference": SysMLv2Parser.typeReference,
        "conjugationPart": SysMLv2Parser.conjugationPart,
        "featureDeclaration": SysMLv2Parser.featureDeclaration,
        "featureIdentification": SysMLv2Parser.featureIdentification,
        "featureRelationshipPart": SysMLv2Parser.featureRelationshipPart,
        "typeRelationshipPart": SysMLv2Parser.typeRelationshipPart,
        "featureChainMember": SysMLv2Parser.featureChainMember,
        "valuePart": SysMLv2Parser.valuePart,
        "featureValue": SysMLv2Parser.featureValue,
        "guardExpressionMember": SysMLv2Parser.guardExpressionMember,
        "effectBehaviorMember": SysMLv2Parser.effectBehaviorMember,
        "triggerActionMember": SysMLv2Parser.triggerActionMember,
        "typings": SysMLv2Parser.typings,
        "comment": SysMLv2Parser.comment,
        "documentation": SysMLv2Parser.documentation,
    }


def parse_with_grammar_entry(
    input_text: str,
    entry_name: str,
    force_finished: bool = True,
    source_path: Optional[str] = None,
) -> SourceElement:
    """Parse text through one explicit SysML grammar entry and return its AST.

    This mirrors :func:`pyfcstm.dsl.parse.parse_with_grammar_entry` while
    preserving this package's structured diagnostics.  It is useful for
    parsing a local ``definition``, ``stateDefinition``, ``ownedExpression``,
    or another supported grammar production without wrapping it in a complete
    ``rootNamespace`` document.

    :param input_text: Source text to parse.
    :type input_text: str
    :param entry_name: Explicit generated-parser entry name.  See
        :func:`supported_grammar_entries` for the complete list.
    :type entry_name: str
    :param force_finished: Require the entry to consume all input, defaults to
        ``True``.
    :type force_finished: bool, optional
    :param source_path: Optional path or URI attached to diagnostics and the AST.
    :type source_path: str, optional
    :return: Concrete AST node assembled by :class:`SysMLAstListener`.
    :rtype: :class:`pysysmlv2.syntax.ast.SourceElement`
    :raises ValueError: If ``entry_name`` is not a supported AST entry.
    :raises ASTParseError: If lexing, parsing, recovery, or AST assembly fails.

    Example::

        >>> node = parse_with_grammar_entry("A and B", "ownedExpression")
        >>> type(node).__name__
        'BinaryExpression'
    """
    entries = _grammar_entry_rules()
    if entry_name not in entries:
        supported = ", ".join(sorted(entries))
        raise ValueError(
            "Unsupported SysML AST grammar entry {!r}. Supported entries: {}".format(
                entry_name, supported
            )
        )

    from .ast_builder import build_ast_node

    lexer_errors = _DiagnosticListener(source_path)
    parser_errors = _DiagnosticListener(source_path)
    from .generated.SysMLv2Lexer import SysMLv2Lexer
    from .generated.SysMLv2Parser import SysMLv2Parser

    lexer = SysMLv2Lexer(InputStream(input_text))
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexer_errors)
    token_stream = CommonTokenStream(lexer)
    parser = SysMLv2Parser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(parser_errors)
    try:
        tree = entries[entry_name](parser)
    except (AttributeError, TypeError) as error:
        raise ASTParseError(
            "Parser entry {!r} could not be invoked: {}".format(entry_name, error),
            _ordered_diagnostics(lexer_errors.items, parser_errors.items),
        ) from error

    if force_finished:
        token_stream.fill()
        if token_stream.LA(1) != Token.EOF:
            token = token_stream.LT(1)
            parser_errors.items.append(
                Diagnostic(
                    "error",
                    "parser did not consume the full input",
                    token.line,
                    token.column + 1,
                    token.line,
                    token.column + len(token.text or "") + 1,
                    source_path,
                )
            )
    diagnostics = _ordered_diagnostics(lexer_errors.items, parser_errors.items)
    if diagnostics:
        raise ASTParseError(
            "Could not parse {!r}: {}".format(
                entry_name, "; ".join(item.message for item in diagnostics)
            ),
            diagnostics,
        )
    try:
        return build_ast_node(input_text, source_path, tree)
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        raise ASTParseError(
            "AST listener did not build entry {!r}: {}".format(entry_name, error),
            diagnostics,
        ) from error


def parse_as_ast_node(
    input_text: str,
    grammar_node: str = "rootNamespace",
    source_path: Optional[str] = None,
    force_finished: bool = True,
) -> SourceElement:
    """Parse a local SysML fragment as the AST node for ``grammar_node``.

    ``grammar_node`` is the grammar rule name used by the generated ANTLR
    parser, for example ``"stateDefinition"`` or ``"ownedExpression"``.
    This spelling is provided as a descriptive API alongside the
    :func:`parse_with_grammar_entry` compatibility name.

    :param input_text: SysML fragment to parse.
    :type input_text: str
    :param grammar_node: Supported grammar entry name, defaults to
        ``"rootNamespace"``.
    :type grammar_node: str, optional
    :param source_path: Optional path or URI attached to the node.
    :type source_path: str, optional
    :param force_finished: Require the fragment to be fully consumed, defaults
        to ``True``.
    :type force_finished: bool, optional
    :return: Typed source AST node.
    :rtype: :class:`pysysmlv2.syntax.ast.SourceElement`
    :raises ValueError: If ``grammar_node`` is unsupported.
    :raises ASTParseError: If the fragment is invalid.

    Example::

        >>> node = parse_as_ast_node("state def S;", grammar_node="stateDefinition")
        >>> type(node).__name__
        'StateDefinition'
    """
    return parse_with_grammar_entry(
        input_text,
        entry_name=grammar_node,
        force_finished=force_finished,
        source_path=source_path,
    )


def supported_grammar_entries() -> List[str]:
    """Return the sorted list of grammar entries that produce typed AST nodes.

    :return: Supported local parsing entry names.
    :rtype: list[str]

    Example::

        >>> "ownedExpression" in supported_grammar_entries()
        True
    """
    return sorted(_grammar_entry_rules())


__all__ = [
    "ASTParseError",
    "Diagnostic",
    "ParseResult",
    "parse",
    "parse_as_ast_node",
    "parse_with_grammar_entry",
    "supported_grammar_entries",
]
