Syntax Pipeline
===============

The pinned grammar submodule is copied into ``pysysmlv2/syntax/generated`` by ``make antlr_update``. ANTLR 4.13.2 generates the Python lexer/parser there. ``pysysmlv2.syntax.parser`` owns diagnostics and the stable parser API, while ``ast_builder`` maps parse results into source AST nodes.

The generated directory is reproducible and must not be edited by hand. Local grammar fixes belong in the outer synchronization tools and are recorded by the generated manifest.
