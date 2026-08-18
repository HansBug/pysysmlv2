"""Unit tests for canonical AST formatting."""

import pytest

from pysysmlv2 import parse
from pysysmlv2.formatter import format_ast

pytestmark = pytest.mark.unit


def test_formatter_delegates_to_ast_export():
    result = parse("package Demo { }")
    assert format_ast(result.ast) == "package Demo { }"
