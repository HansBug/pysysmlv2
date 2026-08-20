"""Integration tests for parser-to-AST canonical round-trip."""

import pytest

from pysysmlv2 import parse
from test.testings import get_testfile

pytestmark = pytest.mark.integration


def test_nested_package_content_remains_parseable():
    original = "package Demo { part def Vehicle; }"
    first = parse(original, "demo.sysml")
    exported = str(first.ast)
    second = parse(exported, "roundtrip.sysml")
    assert first.ok and second.ok
    assert str(second.ast) == exported


@pytest.mark.parametrize(
    "filename",
    ["camera.sysml", "toaster-system.sysml", "vehicle-model.sysml"],
)
def test_checked_in_upstream_examples_parse_and_round_trip(filename):
    """Keep the pinned grammar's representative examples on the AST path."""
    path = get_testfile("upstream_examples", filename)
    first = parse(path.read_text(encoding="utf-8"), str(path))
    exported = str(first.ast)
    second = parse(exported, "roundtrip.sysml")
    assert first.ok and second.ok
    assert str(second.ast) == exported
