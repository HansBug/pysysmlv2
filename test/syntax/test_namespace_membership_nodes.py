"""Exact AST assertions for alias, import, and package-filter syntax."""

import pytest

from pysysmlv2 import parse
from pysysmlv2.syntax.ast import (
    AliasMember,
    BinaryExpression,
    ElementFilterMember,
    FilterPackage,
    Identification,
    ImportRule,
    MembershipImport,
    NamespaceImport,
    QualifiedReference,
    RelationshipBody,
    TypeOperationExpression,
)

pytestmark = pytest.mark.unit


def _package_member(source):
    """Return the first concrete member in a one-package fixture."""
    result = parse(source, "namespace-members.sysml")
    assert result.ok, result.diagnostics
    package = result.ast.members[0].element
    return result, package.members[0]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "package P { alias A for B; }",
            AliasMember(
                target=QualifiedReference(["B"]),
                relationship_body=RelationshipBody(";"),
                identification=Identification(declared_name="A"),
            ),
        ),
        (
            "package P { alias <Short> Long for A::B { } }",
            AliasMember(
                target=QualifiedReference(["A", "B"]),
                relationship_body=RelationshipBody("{ }"),
                identification=Identification(short_name="Short", declared_name="Long"),
            ),
        ),
    ],
)
def test_alias_member_has_explicit_fields_and_round_trips(source, expected):
    """Alias names, target, and relationship body are not opaque text."""
    result, member = _package_member(source)
    assert member == expected
    rendered = str(result.ast)
    reparsed = parse(rendered)
    assert reparsed.ok, reparsed.diagnostics
    assert reparsed.ast == result.ast


@pytest.mark.parametrize(
    ("source", "declaration"),
    [
        ("package P { import A::B; }", MembershipImport(QualifiedReference(["A", "B"]))),
        (
            "package P { import A::**; }",
            MembershipImport(QualifiedReference(["A"]), is_all_members=True),
        ),
        ("package P { import A::*; }", NamespaceImport(QualifiedReference(["A"]))),
        (
            "package P { import A::*::**; }",
            NamespaceImport(QualifiedReference(["A"]), is_recursive=True),
        ),
    ],
)
def test_import_rule_preserves_import_alternative(source, declaration):
    """Membership and namespace wildcard forms retain distinct node types."""
    result, member = _package_member(source)
    assert isinstance(member, ImportRule)
    assert member.import_declaration == declaration
    assert str(parse(str(result.ast)).ast) == str(result.ast)


def test_filtered_import_and_element_filter_retain_expression_nodes():
    """Filtered imports and package filters expose their predicate AST."""
    result, member = _package_member("package P { import A::**[@Safety and ready]; }")
    assert isinstance(member, ImportRule)
    declaration = member.import_declaration
    assert isinstance(declaration, FilterPackage)
    assert isinstance(declaration.import_declaration, MembershipImport)
    assert declaration.import_declaration.is_all_members
    assert isinstance(declaration.filters[0], BinaryExpression)
    assert isinstance(declaration.filters[0].left, TypeOperationExpression)
    assert declaration.filters[0].left.operator == "@"
    assert str(parse(str(result.ast)).ast) == str(result.ast)

    # ``namespaceImportDirect`` is the other filtered-import base alternative;
    # keep it distinct from membership ``::*`` imports.
    namespace_result, namespace_member = _package_member("package P { import A::*[ready]; }")
    namespace_declaration = namespace_member.import_declaration
    assert isinstance(namespace_declaration, FilterPackage)
    assert isinstance(namespace_declaration.import_declaration, NamespaceImport)
    assert str(parse(str(namespace_result.ast)).ast) == str(namespace_result.ast)

    _, filter_member = _package_member("package P { private filter @Safety; }")
    assert isinstance(filter_member, ElementFilterMember)
    assert filter_member.member_prefix == "private"
    assert isinstance(filter_member.expression, TypeOperationExpression)
    assert str(filter_member) == "private filter @Safety;"


@pytest.mark.parametrize(
    "source",
    [
        "package P { part def D { private import A::*; alias A for B; } }",
        "package P { action A { public import B::C; alias X for C; } }",
    ],
)
def test_nested_namespace_members_are_not_raw_elements(source):
    """Definition and action containment dispatches retain typed members."""
    result = parse(source)
    assert result.ok, result.diagnostics
    assert "RawElement" not in repr(result.ast)
    reparsed = parse(str(result.ast))
    assert reparsed.ok, reparsed.diagnostics
    assert reparsed.ast == result.ast
