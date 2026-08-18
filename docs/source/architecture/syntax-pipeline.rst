Syntax Pipeline
===============

The pinned grammar submodule is copied into ``pysysmlv2/syntax/generated`` by ``make antlr_update``. The Makefile downloads the pinned ANTLR 4.13.2 tool, generates and Ruff-formats only the Python lexer/parser artifacts. ``pysysmlv2.syntax.parser`` owns diagnostics and the stable parser API, while ``ast_builder`` invokes ``antlr4.ParseTreeWalker`` with the handwritten ``SysMLAstListener``.

The generated directory is reproducible and must not be edited by hand. ``pysysmlv2.syntax.ast`` and ``pysysmlv2.syntax.listener`` are handwritten source: public nodes are selected from the OMG concrete/abstract syntax boundary, fields are explicit snake_case values, and each node owns its exporter. Runtime AST construction has no generic rule reflection or source-text scanner.
