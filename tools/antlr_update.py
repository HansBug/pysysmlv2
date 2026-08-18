"""Copy pinned upstream G4 inputs into the generated package and build them.

The upstream submodule is the source of grammar files; the generated package
is an intentionally machine-owned directory. This module keeps the update
sequence explicit so ``make antlr_update`` is reproducible across platforms.

.. list-table:: ANTLR update roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`update`
     - Copy the pinned G4 files and invoke :func:`tools.antlr_build.build`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import antlr_build

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream" / "sysml-v2-grammar" / "grammar"
GENERATED = ROOT / "pysysmlv2" / "syntax" / "generated"


def update() -> None:
    """Copy upstream grammar files and invoke ANTLR generation.

    :return: ``None`` after the generated package is rebuilt.
    :rtype: None
    :raises FileNotFoundError: If the submodule or either G4 input is missing.
    :raises subprocess.CalledProcessError: If ANTLR generation fails.

    Example::

        $ make antlr_update
    """
    if not UPSTREAM.is_dir():
        raise FileNotFoundError("upstream grammar submodule is not initialized")
    GENERATED.mkdir(parents=True, exist_ok=True)
    for name in ("SysMLv2Lexer.g4", "SysMLv2Parser.g4"):
        source = UPSTREAM / name
        if not source.is_file():
            raise FileNotFoundError(str(source))
        shutil.copy2(str(source), str(GENERATED / name))
    antlr_build.build()


if __name__ == "__main__":  # pragma: no cover
    update()
