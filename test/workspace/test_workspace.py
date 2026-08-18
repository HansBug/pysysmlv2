"""Unit tests for the request-local workspace boundary."""

import pytest

from pysysmlv2.workspace import Workspace

pytestmark = pytest.mark.unit


def test_workspace_keeps_documents_isolated_by_source_path():
    workspace = Workspace()
    result = workspace.add_text("demo.sysml", "package Demo { }")
    assert result.ok
    assert list(workspace.documents) == ["demo.sysml"]


def test_link_is_a_stable_placeholder():
    workspace = Workspace()
    assert workspace.link() is None
