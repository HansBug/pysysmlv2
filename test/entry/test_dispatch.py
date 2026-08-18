"""Unit tests for the Click CLI entry point."""

import pytest
from click.testing import CliRunner

from pysysmlv2.entry.dispatch import cli

pytestmark = pytest.mark.unit


def test_version_option():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "pysysmlv2" in result.output


def test_parse_json(tmp_path):
    source = tmp_path / "demo.sysml"
    source.write_text("package Demo { }", encoding="utf-8")
    result = CliRunner().invoke(cli, ["parse", str(source), "--json"])
    assert result.exit_code == 0
    assert '"ok": true' in result.output
