"""Unit tests for the staged semantic model boundary."""

import pytest

from pysysmlv2.semantic import SemanticModel
from pysysmlv2.syntax.ast import Model

pytestmark = pytest.mark.unit


def test_semantic_model_wraps_syntax_without_claiming_linking():
    model = SemanticModel(Model())
    assert model.syntax.members == []
