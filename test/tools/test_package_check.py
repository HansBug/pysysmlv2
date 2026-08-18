"""Unit tests for package metadata checks."""

import pytest

from tools import package_check

pytestmark = pytest.mark.unit


def test_clean_removes_local_build_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(package_check, "ROOT", tmp_path)
    (tmp_path / "build").mkdir()
    (tmp_path / "dist").mkdir()
    (tmp_path / "pysysmlv2.egg-info").mkdir()

    package_check.clean()

    assert not (tmp_path / "build").exists()
    assert not (tmp_path / "dist").exists()
    assert not (tmp_path / "pysysmlv2.egg-info").exists()


def test_check_rejects_version_mismatch(tmp_path, monkeypatch):
    meta = tmp_path / "pysysmlv2" / "config"
    generated = tmp_path / "pysysmlv2" / "syntax" / "generated"
    meta.mkdir(parents=True)
    generated.mkdir(parents=True)
    (meta / "meta.py").write_text('__VERSION__ = "1.0"\n', encoding="utf-8")
    (tmp_path / "VERSION").write_text("2.0\n", encoding="utf-8")
    (generated / "SysMLv2Parser.py").write_text("parser", encoding="utf-8")
    monkeypatch.setattr(package_check, "ROOT", tmp_path)

    with pytest.raises(SystemExit, match="VERSION"):
        package_check.check()
