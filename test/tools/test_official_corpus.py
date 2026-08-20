"""Unit tests for the repository-owned official-model corpus reporter."""

import pytest

from pysysmlv2.syntax import RawElement
from test.testings import get_testfile, official_model_files
from tools import official_corpus
from tools.official_corpus import build_report, inspect_model

pytestmark = pytest.mark.unit


def test_official_model_files_are_local_and_complete():
    files = official_model_files()
    assert len(files) == 251
    assert all("test/testfile/omg_release_2026_05" in path.as_posix() for path in files)
    assert {path.suffix for path in files} == {".sysml"}


@pytest.mark.parametrize(
    "path",
    official_model_files(),
    ids=lambda path: path.relative_to(get_testfile("omg_release_2026_05")).as_posix(),
)
def test_every_official_fixture_parses_and_reaches_a_round_trip_fixed_point(path):
    """Keep every copied OMG release example on the AST conformance path."""
    root = get_testfile("omg_release_2026_05")
    result = inspect_model(str(path), str(root))
    assert result == {
        "category": "passed",
        "detail": "",
        "path": path.relative_to(root).as_posix(),
    }


def test_build_report_classifies_a_canonical_local_model(tmp_path):
    model = tmp_path / "demo.sysml"
    model.write_text("package Demo { }", encoding="utf-8")
    report = build_report(tmp_path)
    assert report["total"] == 1
    assert report["corpus_total"] == 1
    assert report["offset"] == 0
    assert report["summary"] == {"passed": 1}
    assert report["rows"] == [{"category": "passed", "detail": "", "path": "demo.sysml"}]


def test_inspect_model_requires_full_ast_equality_after_reparse(tmp_path, monkeypatch):
    model = tmp_path / "demo.sysml"
    model.write_text("demo", encoding="utf-8")
    results = iter(
        [
            type("Result", (), {"ok": True, "ast": RawElement("first"), "diagnostics": []})(),
            type("Result", (), {"ok": True, "ast": RawElement("second"), "diagnostics": []})(),
        ]
    )
    monkeypatch.setattr(official_corpus, "parse", lambda *args, **kwargs: next(results))
    result = inspect_model(str(model), str(tmp_path))
    assert result["category"] == "ast_mismatch"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        pytest.param({"jobs": 0}, "jobs", id="worker-count"),
        pytest.param({"offset": -1}, "offset", id="negative-offset"),
        pytest.param({"limit": 0}, "limit", id="zero-limit"),
    ],
)
def test_build_report_rejects_invalid_slice_options(tmp_path, kwargs, message):
    with pytest.raises(ValueError, match=message):
        build_report(tmp_path, **kwargs)
