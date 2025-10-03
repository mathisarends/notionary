import pytest

from notionary.blocks.mappings.breadcrumb import BreadcrumbElement
from notionary.blocks.schemas import (
    Block,
    BlockType,
    BreadcrumbBlock,
    CreateBreadcrumbBlock,
)


def create_block_with_required_fields(**kwargs) -> Block:
    """Helper to create Block with all required fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": {"object": "user", "id": "user-id", "type": "person", "person": {}},
        "last_edited_by": {"object": "user", "id": "user-id", "type": "person", "person": {}},
    }
    defaults.update(kwargs)
    return Block(**defaults)


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid breadcrumb syntax."""
    assert await BreadcrumbElement.markdown_to_notion("[breadcrumb]") is not None
    assert await BreadcrumbElement.markdown_to_notion("[BREADCRUMB]")  # Case insensitive
    assert await BreadcrumbElement.markdown_to_notion("  [breadcrumb]  ")  # With spaces
    assert await BreadcrumbElement.markdown_to_notion("\t[breadcrumb]\n")  # With whitespace


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not await BreadcrumbElement.markdown_to_notion("breadcrumb")  # Missing brackets
    assert not await BreadcrumbElement.markdown_to_notion("[breadcrumb")  # Missing closing bracket
    assert not await BreadcrumbElement.markdown_to_notion("breadcrumb]")  # Missing opening bracket
    assert not await BreadcrumbElement.markdown_to_notion("[bread crumb]")  # Space in name
    assert not await BreadcrumbElement.markdown_to_notion("[breadcrumbs]")  # Wrong plural
    assert not await BreadcrumbElement.markdown_to_notion("[toc]")  # Different element
    assert not await BreadcrumbElement.markdown_to_notion("")  # Empty string


def test_match_notion_valid():
    """Test recognition of valid breadcrumb blocks."""
    block = create_block_with_required_fields(type=BlockType.BREADCRUMB, breadcrumb=BreadcrumbBlock())
    assert BreadcrumbElement.match_notion(block)


def test_match_notion_invalid():
    """Test rejection of invalid blocks."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(type=BlockType.PARAGRAPH, breadcrumb=BreadcrumbBlock())
    assert not BreadcrumbElement.match_notion(paragraph_block)

    # Right type but no breadcrumb
    no_breadcrumb_block = create_block_with_required_fields(type=BlockType.BREADCRUMB, breadcrumb=None)
    assert not BreadcrumbElement.match_notion(no_breadcrumb_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_valid():
    """Test conversion from valid markdown to Notion blocks."""
    result = await BreadcrumbElement.markdown_to_notion("[breadcrumb]")

    assert isinstance(result, CreateBreadcrumbBlock)
    assert isinstance(result.breadcrumb, BreadcrumbBlock)


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert await BreadcrumbElement.markdown_to_notion("breadcrumb") is None
    assert await BreadcrumbElement.markdown_to_notion("[bread crumb]") is None
    assert await BreadcrumbElement.markdown_to_notion("[toc]") is None
    assert await BreadcrumbElement.markdown_to_notion("") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_valid():
    """Test conversion from valid Notion blocks to markdown."""
    block = create_block_with_required_fields(type=BlockType.BREADCRUMB, breadcrumb=BreadcrumbBlock())

    result = await BreadcrumbElement.notion_to_markdown(block)
    assert result == "[breadcrumb]"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    # Wrong type
    paragraph_block = create_block_with_required_fields(type=BlockType.PARAGRAPH, breadcrumb=BreadcrumbBlock())
    assert await BreadcrumbElement.notion_to_markdown(paragraph_block) is None

    # Right type but no breadcrumb
    no_breadcrumb_block = create_block_with_required_fields(type=BlockType.BREADCRUMB, breadcrumb=None)
    assert await BreadcrumbElement.notion_to_markdown(no_breadcrumb_block) is None
