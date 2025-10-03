import pytest

from notionary.blocks.mappings.breadcrumb import BreadcrumbMapper
from notionary.blocks.schemas import (
    BlockType,
    BreadcrumbBlock,
    BreadcrumbData,
    CreateBreadcrumbBlock,
    PartialUserDto,
)


def create_breadcrumb_block_with_required_fields(**kwargs) -> BreadcrumbBlock:
    """Helper to create BreadcrumbBlock with all required BaseBlock fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "type": BlockType.BREADCRUMB,
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": PartialUserDto(object="user", id="user-id"),
        "last_edited_by": PartialUserDto(object="user", id="user-id"),
        "breadcrumb": BreadcrumbData(),
    }
    defaults.update(kwargs)
    return BreadcrumbBlock(**defaults)


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid breadcrumb syntax."""
    assert await BreadcrumbMapper.markdown_to_notion("[breadcrumb]") is not None
    assert await BreadcrumbMapper.markdown_to_notion("[BREADCRUMB]")  # Case insensitive
    assert await BreadcrumbMapper.markdown_to_notion("  [breadcrumb]  ")  # With spaces
    assert await BreadcrumbMapper.markdown_to_notion("\t[breadcrumb]\n")  # With whitespace


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not await BreadcrumbMapper.markdown_to_notion("breadcrumb")  # Missing brackets
    assert not await BreadcrumbMapper.markdown_to_notion("[breadcrumb")  # Missing closing bracket
    assert not await BreadcrumbMapper.markdown_to_notion("breadcrumb]")  # Missing opening bracket
    assert not await BreadcrumbMapper.markdown_to_notion("[bread crumb]")  # Space in name
    assert not await BreadcrumbMapper.markdown_to_notion("[breadcrumbs]")  # Wrong plural
    assert not await BreadcrumbMapper.markdown_to_notion("[toc]")  # Different element
    assert not await BreadcrumbMapper.markdown_to_notion("")  # Empty string


def test_match_notion_valid():
    """Test recognition of valid breadcrumb blocks."""
    block = create_breadcrumb_block_with_required_fields()
    assert BreadcrumbMapper.match_notion(block)


def test_match_notion_invalid():
    """Test rejection of invalid blocks."""
    # Wrong type - use Mock for paragraph
    from unittest.mock import Mock

    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.breadcrumb = BreadcrumbData()
    assert not BreadcrumbMapper.match_notion(paragraph_block)

    # Right type but no breadcrumb - use Mock
    no_breadcrumb_block = Mock()
    no_breadcrumb_block.type = BlockType.BREADCRUMB
    no_breadcrumb_block.breadcrumb = None
    assert not BreadcrumbMapper.match_notion(no_breadcrumb_block)


@pytest.mark.asyncio
async def test_markdown_to_notion_valid():
    """Test conversion from valid markdown to Notion blocks."""
    result = await BreadcrumbMapper.markdown_to_notion("[breadcrumb]")

    assert isinstance(result, CreateBreadcrumbBlock)
    assert isinstance(result.breadcrumb, BreadcrumbData)


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert await BreadcrumbMapper.markdown_to_notion("breadcrumb") is None
    assert await BreadcrumbMapper.markdown_to_notion("[bread crumb]") is None
    assert await BreadcrumbMapper.markdown_to_notion("[toc]") is None
    assert await BreadcrumbMapper.markdown_to_notion("") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_valid():
    """Test conversion from valid Notion blocks to markdown."""
    block = create_breadcrumb_block_with_required_fields()

    result = await BreadcrumbMapper.notion_to_markdown(block)
    assert result == "[breadcrumb]"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    # Wrong type - use Mock for paragraph
    from unittest.mock import Mock

    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.breadcrumb = BreadcrumbData()
    assert await BreadcrumbMapper.notion_to_markdown(paragraph_block) is None

    # Right type but no breadcrumb - use Mock
    no_breadcrumb_block = Mock()
    no_breadcrumb_block.type = BlockType.BREADCRUMB
    no_breadcrumb_block.breadcrumb = None
    assert await BreadcrumbMapper.notion_to_markdown(no_breadcrumb_block) is None
