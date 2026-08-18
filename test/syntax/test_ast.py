"""Unit tests for syntax AST nodes."""

import pytest

from pysysmlv2.syntax.ast import Comment, Documentation, Model, Package, SourceSpan

pytestmark = pytest.mark.unit


def test_source_span_contains_child():
    assert SourceSpan(1, 1, 1, 20).contains(SourceSpan(1, 2, 1, 5))


def test_package_str_is_canonical_sysml():
    tree = Model(members=[Package(name="Demo")])
    assert str(tree) == "package Demo {}"


def test_documentation_is_model_content_and_round_trips():
    tree = Model(
        members=[
            Package(
                name="Demo",
                documentation=[Documentation(text="A demo package")],
            )
        ]
    )
    rendered = str(tree)
    assert "/**" in rendered
    assert "A demo package" in rendered


def test_model_owned_comment_is_exported():
    rendered = str(Model(members=[Comment(text="A note"), Package(name="Demo")]))
    assert rendered == "/* A note */\n\npackage Demo {}"
