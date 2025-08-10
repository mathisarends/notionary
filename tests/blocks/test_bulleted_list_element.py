"""
Minimal tests for BulletedListElement.
Tests core functionality for bulleted list items (-, *, +).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.bulleted_list.bulleted_list_element import BulletedListElement
from notionary.blocks.bulleted_list.bulleted_list_models import (
    CreateBulletedListItemBlock,
    BulletedListItemBlock,
)


def test_match_markdown_valid():
    """Test recognition of valid bulleted list formats."""
    assert BulletedListElement.match_markdown("- First item")
    assert BulletedListElement.match_markdown("* Second item")
    assert BulletedListElement.match_markdown("+ Third item")
    assert BulletedListElement.match_markdown("  - Indented item")
    assert BulletedListElement.match_markdown("    * Deep indented")


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not BulletedListElement.match_markdown("- [ ] Todo item")
    assert not BulletedListElement.match_markdown("- [x] Completed todo")
    assert not BulletedListElement.match_markdown("1. Numbered item")
    assert not BulletedListElement.match_markdown("Regular text")
    assert not BulletedListElement.match_markdown("")


def test_match_notion_valid():
    """Test recognition of valid Notion blocks."""
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.bulleted_list_item = Mock()

    assert BulletedListElement.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Wrong type
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.bulleted_list_item = Mock()
    assert not BulletedListElement.match_notion(mock_block)

    # None content
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.bulleted_list_item = None
    assert not BulletedListElement.match_notion(mock_block)


def test_markdown_to_notion():
    """Test conversion from markdown to Notion."""
    result = BulletedListElement.markdown_to_notion("- Test item")

    assert result is not None
    assert isinstance(result, CreateBulletedListItemBlock)
    assert isinstance(result.bulleted_list_item, BulletedListItemBlock)
    assert result.bulleted_list_item.color == "default"
    assert isinstance(result.bulleted_list_item.rich_text, list)


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert BulletedListElement.markdown_to_notion("- [ ] Todo") is None
    assert BulletedListElement.markdown_to_notion("Regular text") is None
    assert BulletedListElement.markdown_to_notion("") is None


def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Create mock rich text
    mock_rich_text = Mock()
    mock_rich_text.model_dump.return_value = {"text": {"content": "Test content"}}

    # Create mock block
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.bulleted_list_item = Mock()
    mock_block.bulleted_list_item.rich_text = [mock_rich_text]

    result = BulletedListElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result.startswith("- ")


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    assert BulletedListElement.notion_to_markdown(mock_block) is None

    mock_block.type = "bulleted_list_item"
    mock_block.bulleted_list_item = None
    assert BulletedListElement.notion_to_markdown(mock_block) is None

def test_different_bullet_types():
    """Test different bullet characters."""
    bullets = ["- Item", "* Item", "+ Item"]

    for bullet in bullets:
        assert BulletedListElement.match_markdown(bullet)
        result = BulletedListElement.markdown_to_notion(bullet)
        assert result is not None


def test_whitespace_handling():
    """Test handling of whitespace."""
    assert BulletedListElement.match_markdown("- Item   ")  # trailing
    assert BulletedListElement.match_markdown("- Item\n")  # newline
    assert BulletedListElement.match_markdown("  - Item")  # leading


def test_special_characters():
    """Test with special characters."""
    test_cases = [
        "- Text with äöü",
        "- Text with 😀",
        "- Text with symbols !@#",
    ]

    for text in test_cases:
        assert BulletedListElement.match_markdown(text)
        result = BulletedListElement.markdown_to_notion(text)
        assert result is not None
