"""Click command-line entry points.

The public command group is implemented in :mod:`pysysmlv2.entry.dispatch`.
The commands deliberately consume service-owned parser and formatter APIs so
CLI output does not expose generated ANTLR implementation details.

.. list-table:: CLI roadmap
   :header-rows: 1

   * - Command
     - Responsibility
   * - ``parse``
     - Parse one document and print diagnostics or JSON.
   * - ``inspect``
     - Print canonical AST export.
   * - ``validate``
     - Return a CI-friendly syntax validation status.
   * - ``format``
     - Write canonical model text to stdout or a destination file.
"""
