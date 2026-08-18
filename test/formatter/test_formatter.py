"""Unit tests for canonical AST formatting."""

import pytest

from pysysmlv2.formatter import format_ast
from pysysmlv2.syntax.ast import Model, Package

pytestmark = pytest.mark.unit


def test_formatter_delegates_to_ast_export():
    assert format_ast(Model(members=[Package(name="Demo")])) == "package Demo {}"
