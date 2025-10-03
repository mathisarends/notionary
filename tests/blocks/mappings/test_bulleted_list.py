from unittest.mock import Mock

import pytest

from notionary.blocks.mappings.bulleted_list import BulletedListMapper
from notionary.blocks.schemas import (
    BulletedListItemData,
    CreateBulletedListItemBlock,
)


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid bulleted list formats."""
    assert await BulletedListMapper.markdown_to_notion("- First item") is not None
    assert await BulletedListMapper.markdown_to_notion("* Second item") is not None
    assert await BulletedListMapper.markdown_to_notion("+ Third item") is not None
    assert await BulletedListMapper.markdown_to_notion("  - Indented item") is not None
    assert await BulletedListMapper.markdown_to_notion("    * Deep indented") is not None


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert await BulletedListMapper.markdown_to_notion("- [ ] Todo item") is None
    assert await BulletedListMapper.markdown_to_notion("- [x] Completed todo") is None
    assert await BulletedListMapper.markdown_to_notion("1. Numbered item") is None
    assert await BulletedListMapper.markdown_to_notion("Regular text") is None
    assert await BulletedListMapper.markdown_to_notion("") is None


def test_match_notion_valid():
    """Test recognition of valid Notion blocks."""
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.bulleted_list_item = Mock()

    assert BulletedListMapper.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Wrong type
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.bulleted_list_item = Mock()
    assert not BulletedListMapper.match_notion(mock_block)

    # None content
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.bulleted_list_item = None
    assert not BulletedListMapper.match_notion(mock_block)


@pytest.mark.asyncio
async def test_markdown_to_notion():
    """Test conversion from markdown to Notion."""
    result = await BulletedListMapper.markdown_to_notion("- Test item")

    assert result is not None
    assert isinstance(result, CreateBulletedListItemBlock)
    assert isinstance(result.bulleted_list_item, BulletedListItemData)
    assert result.bulleted_list_item.color == "default"
    assert isinstance(result.bulleted_list_item.rich_text, list)


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert await BulletedListMapper.markdown_to_notion("- [ ] Todo") is None
    assert await BulletedListMapper.markdown_to_notion("Regular text") is None
    assert await BulletedListMapper.markdown_to_notion("") is None


@pytest.mark.asyncio
async def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Create mock rich text
    mock_rich_text = Mock()
    mock_rich_text.model_dump.return_value = {"text": {"content": "Test content"}}

    # Create mock block
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.bulleted_list_item = Mock()
    mock_block.bulleted_list_item.rich_text = [mock_rich_text]

    result = await BulletedListMapper.notion_to_markdown(mock_block)

    assert result is not None
    assert result.startswith("- ")


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    assert await BulletedListMapper.notion_to_markdown(mock_block) is None

    mock_block.type = "bulleted_list_item"
    mock_block.bulleted_list_item = None
    assert await BulletedListMapper.notion_to_markdown(mock_block) is None


@pytest.mark.asyncio
async def test_different_bullet_types():
    """Test different bullet characters."""
    bullets = ["- Item", "* Item", "+ Item"]

    for bullet in bullets:
        assert await BulletedListMapper.markdown_to_notion(bullet) is not None
        result = await BulletedListMapper.markdown_to_notion(bullet)
        assert result is not None


@pytest.mark.asyncio
async def test_whitespace_handling():
    """Test handling of whitespace."""
    assert await BulletedListMapper.markdown_to_notion("- Item   ")  # trailing
    assert await BulletedListMapper.markdown_to_notion("- Item\n")  # newline
    assert await BulletedListMapper.markdown_to_notion("  - Item")  # leading


@pytest.mark.asyncio
async def test_special_characters():
    """Test with special characters."""
    test_cases = [
        "- Text with äöü",
        "- Text with 😀",
        "- Text with symbols !@#",
    ]

    for text in test_cases:
        assert await BulletedListMapper.markdown_to_notion(text) is not None
        result = await BulletedListMapper.markdown_to_notion(text)
        assert result is not None
