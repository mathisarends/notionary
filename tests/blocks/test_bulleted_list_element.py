"""
Minimal tests for NumberedListElement.
Tests core functionality for numbered list items (1., 2., etc.).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.numbered_list import NumberedListElement
from notionary.blocks.numbered_list.numbered_list_models import (
    CreateNumberedListItemBlock,
    NumberedListItemBlock,
)
from notionary.blocks.rich_text.rich_text_models import RichTextObject


def test_match_markdown_valid():
    """Test recognition of valid numbered list formats."""
    assert NumberedListElement.match_markdown("1. First item")
    assert NumberedListElement.match_markdown("2. Second item")
    assert NumberedListElement.match_markdown("123. Item with big number")
    assert NumberedListElement.match_markdown("  1. Indented item")
    assert NumberedListElement.match_markdown("    10. Deep indented")


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not NumberedListElement.match_markdown("- Bullet item")
    assert not NumberedListElement.match_markdown("* Another bullet")
    assert not NumberedListElement.match_markdown("a. Letter item")
    assert not NumberedListElement.match_markdown("1) Wrong punctuation")
    assert not NumberedListElement.match_markdown("1.")  # No content
    assert not NumberedListElement.match_markdown("Regular text")
    assert not NumberedListElement.match_markdown("")


def test_match_notion():
    """Test recognition of Notion numbered list blocks."""
    # Valid numbered list block
    numbered_block = Mock()
    numbered_block.type = "numbered_list_item"
    numbered_block.numbered_list_item = Mock()  # Not None
    assert NumberedListElement.match_notion(numbered_block)

    # Invalid blocks
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.numbered_list_item = None
    assert not NumberedListElement.match_notion(paragraph_block)

    bullet_block = Mock()
    bullet_block.type = "bulleted_list_item"
    bullet_block.numbered_list_item = None
    assert not NumberedListElement.match_notion(bullet_block)

    # Numbered list type but numbered_list_item is None
    empty_numbered_block = Mock()
    empty_numbered_block.type = "numbered_list_item"
    empty_numbered_block.numbered_list_item = None
    assert not NumberedListElement.match_notion(empty_numbered_block)


def test_markdown_to_notion():
    """Test conversion from markdown to Notion."""
    result = NumberedListElement.markdown_to_notion("1. Buy groceries")

    assert result is not None
    assert isinstance(result, CreateNumberedListItemBlock)
    assert result.type == "numbered_list_item"
    assert isinstance(result.numbered_list_item, NumberedListItemBlock)
    assert result.numbered_list_item.color == "default"
    assert len(result.numbered_list_item.rich_text) > 0
    assert result.numbered_list_item.rich_text[0].plain_text == "Buy groceries"


def test_markdown_to_notion_different_numbers():
    """Test conversion with different starting numbers."""
    test_cases = [
        ("1. First item", "First item"),
        ("5. Fifth item", "Fifth item"),
        ("100. Hundredth item", "Hundredth item"),
    ]

    for markdown, expected_content in test_cases:
        result = NumberedListElement.markdown_to_notion(markdown)
        assert result is not None
        assert result.numbered_list_item.rich_text[0].plain_text == expected_content


def test_markdown_to_notion_with_formatting():
    """Test markdown with inline formatting."""
    result = NumberedListElement.markdown_to_notion("1. **Bold** and *italic* text")

    assert result is not None
    # Should have multiple rich text objects for formatting
    assert len(result.numbered_list_item.rich_text) > 1


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert NumberedListElement.markdown_to_notion("- Bullet item") is None
    assert NumberedListElement.markdown_to_notion("a. Letter item") is None
    assert NumberedListElement.markdown_to_notion("1)") is None
    assert NumberedListElement.markdown_to_notion("text") is None


def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Mock numbered list block
    block = Mock()
    block.type = "numbered_list_item"
    block.numbered_list_item = Mock()

    # Mock rich text with real RichTextObject
    rich_text = RichTextObject.from_plain_text("Test item")
    block.numbered_list_item.rich_text = [rich_text]

    result = NumberedListElement.notion_to_markdown(block)
    assert result == "1. Test item"


def test_notion_to_markdown_normalization():
    """Test that output is always normalized to '1.'."""
    # Create different mock blocks - they should all output "1. content"
    block = Mock()
    block.type = "numbered_list_item"
    block.numbered_list_item = Mock()

    rich_text = RichTextObject.from_plain_text("Same content")
    block.numbered_list_item.rich_text = [rich_text]

    # Always outputs "1." regardless of original number
    result = NumberedListElement.notion_to_markdown(block)
    assert result == "1. Same content"


def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.numbered_list_item = None
    assert NumberedListElement.notion_to_markdown(paragraph_block) is None

    # No numbered_list_item content
    numbered_block = Mock()
    numbered_block.type = "numbered_list_item"
    numbered_block.numbered_list_item = None
    assert NumberedListElement.notion_to_markdown(numbered_block) is None


@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("1. First item", True),
        ("2. Second item", True),
        ("123. Big number", True),
        ("  1. Indented", True),
        ("    10. Deep indent", True),
        ("- Bullet item", False),
        ("* Asterisk bullet", False),
        ("a. Letter item", False),
        ("1) Wrong punct", False),
        ("1.", False),  # No content
        ("Regular text", False),
        ("", False),
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test various markdown patterns."""
    result = NumberedListElement.match_markdown(markdown)
    assert result == should_match


