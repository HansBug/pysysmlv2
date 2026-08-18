"""Top-level Click command group for ``pysysmlv2``.

The module owns only command dispatch and text-file I/O. Parsing, diagnostics,
AST export, and formatting remain in their package layers so library callers
and CLI callers observe the same behavior.

.. list-table:: Command module roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`cli`
     - Root Click group and version option.
   * - :func:`parse_command`
     - Parse and report diagnostics.
   * - :func:`inspect_command`
     - Print canonical AST export.
   * - :func:`validate_command`
     - Return syntax validation status.
   * - :func:`format_command`
     - Export canonical source to stdout or a file.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from .. import __version__
from ..formatter import format_ast
from ..syntax.parser import parse


@click.group()
@click.version_option(__version__, prog_name="pysysmlv2")
def cli() -> None:
    """Inspect and transform SysML v2 source documents.

    :return: ``None``; Click dispatches the selected subcommand.
    :rtype: None

    Example::

        $ pysysmlv2 --help
    """


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


@cli.command("parse")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--json", "as_json", is_flag=True, help="Emit diagnostics and AST text as JSON.")
def parse_command(input_path: str, as_json: bool) -> None:
    """Parse one SysML document and report structured diagnostics.

    :param input_path: Path to the source document.
    :type input_path: str
    :param as_json: Whether to emit the result as JSON.
    :type as_json: bool
    :return: ``None`` after writing the result to standard output.
    :rtype: None
    :raises click.exceptions.Exit: If syntax diagnostics contain an error.

    Example::

        $ pysysmlv2 parse demo.sysml --json
    """
    result = parse(_read(input_path), input_path)
    payload = {
        "ok": result.ok,
        "source_path": input_path,
        "diagnostics": [item.__dict__ for item in result.diagnostics],
        "ast": str(result.ast),
    }
    if as_json:
        click.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        click.echo("ok" if result.ok else "invalid")
        for item in result.diagnostics:
            click.echo("{}:{}:{}: {}".format(input_path, item.line, item.column, item.message))
    if not result.ok:
        raise click.exceptions.Exit(1)


@cli.command("inspect")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
def inspect_command(input_path: str) -> None:
    """Print the canonical AST export for one SysML document.

    :param input_path: Path to the source document.
    :type input_path: str
    :return: ``None`` after writing canonical source.
    :rtype: None
    :raises click.exceptions.Exit: If syntax diagnostics contain an error.

    Example::

        $ pysysmlv2 inspect demo.sysml
    """
    result = parse(_read(input_path), input_path)
    if not result.ok:
        for item in result.diagnostics:
            click.echo(
                "{}:{}:{}: {}".format(input_path, item.line, item.column, item.message), err=True
            )
        raise click.exceptions.Exit(1)
    click.echo(str(result.ast))


@cli.command("validate")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
def validate_command(input_path: str) -> None:
    """Validate syntax and return a process status suitable for CI.

    :param input_path: Path to the source document.
    :type input_path: str
    :return: ``None`` when validation succeeds.
    :rtype: None
    :raises click.exceptions.Exit: If syntax diagnostics contain an error.

    Example::

        $ pysysmlv2 validate demo.sysml
    """
    result = parse(_read(input_path), input_path)
    for item in result.diagnostics:
        click.echo("{}:{}:{}: {}".format(input_path, item.line, item.column, item.message))
    if not result.ok:
        raise click.exceptions.Exit(1)


@cli.command("format")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-o", "output_path", type=click.Path(dir_okay=False), help="Write formatted SysML to this path."
)
def format_command(input_path: str, output_path: str) -> None:
    """Export the model-level canonical form of a SysML document.

    :param input_path: Path to the source document.
    :type input_path: str
    :param output_path: Optional destination path, defaults to standard output.
    :type output_path: str, optional
    :return: ``None`` after writing canonical source.
    :rtype: None
    :raises click.ClickException: If syntax diagnostics prevent formatting.

    Example::

        $ pysysmlv2 format demo.sysml
    """
    result = parse(_read(input_path), input_path)
    if not result.ok:
        raise click.ClickException("cannot format a document with syntax errors")
    rendered = format_ast(result.ast) + "\n"
    if output_path:
        Path(output_path).write_text(rendered, encoding="utf-8")
    else:
        click.echo(rendered, nl=False)


def main() -> None:
    """Invoke the Click command group.

    :return: ``None`` after Click dispatches the command.
    :rtype: None

    Example::

        $ python -m pysysmlv2 --help
    """
    cli()
