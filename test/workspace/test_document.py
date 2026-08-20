"""Unit tests for immutable workspace document identity."""

import pytest

from pysysmlv2.workspace.document import Document

pytestmark = pytest.mark.unit


def test_document_keeps_source_identity_and_text_together():
    """Expose the stable source-path/text value-object contract."""
    document = Document("demo.sysml", "package Demo { }")
    assert document.source_path == "demo.sysml"
    assert document.text == "package Demo { }"


def test_document_is_immutable_after_construction():
    """Prevent workspace keys from drifting after insertion."""
    document = Document("demo.sysml", "package Demo { }")
    with pytest.raises(AttributeError):
        document.source_path = "other.sysml"
