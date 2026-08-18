"""Unit tests for generated artifact verification."""

import subprocess

import pytest

from tools import check_generated

pytestmark = pytest.mark.unit


def test_repository_guidance_link_and_generated_tree_are_valid():
    check_generated._check_agents_link()
    check_generated._check_generated_files()


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
        "_check_tracked_files",
    ]
