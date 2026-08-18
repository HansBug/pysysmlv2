"""Generate deterministic Sphinx API pages from Python source modules.

The generator is intentionally a small repository tool, not a runtime package
dependency. ``make rst_auto`` writes the committed API pages; ``--check``
regenerates into a temporary directory and detects drift without modifying the
working tree.

.. list-table:: API RST roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`generate`
     - Write module API pages and the generated toctree.
   * - :func:`main`
     - Expose generation and drift-check CLI behavior.
"""

from __future__ import annotations

import argparse
import ast
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "pysysmlv2"
OUTPUT = ROOT / "docs" / "source" / "api_doc"


def _module_name(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    return ".".join(relative.parts)


def _public_symbols(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names = []
    for node in tree.body:
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ) and not node.name.startswith("_"):
            names.append(node.name)
    return names


def _render(path: Path, destination: Path) -> str:
    module = _module_name(path)
    title = module + " API"
    lines = [
        title,
        "=" * len(title),
        "",
        ".. automodule:: " + module,
        "    :members:",
        "    :undoc-members:",
        "    :show-inheritance:",
        "",
    ]
    return "\n".join(lines)


def _source_files():
    for path in sorted(SOURCE.rglob("*.py")):
        relative = path.relative_to(SOURCE)
        if (
            "generated" in relative.parts
            or path.name.startswith("_")
            and path.name != "__init__.py"
        ):
            continue
        yield path


def generate(output: Path) -> None:
    """Generate deterministic API RST files into a destination directory.

    :param output: Directory receiving generated API pages.
    :type output: :class:`pathlib.Path`
    :return: ``None``.
    :rtype: None

    Example::

        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as directory:
        ...     generate(Path(directory))
        ...     (Path(directory) / "index.rst").is_file()
        True
    """
    output.mkdir(parents=True, exist_ok=True)
    entries = []
    for source in _source_files():
        relative = source.relative_to(SOURCE)
        if source.name == "__init__.py":
            target = output / relative.parent / "index.rst"
            entry = str((relative.parent / "index").as_posix())
        else:
            target = output / relative.with_suffix(".rst")
            entry = str(relative.with_suffix("").as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_render(source, target), encoding="utf-8")
        if target != output / "index.rst":
            entries.append(entry)
    index = output / "index.rst"
    lines = ["pysysmlv2 API", "===============", "", ".. toctree::", "   :maxdepth: 3", ""]
    lines.extend("   " + entry for entry in sorted(set(entries)))
    lines.append("")
    index.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Run the API RST generator command-line interface.

    :return: ``None``.
    :rtype: None

    Example::

        $ python -m tools.auto_rst --check
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        generate(OUTPUT)
        return
    with tempfile.TemporaryDirectory() as directory:
        generated = Path(directory) / "api_doc"
        generate(generated)
        left = sorted(path.relative_to(generated) for path in generated.rglob("*.rst"))
        right = (
            sorted(path.relative_to(OUTPUT) for path in OUTPUT.rglob("*.rst"))
            if OUTPUT.exists()
            else []
        )
        if left != right or any(
            (generated / path).read_text(encoding="utf-8")
            != (OUTPUT / path).read_text(encoding="utf-8")
            for path in left
        ):
            raise SystemExit("generated API RST is out of date; run make rst_auto")


if __name__ == "__main__":  # pragma: no cover
    main()
