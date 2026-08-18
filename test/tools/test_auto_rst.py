"""Unit tests for Python API RST generation."""

import pytest

from tools import auto_rst

pytestmark = pytest.mark.unit


def test_public_symbols_ignores_private_declarations(tmp_path):
    source = tmp_path / "module.py"
    source.write_text(
        "def public(): pass\nclass Public: pass\ndef _private(): pass\n",
        encoding="utf-8",
    )

    assert auto_rst._public_symbols(source) == ["public", "Public"]


def test_generate_writes_module_pages_and_index(tmp_path, monkeypatch):
    source = tmp_path / "pysysmlv2"
    (source / "config").mkdir(parents=True)
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "config" / "meta.py").write_text("VALUE = 1\n", encoding="utf-8")
    (source / "config" / "_private.py").write_text("VALUE = 2\n", encoding="utf-8")
    (source / "config" / "generated").mkdir()
    (source / "config" / "generated" / "parser.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(auto_rst, "SOURCE", source)
    monkeypatch.setattr(auto_rst, "ROOT", tmp_path)
    output = tmp_path / "docs"

    auto_rst.generate(output)

    assert (output / "index.rst").is_file()
    assert (output / "config" / "meta.rst").is_file()
    assert not (output / "config" / "_private.rst").exists()
    assert "config/meta" in (output / "index.rst").read_text(encoding="utf-8")
