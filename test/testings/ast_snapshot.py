"""Stable, span-free structural snapshots for exact AST fixture assertions."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any


def ast_snapshot(value: Any) -> Any:
    """Return every dataclass field except source provenance ``span``.

    :param value: AST value, sequence, enum, or scalar to normalize.
    :type value: object
    :return: JSON-compatible structural representation preserving class names
        and field names.
    :rtype: object

    Example::

        >>> from pysysmlv2.syntax.ast import ASTNode
        >>> ast_snapshot(ASTNode())
        {'__class__': 'ASTNode'}
    """
    if is_dataclass(value):
        result = {"__class__": type(value).__name__}
        for item in fields(value):
            if item.name != "span":
                result[item.name] = ast_snapshot(getattr(value, item.name))
        return result
    if isinstance(value, Enum):
        return {"__enum__": type(value).__name__, "value": value.value}
    if isinstance(value, (list, tuple)):
        return [ast_snapshot(item) for item in value]
    if isinstance(value, dict):
        return {str(key): ast_snapshot(item) for key, item in value.items()}
    return value
