Syntax Pipeline
===============

The pinned grammar submodule is copied into ``pysysmlv2/syntax/generated`` by ``make antlr_update``. The Makefile then applies a narrow, version-guarded SysML v2 overlay for the state-machine forms shown in OMG SysML 2.0 Language Clause 7.18.3 and Clause 7.17.10: both trigger/guard orders for complete ``TransitionUsage`` forms, closed transition effects terminated by ``;``, and the ``action ... terminate;`` shorthand. Target-transition shorthand remains the upstream trigger-before-guard or guard-only grammar; it is not extended with a guard-first target alternative. KerML-only root, package, expression, invariant, and contextual-keyword extensions are deliberately not included. The overlay is source-controlled in ``tools.grammar_overlay`` rather than hand-editing copied G4 files; ``grammar-provenance.json`` records the actual submodule revision, git describe value, input hash, overlay identifier, and effective G4 hash.

The listener's private lossless fallback is separately audited in
``docs/research/raw_element_compatibility_ledger.json``. It is limited to
deferred non-core productions and parser-recovery fragments; valid state,
expression, action, transition, import, alias, filter, connection, and
interface paths must produce typed source-AST nodes.

The generated directory is reproducible and must not be edited by hand. ``pysysmlv2.syntax.ast`` and ``pysysmlv2.syntax.listener`` are handwritten source: public nodes are selected from the OMG concrete/abstract syntax boundary, fields are explicit snake_case values, and each node owns its exporter. Runtime AST construction has no generic rule reflection or source-text scanner.
