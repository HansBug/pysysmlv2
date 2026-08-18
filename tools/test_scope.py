"""Resolve source-mirrored unit-test scopes and run pytest.

The source/test layout is part of the repository workflow: ``pysysmlv2/x.py``
maps to ``test/test_x.py`` and subdirectories map one-to-one. This module keeps
``make unittest RANGE_DIR=...`` consistent on Windows, macOS, and Linux.

.. list-table:: Test-scope roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`resolve`
     - Map a source scope to mirrored tests.
   * - :func:`main`
     - Invoke pytest for the selected scope.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "pysysmlv2"
TEST = ROOT / "test"


def _file_scope(value: str):
    source = SRC / value
    if source.suffix != ".py":
        return None
    relative = source.relative_to(SRC)
    name = relative.stem
    if name == "__init__":
        name = "init"
    target = TEST / relative.parent / ("test_" + name + ".py")
    return source, target


def resolve(value: str):
    """Resolve a source scope to its mirrored pytest path and source root.

    :param value: Source directory, source Python path, or ``.`` for all tests.
    :type value: str
    :return: A pair containing pytest paths and the covered source path.
    :rtype: tuple[list[pathlib.Path], pathlib.Path]
    :raises SystemExit: If the requested source or mirrored test does not exist.

    Example::

        >>> tests, source = resolve("syntax")
        >>> source.name
        'syntax'
    """
    if value in ("", "."):
        return [TEST], SRC
    file_scope = _file_scope(value)
    if file_scope is not None:
        source, test = file_scope
        if not source.is_file():
            raise SystemExit("source file does not exist: " + value)
        if not test.is_file():
            raise SystemExit("mirrored test file does not exist: " + str(test.relative_to(ROOT)))
        return [test], source.parent
    source_dir = SRC / value
    test_dir = TEST / value
    if not source_dir.is_dir() or not test_dir.is_dir():
        raise SystemExit("scope must be a source directory or source .py path: " + value)
    return [test_dir], source_dir


def main() -> None:
    """Run source-mirrored unit tests selected by ``--range``.

    :return: The pytest process status via ``SystemExit``.
    :rtype: None
    :raises SystemExit: With the pytest process status or invalid-scope errors.

    Example::

        $ make unittest RANGE_DIR=syntax
    """
    parser = argparse.ArgumentParser(description="Run source-mirrored pysysmlv2 unit tests.")
    parser.add_argument("--range", default=".", dest="range_value")
    args = parser.parse_args()
    tests, source = resolve(args.range_value)
    command = [sys.executable, "-m", "pytest"] + [str(path) for path in tests]
    command += ["-m", "unit", "--cov=" + str(source.relative_to(ROOT))]
    raise SystemExit(subprocess.call(command, cwd=str(ROOT)))


if __name__ == "__main__":  # pragma: no cover
    main()
