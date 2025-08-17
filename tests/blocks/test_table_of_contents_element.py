"""
Pytest tests for TableOfContentsElement.
Tests the essential functionality for table of contents block handling.
"""

import pytest
from notionary.blocks.table_of_contents.table_of_contents_element import (
    TableOfContentsElement,
)
from notionary.blocks.table_of_contents.table_of_contents_models import (
    TableOfContentsBlock,
    CreateTableOfContentsBlock,
)
from notionary.blocks.models import Block, BlockType


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id"},
        "last_edited_by": {"object": "user", "id": "user-id"},
    }
    defaults.update(kwargs)
    return Block(**defaults)


def test_match_markdown_valid_default():
    """Test recognition of valid default TOC syntax."""
    assert TableOfContentsElement.markdown_to_notion("[toc]") is not None
    assert TableOfContentsElement.markdown_to_notion("[TOC]")  # Case insensitive
    assert TableOfContentsElement.markdown_to_notion("  [toc]  ")  # With spaces


def test_match_markdown_valid_with_color():
    """Test recognition of valid TOC syntax with colors."""
    assert TableOfContentsElement.markdown_to_notion("[toc](blue)")
    assert TableOfContentsElement.markdown_to_notion("[toc](gray)")
    assert TableOfContentsElement.markdown_to_notion("[toc](blue_background)")
    assert TableOfContentsElement.markdown_to_notion("[toc](red_background)")
    assert TableOfContentsElement.markdown_to_notion("[TOC](BLUE)")  # Case insensitive


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not TableOfContentsElement.markdown_to_notion("toc")  # Missing brackets
    assert not TableOfContentsElement.markdown_to_notion(
        "[toc"
    )  # Missing closing bracket
    assert not TableOfContentsElement.markdown_to_notion(
        "toc]"
    )  # Missing opening bracket
    assert not TableOfContentsElement.markdown_to_notion(
        "[table_of_contents]"
    )  # Wrong name
    assert not TableOfContentsElement.markdown_to_notion("[toc]()")  # Empty parentheses
    assert not TableOfContentsElement.markdown_to_notion(
        "[breadcrumb]"
    )  # Different element
    assert not TableOfContentsElement.markdown_to_notion("")  # Empty string


def test_match_notion_valid():
    """Test recognition of valid table of contents blocks."""
    block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS,
        table_of_contents=TableOfContentsBlock(color="default"),
    )
    assert TableOfContentsElement.match_notion(block)


def test_match_notion_invalid():
    """Test rejection of invalid blocks."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(
        type=BlockType.PARAGRAPH,
        table_of_contents=TableOfContentsBlock(color="default"),
    )
    assert not TableOfContentsElement.match_notion(paragraph_block)

    # Right type but no table_of_contents
    no_toc_block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS, table_of_contents=None
    )
    assert not TableOfContentsElement.match_notion(no_toc_block)


def test_markdown_to_notion_default():
    """Test conversion from default markdown to Notion blocks."""
    result = TableOfContentsElement.markdown_to_notion("[toc]")

    assert isinstance(result, CreateTableOfContentsBlock)
    assert isinstance(result.table_of_contents, TableOfContentsBlock)
    assert result.table_of_contents.color == "default"


def test_markdown_to_notion_with_color():
    """Test conversion from colored markdown to Notion blocks."""
    result = TableOfContentsElement.markdown_to_notion("[toc](blue)")

    assert isinstance(result, CreateTableOfContentsBlock)
    assert isinstance(result.table_of_contents, TableOfContentsBlock)
    assert result.table_of_contents.color == "blue"


def test_markdown_to_notion_with_background_color():
    """Test conversion with background colors."""
    result = TableOfContentsElement.markdown_to_notion("[toc](blue_background)")

    assert isinstance(result, CreateTableOfContentsBlock)
    assert isinstance(result.table_of_contents, TableOfContentsBlock)
    assert result.table_of_contents.color == "blue_background"


def test_markdown_to_notion_case_insensitive():
    """Test that color matching is case insensitive."""
    result = TableOfContentsElement.markdown_to_notion("[TOC](BLUE)")

    assert isinstance(result, CreateTableOfContentsBlock)
    assert result.table_of_contents.color == "blue"  # Should be lowercase


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert TableOfContentsElement.markdown_to_notion("toc") is None
    assert TableOfContentsElement.markdown_to_notion("[table_of_contents]") is None
    assert TableOfContentsElement.markdown_to_notion("[breadcrumb]") is None
    assert TableOfContentsElement.markdown_to_notion("") is None


def test_notion_to_markdown_default():
    """Test conversion from default Notion blocks to markdown."""
    block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS,
        table_of_contents=TableOfContentsBlock(color="default"),
    )

    result = TableOfContentsElement.notion_to_markdown(block)
    assert result == "[toc]"


def test_notion_to_markdown_with_color():
    """Test conversion from colored Notion blocks to markdown."""
    block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS,
        table_of_contents=TableOfContentsBlock(color="blue"),
    )

    result = TableOfContentsElement.notion_to_markdown(block)
    assert result == "[toc](blue)"


def test_notion_to_markdown_with_background_color():
    """Test conversion with background colors."""
    block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS,
        table_of_contents=TableOfContentsBlock(color="blue_background"),
    )

    result = TableOfContentsElement.notion_to_markdown(block)
    assert result == "[toc](blue_background)"


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(
        type=BlockType.PARAGRAPH, table_of_contents=TableOfContentsBlock(color="blue")
    )
    assert TableOfContentsElement.notion_to_markdown(paragraph_block) is None

    # Right type but no table_of_contents
    no_toc_block = create_block_with_required_fields(
        type=BlockType.TABLE_OF_CONTENTS, table_of_contents=None
    )
    assert TableOfContentsElement.notion_to_markdown(no_toc_block) is None


def test_bidirectional_conversion():
    """Test that markdown -> notion -> markdown is consistent."""
    original_inputs = ["[toc]", "[toc](blue)", "[toc](gray_background)"]

    for original in original_inputs:
        notion_result = TableOfContentsElement.markdown_to_notion(original)
        assert notion_result is not None

        block = create_block_with_required_fields(
            type=BlockType.TABLE_OF_CONTENTS,
            table_of_contents=notion_result.table_of_contents,
        )

        # Convert back to markdown
        markdown_result = TableOfContentsElement.notion_to_markdown(block)
        assert (
            markdown_result == original.lower()
        )  # Should match (potentially lowercased)
