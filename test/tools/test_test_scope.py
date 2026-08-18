"""Unit tests for source-mirrored test scope resolution."""

import sys

import pytest

from tools import test_scope

pytestmark = pytest.mark.unit


def test_resolve_maps_source_module_to_mirrored_test(tmp_path, monkeypatch):
    source = tmp_path / "pysysmlv2"
    tests = tmp_path / "test"
    (source / "syntax").mkdir(parents=True)
    (tests / "syntax").mkdir(parents=True)
    (source / "syntax" / "parser.py").write_text("", encoding="utf-8")
    (tests / "syntax" / "test_parser.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(test_scope, "SRC", source)
    monkeypatch.setattr(test_scope, "TEST", tests)

    resolved_tests, resolved_source = test_scope.resolve("syntax/parser.py")

    assert resolved_tests == [tests / "syntax" / "test_parser.py"]
    assert resolved_source == source / "syntax"


def test_resolve_rejects_missing_mirrored_test(tmp_path, monkeypatch):
    source = tmp_path / "pysysmlv2"
    (source / "syntax").mkdir(parents=True)
    (source / "syntax" / "parser.py").write_text("", encoding="utf-8")
    monkeypatch.setattr(test_scope, "SRC", source)
    monkeypatch.setattr(test_scope, "TEST", tmp_path / "test")
    monkeypatch.setattr(test_scope, "ROOT", tmp_path)

    with pytest.raises(SystemExit, match="mirrored test"):
        test_scope.resolve("syntax/parser.py")


def test_main_uses_current_interpreter(monkeypatch):
    monkeypatch.setattr(test_scope, "resolve", lambda value: ([test_scope.TEST], test_scope.SRC))
    monkeypatch.setattr(test_scope.subprocess, "call", lambda command, cwd: command)
    monkeypatch.setattr(sys, "argv", ["test_scope", "--range", "."])

    with pytest.raises(SystemExit) as error:
        test_scope.main()

    assert error.value.code[0:3] == [sys.executable, "-m", "pytest"]
