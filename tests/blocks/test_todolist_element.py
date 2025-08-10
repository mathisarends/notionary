"""
Minimal tests for TodoElement.
Tests core functionality for todo blocks with checkbox syntax.
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.todo.todo_element import TodoElement
from notionary.blocks.todo.todo_models import (
    CreateToDoBlock,
    ToDoBlock,
)


def test_match_markdown_unchecked():
    """Test recognition of unchecked todo formats."""
    assert TodoElement.match_markdown("- [ ] Unchecked task")
    assert TodoElement.match_markdown("* [ ] Asterisk todo")
    assert TodoElement.match_markdown("+ [ ] Plus todo")
    assert TodoElement.match_markdown("  - [ ] Indented todo")
    assert TodoElement.match_markdown("    * [ ] Deep indented")


def test_match_markdown_checked():
    """Test recognition of checked todo formats."""
    assert TodoElement.match_markdown("- [x] Checked task")
    assert TodoElement.match_markdown("* [x] Asterisk checked")
    assert TodoElement.match_markdown("+ [x] Plus checked")
    assert TodoElement.match_markdown("- [X] Uppercase X")
    assert TodoElement.match_markdown("* [X] Uppercase asterisk")


def test_match_markdown_invalid():
    """Test rejection of invalid todo formats."""
    # Regular bullets without checkboxes
    assert not TodoElement.match_markdown("- Regular bullet")
    assert not TodoElement.match_markdown("* Regular asterisk")
    assert not TodoElement.match_markdown("+ Regular plus")

    # Wrong checkbox syntax
    assert not TodoElement.match_markdown("- [?] Wrong symbol")
    assert not TodoElement.match_markdown("- [] Missing space")
    assert not TodoElement.match_markdown("- [ Missing bracket")
    assert not TodoElement.match_markdown("- Missing checkbox")

    # Other formats
    assert not TodoElement.match_markdown("1. [ ] Numbered todo")
    assert not TodoElement.match_markdown("Regular text")
    assert not TodoElement.match_markdown("")


def test_match_notion_valid():
    """Test recognition of valid Notion to_do blocks."""
    mock_block = Mock()
    mock_block.type = "to_do"
    mock_block.to_do = Mock()

    assert TodoElement.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Wrong type
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.to_do = Mock()
    assert not TodoElement.match_notion(mock_block)

    # None content
    mock_block = Mock()
    mock_block.type = "to_do"
    mock_block.to_do = None
    assert not TodoElement.match_notion(mock_block)


def test_markdown_to_notion_unchecked():
    """Test conversion of unchecked todos to Notion."""
    result = TodoElement.markdown_to_notion("- [ ] Test task")

    assert result is not None
    assert isinstance(result, CreateToDoBlock)
    assert isinstance(result.to_do, ToDoBlock)
    assert result.to_do.checked is False
    assert result.to_do.color == "default"
    assert isinstance(result.to_do.rich_text, list)


def test_markdown_to_notion_checked():
    """Test conversion of checked todos to Notion."""
    result = TodoElement.markdown_to_notion("- [x] Completed task")

    assert result is not None
    assert isinstance(result, CreateToDoBlock)
    assert result.to_do.checked is True


def test_markdown_to_notion_different_bullets():
    """Test conversion with different bullet types."""
    test_cases = [
        ("- [ ] Dash unchecked", False),
        ("* [ ] Star unchecked", False),
        ("+ [ ] Plus unchecked", False),
        ("- [x] Dash checked", True),
        ("* [X] Star checked uppercase", True),
        ("+ [x] Plus checked", True),
    ]

    for markdown_text, expected_checked in test_cases:
        result = TodoElement.markdown_to_notion(markdown_text)
        assert result is not None
        assert result.to_do.checked == expected_checked


def test_markdown_to_notion_case_insensitive():
    """Test that [x] and [X] both work for checked state."""
    lower_result = TodoElement.markdown_to_notion("- [x] lowercase")
    upper_result = TodoElement.markdown_to_notion("- [X] uppercase")

    assert lower_result is not None
    assert upper_result is not None
    assert lower_result.to_do.checked is True
    assert upper_result.to_do.checked is True


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert TodoElement.markdown_to_notion("- Regular bullet") is None
    assert TodoElement.markdown_to_notion("- [?] Wrong symbol") is None
    assert TodoElement.markdown_to_notion("Regular text") is None
    assert TodoElement.markdown_to_notion("") is None


def test_notion_to_markdown_unchecked():
    """Test conversion from unchecked Notion to_do to markdown."""
    # Create mock rich text
    mock_rich_text = Mock()
    mock_rich_text.model_dump.return_value = {"text": {"content": "Test task"}}

    # Create mock block
    mock_block = Mock()
    mock_block.type = "to_do"
    mock_block.to_do = Mock()
    mock_block.to_do.checked = False
    mock_block.to_do.rich_text = [mock_rich_text]

    result = TodoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result.startswith("- [ ] ")


def test_notion_to_markdown_checked():
    """Test conversion from checked Notion to_do to markdown."""
    # Create mock rich text
    mock_rich_text = Mock()
    mock_rich_text.model_dump.return_value = {"text": {"content": "Done task"}}

    # Create mock block
    mock_block = Mock()
    mock_block.type = "to_do"
    mock_block.to_do = Mock()
    mock_block.to_do.checked = True
    mock_block.to_do.rich_text = [mock_rich_text]

    result = TodoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result.startswith("- [x] ")


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    assert TodoElement.notion_to_markdown(mock_block) is None

    mock_block.type = "to_do"
    mock_block.to_do = None
    assert TodoElement.notion_to_markdown(mock_block) is None


def test_pattern_regex_directly():
    """Test the PATTERN and DONE_PATTERN regex directly."""
    unchecked_pattern = TodoElement.PATTERN
    checked_pattern = TodoElement.DONE_PATTERN

    # Unchecked pattern tests
    assert unchecked_pattern.match("- [ ] Task")
    assert unchecked_pattern.match("* [ ] Task")
    assert unchecked_pattern.match("+ [ ] Task")
    assert not unchecked_pattern.match("- [x] Task")

    # Checked pattern tests
    assert checked_pattern.match("- [x] Task")
    assert checked_pattern.match("- [X] Task")
    assert checked_pattern.match("* [x] Task")
    assert not checked_pattern.match("- [ ] Task")


def test_whitespace_handling():
    """Test handling of whitespace."""
    whitespace_cases = [
        "- [ ] Task with trailing spaces   ",
        "- [x] Task with newline\n",
        "  - [ ] Indented task",
        "    * [x] Deep indented",
    ]

    for text in whitespace_cases:
        assert TodoElement.match_markdown(text)
        result = TodoElement.markdown_to_notion(text)
        assert result is not None


def test_inline_formatting():
    """Test todos with inline formatting."""
    formatting_cases = [
        "- [ ] Task with **bold** text",
        "- [x] Task with *italic* text",
        "- [ ] Task with `code` text",
        "- [x] Task with [link](https://example.com)",
    ]

    for text in formatting_cases:
        assert TodoElement.match_markdown(text)
        result = TodoElement.markdown_to_notion(text)
        assert result is not None


def test_special_characters():
    """Test with special characters."""
    special_cases = [
        "- [ ] Task with äöü ß",
        "- [x] Task with 😀 emojis",
        "- [ ] Task with symbols !@#$%",
        "- [x] Task with numbers 123",
    ]

    for text in special_cases:
        assert TodoElement.match_markdown(text)
        result = TodoElement.markdown_to_notion(text)
        assert result is not None


def test_content_extraction():
    """Test that content is correctly extracted."""
    test_cases = [
        ("- [ ] Simple task", "Simple task"),
        ("* [x] Completed task", "Completed task"),
        ("+ [ ] Multi word task content", "Multi word task content"),
    ]

    for markdown_text, expected_content in test_cases:
        # Test unchecked pattern
        unchecked_match = TodoElement.PATTERN.match(markdown_text)
        checked_match = TodoElement.DONE_PATTERN.match(markdown_text)

        if unchecked_match:
            assert unchecked_match.group(1) == expected_content
        elif checked_match:
            assert checked_match.group(1) == expected_content


def test_roundtrip_conversion():
    """Test that conversion works both ways."""
    original_todos = [
        "- [ ] Unchecked task",
        "- [x] Checked task",
        "* [ ] Star unchecked",
        "+ [X] Plus checked uppercase",
    ]

    for original in original_todos:
        # Markdown -> Notion
        notion_block = TodoElement.markdown_to_notion(original)
        assert notion_block is not None

        # Create mock block for reverse conversion
        mock_block = Mock()
        mock_block.type = "to_do"
        mock_block.to_do = notion_block.to_do

        # Notion -> Markdown
        converted = TodoElement.notion_to_markdown(mock_block)
        assert converted is not None
        assert "[ ]" in converted or "[x]" in converted


def test_edge_cases():
    """Test edge cases."""
    edge_cases = [
        ("- [ ] x", True),  # Single character content
        ("- [x] A", True),  # Single letter
        ("- [ ] 1", True),  # Single digit
    ]

    for text, should_match in edge_cases:
        match_result = TodoElement.match_markdown(text)
        assert match_result == should_match

        if should_match:
            result = TodoElement.markdown_to_notion(text)
            assert result is not None
