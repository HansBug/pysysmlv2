"""Generate English and Chinese top-level API index pages.

This companion tool keeps the bilingual API entry points deterministic while
the detailed module pages remain owned by :mod:`tools.auto_rst`.

.. list-table:: Bilingual index roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`generate`
     - Write English and Chinese API index pages.
   * - :func:`main`
     - Expose generation and drift-check CLI behavior.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "source"


def _render(language: str) -> str:
    if language == "en":
        return "\n".join(
            [
                "API Documentation",
                "=================",
                "",
                "This page is generated from the public pysysmlv2 Python modules.",
                "",
                ".. toctree::",
                "   :maxdepth: 2",
                "",
                "   api_doc/index",
                "",
            ]
        )
    return "\n".join(
        [
            "API 文档",
            "========",
            "",
            "本页由 pysysmlv2 的公开 Python 模块自动生成。",
            "",
            ".. toctree::",
            "   :maxdepth: 2",
            "",
            "   api_doc/index",
            "",
        ]
    )


def generate(output: Path) -> None:
    """Generate bilingual top-level API index pages.

    :param output: Documentation source directory receiving the pages.
    :type output: :class:`pathlib.Path`
    :return: ``None``.
    :rtype: None

    Example::

        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as directory:
        ...     generate(Path(directory))
        ...     (Path(directory) / "api_doc_en.rst").is_file()
        True
    """
    output.mkdir(parents=True, exist_ok=True)
    (output / "api_doc_en.rst").write_text(_render("en"), encoding="utf-8")
    (output / "api_doc_zh.rst").write_text(_render("zh"), encoding="utf-8")


def main() -> None:
    """Run the bilingual API index generator command-line interface.

    :return: ``None``.
    :rtype: None

    Example::

        $ python -m tools.auto_rst_top_index --check
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        generate(OUTPUT)
        return
    with tempfile.TemporaryDirectory() as directory:
        generated = Path(directory)
        generate(generated)
        for name in ("api_doc_en.rst", "api_doc_zh.rst"):
            if not (OUTPUT / name).is_file() or (OUTPUT / name).read_text(encoding="utf-8") != (
                generated / name
            ).read_text(encoding="utf-8"):
                raise SystemExit("generated bilingual API index is out of date; run make rst_auto")


if __name__ == "__main__":  # pragma: no cover
    main()
