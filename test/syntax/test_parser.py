"""Unit tests for the ANTLR parser adapter."""

import pytest

from pysysmlv2.syntax.parser import parse

pytestmark = pytest.mark.unit


def test_valid_package_has_no_diagnostics():
    result = parse("package Demo { part def Vehicle; }", "demo.sysml")
    assert result.ok
    assert result.diagnostics == []
    assert "package Demo" in str(result.ast)


def test_invalid_package_reports_structured_diagnostic():
    result = parse("package Demo {", "demo.sysml")
    assert not result.ok
    assert result.diagnostics[0].source_path == "demo.sysml"
    assert result.diagnostics[0].line == 1
    assert result.diagnostics[0].column > 0


def test_ast_export_can_be_parsed_again():
    first = parse("package Demo { part def Vehicle; }")
    second = parse(str(first.ast))
    assert first.ok and second.ok
    assert str(second.ast) == str(first.ast)


def test_model_comment_before_package_survives_export():
    result = parse("/* note */ package Demo { }")
    assert result.ok
    assert "/* note */" in str(result.ast)
    assert parse(str(result.ast)).ok
