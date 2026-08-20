"""Unit tests for the staged semantic-query extension boundary."""

import pytest

import pysysmlv2.query.model_query as model_query

pytestmark = pytest.mark.unit


def test_model_query_module_remains_an_explicit_future_boundary():
    """Document that query implementation is intentionally deferred."""
    assert "semantic model" in model_query.__doc__
    assert not [name for name in vars(model_query) if not name.startswith("_")]
