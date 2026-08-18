"""Build, documentation, and repository verification tools.

The modules in this package are maintainer-facing command-line tools rather
than runtime APIs. They keep generated ANTLR artifacts, API RST pages, and
package metadata reproducible; the Makefile invokes pytest directly for
source-mirrored unit-test scopes.

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
"""
