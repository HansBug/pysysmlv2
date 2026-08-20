AST Round-Trip
==============

Every concrete AST node declares its own readable fields and implements ``to_sysml`` and ``__str__`` by composing those fields. ``ASTNode`` only stores ``span``; the optional source path belongs to ``SourceSpan`` rather than being duplicated by every AST node. It does not provide a generic child list or renderer. Model-owned documentation and comments are AST content and therefore survive export. Whitespace and non-model trivia are intentionally outside the AST contract and are handled by the formatter layer.

Round-trip tests parse source, export ``str(ast)``, parse the exported source again, and compare structural content while ignoring source spans.
