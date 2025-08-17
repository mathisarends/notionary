"""
Pytest tests for BreadcrumbElement.
Tests the essential functionality for breadcrumb block handling.
"""

from notionary.blocks.breadcrumbs.breadcrumb_element import BreadcrumbElement
from notionary.blocks.breadcrumbs.breadcrumb_models import (
    BreadcrumbBlock,
    CreateBreadcrumbBlock,
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


def test_match_markdown_valid():
    """Test recognition of valid breadcrumb syntax."""
    assert BreadcrumbElement.markdown_to_notion("[breadcrumb]") is not None
    assert BreadcrumbElement.markdown_to_notion("[BREADCRUMB]")  # Case insensitive
    assert BreadcrumbElement.markdown_to_notion("  [breadcrumb]  ")  # With spaces
    assert BreadcrumbElement.markdown_to_notion("\t[breadcrumb]\n")  # With whitespace


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not BreadcrumbElement.markdown_to_notion("breadcrumb")  # Missing brackets
    assert not BreadcrumbElement.markdown_to_notion(
        "[breadcrumb"
    )  # Missing closing bracket
    assert not BreadcrumbElement.markdown_to_notion(
        "breadcrumb]"
    )  # Missing opening bracket
    assert not BreadcrumbElement.markdown_to_notion("[bread crumb]")  # Space in name
    assert not BreadcrumbElement.markdown_to_notion("[breadcrumbs]")  # Wrong plural
    assert not BreadcrumbElement.markdown_to_notion("[toc]")  # Different element
    assert not BreadcrumbElement.markdown_to_notion("")  # Empty string


def test_match_notion_valid():
    """Test recognition of valid breadcrumb blocks."""
    block = create_block_with_required_fields(
        type=BlockType.BREADCRUMB, breadcrumb=BreadcrumbBlock()
    )
    assert BreadcrumbElement.match_notion(block)


def test_match_notion_invalid():
    """Test rejection of invalid blocks."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(
        type=BlockType.PARAGRAPH, breadcrumb=BreadcrumbBlock()
    )
    assert not BreadcrumbElement.match_notion(paragraph_block)

    # Right type but no breadcrumb
    no_breadcrumb_block = create_block_with_required_fields(
        type=BlockType.BREADCRUMB, breadcrumb=None
    )
    assert not BreadcrumbElement.match_notion(no_breadcrumb_block)


def test_markdown_to_notion_valid():
    """Test conversion from valid markdown to Notion blocks."""
    result = BreadcrumbElement.markdown_to_notion("[breadcrumb]")

    assert isinstance(result, CreateBreadcrumbBlock)
    assert isinstance(result.breadcrumb, BreadcrumbBlock)


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert BreadcrumbElement.markdown_to_notion("breadcrumb") is None
    assert BreadcrumbElement.markdown_to_notion("[bread crumb]") is None
    assert BreadcrumbElement.markdown_to_notion("[toc]") is None
    assert BreadcrumbElement.markdown_to_notion("") is None


def test_notion_to_markdown_valid():
    """Test conversion from valid Notion blocks to markdown."""
    block = create_block_with_required_fields(
        type=BlockType.BREADCRUMB, breadcrumb=BreadcrumbBlock()
    )

    result = BreadcrumbElement.notion_to_markdown(block)
    assert result == "[breadcrumb]"


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(
        type=BlockType.PARAGRAPH, breadcrumb=BreadcrumbBlock()
    )
    assert BreadcrumbElement.notion_to_markdown(paragraph_block) is None

    # Right type but no breadcrumb
    no_breadcrumb_block = create_block_with_required_fields(
        type=BlockType.BREADCRUMB, breadcrumb=None
    )
    assert BreadcrumbElement.notion_to_markdown(no_breadcrumb_block) is None
