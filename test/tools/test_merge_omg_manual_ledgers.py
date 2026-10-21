"""Regression tests for manual OMG example ledger materialization."""

from __future__ import annotations

import pytest

from tools.merge_omg_manual_ledgers import materialize


def test_materialize_replaces_stale_generated_fixture_files(tmp_path):
    """Keep a ledger rerun from leaving excluded fixtures behind."""
    (tmp_path / "current.sysml").write_text("stale", encoding="utf-8")
    (tmp_path / "removed.sysml").write_text("stale", encoding="utf-8")
    inventory = {
        "entries": [
            {
                "fixture_name": "current.sysml",
                "source_code": "package Current { }",
            }
        ]
    }

    assert materialize(inventory, tmp_path) == 1
    assert (tmp_path / "current.sysml").read_text(encoding="utf-8") == "package Current { }\n"
    assert not (tmp_path / "removed.sysml").exists()


def test_materialize_preserves_declared_nested_fixture_names(tmp_path):
    """Keep manually chosen fixture paths and clean stale nested files."""
    stale = tmp_path / "annex_a" / "stale.sysml"
    stale.parent.mkdir()
    stale.write_text("stale", encoding="utf-8")
    inventory = {
        "entries": [
            {
                "fixture_name": "annex_a/vehicle.sysml",
                "source_code": "part def Vehicle;",
            }
        ]
    }

    assert materialize(inventory, tmp_path) == 1
    fixture = tmp_path / "annex_a" / "vehicle.sysml"
    assert fixture.read_text(encoding="utf-8") == "part def Vehicle;\n"
    assert not stale.exists()


@pytest.mark.parametrize("fixture_name", ["../escaped.sysml", "/tmp/escaped.sysml"])
def test_materialize_rejects_fixture_path_escape(tmp_path, fixture_name):
    """Never let ledger-controlled names write outside the fixture root."""
    with pytest.raises(ValueError, match="fixture_name"):
        materialize(
            {
                "entries": [
                    {
                        "fixture_name": fixture_name,
                        "source_code": "package Escaped { }",
                    }
                ]
            },
            tmp_path,
        )
