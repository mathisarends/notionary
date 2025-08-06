"""
Minimal tests for TodoElement.
Tests core functionality for todo items (- [ ], - [x]).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.todo import TodoElement
from notionary.blocks.todo.todo_models import CreateToDoBlock, ToDoBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject


def test_match_markdown_valid():
    """Test recognition of valid todo formats."""
    # Unchecked todos
    assert TodoElement.match_markdown("- [ ] Buy groceries")
    assert TodoElement.match_markdown("* [ ] Call dentist")
    assert TodoElement.match_markdown("+ [ ] Write report")
    assert TodoElement.match_markdown("  - [ ] Indented todo")

    # Checked todos
    assert TodoElement.match_markdown("- [x] Task completed")
    assert TodoElement.match_markdown("* [X] Also completed")  # Case insensitive
    assert TodoElement.match_markdown("+ [x] Done item")


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not TodoElement.match_markdown("- Regular list item")
    assert not TodoElement.match_markdown("[ ] Not a todo")  # Missing marker
    assert not TodoElement.match_markdown("- [o] Invalid checkbox")
    assert not TodoElement.match_markdown("- [ ]")  # No content
    assert not TodoElement.match_markdown("Regular text")
    assert not TodoElement.match_markdown("")


def test_match_notion():
    """Test recognition of Notion to_do blocks."""
    # Valid todo block
    todo_block = Mock()
    todo_block.type = "to_do"
    todo_block.to_do = Mock()  # Not None
    assert TodoElement.match_notion(todo_block)

    # Invalid blocks
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.to_do = None
    assert not TodoElement.match_notion(paragraph_block)

    # Todo type but to_do is None
    empty_todo_block = Mock()
    empty_todo_block.type = "to_do"
    empty_todo_block.to_do = None
    assert not TodoElement.match_notion(empty_todo_block)


def test_markdown_to_notion_unchecked():
    """Test conversion of unchecked todo to Notion."""
    result = TodoElement.markdown_to_notion("- [ ] Buy groceries")

    assert result is not None
    assert isinstance(result, CreateToDoBlock)
    assert result.type == "to_do"
    assert isinstance(result.to_do, ToDoBlock)
    assert result.to_do.checked is False
    assert result.to_do.color == "default"
    assert len(result.to_do.rich_text) > 0
    assert result.to_do.rich_text[0].plain_text == "Buy groceries"


def test_markdown_to_notion_checked():
    """Test conversion of checked todo to Notion."""
    result = TodoElement.markdown_to_notion("- [x] Task completed")

    assert result is not None
    assert result.to_do.checked is True
    assert result.to_do.rich_text[0].plain_text == "Task completed"


def test_markdown_to_notion_different_markers():
    """Test different todo markers (-, *, +)."""
    markers = [
        ("- [ ] Dash todo", False),
        ("* [x] Asterisk todo", True),
        ("+ [ ] Plus todo", False),
    ]

    for markdown, expected_checked in markers:
        result = TodoElement.markdown_to_notion(markdown)
        assert result is not None
        assert result.to_do.checked is expected_checked


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert TodoElement.markdown_to_notion("- Regular list") is None
    assert TodoElement.markdown_to_notion("[ ] No marker") is None
    assert TodoElement.markdown_to_notion("- [o] Invalid") is None
    assert TodoElement.markdown_to_notion("text") is None


def test_notion_to_markdown_unchecked():
    """Test conversion from Notion unchecked todo to markdown."""
    # Mock unchecked todo block
    block = Mock()
    block.type = "to_do"
    block.to_do = Mock()
    block.to_do.checked = False

    # Mock rich text with real RichTextObject
    rich_text = RichTextObject.from_plain_text("Buy milk")
    block.to_do.rich_text = [rich_text]

    result = TodoElement.notion_to_markdown(block)
    assert result == "- [ ] Buy milk"


def test_notion_to_markdown_checked():
    """Test conversion from Notion checked todo to markdown."""
    # Mock checked todo block
    block = Mock()
    block.type = "to_do"
    block.to_do = Mock()
    block.to_do.checked = True

    # Mock rich text with real RichTextObject
    rich_text = RichTextObject.from_plain_text("Task done")
    block.to_do.rich_text = [rich_text]

    result = TodoElement.notion_to_markdown(block)
    assert result == "- [x] Task done"


def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.to_do = None
    assert TodoElement.notion_to_markdown(paragraph_block) is None

    # No to_do content
    todo_block = Mock()
    todo_block.type = "to_do"
    todo_block.to_do = None
    assert TodoElement.notion_to_markdown(todo_block) is None


@pytest.mark.parametrize(
    "markdown,should_match,expected_checked",
    [
        ("- [ ] Unchecked", True, False),
        ("* [ ] Also unchecked", True, False),
        ("+ [ ] Plus unchecked", True, False),
        ("- [x] Checked", True, True),
        ("* [X] Also checked", True, True),  # Case insensitive
        ("+ [x] Plus checked", True, True),
        ("  - [ ] Indented", True, False),
        ("- Regular list", False, None),
        ("[ ] No marker", False, None),
        ("- [o] Invalid", False, None),
        ("", False, None),
    ],
)
def test_markdown_patterns(markdown, should_match, expected_checked):
    """Test various markdown patterns."""
    # Test matching
    result = TodoElement.match_markdown(markdown)
    assert result == should_match

    # Test conversion if it should match
    if should_match:
        notion_result = TodoElement.markdown_to_notion(markdown)
        assert notion_result is not None
        assert notion_result.to_do.checked == expected_checked


def test_case_insensitive_checkbox():
    """Test that [X] and [x] both work for checked todos."""
    test_cases = [
        "- [x] Lower case",
        "- [X] Upper case",
        "* [x] Asterisk lower",
        "* [X] Asterisk upper",
    ]

    for markdown in test_cases:
        result = TodoElement.markdown_to_notion(markdown)
        assert result is not None
        assert result.to_do.checked is True


def test_pattern_matching():
    """Test the regex patterns directly."""
    # Test PATTERN (unchecked)
    assert TodoElement.PATTERN.match("- [ ] Test")
    assert TodoElement.PATTERN.match("* [ ] Test")
    assert TodoElement.PATTERN.match("+ [ ] Test")
    assert not TodoElement.PATTERN.match("- [x] Test")  # Wrong pattern

    # Test DONE_PATTERN (checked)
    assert TodoElement.DONE_PATTERN.match("- [x] Done")
    assert TodoElement.DONE_PATTERN.match("* [X] Done")  # Case insensitive
    assert TodoElement.DONE_PATTERN.match("+ [x] Done")
    assert not TodoElement.DONE_PATTERN.match("- [ ] Test")  # Wrong pattern


def test_roundtrip_conversion():
    """Test that markdown -> notion -> markdown preserves content."""
    test_cases = [
        "- [ ] Buy groceries",
        "- [x] Task completed",
        "* [ ] Call dentist",
        "* [x] Email sent",
        "+ [ ] Write report",
        "+ [x] Report done",
    ]

    for original_markdown in test_cases:
        # Convert to notion
        notion_result = TodoElement.markdown_to_notion(original_markdown)
        assert notion_result is not None

        # Create mock block for notion_to_markdown
        block = Mock()
        block.type = "to_do"
        block.to_do = notion_result.to_do

        # Convert back to markdown
        result_markdown = TodoElement.notion_to_markdown(block)

        # Should preserve checked state and content, but normalize to "-" marker
        if "[x]" in original_markdown.lower():
            assert result_markdown.startswith("- [x] ")
        else:
            assert result_markdown.startswith("- [ ] ")

        # Content should be preserved
        original_content = original_markdown.split("] ", 1)[1]
        result_content = result_markdown.split("] ", 1)[1]
        assert result_content == original_content


def test_with_formatting():
    """Test todos with inline formatting."""
    markdown = "- [ ] Remember to **buy** *groceries*"
    result = TodoElement.markdown_to_notion(markdown)

    assert result is not None
    # Should have multiple rich text objects for formatting
    assert len(result.to_do.rich_text) > 1


def test_content_with_special_characters():
    """Test content with special characters."""
    special_todos = [
        "- [ ] Buy milk & eggs",
        "- [x] Send email @ 5pm",
        "- [ ] Review code: main.py",
        "- [x] Task with emoji 🚀",
        "- [ ] Unicode: äöü",
    ]

    for todo in special_todos:
        result = TodoElement.markdown_to_notion(todo)
        assert result is not None
        assert result.type == "to_do"


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = TodoElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, "syntax")
    assert "[ ]" in content.syntax
    assert "[x]" in content.syntax or "checkbox" in content.syntax.lower()
