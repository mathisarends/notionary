import pytest

from notionary.blocks.mappings.divider import DividerElement
from notionary.blocks.schemas import (
    BlockType,
    CreateDividerBlock,
    DividerBlock,
    DividerData,
    PartialUserDto,
)


def create_divider_block_with_required_fields(**kwargs) -> DividerBlock:
    """Helper to create DividerBlock with all required BaseBlock fields."""
    defaults = {
        "object": "block",
        "id": "test-id",
        "type": BlockType.DIVIDER,
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": "2023-01-01T00:00:00.000Z",
        "created_by": PartialUserDto(object="user", id="user-id"),
        "last_edited_by": PartialUserDto(object="user", id="user-id"),
        "divider": DividerData(),
    }
    defaults.update(kwargs)
    return DividerBlock(**defaults)


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid divider syntax."""
    assert await DividerElement.markdown_to_notion("---") is not None
    assert await DividerElement.markdown_to_notion("----")  # More dashes
    assert await DividerElement.markdown_to_notion("-----") is not None
    assert await DividerElement.markdown_to_notion("  ---  ")  # With spaces


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not await DividerElement.markdown_to_notion("--")  # Too few dashes
    assert not await DividerElement.markdown_to_notion("text ---")  # Not alone
    assert await DividerElement.markdown_to_notion("--- text") is None
    assert await DividerElement.markdown_to_notion("This is just text.") is None


def test_match_notion():
    """Test recognition of Notion divider blocks."""
    divider_block = create_divider_block_with_required_fields()
    assert DividerElement.match_notion(divider_block)

    # Use Mock for paragraph
    from unittest.mock import Mock

    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.divider = None
    assert not DividerElement.match_notion(paragraph_block)

    # Test divider block without divider property
    from unittest.mock import Mock

    invalid_divider = Mock()
    invalid_divider.type = BlockType.DIVIDER
    invalid_divider.divider = None
    assert not DividerElement.match_notion(invalid_divider)


@pytest.mark.asyncio
async def test_markdown_to_notion():
    """Test conversion of divider to Notion blocks."""
    result = await DividerElement.markdown_to_notion("---")

    # Should return just the divider block
    assert isinstance(result, CreateDividerBlock)
    assert result.type == "divider"


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = await DividerElement.markdown_to_notion("--")  # Too few dashes
    assert result is None

    result = await DividerElement.markdown_to_notion("text ---")
    assert result is None


@pytest.mark.asyncio
async def test_notion_to_markdown():
    """Test conversion of Notion divider to markdown."""
    block = create_divider_block_with_required_fields()

    result = await DividerElement.notion_to_markdown(block)
    assert result == "---"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    # Use Mock for paragraph
    from unittest.mock import Mock

    paragraph_block = Mock()
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.divider = None
    result = await DividerElement.notion_to_markdown(paragraph_block)
    assert result is None

    # Test divider block without divider property
    invalid_divider = Mock()
    invalid_divider.type = BlockType.DIVIDER
    invalid_divider.divider = None
    result = await DividerElement.notion_to_markdown(invalid_divider)
    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("---", True),
        ("----", True),
        ("-----", True),
        ("  ---  ", True),
        ("--", False),
        ("text ---", False),
        ("--- text", False),
        ("", False),
    ],
)
async def test_markdown_patterns(markdown, should_match):
    """Test recognition of various divider patterns."""
    result = await DividerElement.markdown_to_notion(markdown)
    if should_match:
        assert result is not None
    else:
        assert result is None
