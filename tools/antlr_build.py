"""Generate checked-in Python ANTLR artifacts from copied G4 files.

This maintainer tool is the only place that invokes the Java ANTLR tool. The
runtime wheel ships the generated Python modules, while this module records
tool, grammar, and source-submodule provenance in ``manifest.json``. Grammar
version metadata is read from the pinned submodule's ``scripts/config.json``;
this repository deliberately does not maintain a second grammar-version
constant.

.. list-table:: ANTLR build roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`ensure_antlr_jar`
     - Obtain and checksum the pinned ANTLR tool.
   * - :func:`build`
     - Generate Python lexer/parser artifacts and manifest metadata.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "pysysmlv2" / "syntax" / "generated"
ANTLR_DIR = ROOT / ".antlr"
UPSTREAM = ROOT / "upstream" / "sysml-v2-grammar"
UPSTREAM_CONFIG = UPSTREAM / "scripts" / "config.json"
ANTLR_VERSION = "4.13.2"
ANTLR_SHA256 = "eae2dfa119a64327444672aff63e9ec35a20180dc5b8090b7a6ab85125df4d76"
ANTLR_JAR = ANTLR_DIR / ("antlr-" + ANTLR_VERSION + "-complete.jar")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_antlr_jar() -> Path:
    """Download and verify the pinned ANTLR tool when absent.

    :return: Path to the checksum-verified ANTLR complete JAR.
    :rtype: :class:`pathlib.Path`
    :raises RuntimeError: If the downloaded or existing JAR has the wrong hash.
    :raises urllib.error.URLError: If the tool cannot be downloaded.

    Example::

        >>> ANTLR_JAR.name
        'antlr-4.13.2-complete.jar'
    """
    ANTLR_DIR.mkdir(parents=True, exist_ok=True)
    if not ANTLR_JAR.exists():
        url = "https://www.antlr.org/download/antlr-" + ANTLR_VERSION + "-complete.jar"
        urllib.request.urlretrieve(url, str(ANTLR_JAR))
    actual = _sha256(ANTLR_JAR)
    if actual != ANTLR_SHA256:
        raise RuntimeError("ANTLR jar checksum mismatch: " + actual)
    return ANTLR_JAR


def _upstream_metadata() -> Dict[str, str]:
    """Read grammar and OMG release versions from the upstream configuration.

    :return: Upstream ``grammar_version`` and ``release_tag`` values.
    :rtype: dict[str, str]
    :raises FileNotFoundError: If the initialized grammar submodule is incomplete.
    :raises ValueError: If upstream version metadata is missing or malformed.
    """
    try:
        data = json.loads(UPSTREAM_CONFIG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("upstream grammar config is not valid JSON") from error
    except OSError as error:
        raise FileNotFoundError(str(UPSTREAM_CONFIG)) from error
    if not isinstance(data, dict):
        raise ValueError("upstream grammar config must be a JSON object")
    values = {}
    for key in ("grammar_version", "release_tag"):
        value = data.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError("upstream grammar config field is invalid: " + key)
        values[key] = value
    return values


def _git_metadata() -> Dict[str, str]:
    upstream = UPSTREAM
    metadata = _upstream_metadata()
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "unknown"
    try:
        tag = subprocess.check_output(
            ["git", "-C", str(upstream), "describe", "--tags", "--exact-match"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        # Shallow submodule checkouts may omit tag refs; the pinned grammar
        # version remains authoritative and keeps manifest generation reproducible.
        tag = "v" + metadata["grammar_version"]
    return {"source_commit": commit, "source_tag": tag}


def _write_generated_init() -> None:
    (GENERATED / "__init__.py").write_text(
        '"""Generated ANTLR4 Python modules; regenerate with ``make antlr_build``."""\n',
        encoding="utf-8",
    )


def build() -> None:
    """Generate parser modules and write reproducibility metadata.

    :return: ``None`` after the generated package is updated.
    :rtype: None
    :raises FileNotFoundError: If the copied G4 inputs are missing.
    :raises RuntimeError: If the pinned ANTLR tool checksum is invalid.
    :raises subprocess.CalledProcessError: If Java or ANTLR generation fails.

    Example::

        $ make antlr_build
    """
    lexer = GENERATED / "SysMLv2Lexer.g4"
    parser = GENERATED / "SysMLv2Parser.g4"
    if not lexer.is_file() or not parser.is_file():
        raise FileNotFoundError("generated G4 inputs are missing; run make antlr_update")

    jar = ensure_antlr_jar()
    temp = ANTLR_DIR / "generated"
    if temp.exists():
        shutil.rmtree(str(temp))
    temp.mkdir(parents=True)
    subprocess.check_call(
        [
            "java",
            "-jar",
            str(jar),
            "-Dlanguage=Python3",
            "-Xexact-output-dir",
            "-o",
            str(temp),
            str(lexer),
            str(parser),
        ]
    )

    for path in GENERATED.iterdir():
        if path.name == "__init__.py" or path.suffix in {".py", ".tokens", ".interp"}:
            path.unlink()
    for path in temp.iterdir():
        if path.is_file() and path.suffix in {".py", ".tokens", ".interp"}:
            shutil.copy2(str(path), str(GENERATED / path.name))
    _write_generated_init()

    upstream_metadata = _upstream_metadata()
    metadata = {
        "antlr_version": ANTLR_VERSION,
        "antlr_jar_sha256": _sha256(jar),
        "grammar_version": upstream_metadata["grammar_version"],
        "omg_release": upstream_metadata["release_tag"],
        "source_repository": "https://github.com/daltskin/sysml-v2-grammar",
        "source_grammar_sha256": {
            "lexer": _sha256(lexer),
            "parser": _sha256(parser),
        },
    }
    metadata.update(_git_metadata())
    (GENERATED / "manifest.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":  # pragma: no cover
    build()