def test_pattern_matching():
    """Test the regex pattern directly."""
    pattern = NumberedListElement.PATTERN

    # Valid patterns
    assert pattern.match("1. Item")
    assert pattern.match("999. High number")
    assert pattern.match("  5. Indented")

    # Invalid patterns
    assert not pattern.match("a. Letter")
    assert not pattern.match("1) Parenthesis")
    assert not pattern.match("1.")  # No content
    assert not pattern.match("- Bullet")


def test_content_extraction():
    """Test that content is properly extracted from pattern."""
    test_cases = [
        ("1. Simple content", "Simple content"),
        ("123. Content with number", "Content with number"),
        ("  5. Indented content", "Indented content"),
        (
            "10. Content with special chars: äöü 🚀",
            "Content with special chars: äöü 🚀",
        ),
    ]

    for markdown, expected_content in test_cases:
        result = NumberedListElement.markdown_to_notion(markdown)
        assert result is not None
        actual_content = result.numbered_list_item.rich_text[0].plain_text
        assert actual_content == expected_content


def test_roundtrip_conversion():
    """Test that markdown -> notion -> markdown preserves content."""
    test_cases = [
        "1. First item",
        "5. Fifth item",
        "100. Hundredth item",
        "1. Item with **bold** text",
    ]

    for original_markdown in test_cases:
        # Convert to notion
        notion_result = NumberedListElement.markdown_to_notion(original_markdown)
        assert notion_result is not None

        # Create mock block for notion_to_markdown
        block = Mock()
        block.type = "numbered_list_item"
        block.numbered_list_item = notion_result.numbered_list_item

        # Convert back to markdown
        result_markdown = NumberedListElement.notion_to_markdown(block)

        # Number is normalized to "1." but content is preserved
        expected_content = original_markdown.split(". ", 1)[1]
        result_content = result_markdown.split(". ", 1)[1]
        assert result_content == expected_content
        assert result_markdown.startswith("1. ")


def test_indentation_levels():
    """Test various indentation levels."""
    indented_items = [
        "1. Level 0",
        "  2. Level 1",
        "    3. Level 2",
        "      10. Level 3",
        "\t5. Tab indented",
    ]

    for item in indented_items:
        assert NumberedListElement.match_markdown(item)
        result = NumberedListElement.markdown_to_notion(item)
        assert result is not None


def test_large_numbers():
    """Test handling of large numbers."""
    large_numbers = [
        "999. Large number",
        "1000. Four digits",
        "12345. Five digits",
    ]

    for item in large_numbers:
        assert NumberedListElement.match_markdown(item)
        result = NumberedListElement.markdown_to_notion(item)
        assert result is not None


def test_with_special_content():
    """Test items with special characters and formatting."""
    special_items = [
        "1. Item with émoji 🚀",
        "2. Chinese text: 这是中文",
        "3. Special chars: !@#$%^&*()",
        "4. URLs: https://example.com",
        "5. Code: `inline code`",
    ]

    for item in special_items:
        result = NumberedListElement.markdown_to_notion(item)
        assert result is not None
        assert result.type == "numbered_list_item"


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = NumberedListElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, "syntax")
    assert "1." in content.syntax
    assert "ordered" in content.syntax.lower() or "numbered" in content.syntax.lower()
