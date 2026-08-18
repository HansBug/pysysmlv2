AST Round-Trip
==============

Every concrete AST node implements ``to_sysml`` and inherits ``__str__`` as its canonical exporter. Model-owned documentation and comments are AST content and therefore survive export. Whitespace and non-model trivia are intentionally outside the AST contract and are handled by the formatter layer.

Round-trip tests parse source, export ``str(ast)``, parse the exported source again, and compare structural content while ignoring source spans.
