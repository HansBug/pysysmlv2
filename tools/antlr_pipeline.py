"""Run the checked-in ANTLR generation pipeline on every supported host.

The repository keeps the pinned grammar submodule as the only source for the
copied ``.g4`` files, while ``pysysmlv2/syntax/generated/`` is generated-only.
This module owns the filesystem and process orchestration around that boundary
so the Makefile does not depend on POSIX ``mkdir``, ``cp``, ``rm``, globbing, or
shell conditionals.  The ANTLR Java invocation itself remains the same as the
historical Makefile pipeline, and generated Python files are Ruff-formatted
after they are copied into the package.

.. list-table:: ANTLR pipeline roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`update`
     - Copy the pinned grammar, apply the reviewed overlay, and build artifacts.
   * - :func:`build`
     - Generate Python artifacts from the copied effective grammar.
   * - :func:`main`
     - Provide the Makefile and CI command-line entry point.

The helper deliberately does not edit handwritten AST or listener sources.
Only files under the generated directory and the ignored ``.antlr`` working
directory are written.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional, Sequence

from tools import grammar_overlay

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_GRAMMAR_ROOT = ROOT / "upstream" / "sysml-v2-grammar"
UPSTREAM_GRAMMAR = UPSTREAM_GRAMMAR_ROOT / "grammar"
GENERATED = ROOT / "pysysmlv2" / "syntax" / "generated"
ANTLR_DIR = ROOT / ".antlr"
ANTLR_VERSION = "4.13.2"
ANTLR_JAR = ANTLR_DIR / ("antlr-{}-complete.jar".format(ANTLR_VERSION))
ANTLR_TEMP = ANTLR_DIR / "generated"
ANTLR_DOWNLOAD = "https://www.antlr.org/download/antlr-{}-complete.jar".format(ANTLR_VERSION)

_UPSTREAM_COPIES = (
    (UPSTREAM_GRAMMAR / "SysMLv2Lexer.g4", GENERATED / "SysMLv2Lexer.g4"),
    (UPSTREAM_GRAMMAR / "SysMLv2Parser.g4", GENERATED / "SysMLv2Parser.g4"),
    (UPSTREAM_GRAMMAR_ROOT / "LICENSE", GENERATED / "UPSTREAM_LICENSE.txt"),
)
_DESTINATION_SUFFIXES = (".py", ".tokens", ".interp")


def _command_path(path: Path) -> str:
    """Return a stable repository-relative path for external tool arguments."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _normalize_lf(path: Path) -> None:
    """Normalize one generated text file to deterministic LF line endings.

    ANTLR and Ruff can emit the host platform's native line ending.  Generated
    artifacts are committed as LF (see ``.gitattributes``), so normalize after
    every external filesystem boundary instead of relying on Git checkout
    settings or the host's ``newline`` default.

    :param path: Text artifact whose bytes should use LF line endings.
    :type path: pathlib.Path
    :return: ``None`` after the file is normalized in place.
    :rtype: None
    """
    data = path.read_bytes()
    normalized = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if normalized != data:
        path.write_bytes(normalized)


def _copy_upstream_grammar() -> None:
    """Copy the pinned grammar inputs into the generated-only directory."""
    GENERATED.mkdir(parents=True, exist_ok=True)
    for source, destination in _UPSTREAM_COPIES:
        if not source.is_file():
            raise SystemExit("upstream grammar input is missing: {}".format(source))
        shutil.copyfile(str(source), str(destination))
        _normalize_lf(destination)


def _run_overlay() -> None:
    """Apply the reviewed overlay and write grammar provenance."""
    parser_grammar = GENERATED / "SysMLv2Parser.g4"
    manifest = GENERATED / "grammar-provenance.json"
    upstream_hash = grammar_overlay.sha256_file(parser_grammar)
    grammar_overlay.apply_overlay(parser_grammar)
    grammar_overlay.write_manifest(
        manifest,
        UPSTREAM_GRAMMAR,
        upstream_hash,
        grammar_overlay.sha256_file(parser_grammar),
    )


