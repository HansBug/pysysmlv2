"""Field-level tests for model-owned relationship-body content.

Relationship bodies occur on aliases, imports, dependencies, and several
other relationship productions.  Their braces/semicolon choice and nested
model-owned annotations are syntax-model data; keeping only one source string
would make those children invisible to downstream AST consumers.
"""

from __future__ import annotations

import pytest

from pysysmlv2 import parse, parse_as_ast_node
from pysysmlv2.syntax import Comment, Documentation, RelationshipBody

pytestmark = pytest.mark.unit


def _alias_body(source: str) -> RelationshipBody:
    """Return the relationship body of the first alias in ``source``."""
    result = parse(source, "relationship-body.sysml")
    assert result.ok, result.diagnostics
    package = result.ast.members[0].element
    alias = package.members[0]
    return alias.relationship_body


def test_semicolon_relationship_body_retains_declaration_only_form():
    """A semicolon body is represented as a distinct empty body form."""
    body = _alias_body("package P { alias A for B; }")

    assert body.declaration_only is True
    assert body.members == []
    assert not hasattr(body, "source_text")
    assert str(body) == ";"


def test_braced_relationship_body_exposes_ordered_model_annotations():
    """Comments and documentation remain typed ordered body children."""
    body = _alias_body("package P { alias A for B { /* note */ doc /* docs */ } }")

    assert body.declaration_only is False
    assert body.members == [Comment(body="/* note */"), Documentation(body="/* docs */")]
    assert not hasattr(body, "source_text")
    assert str(body) == "{\n    /* note */\n    doc /* docs */\n}"


@pytest.mark.parametrize(
    "source",
    [
        ";",
        "{ /* note */ doc /* docs */ }",
    ],
)
def test_relationship_body_parse_as_ast_node_round_trips_each_form(source):
    """The local grammar-entry API supports exact relationship-body parsing."""
    first = parse_as_ast_node(source, grammar_node="relationshipBody")
    second = parse_as_ast_node(str(first), grammar_node="relationshipBody")

    assert isinstance(first, RelationshipBody)
    assert first == second
