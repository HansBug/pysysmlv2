"""Unit tests for generated artifact verification."""

import json
import subprocess

import pytest

from tools import check_generated

pytestmark = pytest.mark.unit


def test_repository_guidance_link_and_generated_tree_are_valid():
    check_generated._check_agents_link()
    check_generated._check_generated_files()
    check_generated._check_manifest()


def test_guidance_file_must_be_a_symlink(tmp_path, monkeypatch):
    (tmp_path / "CLAUDE.md").write_text("rules", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("rules", encoding="utf-8")
    monkeypatch.setattr(check_generated, "ROOT", tmp_path)

    with pytest.raises(SystemExit, match="symlink"):
        check_generated._check_agents_link()


def test_generated_tree_must_include_every_artifact(tmp_path, monkeypatch):
    generated = tmp_path / "generated"
    generated.mkdir()
    monkeypatch.setattr(check_generated, "GENERATED", generated)

    with pytest.raises(SystemExit, match="missing"):
        check_generated._check_generated_files()


def test_check_uses_current_interpreter_and_runs_all_verifiers(monkeypatch):
    calls = []
    for name in (
        "_check_agents_link",
        "_check_generated_files",
        "_check_manifest",
        "_check_tracked_files",
    ):
        monkeypatch.setattr(check_generated, name, lambda name=name: calls.append(name))
    command = []
    monkeypatch.setattr(
        check_generated.subprocess,
        "check_call",
        lambda args, cwd: command.extend((args, cwd)),
    )
    monkeypatch.setattr(
        check_generated.subprocess,
        "run",
        lambda args, cwd: subprocess.CompletedProcess(args, 0),
    )

    check_generated.check()

    assert command == [
        [check_generated.os.environ.get("MAKE", "make"), "antlr_update"],
        str(check_generated.ROOT),
    ]
    assert calls == [
        "_check_agents_link",
        "_check_generated_files",
        "_check_manifest",
        "_check_tracked_files",
    ]


def test_manifest_hashes_must_match_grammar_inputs(tmp_path, monkeypatch):
    generated = tmp_path / "generated"
    generated.mkdir()
    for name in check_generated.GENERATED_FILES:
        (generated / name).write_text("artifact", encoding="utf-8")
    (generated / "SysMLv2Lexer.g4").write_text("lexer", encoding="utf-8")
    (generated / "SysMLv2Parser.g4").write_text("parser", encoding="utf-8")
    manifest = {
        "antlr_jar_sha256": "0" * 64,
        "antlr_version": "4.13.2",
        "grammar_version": "2026.05.0",
        "omg_release": "2026-05",
        "source_commit": "abc",
        "source_grammar_sha256": {"lexer": "bad", "parser": "bad"},
        "source_repository": "https://example.invalid/grammar",
        "source_tag": "v1",
    }
    (generated / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(check_generated, "GENERATED", generated)

    with pytest.raises(SystemExit, match="grammar hashes"):
        check_generated._check_manifest()
