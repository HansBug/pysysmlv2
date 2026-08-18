"""Build, documentation, and repository verification tools.

The modules in this package are maintainer-facing command-line tools rather
than runtime APIs. They keep generated ANTLR artifacts, API RST pages, package
metadata, and source-mirrored test selection reproducible.

.. list-table:: Tool roadmap
   :header-rows: 1

   * - Module
     - Responsibility
   * - :mod:`tools.antlr_update`
     - Copy pinned upstream grammars and invoke generation.
   * - :mod:`tools.antlr_build`
     - Run the pinned ANTLR tool and write the manifest.
   * - :mod:`tools.check_generated`
     - Verify generated artifacts are reproducible and tracked.
   * - :mod:`tools.auto_rst`
     - Generate API RST pages from package modules.
   * - :mod:`tools.test_scope`
     - Map source paths to mirrored unit-test paths.
"""
