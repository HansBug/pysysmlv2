"""Static package metadata consumed by ``setup.py`` and the CLI.

This module is the metadata roadmap's source of truth. Packaging reads these
constants instead of duplicating values in several build files, while runtime
code imports only the public version value through :mod:`pysysmlv2.config`.

.. list-table:: Metadata roadmap
   :header-rows: 1

   * - Constant
     - Responsibility
   * - ``__VERSION__``
     - Distribution and runtime version.
   * - ``__PACKAGE_NAME__``
     - PyPI project name.
   * - ``__DESCRIPTION__``
     - Package summary used by packaging metadata.
   * - ``__AUTHOR__`` / ``__AUTHOR_EMAIL__``
     - Maintainer identity used by packaging metadata.
"""

__VERSION__ = "0.1.0"
__PACKAGE_NAME__ = "pysysmlv2"
__DESCRIPTION__ = "Pure-Python SysML v2 syntax, AST, workspace, and semantic foundation"
__AUTHOR__ = "HansBug"
__AUTHOR_EMAIL__ = "hansbug@buaa.edu.cn"
