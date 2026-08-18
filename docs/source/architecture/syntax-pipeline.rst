Syntax Pipeline
===============

The pinned grammar submodule is copied into ``pysysmlv2/syntax/generated`` by ``make antlr_update``. The Makefile downloads and verifies the pinned ANTLR 4.13.2 tool, generates and Ruff-formats the Python lexer/parser, and writes the provenance manifest there. ``pysysmlv2.syntax.parser`` owns diagnostics and the stable parser API, while ``ast_builder`` maps parse results into source AST nodes.

The generated directory is reproducible and must not be edited by hand. Local grammar fixes belong in the upstream submodule or an explicit outer patch step and are recorded by the generated manifest.
