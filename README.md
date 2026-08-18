# pysysmlv2

`pysysmlv2` is an open-source, pure-Python foundation for parsing and analyzing SysML v2 textual models. It provides a pinned ANTLR4 syntax frontend, a source-aware AST with model-level round-trip export, structured diagnostics, and the initial workspace boundary for future semantic linking and symbol resolution.

The project deliberately separates syntax AST responsibilities from workspace and semantic identity. AST nodes retain `source_path` and `span`, preserve SysML documentation and model-owned comments, and export canonical parseable SysML through `str(node)`. Trivia-preserving formatting belongs to the formatter layer. State-machine discovery and model checking are downstream applications, not part of this foundation package.

## Status

This is the initial `0.1.0` foundation release. The ANTLR parser, diagnostics, source AST, canonical AST export, Click CLI, generated API documentation, and cross-platform test/build scaffolding are in place. Full SysML/KerML semantic linking and symbol resolution remain staged work and are tracked in the project issue plan.

## Install

```bash
python -m pip install pysysmlv2
```

The published wheel contains generated Python parser code and does not require Java. Java and the pinned ANTLR tool are needed only when maintainers regenerate parser artifacts from `upstream/sysml-v2-grammar`.

## Quick start

```python
from pysysmlv2 import parse

result = parse("package Demo { part def Vehicle; }", source_path="demo.sysml")
if result.ok:
    print(str(result.ast))
else:
    for diagnostic in result.diagnostics:
        print(diagnostic.message)
```

The command line is available through Click:

```bash
pysysmlv2 --version
pysysmlv2 parse demo.sysml --json
pysysmlv2 validate demo.sysml
pysysmlv2 format demo.sysml
```

## Development

```bash
git submodule update --init --recursive
python -m pip install -e ".[dev,test,docs,tooling]"
make antlr_update
make antlr_check
make rst_auto
make unittest
make doctest
make test
make docs_check
make package
make package_check
```

The generated directory `pysysmlv2/syntax/generated/` is never edited by hand. Change the pinned submodule or an outer generator/patch tool and rerun `make antlr_update`; generation formats the committed Python artifacts with Ruff, while normal Ruff and coverage checks exclude this generated tree. `make unittest RANGE_DIR=syntax` runs the syntax test subtree and emits `coverage.xml` plus terminal `term-missing` coverage by default; `make unittest RANGE_DIR=workspace` runs the corresponding source subtree.

## Documentation

The documentation site is built with a clean Sphinx configuration and has English and Chinese entry points:

```bash
make docs_en
make docs_zh
make docs
```

`make rst_auto` generates the API RST pages from the public Python modules. Generated API pages are checked for drift in CI.

## Grammar provenance

The checked-in grammar is generated from [daltskin/sysml-v2-grammar](https://github.com/daltskin/sysml-v2-grammar), pinned as a git submodule. The generated G4 files and ANTLR runtime artifacts are refreshed by `make antlr_update`.

## License

The project code is released under the MIT License. The derived grammar remains subject to the upstream grammar and SysML specification notices documented in `NOTICE` and the submodule.
