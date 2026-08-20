"""Unit tests for the package metadata source of truth."""

import pytest

from pysysmlv2.config import meta

pytestmark = pytest.mark.unit


def test_metadata_matches_the_public_distribution_contract():
    """Keep the package identity and maintainer metadata explicit."""
    assert meta.__PACKAGE_NAME__ == "pysysmlv2"
    assert meta.__VERSION__ == "0.1.0"
    assert meta.__AUTHOR__ == "HansBug"
    assert meta.__AUTHOR_EMAIL__ == "hansbug@buaa.edu.cn"
