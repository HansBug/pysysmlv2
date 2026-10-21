"""Install a built wheel in an isolated virtual environment and import it.

The package-smoke command is intentionally implemented in Python so the same
wheel validation works on Windows, macOS, and Linux without shell-specific
virtual-environment paths or glob expansion.

.. list-table:: Package-smoke roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`find_wheel`
     - Select the single wheel produced for a smoke run.
   * - :func:`smoke`
     - Install the wheel without dependencies and import the public package.
   * - :func:`main`
     - Provide the CI-facing command-line entry point.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import Optional, Sequence


def find_wheel(directory: Path) -> Path:
    """Return the only wheel in ``directory``.

    :param directory: Distribution directory to inspect.
    :type directory: pathlib.Path
    :return: The wheel selected for the smoke test.
    :rtype: pathlib.Path
    :raises SystemExit: If the directory does not contain exactly one wheel.

    Example::

        >>> find_wheel(Path("dist")).name  # doctest: +SKIP
        'pysysmlv2-0.1.0-py3-none-any.whl'
    """
    wheels = sorted(path for path in directory.glob("*.whl") if path.is_file())
    if len(wheels) != 1:
        raise SystemExit(
            "expected exactly one wheel in {} (found {})".format(directory, len(wheels))
        )
    return wheels[0]


def _venv_python(directory: Path) -> Path:
    """Return the platform-specific Python executable in a virtualenv."""
    relative = Path("Scripts") / "python.exe" if sys.platform == "win32" else Path("bin") / "python"
    return directory / relative


def smoke(directory: Path) -> None:
    """Install and import the wheel in a temporary isolated environment.

    :param directory: Distribution directory containing one wheel.
    :type directory: pathlib.Path
    :return: ``None`` after installation and import succeed.
    :rtype: None
    :raises SystemExit: If wheel selection or a subprocess fails.

    Example::

        $ python -m tools.package_smoke --dist-dir dist
    """
    wheel = find_wheel(directory)
    with tempfile.TemporaryDirectory(prefix="pysysmlv2-package-smoke-") as temporary:
        environment = Path(temporary) / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(str(environment))
        interpreter = _venv_python(environment)
        subprocess.check_call([str(interpreter), "-m", "pip", "install", str(wheel)])
        subprocess.check_call(
            [
                str(interpreter),
                "-c",
                "import pysysmlv2; print(pysysmlv2.__version__)",
            ]
        )


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Run a platform-independent wheel smoke test.

    :param arguments: Optional command-line arguments, defaults to ``None``.
    :type arguments: sequence[str], optional
    :return: Zero after the smoke test succeeds.
    :rtype: int

    Example::

        $ python -m tools.package_smoke --dist-dir dist
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    options = parser.parse_args(arguments)
    smoke(options.dist_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
