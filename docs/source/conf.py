"""Clean Sphinx configuration for the bilingual pysysmlv2 documentation."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pysysmlv2.config.meta import __VERSION__

project = "pysysmlv2"
copyright = "2026, HansBug"
author = "HansBug"
release = __VERSION__
version = __VERSION__
language = os.environ.get("READTHEDOCS_LANGUAGE", "en")
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
templates_path = ["_templates"]
master_doc = os.environ.get("PY_SYSMLV2_MASTER_DOC", "index_en")
exclude_patterns = ["_build", "build", "_static", "_templates"]
if master_doc == "index_en":
    exclude_patterns.extend(["index_zh.rst", "api_doc_zh.rst"])
else:
    exclude_patterns.extend(["index_en.rst", "api_doc_en.rst"])
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"
autodoc_typehints = "none"
nitpicky = False
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
