"""Build the initial source AST from a validated SysML parse tree.

The full SysML metamodel is intentionally a later semantic layer. This module
provides a conservative, loss-minimizing AST boundary: package declarations
are typed and other valid top-level elements remain as ``RawElement`` nodes
until their dedicated grammar mapping is implemented.

The builder is deliberately conservative: the parser remains authoritative for
syntax validity, while this module handles source spans and the first typed
package mapping. Deeper identity and symbol traces belong to the workspace and
semantic modules.

.. list-table:: AST builder roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`build_ast`
     - Convert a validated parse boundary into a source AST.
   * - ``RawElement`` fallback
     - Preserve valid but not-yet-typed source content.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from .ast import ASTNode, Comment, Documentation, Model, Package, RawElement, SourceSpan

_DECLARATION = re.compile(r"\bpackage(?:\s+([A-Za-z_][A-Za-z0-9_]*))?\s*\{")
_DOC = re.compile(r"/\*\*(.*?)\*/", re.DOTALL)
_COMMENT = re.compile(r"/\*(?!\*)(.*?)\*/", re.DOTALL)


def _offset_to_position(text: str, offset: int) -> Tuple[int, int]:
    before = text[:offset]
    line = before.count("\n") + 1
    column = offset - (before.rfind("\n") + 1) + 1
    return line, column


def _span(text: str, start: int, end: int) -> SourceSpan:
    line, column = _offset_to_position(text, start)
    end_line, end_column = _offset_to_position(text, end)
    return SourceSpan(line, column, end_line, end_column)


def _matching_brace(text: str, opening: int) -> Optional[int]:
    depth = 0
    quote = None
    index = opening
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif text.startswith("/*", index):
            close = text.find("*/", index + 2)
            if close < 0:
                return None
            index = close + 1
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _documentation(raw: str, path: Optional[str], text: str, start: int) -> Documentation:
    body = raw[3:-2]
    lines = []
    for line in body.splitlines():
        lines.append(re.sub(r"^\s*\* ?", "", line).strip())
    return Documentation(
        text="\n".join(lines).strip(),
        source_path=path,
        span=_span(text, start, start + len(raw)),
    )


def build_ast(text: str, source_path: Optional[str], parse_tree) -> Model:
    """Build a source AST while retaining unmapped elements losslessly.

    Package declarations are mapped to :class:`pysysmlv2.syntax.ast.Package`
    nodes. Valid content that does not yet have a typed mapping remains a
    :class:`pysysmlv2.syntax.ast.RawElement`, so downstream layers can inspect
    it without silently losing source text.

    :param text: Complete SysML v2 document text.
    :type text: str
    :param source_path: Original path or URI, defaults to ``None``.
    :type source_path: str, optional
    :param parse_tree: ANTLR parse tree used as the validation boundary.
    :type parse_tree: object
    :return: Source AST root.
    :rtype: :class:`pysysmlv2.syntax.ast.Model`

    Example::

        >>> tree = build_ast("package Demo { }", "demo.sysml", None)
        >>> str(tree)
        'package Demo {}'
    """
    del parse_tree
    members: List[ASTNode] = []
    package_match = _DECLARATION.search(text)
    if package_match:
        start = package_match.start()
        close = _matching_brace(text, package_match.end() - 1)
        if close is not None:
            docs = [
                _documentation(match.group(0), source_path, text, match.start())
                for match in _DOC.finditer(text[:start])
            ]
            for match in _COMMENT.finditer(text[:start]):
                if any(
                    item.span and item.span.contains(_span(text, match.start(), match.end()))
                    for item in docs
                ):
                    continue
                members.append(
                    Comment(
                        text=match.group(1).strip(),
                        source_path=source_path,
                        span=_span(text, match.start(), match.end()),
                    )
                )
            body = text[package_match.end() : close].strip()
            body_node = RawElement(
                text=body,
                source_path=source_path,
                span=_span(text, package_match.end(), close),
            )
            package = Package(
                name=package_match.group(1),
                members=[body_node] if body else [],
                documentation=docs,
                source_path=source_path,
                span=_span(text, start, close + 1),
            )
            members.append(package)

    if not members and text.strip():
        docs = [
            _documentation(match.group(0), source_path, text, match.start())
            for match in _DOC.finditer(text)
        ]
        for match in _COMMENT.finditer(text):
            if not any(
                item.span and item.span.line == _offset_to_position(text, match.start())[0]
                for item in docs
            ):
                members.append(
                    Comment(
                        text=match.group(1).strip(),
                        source_path=source_path,
                        span=_span(text, match.start(), match.end()),
                    )
                )
        stripped = text.strip()
        members.append(
            RawElement(text=stripped, source_path=source_path, span=_span(text, 0, len(text)))
        )
        del docs

    return Model(members=members, source_path=source_path, span=_span(text, 0, len(text)))
