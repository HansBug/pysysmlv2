# pysysmlv2 Development Contract

`AGENTS.md` is a real symbolic link to this file; edit `CLAUDE.md` only.

`pysysmlv2` is an open-source, pure-Python SysML v2 foundation library. The package owns the parser boundary, syntax AST, model-level round-trip export, workspace linking, symbol resolution, diagnostics, and Click command line. State-machine discovery and model checking belong to a downstream project.

## Repository Boundaries

- `pysysmlv2/syntax/generated/` is generated-only. Never edit it by hand; update the pinned grammar submodule and run `make antlr_update`.
- `upstream/sysml-v2-grammar` is a pinned git submodule and the source of the copied G4 files.
- `pysysmlv2/syntax/generated/` is excluded from Ruff and coverage metrics. The `make antlr_build` recipe runs Ruff formatting explicitly after generation so the committed parser artifacts remain readable without becoming hand-maintained source.
- `pysysmlv2/syntax/ast.py` and `pysysmlv2/syntax/listener.py` are handwritten service-owned code. Do not regenerate or overwrite either from the ANTLR grammar.
- The public source AST is not the OMG abstract semantic model. It retains concrete-syntax choices and source provenance; the future semantic layer maps those nodes to normative SysML v2 XMI/JSON metaclasses, resolved references, derived properties, and validation rules. KerML documents and KerML-only syntax are explicitly outside this repository's parser contract.
- `ASTNode` is a minimal dataclass containing only `span`. `SourceSpan` owns the optional `source_path`; AST nodes must not duplicate it. `ASTNode` must not acquire `children`, generic traversal, generic rendering, token bags, reflection helpers, or semantic identity.
- Every public concrete AST node has explicitly declared, readable, snake_case fields and implements its own `to_sysml()`/`__str__()` by composing those fields. Use `hbutils.string.underscore` when a grammar/context name must become a Python field or trace name.
- AST typing is layered and intentional: `ASTNode` is provenance only; `SourceElement` is exportable syntax; `Expression` is the base for every structured expression node; `Statement` is executable action-body content; `ActionNode` is the concrete action-node family; and `ActionUsageNode` is the action-usage/effect family. Concrete fields must use the narrowest meaningful layer or an explicit union of grammar alternatives. Never declare a semantic field as bare `ASTNode` and never make callers guess what an arbitrary node contains.
- Keep grammar-required children as required dataclass constructor arguments. Use `Optional[...]` and defaults only for grammar alternatives that are actually optional. A node may omit `span` when constructed directly, but that convenience must never make a required grammar child optional.
- Expressions must be decomposed to parser-production granularity: literals, references, recursive operators, calls, indexing, member access, constructors, metadata, casts, arrows, argument lists, and body expressions each retain typed fields. A normal expression path must never use `source_text` or `RawElement` as a silent fallback.
- Action and state syntax follows the same rule. Use explicit `ActionNode`, `ControlNode`, action statement, transition, guard, effect, and body-member classes. Keep grammar-specific declaration variants separate when their required fields differ (for example full `sendNode` versus `sendNodeDeclaration`, and transition perform effects versus `performActionUsage`).
- A one-child parser wrapper may be passed through only when it contributes no token, prefix, choice, or provenance ownership. If a wrapper owns visibility, succession, declaration, or another source token, retain a named node for that relationship. Each retained concrete node owns canonical pretty SysML output; `__str__()` delegates to `to_sysml()`.
- `SysMLAstListener` is the only AST assembler and is driven by `antlr4.ParseTreeWalker`. Write an explicit callback for every public-node mapping; do not use `exitEveryRule`, `getattr`, `type()`, dataclass reflection, dynamic field maps, or source-text scanning to assemble public AST nodes.
- Model-owned `Comment`, `Documentation`, and `TextualRepresentation` are model syntax, not ordinary trivia. Preserve them in explicit nodes as their mappings are introduced. Ordinary whitespace and notes belong to the formatter/trivia layer.
- The exported lossless `RawElement` syntax bridge may preserve a valid unimplemented grammar production during staged coverage, but it is never a semantic-model API. Downstream semantic code must explicitly reject or account for it, and each deferred production must be replaced by an explicit handwritten node before semantic code depends on it.
- Every lossless bridge is recorded in `docs/research/raw_element_compatibility_ledger.json` with its grammar production, listener callback, reason, regression test, and typed-node follow-up. The ledger is an audit boundary, not permission to use `RawElement` in ordinary expression, action, state, transition, import, alias, filter, connection, or interface paths.
- `str(ast_node)` must emit parseable SysML v2 text. Trivia-preserving source formatting is a formatter concern, not an AST concern.
- `test/` mirrors source module paths for unit tests: `foo/bar.py` maps to `test/foo/test_bar.py`; `make unittest RANGE_DIR=...` directly invokes pytest against the mirrored test subtree and emits `coverage.xml` plus terminal `term-missing` coverage by default.
- `docs/source/api_doc/` is generated by `make rst_auto`; do not hand-edit generated API pages.

