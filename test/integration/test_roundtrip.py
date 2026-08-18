"""Integration tests for parser-to-AST canonical round-trip."""

import pytest

from pysysmlv2 import parse

pytestmark = pytest.mark.integration


def test_nested_package_content_remains_parseable():
    original = "package Demo { part def Vehicle; }"
    first = parse(original, "demo.sysml")
    exported = str(first.ast)
    second = parse(exported, "roundtrip.sysml")
    assert first.ok and second.ok
    assert str(second.ast) == exported