def _download_antlr_jar() -> None:
    """Download the pinned ANTLR JAR with an argument-list subprocess call."""
    ANTLR_DIR.mkdir(parents=True, exist_ok=True)
    if ANTLR_JAR.is_file():
        return
    subprocess.check_call(
        [
            "curl",
            "-fL",
            "--retry",
            "3",
            "--output",
            str(ANTLR_JAR),
            ANTLR_DOWNLOAD,
        ],
        cwd=str(ROOT),
    )


def _remove_generated_outputs() -> None:
    """Remove only ANTLR outputs that the next generation replaces."""
    for path in GENERATED.iterdir():
        if not path.is_file():
            continue
        if path.suffix in _DESTINATION_SUFFIXES or path.name == "manifest.json":
            path.unlink()


def _remove_temp_outputs() -> None:
    """Remove the ignored temporary ANTLR output tree if it exists."""
    shutil.rmtree(str(ANTLR_TEMP), ignore_errors=True)
    ANTLR_TEMP.mkdir(parents=True, exist_ok=True)


def _generated_outputs() -> Iterable[Path]:
    """Yield all ANTLR output files accepted by the historical copy step."""
    paths = list(ANTLR_TEMP.glob("*.py"))
    paths.extend(ANTLR_TEMP.glob("*.tokens"))
    paths.extend(ANTLR_TEMP.glob("*.interp"))
    return sorted(path for path in paths if path.is_file())


def _write_generated_init() -> None:
    """Write a stable package marker for the generated Python modules."""
    init_path = GENERATED / "__init__.py"
    with init_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(
            '"""Generated ANTLR4 Python modules; regenerate with ``make antlr_build``."""\n'
        )


def _format_generated_python(paths: Sequence[Path]) -> None:
    """Ruff-format generated Python modules using the active interpreter."""
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--no-force-exclude",
            *(str(path) for path in paths),
        ],
        cwd=str(ROOT),
    )


def build() -> None:
    """Generate Python lexer/parser artifacts from the copied G4 files.

    :return: ``None`` after generated artifacts are copied and formatted.
    :rtype: None
    :raises SystemExit: If a required grammar input or generated output is
        unavailable.

    Example::

        $ python -m tools.antlr_pipeline build
    """
    if not GENERATED.is_dir():
        raise SystemExit("generated grammar directory is missing: {}".format(GENERATED))
    grammar_files = (
        GENERATED / "SysMLv2Lexer.g4",
        GENERATED / "SysMLv2Parser.g4",
    )
    missing = [str(path) for path in grammar_files if not path.is_file()]
    if missing:
        raise SystemExit("copied grammar input is missing: " + ", ".join(missing))

    _download_antlr_jar()
    _remove_temp_outputs()
    subprocess.check_call(
        [
            "java",
            "-jar",
            _command_path(ANTLR_JAR),
            "-Dlanguage=Python3",
            "-Xexact-output-dir",
            "-o",
            _command_path(ANTLR_TEMP),
            *(_command_path(path) for path in grammar_files),
        ],
        cwd=str(ROOT),
    )
    outputs = tuple(_generated_outputs())
    if not outputs:
        raise SystemExit("ANTLR generated no Python/token artifacts")
    _remove_generated_outputs()
    GENERATED.mkdir(parents=True, exist_ok=True)
    copied = []
    for source in outputs:
        destination = GENERATED / source.name
        shutil.copyfile(str(source), str(destination))
        _normalize_lf(destination)
        copied.append(destination)
    _write_generated_init()
    python_outputs = tuple(path for path in copied if path.suffix == ".py")
    _format_generated_python(python_outputs + (GENERATED / "__init__.py",))
    for path in python_outputs + (GENERATED / "__init__.py",):
        _normalize_lf(path)


def update() -> None:
    """Copy the pinned grammar, apply provenance, and rebuild artifacts.

    :return: ``None`` after the complete update pipeline succeeds.
    :rtype: None

    Example::

        $ python -m tools.antlr_pipeline update
    """
    _copy_upstream_grammar()
    _run_overlay()
    build()


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Run one portable ANTLR pipeline operation.

    :param arguments: Optional command-line arguments, defaults to ``None``.
    :type arguments: sequence[str], optional
    :return: Zero after the requested operation succeeds.
    :rtype: int

    Example::

        $ python -m tools.antlr_pipeline --help
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("build", "update"))
    options = parser.parse_args(arguments)
    {"build": build, "update": update}[options.operation]()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
