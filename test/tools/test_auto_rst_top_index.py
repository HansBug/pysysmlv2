"""Unit tests for bilingual API index generation."""

import pytest

from tools import auto_rst_top_index

pytestmark = pytest.mark.unit


def test_render_supports_both_documentation_languages():
    assert "API Documentation" in auto_rst_top_index._render("en")
    assert "API 文档" in auto_rst_top_index._render("zh")


def test_generate_writes_bilingual_indexes(tmp_path):
    auto_rst_top_index.generate(tmp_path)

    assert (tmp_path / "api_doc_en.rst").read_text(encoding="utf-8").startswith("API Documentation")
    assert (tmp_path / "api_doc_zh.rst").read_text(encoding="utf-8").startswith("API 文档")
