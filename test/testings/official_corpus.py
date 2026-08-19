"""Locate the repository-owned OMG release corpus used by conformance tests."""

from pathlib import Path
from typing import Tuple

from .testfile import get_testfile


def official_model_files() -> Tuple[Path, ...]:
    """Return every checked-in SysML v2 fixture in stable path order."""
    root = get_testfile("omg_release_2026_05")
    return tuple(sorted(root.rglob("*.sysml")))
