"""Expose the ``python -m pysysmlv2`` command-line entry point.

The implementation lives in :mod:`pysysmlv2.entry.dispatch`; this thin module
keeps module execution and the installed ``pysysmlv2`` console script on the
same Click command group.
"""

from .entry.dispatch import main

if __name__ == "__main__":  # pragma: no cover
    main()
