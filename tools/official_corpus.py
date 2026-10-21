"""Report parser and AST conformance for local official-model fixtures.

The tool deliberately reads only the repository-owned fixture corpus under
``test/testfile/omg_release_2026_05``.  It classifies each input as a parser
diagnostic, an AST construction/export failure, a reparse failure, a full AST
equality failure, a canonical round-trip mismatch, or a successful fixed point.
This makes grammar and listener gaps reproducible without making tests depend on
a git submodule or network checkout.

Example::

    $ python -m tools.official_corpus --help
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from pysysmlv2 import parse
from pysysmlv2.syntax import RawElement


def _corpus_root() -> Path:
    """Return the checked-in official corpus root.

    :return: Fixture root containing copied OMG models.
    :rtype: pathlib.Path
    """
    return Path(__file__).parents[1] / "test" / "testfile" / "omg_release_2026_05"


def _model_paths(root: Path) -> Tuple[Path, ...]:
    """Return all supported fixture paths in deterministic order.

    :param root: Local official-model fixture root.
    :type root: pathlib.Path
    :return: SysML v2 model files ordered by relative path.
    :rtype: tuple[pathlib.Path, ...]
    """
    return tuple(sorted(root.rglob("*.sysml")))


def _failure(category: str, path: Path, root: Path, detail: str) -> Dict[str, object]:
    """Build one JSON-serializable report row for a failed corpus entry.

    :param category: Stable result category.
    :type category: str
    :param path: Local model path.
    :type path: pathlib.Path
    :param root: Corpus root used to make paths portable.
    :type root: pathlib.Path
    :param detail: Human-readable failure evidence.
    :type detail: str
    :return: One normalized report row.
    :rtype: dict[str, str]
    """
    return {
        "category": category,
        "path": path.relative_to(root).as_posix(),
        "detail": detail,
    }


def _raw_element_texts(value: object) -> Tuple[str, ...]:
    """Return lossless compatibility fragments nested in one AST.

    :param value: AST value to inspect recursively.
    :type value: object
    :return: Raw-element source fragments in traversal order.
    :rtype: tuple[str, ...]
    """
    if isinstance(value, RawElement):
        return (value.source_text,)
    if is_dataclass(value):
        result = []
        for item in fields(value):
            if item.name != "span":
                result.extend(_raw_element_texts(getattr(value, item.name)))
        return tuple(result)
    if isinstance(value, (list, tuple)):
        result = []
        for item in value:
            result.extend(_raw_element_texts(item))
        return tuple(result)
    return ()


def _line_offsets(source_text: str) -> Tuple[int, ...]:
    """Return zero-based offsets for each one-based source line."""
    offsets: List[int] = []
    offset = 0
    for line in source_text.splitlines(keepends=True):
        offsets.append(offset)
        offset += len(line)
    return tuple(offsets)


def _context_ranges(parse_tree: object) -> Dict[Tuple[int, int], Tuple[str, ...]]:
    """Index parser-context source ranges by their concrete grammar rule."""
    ranges: Dict[Tuple[int, int], List[str]] = {}

    def visit(context: object) -> None:
        start_token = getattr(context, "start", None)
        stop_token = getattr(context, "stop", None)
        start = getattr(start_token, "start", None)
        stop = getattr(stop_token, "stop", None)
        if isinstance(start, int) and isinstance(stop, int) and start >= 0 and stop >= start:
            name = type(context).__name__
            if name.endswith("Context"):
                name = name[: -len("Context")]
            if name:
                name = name[0].lower() + name[1:]
            ranges.setdefault((start, stop + 1), []).append(name)
        for child in getattr(context, "getChildren", lambda: ())():
            if hasattr(child, "getChildren"):
                visit(child)

    visit(parse_tree)
    return {key: tuple(value) for key, value in ranges.items()}


def _raw_records(value: object, source_text: str, parse_tree: object) -> List[Dict[str, object]]:
    """Describe nested RawElement fragments with their exact grammar production."""
    offsets = _line_offsets(source_text)
    ranges = _context_ranges(parse_tree)
    records: List[Dict[str, object]] = []
    for raw in _walk_raw_elements(value):
        span = raw.span
        if span is None or span.line < 1 or span.end_line < 1:
            production = None
        else:
            try:
                start = offsets[span.line - 1] + span.column - 1
                end = offsets[span.end_line - 1] + span.end_column - 1
            except IndexError:
                production = None
            else:
                names = ranges.get((start, end), ())
                production = names[-1] if names else None
        records.append(
            {
                "production": production,
                "source_text": raw.source_text,
                "line": span.line if span else None,
            }
        )
    return records


def _walk_raw_elements(value: object):
    """Yield nested RawElement nodes without relying on AST reflection helpers."""
    if isinstance(value, RawElement):
        yield value
        return
    if is_dataclass(value):
        for item in fields(value):
            if item.name != "span":
                yield from _walk_raw_elements(getattr(value, item.name))
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_raw_elements(item)


def inspect_model(path_text: str, root_text: str) -> Dict[str, object]:
    """Classify parser, AST, and canonical round-trip behavior for one file.

    :param path_text: Absolute fixture path supplied to a worker process.
    :type path_text: str
    :param root_text: Absolute corpus root for portable reporting.
    :type root_text: str
    :return: Normalized conformance result row.
    :rtype: dict[str, str]
    """
    path = Path(path_text)
    root = Path(root_text)
    try:
        first = parse(path.read_text(encoding="utf-8"), str(path))
    except Exception as error:
        return _failure("ast_error", path, root, "{}: {}".format(type(error).__name__, error))
    if not first.ok:
        message = first.diagnostics[0].message if first.diagnostics else "unknown parser diagnostic"
        return _failure("parser_diagnostic", path, root, message)
    try:
        exported = str(first.ast)
    except Exception as error:
        return _failure("export_error", path, root, "{}: {}".format(type(error).__name__, error))
    try:
        second = parse(exported, "roundtrip.sysml")
    except Exception as error:
        return _failure(
            "roundtrip_ast_error", path, root, "{}: {}".format(type(error).__name__, error)
        )
    if not second.ok:
        message = (
            second.diagnostics[0].message if second.diagnostics else "unknown parser diagnostic"
        )
        return _failure("roundtrip_diagnostic", path, root, message)
    if first.ast != second.ast:
        return _failure(
            "ast_mismatch",
            path,
            root,
            "full AST dataclass equality failed after canonical round-trip",
        )
    if str(second.ast) != exported:
        return _failure("roundtrip_mismatch", path, root, "canonical export is not idempotent")
    raw_records = _raw_records(first.ast, path.read_text(encoding="utf-8"), first.parse_tree)
    if raw_records:
        sample = " | ".join(
            str(record["source_text"]).replace("\n", " ").strip() for record in raw_records[:2]
        )
        productions = ", ".join(str(record["production"]) for record in raw_records)
        result = _failure(
            "raw_element",
            path,
            root,
            "{} deferred/recovery RawElement fragment(s) [{}]: {}".format(
                len(raw_records), productions, sample
            ),
        )
        result["raw_elements"] = raw_records
        return result
    return _failure("passed", path, root, "")


def build_report(
    root: Path, jobs: int = 1, offset: int = 0, limit: Optional[int] = None
) -> Dict[str, object]:
    """Run conformance classification for every local official fixture.

    :param root: Local fixture corpus root.
    :type root: pathlib.Path
    :param jobs: Worker process count, defaults to ``1``.
    :type jobs: int, optional
    :param offset: Zero-based start offset in stable fixture order, defaults to
        ``0``.
    :type offset: int, optional
    :param limit: Optional maximum number of fixtures to inspect.
    :type limit: int, optional
    :return: Versioned report with rows and category summary.
    :rtype: dict[str, object]
    :raises ValueError: If a worker count, offset, or limit is invalid.
    """
    if jobs < 1:
        raise ValueError("jobs must be at least one")
    if offset < 0:
        raise ValueError("offset must not be negative")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least one when supplied")
    all_paths = _model_paths(root)
    paths = all_paths[offset:] if limit is None else all_paths[offset : offset + limit]
    arguments = [(str(path), str(root)) for path in paths]
    if jobs == 1:
        rows = [inspect_model(*argument) for argument in arguments]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            rows = list(executor.map(_inspect_argument, arguments))
    rows.sort(key=lambda item: item["path"])
    summary: Dict[str, int] = {}
    for row in rows:
        category = row["category"]
        summary[category] = summary.get(category, 0) + 1
    return {
        "schema_version": 1,
        "fixture_root": str(root),
        "corpus_total": len(all_paths),
        "offset": offset,
        "total": len(rows),
        "summary": summary,
        "rows": rows,
    }


def _inspect_argument(argument: Tuple[str, str]) -> Dict[str, object]:
    """Adapt an executor argument pair to :func:`inspect_model`.

    :param argument: File and corpus-root path pair.
    :type argument: tuple[str, str]
    :return: Per-file conformance row.
    :rtype: dict[str, str]
    """
    return inspect_model(*argument)


def _parse_args(arguments: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for the local corpus reporter.

    :param arguments: Optional explicit argument vector, defaults to ``None``.
    :type arguments: sequence[str], optional
    :return: Parsed command-line namespace.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=1, help="worker process count")
    parser.add_argument("--offset", type=int, default=0, help="zero-based fixture start offset")
    parser.add_argument("--limit", type=int, help="maximum fixture count to inspect")
    parser.add_argument("--output", type=Path, help="optional JSON report output path")
    return parser.parse_args(arguments)


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Run the official-corpus report command.

    :param arguments: Optional explicit command-line argument vector.
    :type arguments: sequence[str], optional
    :return: Process exit status.
    :rtype: int
    """
    options = _parse_args(arguments)
    report = build_report(_corpus_root(), options.jobs, options.offset, options.limit)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if options.output:
        options.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["summary"].get("passed", 0) == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
