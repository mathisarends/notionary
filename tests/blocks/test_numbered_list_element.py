"""
Minimal tests for NumberedListElement.
Tests core functionality for numbered list items (1., 2., etc.).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.numbered_list.numbered_list_element import NumberedListElement
from notionary.blocks.numbered_list.numbered_list_models import (
    CreateNumberedListItemBlock,
    NumberedListItemBlock,
)


def test_match_markdown_valid():
    """Test recognition of valid numbered list formats."""
    assert NumberedListElement.match_markdown("1. First item")
    assert NumberedListElement.match_markdown("2. Second item")
    assert NumberedListElement.match_markdown("123. Item with big number")
    assert NumberedListElement.match_markdown("  1. Indented item")
    assert NumberedListElement.match_markdown("    10. Deep indented")


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not NumberedListElement.match_markdown("- Bulleted item")
    assert not NumberedListElement.match_markdown("* Another bullet")
    assert not NumberedListElement.match_markdown("1 Missing dot")
    assert not NumberedListElement.match_markdown("1.Missing space")
    assert not NumberedListElement.match_markdown("a. Letter instead of number")
    assert not NumberedListElement.match_markdown("Regular text")
    assert not NumberedListElement.match_markdown("")


def test_match_notion_valid():
    """Test recognition of valid Notion blocks."""
    mock_block = Mock()
    mock_block.type = "numbered_list_item"
    mock_block.numbered_list_item = Mock()

    assert NumberedListElement.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Wrong type
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.numbered_list_item = Mock()
    assert not NumberedListElement.match_notion(mock_block)

    # None content
    mock_block = Mock()
    mock_block.type = "numbered_list_item"
    mock_block.numbered_list_item = None
    assert not NumberedListElement.match_notion(mock_block)


def test_markdown_to_notion():
    """Test conversion from markdown to Notion."""
    result = NumberedListElement.markdown_to_notion("1. Test item")

    assert result is not None
    assert isinstance(result, CreateNumberedListItemBlock)
    assert isinstance(result.numbered_list_item, NumberedListItemBlock)
    assert result.numbered_list_item.color == "default"
    assert isinstance(result.numbered_list_item.rich_text, list)


def test_markdown_to_notion_different_numbers():
    """Test conversion with different numbers."""
    test_cases = ["1. First", "5. Fifth", "100. Hundredth"]

    for markdown_text in test_cases:
        result = NumberedListElement.markdown_to_notion(markdown_text)
        assert result is not None
        assert isinstance(result, CreateNumberedListItemBlock)


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert NumberedListElement.markdown_to_notion("- Bullet item") is None
    assert NumberedListElement.markdown_to_notion("1 Missing dot") is None
    assert NumberedListElement.markdown_to_notion("Regular text") is None
    assert NumberedListElement.markdown_to_notion("") is None


def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Create mock rich text
    mock_rich_text = Mock()
    mock_rich_text.model_dump.return_value = {"text": {"content": "Test content"}}

    # Create mock block
    mock_block = Mock()
    mock_block.type = "numbered_list_item"
    mock_block.numbered_list_item = Mock()
    mock_block.numbered_list_item.rich_text = [mock_rich_text]

    result = NumberedListElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result.startswith("1. ")


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    assert NumberedListElement.notion_to_markdown(mock_block) is None

    mock_block.type = "numbered_list_item"
    mock_block.numbered_list_item = None
    assert NumberedListElement.notion_to_markdown(mock_block) is None


def test_pattern_regex_directly():
    """Test the PATTERN regex directly."""
    pattern = NumberedListElement.PATTERN

    # Valid patterns
    assert pattern.match("1. Item")
    assert pattern.match("123. Item")
    assert pattern.match("  5. Indented")

    # Invalid patterns
    assert not pattern.match("1.Missing space")
    assert not pattern.match("1 Missing dot")
    assert not pattern.match("a. Letter")


def test_whitespace_handling():
    """Test handling of whitespace."""
    assert NumberedListElement.match_markdown("1. Item   ")  # trailing
    assert NumberedListElement.match_markdown("1. Item\n")  # newline
    assert NumberedListElement.match_markdown("  1. Item")  # leading indentation


def test_special_characters():
    """Test with special characters."""
    test_cases = [
        "1. Text with äöü",
        "2. Text with 😀",
        "3. Text with symbols !@#",
        "10. Text with numbers 123",
    ]

    for text in test_cases:
        assert NumberedListElement.match_markdown(text)
        result = NumberedListElement.markdown_to_notion(text)
        assert result is not None


def test_large_numbers():
    """Test with large numbers."""
    large_number_cases = [
        "999. Large number",
        "1000. Four digits",
        "12345. Five digits",
    ]

    for text in large_number_cases:
        assert NumberedListElement.match_markdown(text)
        result = NumberedListElement.markdown_to_notion(text)
        assert result is not None


def test_content_extraction():
    """Test that content is correctly extracted from numbered items."""
    test_cases = [
        ("1. Simple text", "Simple text"),
        ("5. Text with **bold**", "Text with **bold**"),
        ("10. Multi word content here", "Multi word content here"),
    ]

    for markdown_text, expected_content in test_cases:
        match = NumberedListElement.PATTERN.match(markdown_text)
        assert match is not None
        assert match.group(2) == expected_content


def test_indentation_levels():
    """Test various indentation levels."""
    indentation_cases = [
        "1. No indent",
        "  2. Two spaces",
        "    3. Four spaces",
        "      4. Six spaces",
        "\t5. Tab indent",
    ]

    for text in indentation_cases:
        assert NumberedListElement.match_markdown(text)
        result = NumberedListElement.markdown_to_notion(text)
        assert result is not None
