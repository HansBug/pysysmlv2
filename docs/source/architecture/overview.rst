Architecture Overview
=====================

The package is intentionally divided into syntax, AST, workspace, semantic, formatter, and CLI layers. Generated ANTLR files live in a generated-only directory; handwritten adapters and AST builders live outside it.

The initial package is a foundation rather than a model checker. Downstream state-machine extraction should consume the public workspace and semantic APIs without importing generated parser classes directly.
