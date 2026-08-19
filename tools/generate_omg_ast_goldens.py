"""Generate the checked-in full-field AST goldens for reviewed OMG examples.

This command is intentionally explicit about its input directory and output
schema.  It is run when a fixture or AST contract changes; normal tests only
read the committed JSON and never regenerate their expected values.

Example::

    $ python -m tools.generate_omg_ast_goldens
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Sequence

from pysysmlv2 import parse, parse_as_ast_node
from pysysmlv2.syntax import Model, PackageMember
from test.testings.ast_snapshot import ast_snapshot

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "test" / "testfile" / "omg_sysml2_language" / "section7"
OUTPUT = FIXTURES / "ast_goldens.json"


def generate(output: Optional[Path] = None) -> int:
    """Parse every reviewed fixture and write complete span-free snapshots.

    :param output: Optional golden output path, defaults to ``ast_goldens``
        beside the fixture directory.
    :type output: pathlib.Path, optional
    :return: Number of golden entries written.
    :rtype: int
    :raises ValueError: If a fixture does not parse successfully.
    """
    entries: Dict[str, object] = {}
    for path in sorted(FIXTURES.glob("*.sysml")):
        source = path.read_text(encoding="utf-8")
        if path.name == "section_7_18_table17_transition_explicit.sysml":
            lines = [line.strip() for line in source.splitlines() if line.strip()]
            nodes = [parse_as_ast_node(line, grammar_node="stateUsage") for line in lines[:2]]
            nodes.append(parse_as_ast_node(lines[2], grammar_node="transitionUsage"))
            ast = Model(
                members=[
                    PackageMember(element=node) if index < 2 else node
                    for index, node in enumerate(nodes)
                ]
            )
        else:
            result = parse(source, str(path))
            if not result.ok:
                detail = "; ".join(item.message for item in result.diagnostics)
                raise ValueError("{}: {}".format(path.name, detail))
            ast = result.ast
        entries[path.name] = ast_snapshot(ast)
    target = output or OUTPUT
    target.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "span_excluded": True,
                "source": "OMG SysML 2.0 Language PDF, section 7.18",
                "span_policy": "ASTNode.span excluded",
                "fixtures": entries,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return len(entries)


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Generate the default golden file.

    :param arguments: Reserved command-line argument vector, defaults to
        ``None``.
    :type arguments: sequence[str], optional
    :return: Process exit status.
    :rtype: int
    """
    del arguments
    print("generated {} OMG AST goldens".format(generate()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
