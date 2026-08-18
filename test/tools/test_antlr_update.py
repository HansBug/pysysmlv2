"""Unit tests for upstream grammar synchronization."""

import pytest

from tools import antlr_build, antlr_update

pytestmark = pytest.mark.unit


def test_update_copies_pinned_grammars_and_builds(tmp_path, monkeypatch):
    upstream = tmp_path / "upstream" / "grammar"
    generated = tmp_path / "generated"
    upstream.mkdir(parents=True)
    (upstream / "SysMLv2Lexer.g4").write_text("lexer", encoding="utf-8")
    (upstream / "SysMLv2Parser.g4").write_text("parser", encoding="utf-8")
    monkeypatch.setattr(antlr_update, "UPSTREAM", upstream)
    monkeypatch.setattr(antlr_update, "GENERATED", generated)
    calls = []
    monkeypatch.setattr(antlr_build, "build", lambda: calls.append(True))

    antlr_update.update()

    assert (generated / "SysMLv2Lexer.g4").read_text(encoding="utf-8") == "lexer"
    assert (generated / "SysMLv2Parser.g4").read_text(encoding="utf-8") == "parser"
    assert calls == [True]


def test_update_reports_missing_submodule(tmp_path, monkeypatch):
    monkeypatch.setattr(antlr_update, "UPSTREAM", tmp_path / "missing")

    with pytest.raises(FileNotFoundError, match="submodule"):
        antlr_update.update()
