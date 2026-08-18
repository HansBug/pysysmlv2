"""Unit tests for the ANTLR artifact builder."""

import json

import pytest

from tools import antlr_build

pytestmark = pytest.mark.unit


def test_sha256_reads_binary_content(tmp_path):
    path = tmp_path / "payload.bin"
    path.write_bytes(b"pysysmlv2")

    assert antlr_build._sha256(path) == (
        "868d406332014c515abae9db2453aa98860689539b5d84b7a6f4cf41a2d8ef6e"
    )


def test_ensure_antlr_jar_accepts_the_pinned_checksum(tmp_path, monkeypatch):
    jar = tmp_path / "antlr.jar"
    jar.write_bytes(b"jar")
    monkeypatch.setattr(antlr_build, "ANTLR_DIR", tmp_path)
    monkeypatch.setattr(antlr_build, "ANTLR_JAR", jar)
    monkeypatch.setattr(antlr_build, "ANTLR_SHA256", antlr_build._sha256(jar))

    assert antlr_build.ensure_antlr_jar() == jar


def test_git_metadata_falls_back_when_upstream_is_not_a_git_checkout(monkeypatch):
    def missing(*args, **kwargs):
        raise antlr_build.subprocess.CalledProcessError(1, args[0])

    monkeypatch.setattr(antlr_build.subprocess, "check_output", missing)

    assert antlr_build._git_metadata() == {
        "source_commit": "unknown",
        "source_tag": "unknown",
    }


def test_build_writes_generated_files_and_manifest(tmp_path, monkeypatch):
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "SysMLv2Lexer.g4").write_text("lexer", encoding="utf-8")
    (generated / "SysMLv2Parser.g4").write_text("parser", encoding="utf-8")
    (generated / "old.py").write_text("stale", encoding="utf-8")
    antlr_dir = tmp_path / "antlr"
    jar = tmp_path / "antlr.jar"
    jar.write_bytes(b"jar")
    temp = antlr_dir / "generated"
    temp.mkdir(parents=True)
    for name in (
        "SysMLv2Lexer.py",
        "SysMLv2Lexer.tokens",
        "SysMLv2Lexer.interp",
        "SysMLv2Parser.py",
        "SysMLv2Parser.tokens",
        "SysMLv2Parser.interp",
        "SysMLv2ParserListener.py",
    ):
        (temp / name).write_text(name, encoding="utf-8")

    monkeypatch.setattr(antlr_build, "GENERATED", generated)
    monkeypatch.setattr(antlr_build, "ANTLR_DIR", antlr_dir)
    monkeypatch.setattr(antlr_build, "ensure_antlr_jar", lambda: jar)
    monkeypatch.setattr(
        antlr_build,
        "_git_metadata",
        lambda: {"source_commit": "abc", "source_tag": "v1"},
    )
    calls = []
    monkeypatch.setattr(antlr_build.subprocess, "check_call", lambda command: calls.append(command))

    antlr_build.build()

    assert calls[0][0:2] == ["java", "-jar"]
    assert not (generated / "old.py").exists()
    assert (generated / "__init__.py").is_file()
    manifest = json.loads((generated / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_commit"] == "abc"
    assert manifest["source_grammar_sha256"] == {
        "lexer": antlr_build._sha256(generated / "SysMLv2Lexer.g4"),
        "parser": antlr_build._sha256(generated / "SysMLv2Parser.g4"),
    }
