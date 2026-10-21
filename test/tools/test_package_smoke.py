"""Unit tests for portable wheel smoke-test setup."""

import pytest

from tools import package_smoke

pytestmark = pytest.mark.unit


def test_find_wheel_requires_exactly_one_wheel(tmp_path):
    """Select one wheel and reject missing or ambiguous distributions."""
    with pytest.raises(SystemExit, match="exactly one wheel"):
        package_smoke.find_wheel(tmp_path)

    first = tmp_path / "first.whl"
    first.write_bytes(b"wheel")
    assert package_smoke.find_wheel(tmp_path) == first

    (tmp_path / "second.whl").write_bytes(b"wheel")
    with pytest.raises(SystemExit, match="exactly one wheel"):
        package_smoke.find_wheel(tmp_path)


def test_venv_python_uses_current_platform_convention(monkeypatch, tmp_path):
    """Keep executable selection explicit for Windows and POSIX hosts."""
    monkeypatch.setattr(package_smoke.sys, "platform", "win32")
    assert package_smoke._venv_python(tmp_path) == tmp_path / "Scripts" / "python.exe"
    monkeypatch.setattr(package_smoke.sys, "platform", "linux")
    assert package_smoke._venv_python(tmp_path) == tmp_path / "bin" / "python"
