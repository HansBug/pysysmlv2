Architecture Overview
=====================

The package is intentionally divided into syntax, AST, workspace, semantic, formatter, and CLI layers. Generated ANTLR files live in a generated-only directory. The public AST and listener are handwritten, explicit source code: they model the selected OMG concrete-syntax concepts and leave semantic identity, linking, and derived relationships to the semantic layer.

The initial package is a foundation rather than a model checker. Downstream state-machine extraction should consume the public workspace and semantic APIs without importing generated parser classes directly.
