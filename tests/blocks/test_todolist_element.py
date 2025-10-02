from unittest.mock import Mock

import pytest

from notionary.blocks.todo.models import CreateToDoBlock, ToDoBlock
from notionary.blocks.todo.todo_element import TodoElement


@pytest.mark.asyncio
async def test_match_markdown_unchecked():
    """Test recognition of unchecked todo formats."""
    assert await TodoElement.markdown_to_notion("- [ ] Unchecked task") is not None
    assert await TodoElement.markdown_to_notion("* [ ] Asterisk todo") is not None
    assert await TodoElement.markdown_to_notion("+ [ ] Plus todo") is not None
    assert await TodoElement.markdown_to_notion("  - [ ] Indented todo") is not None
    assert await TodoElement.markdown_to_notion("    * [ ] Deep indented") is not None


@pytest.mark.asyncio
async def test_match_markdown_checked():
    """Test recognition of checked todo formats."""
    assert await TodoElement.markdown_to_notion("- [x] Checked task") is not None
    assert await TodoElement.markdown_to_notion("* [x] Asterisk checked") is not None
    assert await TodoElement.markdown_to_notion("+ [x] Plus checked") is not None
    assert await TodoElement.markdown_to_notion("- [X] Uppercase X") is not None
    assert await TodoElement.markdown_to_notion("* [X] Uppercase asterisk") is not None


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of invalid todo formats."""
    # Regular bullets without checkboxes
    assert await TodoElement.markdown_to_notion("- Regular bullet") is None
    assert await TodoElement.markdown_to_notion("* Regular asterisk") is None
    assert await TodoElement.markdown_to_notion("+ Regular plus") is None

    # Wrong checkbox syntax
    assert await TodoElement.markdown_to_notion("- [?] Wrong symbol") is None
    assert await TodoElement.markdown_to_notion("- [] Missing space") is None
    assert await TodoElement.markdown_to_notion("- [ Missing bracket") is None
    assert await TodoElement.markdown_to_notion("- Missing checkbox") is None

    # Other formats
    assert await TodoElement.markdown_to_notion("1. [ ] Numbered todo") is None
    assert await TodoElement.markdown_to_notion("Regular text") is None
    assert await TodoElement.markdown_to_notion("") is None


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


@pytest.mark.asyncio
async def test_markdown_to_notion_unchecked():
    """Test conversion of unchecked todos to Notion."""
    result = await TodoElement.markdown_to_notion("- [ ] Test task")

    assert result is not None
    assert isinstance(result, CreateToDoBlock)
    assert isinstance(result.to_do, ToDoBlock)
    assert result.to_do.checked is False
    assert result.to_do.color == "default"
    assert isinstance(result.to_do.rich_text, list)


@pytest.mark.asyncio
async def test_markdown_to_notion_checked():
    """Test conversion of checked todos to Notion."""
    result = await TodoElement.markdown_to_notion("- [x] Completed task")

    assert result is not None
    assert isinstance(result, CreateToDoBlock)
    assert result.to_do.checked is True


@pytest.mark.asyncio
async def test_markdown_to_notion_different_bullets():
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
        result = await TodoElement.markdown_to_notion(markdown_text)
        assert result is not None
        assert result.to_do.checked == expected_checked


@pytest.mark.asyncio
async def test_markdown_to_notion_case_insensitive():
    """Test that [x] and [X] both work for checked state."""
    lower_result = await TodoElement.markdown_to_notion("- [x] lowercase")
    upper_result = await TodoElement.markdown_to_notion("- [X] uppercase")

    assert lower_result is not None
    assert upper_result is not None
    assert lower_result.to_do.checked is True
    assert upper_result.to_do.checked is True


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert await TodoElement.markdown_to_notion("- Regular bullet") is None
    assert await TodoElement.markdown_to_notion("- [?] Wrong symbol") is None
    assert await TodoElement.markdown_to_notion("Regular text") is None
    assert await TodoElement.markdown_to_notion("") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_unchecked():
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

    result = await TodoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result.startswith("- [ ] ")


@pytest.mark.asyncio
async def test_notion_to_markdown_checked():
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

    result = await TodoElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result.startswith("- [x] ")


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    assert await TodoElement.notion_to_markdown(mock_block) is None

    mock_block.type = "to_do"
    mock_block.to_do = None
    assert await TodoElement.notion_to_markdown(mock_block) is None


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


@pytest.mark.asyncio
async def test_whitespace_handling():
    """Test handling of whitespace."""
    whitespace_cases = [
        "- [ ] Task with trailing spaces   ",
        "- [x] Task with newline\n",
        "  - [ ] Indented task",
        "    * [x] Deep indented",
    ]

    for text in whitespace_cases:
        assert await TodoElement.markdown_to_notion(text) is not None
        result = await TodoElement.markdown_to_notion(text)
        assert result is not None


@pytest.mark.asyncio
async def test_inline_formatting():
    """Test todos with inline formatting."""
    formatting_cases = [
        "- [ ] Task with **bold** text",
        "- [x] Task with *italic* text",
        "- [ ] Task with `code` text",
        "- [x] Task with [link](https://example.com)",
    ]

    for text in formatting_cases:
        assert await TodoElement.markdown_to_notion(text) is not None
        result = await TodoElement.markdown_to_notion(text)
        assert result is not None


@pytest.mark.asyncio
async def test_special_characters():
    """Test with special characters."""
    special_cases = [
        "- [ ] Task with äöü ß",
        "- [x] Task with 😀 emojis",
        "- [ ] Task with symbols !@#$%",
        "- [x] Task with numbers 123",
    ]

    for text in special_cases:
        assert await TodoElement.markdown_to_notion(text) is not None
        result = await TodoElement.markdown_to_notion(text)
        assert result is not None


def test_content_extraction():
    """Test that content is correctly extracted from todo items."""
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


@pytest.mark.asyncio
async def test_roundtrip_conversion():
    """Test that conversion works both ways."""
    original_todos = [
        "- [ ] Unchecked task",
        "- [x] Checked task",
        "* [ ] Star unchecked",
        "+ [X] Plus checked uppercase",
    ]

    for original in original_todos:
        # Markdown -> Notion
        notion_block = await TodoElement.markdown_to_notion(original)
        assert notion_block is not None

        # Create mock block for reverse conversion
        mock_block = Mock()
        mock_block.type = "to_do"
        mock_block.to_do = notion_block.to_do

        # Add mock rich text for conversion
        mock_rich_text = Mock()
        text_content = original.split("] ", 1)[1] if "] " in original else ""
        mock_rich_text.model_dump.return_value = {"text": {"content": text_content}}
        mock_block.to_do.rich_text = [mock_rich_text]

        # Notion -> Markdown
        converted = await TodoElement.notion_to_markdown(mock_block)
        assert converted is not None
        assert "[ ]" in converted or "[x]" in converted


@pytest.mark.asyncio
async def test_edge_cases():
    """Test edge cases."""
    edge_cases = [
        ("- [ ] x", True),  # Single character content
        ("- [x] A", True),  # Single letter
        ("- [ ] 1", True),  # Single digit
    ]

    for text, should_match in edge_cases:
        match_result = await TodoElement.markdown_to_notion(text)
        if should_match:
            assert match_result is not None
        else:
            assert match_result is None

        if should_match:
            result = await TodoElement.markdown_to_notion(text)
            assert result is not None
