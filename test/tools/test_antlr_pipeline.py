"""Unit tests for the portable ANTLR generation orchestration."""

import pytest

from tools import antlr_pipeline

pytestmark = pytest.mark.unit


def test_copy_upstream_grammar_copies_only_declared_inputs(tmp_path, monkeypatch):
    upstream = tmp_path / "upstream"
    source_grammar = upstream / "grammar"
    generated = tmp_path / "generated"
    source_grammar.mkdir(parents=True)
    (upstream / "LICENSE").write_bytes(b"license\r\n")
    (source_grammar / "SysMLv2Lexer.g4").write_bytes(b"lexer\r\n")
    (source_grammar / "SysMLv2Parser.g4").write_bytes(b"parser\r\n")
    copies = (
        (source_grammar / "SysMLv2Lexer.g4", generated / "SysMLv2Lexer.g4"),
        (source_grammar / "SysMLv2Parser.g4", generated / "SysMLv2Parser.g4"),
        (upstream / "LICENSE", generated / "UPSTREAM_LICENSE.txt"),
    )
    monkeypatch.setattr(antlr_pipeline, "GENERATED", generated)
    monkeypatch.setattr(antlr_pipeline, "_UPSTREAM_COPIES", copies)

    antlr_pipeline._copy_upstream_grammar()

    assert sorted(path.name for path in generated.iterdir()) == [
        "SysMLv2Lexer.g4",
        "SysMLv2Parser.g4",
        "UPSTREAM_LICENSE.txt",
    ]
    assert (generated / "SysMLv2Parser.g4").read_text(encoding="utf-8") == "parser\n"
    assert all(b"\r\n" not in path.read_bytes() for path in generated.iterdir())


def test_copy_upstream_grammar_reports_missing_input(tmp_path, monkeypatch):
    generated = tmp_path / "generated"
    missing = tmp_path / "missing.g4"
    monkeypatch.setattr(antlr_pipeline, "GENERATED", generated)
    monkeypatch.setattr(
        antlr_pipeline,
        "_UPSTREAM_COPIES",
        ((missing, generated / "missing.g4"),),
    )

    with pytest.raises(SystemExit, match="upstream grammar input is missing"):
        antlr_pipeline._copy_upstream_grammar()


def test_build_uses_argument_lists_and_replaces_generated_outputs(tmp_path, monkeypatch):
    generated = tmp_path / "generated"
    temp = tmp_path / "antlr-temp"
    jar = tmp_path / "antlr.jar"
    generated.mkdir()
    (generated / "SysMLv2Lexer.g4").write_text("lexer\n", encoding="utf-8")
    (generated / "SysMLv2Parser.g4").write_text("parser\n", encoding="utf-8")
    (generated / "old.py").write_text("old\n", encoding="utf-8")
    (generated / "old.tokens").write_text("old\n", encoding="utf-8")
    (generated / "old.interp").write_text("old\n", encoding="utf-8")
    (generated / "manifest.json").write_text("old\n", encoding="utf-8")
    commands = []
    formatted = []

    def fake_check_call(arguments, cwd):
        commands.append((arguments, cwd))
        if arguments[0] == "java":
            temp.mkdir(parents=True, exist_ok=True)
            (temp / "SysMLv2Lexer.py").write_bytes(b"lexer\r\n")
            (temp / "SysMLv2Parser.py").write_bytes(b"parser\r\n")
            (temp / "SysMLv2ParserListener.py").write_bytes(b"listener\r\n")
            (temp / "SysMLv2Lexer.tokens").write_bytes(b"tokens\r\n")
            (temp / "SysMLv2Parser.tokens").write_bytes(b"tokens\r\n")
            (temp / "SysMLv2Lexer.interp").write_bytes(b"interp\r\n")
            (temp / "SysMLv2Parser.interp").write_bytes(b"interp\r\n")

    monkeypatch.setattr(antlr_pipeline, "GENERATED", generated)
    monkeypatch.setattr(antlr_pipeline, "ANTLR_TEMP", temp)
    monkeypatch.setattr(antlr_pipeline, "ANTLR_JAR", jar)
    monkeypatch.setattr(antlr_pipeline, "_download_antlr_jar", lambda: None)
    monkeypatch.setattr(
        antlr_pipeline,
        "_format_generated_python",
        lambda paths: formatted.extend(paths),
    )
    monkeypatch.setattr(antlr_pipeline.subprocess, "check_call", fake_check_call)

    antlr_pipeline.build()

    java_command = commands[0][0]
    assert java_command[:4] == ["java", "-jar", str(jar), "-Dlanguage=Python3"]
    assert all(isinstance(value, str) for value in java_command)
    assert not (generated / "old.py").exists()
    assert not (generated / "manifest.json").exists()
    assert (generated / "SysMLv2Parser.py").read_text(encoding="utf-8") == "parser\n"
    assert all(b"\r\n" not in path.read_bytes() for path in generated.iterdir())
    assert (
        (generated / "__init__.py")
        .read_text(encoding="utf-8")
        .startswith('"""Generated ANTLR4 Python modules;')
    )
    assert {path.name for path in formatted} == {
        "SysMLv2Lexer.py",
        "SysMLv2Parser.py",
        "SysMLv2ParserListener.py",
        "__init__.py",
    }


def test_build_rejects_empty_java_output(tmp_path, monkeypatch):
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "SysMLv2Lexer.g4").write_text("lexer\n", encoding="utf-8")
    (generated / "SysMLv2Parser.g4").write_text("parser\n", encoding="utf-8")
    monkeypatch.setattr(antlr_pipeline, "GENERATED", generated)
    monkeypatch.setattr(antlr_pipeline, "ANTLR_TEMP", tmp_path / "temp")
    monkeypatch.setattr(antlr_pipeline, "_download_antlr_jar", lambda: None)
    monkeypatch.setattr(antlr_pipeline.subprocess, "check_call", lambda *args, **kwargs: None)

    with pytest.raises(SystemExit, match="ANTLR generated no"):
        antlr_pipeline.build()


def test_main_dispatches_to_requested_operation(monkeypatch):
    calls = []
    monkeypatch.setattr(antlr_pipeline, "build", lambda: calls.append("build"))
    monkeypatch.setattr(antlr_pipeline, "update", lambda: calls.append("update"))

    assert antlr_pipeline.main(["build"]) == 0
    assert antlr_pipeline.main(["update"]) == 0
    assert calls == ["build", "update"]
