"""Package metadata and build configuration.

This package is intentionally small. :mod:`pysysmlv2.config.meta` is the
single source for the distribution name, version, description, and author
metadata consumed by ``setup.py`` and the Click version option.

.. list-table:: Configuration roadmap
   :header-rows: 1

   * - Export
     - Responsibility
   * - :data:`__VERSION__`
     - Current package version shared by packaging and runtime metadata.
"""

from .meta import __VERSION__

__all__ = ["__VERSION__"]
