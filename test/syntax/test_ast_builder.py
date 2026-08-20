"""Unit tests for the parse-tree-to-AST builder boundary."""

import pytest
from antlr4 import CommonTokenStream, InputStream

from pysysmlv2.syntax.ast import BooleanLiteral, Model, Package
from pysysmlv2.syntax.ast_builder import build_ast, build_ast_node
from pysysmlv2.syntax.generated.SysMLv2Lexer import SysMLv2Lexer
from pysysmlv2.syntax.generated.SysMLv2Parser import SysMLv2Parser

pytestmark = pytest.mark.unit


def _parser(source: str) -> SysMLv2Parser:
    """Create a parser over one source fragment for builder tests."""
    return SysMLv2Parser(CommonTokenStream(SysMLv2Lexer(InputStream(source))))


def test_build_ast_node_walks_a_local_grammar_entry_and_attaches_span():
    """Build a typed local node without going through the public parse wrapper."""
    source = "true"
    parser = _parser(source)
    node = build_ast_node(source, "fragment.sysml", parser.ownedExpression())
    assert node == BooleanLiteral("true")
    assert node.span is not None
    assert node.span.source_path == "fragment.sysml"
    assert str(node) == source


def test_build_ast_requires_the_root_namespace_mapping():
    """Build a complete model and retain its source path in the root span."""
    source = "package Demo { }"
    parser = _parser(source)
    model = build_ast(source, "demo.sysml", parser.rootNamespace())
    assert isinstance(model, Model)
    assert isinstance(model.members[0].element, Package)
    assert model.span is not None
    assert model.span.source_path == "demo.sysml"
