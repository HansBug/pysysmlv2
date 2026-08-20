"""Regression tests for manual OMG example ledger materialization."""

from __future__ import annotations

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