## Supported Environments

The package targets CPython 3.7 through 3.14 and is intended to run on Linux, Windows, and macOS. Runtime installation includes generated ANTLR Python code; Java is required only to regenerate parser artifacts during development. CI covers the complete 3-by-8 operating-system/Python-line matrix; exact patch versions may vary by runner where the official setup-python manifest publishes different legacy artifacts.

## Required Checks

```text
make format_check
make lint
make unittest
make doctest
make test
make rst_auto_check
make docs_check
make antlr_check
make package_check
```

## Python Docstring Style Guide

All service-owned Python documentation follows the same reStructuredText docstring contract as `pyfcstm`. Use reST exclusively, following PEP 257 and Sphinx conventions. This applies to public modules, classes, functions, and methods under `pysysmlv2/` and to public repository tools under `tools/`; generated ANTLR code is exempt.

1. Explain the responsibility and the reason the API exists in the library boundary, not merely its implementation steps.
2. Document every argument with `:param name:` and `:type name:`, including optional/default behavior. Document returned values with `:return:` and `:rtype:`, including `None` returns.
3. Document every intentional public exception with `:raises:`. Do not claim exceptions that ordinary callers cannot receive.
4. Use reST cross-references such as `:class:`, `:func:`, `:mod:`, `:meth:`, `:data:`, and `:exc:` where a reference improves navigation.
5. Give public classes and callable APIs a practical `Example::`; examples must remain runnable under `make doctest`. CLI examples use a shell `$` prompt rather than doctest prompts.
6. Dataclass documentation describes constructor fields with `:param:`/`:type:` and persistent attributes with `:ivar:`/`:vartype:` where that clarifies the object contract.
7. Inline literals always use double backticks. Keep reST markup boundaries valid; when Chinese text or full-width punctuation touches markup, use a separating `\ ` escape where necessary.
8. Module-level and package `__init__.py` docstrings are detailed roadmaps: identify the module's ownership boundary, list important symbols or submodules, explain how they fit the package, and state what is intentionally deferred.

The minimum callable template is:

```python
def function_name(value: str, optional: bool = False) -> str:
    """Summarize the public behavior and its role in the library.

    :param value: Input value to process.
    :type value: str
    :param optional: Whether to enable optional behavior, defaults to ``False``.
    :type optional: bool, optional
    :return: The processed value.
    :rtype: str
    :raises ValueError: If ``value`` violates the documented contract.

    Example::

        >>> function_name("demo")
        'demo'
    """
```

The minimum dataclass template is:

```python
@dataclass
class Result:
    """Represent a stable public result.

    :param text: Canonical textual value.
    :type text: str
    :ivar text: Canonical textual value.
    :vartype text: str

    Example::

        >>> Result("demo").text
        'demo'
    """
```

Do not use Google or NumPy docstring sections, single-backtick inline code, vague descriptions, or undocumented public parameters. Run `make doctest` and the relevant Sphinx build after changing a public docstring.

## Editing and Release Rules

Use `apply_patch` for focused edits. Keep generated files reproducible and review the generated diff together with the source grammar metadata. Public APIs require English reStructuredText docstrings with examples. Keep the English README operational; project planning and design issues are written in Chinese. Do not edit `AGENTS.md` separately from `CLAUDE.md`.
