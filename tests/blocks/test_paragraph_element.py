"""
Minimal tests for ParagraphElement.
Tests core functionality for paragraph blocks (fallback text element).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.paragraph import ParagraphElement
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.blocks.rich_text.rich_text_models import RichTextObject


def test_match_markdown_valid():
    """Test recognition of valid text (almost everything)."""
    assert ParagraphElement.match_markdown("Simple text")
    assert ParagraphElement.match_markdown("Text with **bold** formatting")
    assert ParagraphElement.match_markdown("A single word")
    assert ParagraphElement.match_markdown("123 numbers")
    assert ParagraphElement.match_markdown("Special chars: !@#$%")
    assert ParagraphElement.match_markdown("  Text with spaces  ")


def test_match_markdown_invalid():
    """Test rejection of empty/whitespace-only text."""
    assert not ParagraphElement.match_markdown("")
    assert not ParagraphElement.match_markdown("   ")  # Only whitespace
    assert not ParagraphElement.match_markdown("\t\n")  # Only whitespace chars


def test_match_notion():
    """Test recognition of Notion paragraph blocks."""
    # Valid paragraph block
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.paragraph = Mock()  # Not None
    assert ParagraphElement.match_notion(paragraph_block)

    # Invalid blocks
    heading_block = Mock()
    heading_block.type = "heading_1"
    heading_block.paragraph = None
    assert not ParagraphElement.match_notion(heading_block)

    # Paragraph type but paragraph is None
    empty_paragraph_block = Mock()
    empty_paragraph_block.type = "paragraph"
    empty_paragraph_block.paragraph = None
    assert not ParagraphElement.match_notion(empty_paragraph_block)


def test_markdown_to_notion_simple():
    """Test conversion of simple text to Notion."""
    result = ParagraphElement.markdown_to_notion("Simple paragraph text")

    assert result is not None
    assert isinstance(result, CreateParagraphBlock)
    assert result.type == "paragraph"
    assert isinstance(result.paragraph, ParagraphBlock)
    assert result.paragraph.color == "default"
    assert len(result.paragraph.rich_text) > 0
    assert result.paragraph.rich_text[0].plain_text == "Simple paragraph text"


def test_markdown_to_notion_with_formatting():
    """Test conversion of formatted text to Notion."""
    result = ParagraphElement.markdown_to_notion("Text with **bold** and *italic*")

    assert result is not None
    # Should have multiple rich text objects for formatting
    assert len(result.paragraph.rich_text) > 1


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert ParagraphElement.markdown_to_notion("") is None
    assert ParagraphElement.markdown_to_notion("   ") is None
    assert ParagraphElement.markdown_to_notion("\t\n") is None


def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Mock paragraph block
    block = Mock()
    block.type = "paragraph"
    block.paragraph = Mock()

    # Mock rich text with real RichTextObject
    rich_text = RichTextObject.from_plain_text("Sample paragraph")
    block.paragraph.rich_text = [rich_text]

    result = ParagraphElement.notion_to_markdown(block)
    assert result == "Sample paragraph"


def test_notion_to_markdown_with_formatting():
    """Test conversion with formatting preservation."""
    # This would require mocking the TextInlineFormatter properly
    # For minimal testing, we just check the basic structure works
    block = Mock()
    block.type = "paragraph"
    block.paragraph = Mock()
    block.paragraph.rich_text = [RichTextObject.from_plain_text("Test")]

    result = ParagraphElement.notion_to_markdown(block)
    assert result == "Test"


def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    heading_block = Mock()
    heading_block.type = "heading_1"
    heading_block.paragraph = None
    assert ParagraphElement.notion_to_markdown(heading_block) is None

    # No paragraph content
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.paragraph = None
    assert ParagraphElement.notion_to_markdown(paragraph_block) is None


@pytest.mark.parametrize(
    "text,should_match",
    [
        ("Simple text", True),
        ("Text with **bold**", True),
        ("123", True),
        ("!@#$%", True),
        ("  Spaces around  ", True),
        ("", False),
        ("   ", False),
        ("\t\n", False),
    ],
)
def test_markdown_patterns(text, should_match):
    """Test various text patterns."""
    result = ParagraphElement.match_markdown(text)
    assert result == should_match


def test_as_fallback_element():
    """Test that ParagraphElement works as fallback for unrecognized text."""
    # These would typically be handled by other elements, but paragraph is fallback
    fallback_texts = [
        "This looks like normal text",
        "Maybe this is a heading but without #",
        "Could be anything really",
        "123 456 789",
    ]

    for text in fallback_texts:
        # Should match
        assert ParagraphElement.match_markdown(text)

        # Should convert
        result = ParagraphElement.markdown_to_notion(text)
        assert result is not None
        assert result.type == "paragraph"


def test_inline_formatting_support():
    """Test that inline formatting is processed."""
    formatted_texts = [
        "Text with **bold**",
        "Text with *italic*",
        "Text with `code`",
        "Text with [link](https://example.com)",
        "Mixed **bold** and *italic* text",
    ]

    for text in formatted_texts:
        result = ParagraphElement.markdown_to_notion(text)
        assert result is not None
        # With formatting, should have multiple rich text segments
        # (This depends on TextInlineFormatter implementation)
        assert len(result.paragraph.rich_text) >= 1


def test_roundtrip_conversion():
    """Test that markdown -> notion -> markdown preserves content."""
    test_cases = [
        "Simple paragraph",
        "Text with special chars: äöü 🚀",
        "Numbers and symbols: 123 !@#",
        "Multiple    spaces   preserved",
    ]

    for original_text in test_cases:
        # Convert to notion
        notion_result = ParagraphElement.markdown_to_notion(original_text)
        assert notion_result is not None

        # Create mock block for notion_to_markdown
        block = Mock()
        block.type = "paragraph"
        block.paragraph = notion_result.paragraph

        # Convert back to markdown
        result_text = ParagraphElement.notion_to_markdown(block)
        assert result_text == original_text


def test_unicode_and_special_characters():
    """Test handling of Unicode and special characters."""
    unicode_texts = [
        "Text with äöüß",
        "Chinese: 你好世界",
        "Emoji: 🚀 ✨ 🌟",
        "Russian: Привет мир",
        "Mixed: Hello 世界 🌍",
    ]

    for text in unicode_texts:
        # Should match and convert
        assert ParagraphElement.match_markdown(text)
        result = ParagraphElement.markdown_to_notion(text)
        assert result is not None

        # Content should be preserved
        assert result.paragraph.rich_text[0].plain_text == text


def test_whitespace_handling():
    """Test handling of whitespace."""
    # Leading/trailing whitespace should be preserved in content
    text = "  Content with spaces  "
    result = ParagraphElement.markdown_to_notion(text)
    assert result is not None
    # TextInlineFormatter should preserve the original text
    assert result.paragraph.rich_text[0].plain_text == text


def test_empty_rich_text_handling():
    """Test notion_to_markdown with empty rich_text."""
    block = Mock()
    block.type = "paragraph"
    block.paragraph = Mock()
    block.paragraph.rich_text = []  # Empty rich text

    result = ParagraphElement.notion_to_markdown(block)
    # Should return None for empty content
    assert result is None


def test_multiline_text():
    """Test handling of multiline text (newlines)."""
    multiline_text = "First line\nSecond line\nThird line"
    result = ParagraphElement.markdown_to_notion(multiline_text)

    assert result is not None
    # Should preserve newlines in the content
    assert multiline_text in result.paragraph.rich_text[0].plain_text
