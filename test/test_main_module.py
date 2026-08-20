"""Unit tests for the ``python -m pysysmlv2`` bootstrap module."""

import pytest

import pysysmlv2.__main__ as main_module
from pysysmlv2.entry.dispatch import main as dispatch_main

pytestmark = pytest.mark.unit


def test_main_module_reuses_the_public_click_bootstrap():
    """Keep module execution and the installed console script aligned."""
    assert main_module.main is dispatch_main
