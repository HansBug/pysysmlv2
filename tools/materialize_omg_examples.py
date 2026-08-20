"""Materialize reviewed OMG PDF examples as repository-owned test assets.

The source inventory in ``docs/research/omg_sysml2_language_examples.json``
records the official clause and printed page for each example.  This small
one-shot utility copies only the reviewed SysML code into ``test/testfile`` so
tests never read a network checkout or a PDF at runtime.

Example::

    $ python -m tools.materialize_omg_examples
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "research" / "omg_sysml2_language_examples.json"
DESTINATION = ROOT / "test" / "testfile" / "omg_sysml2_language" / "section7"


def materialize(destination: Optional[Path] = None) -> int:
    """Write reviewed PDF examples below a local fixture directory.

    :param destination: Optional output directory, defaults to the checked-in
        ``test/testfile`` location.
    :type destination: pathlib.Path, optional
    :return: Number of materialized examples.
    :rtype: int
    :raises ValueError: If an inventory entry is missing its fixture name or
        source code.
    """
    output = destination or DESTINATION
    inventory: Dict[str, object] = json.loads(INVENTORY.read_text(encoding="utf-8"))
    examples = inventory.get("known_examples")
    if not isinstance(examples, list):
        raise ValueError("OMG inventory has no known_examples list")
    output.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in examples:
        if not isinstance(item, dict):
            raise ValueError("OMG inventory entry is not an object")
        filename = item.get("fixture_name")
        code = item.get("code")
        if not isinstance(filename, str) or not isinstance(code, str):
            raise ValueError("OMG inventory entry lacks fixture_name or code")
        (output / filename).write_text(code.rstrip() + "\n", encoding="utf-8")
        count += 1
    return count


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Materialize the default reviewed example set.

    :param arguments: Reserved command-line argument vector, defaults to
        ``None``.
    :type arguments: sequence[str], optional
    :return: Process exit status.
    :rtype: int
    """
    del arguments
    print("materialized {} OMG PDF examples".format(materialize()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
