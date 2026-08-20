"""Clean package artifacts and validate package metadata.

This tool keeps source-tree package checks independent of shell syntax. It
validates the canonical version and generated parser presence, while package
building itself remains delegated to ``python -m build`` through the Makefile.

.. list-table:: Package-check roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`clean`
     - Remove local build and distribution output.
   * - :func:`check`
     - Verify version metadata and generated package data.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATED_PACKAGE_FILES = (
    "__init__.py",
    "SysMLv2Lexer.g4",
    "SysMLv2Lexer.py",
    "SysMLv2Lexer.interp",
    "SysMLv2Lexer.tokens",
    "SysMLv2Parser.g4",
    "SysMLv2Parser.py",
    "SysMLv2Parser.interp",
    "SysMLv2Parser.tokens",
    "SysMLv2ParserListener.py",
    "UPSTREAM_LICENSE.txt",
    "grammar-provenance.json",
)


def clean() -> None:
    """Remove local Python build output without shell-specific commands.

    :return: ``None`` after ignored build directories are removed.
    :rtype: None

    Example::

        $ python -m tools.package_check --clean
    """
    for name in ("build", "dist"):
        path = ROOT / name
        if path.exists():
            shutil.rmtree(str(path))
    for path in ROOT.glob("*.egg-info"):
        shutil.rmtree(str(path))


def check() -> None:
    """Check setup metadata and required generated package data.

    :return: ``None`` when package invariants hold.
    :rtype: None
    :raises SystemExit: If version metadata or generated parser files disagree.

    Example::

        $ make package_check
    """
    namespace = {}
    exec((ROOT / "pysysmlv2" / "config" / "meta.py").read_text(encoding="utf-8"), namespace)
    if namespace["__VERSION__"] != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
        raise SystemExit("VERSION and package metadata disagree")
    generated = ROOT / "pysysmlv2" / "syntax" / "generated"
    missing = [name for name in GENERATED_PACKAGE_FILES if not (generated / name).is_file()]
    if missing:
        raise SystemExit("generated package data is missing: {}".format(", ".join(missing)))


if __name__ == "__main__":  # pragma: no cover
    cli = argparse.ArgumentParser()
    cli.add_argument("--clean", action="store_true")
    options = cli.parse_args()
    if options.clean:
        clean()
    else:
        check()
