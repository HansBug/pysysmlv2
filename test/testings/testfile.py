"""Locate repository-owned fixture assets without depending on a submodule."""

from pathlib import Path

TESTFILE_DIR = Path(__file__).parents[1] / "testfile"


def get_testfile(filename: str, *segments: str) -> Path:
    """Return the path of a fixture below the non-module ``test/testfile`` tree."""
    return TESTFILE_DIR.joinpath(filename, *segments)
