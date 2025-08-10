"""
Minimale Tests für QuoteElement - nur das Wesentliche.
"""

from unittest.mock import Mock

from notionary.blocks.quote.quote_element import QuoteElement
from notionary.blocks.quote.quote_models import QuoteBlock
from notionary.blocks.block_types import BlockType
from notionary.blocks.rich_text.rich_text_models import RichTextObject


def create_rich_text(content: str) -> RichTextObject:
    """Helper to create RichTextObject."""
    return RichTextObject.from_plain_text(content)


def test_match_markdown():
    """Test Markdown pattern matching."""
    # Valid
    assert QuoteElement.markdown_to_notion("[quote](Simple quote text)")
    assert QuoteElement.markdown_to_notion("[quote](Quote with **bold** text)")
    assert QuoteElement.markdown_to_notion("  [quote](Quote with whitespace)  ")

    # Invalid
    assert QuoteElement.markdown_to_notion("> Standard blockquote") is None
    assert not QuoteElement.markdown_to_notion("[quote]()")  # Empty
    assert not QuoteElement.markdown_to_notion("[quote](   )")  # Whitespace only
    assert not QuoteElement.markdown_to_notion("[quote](Multi\nline)")  # Multiline
    assert QuoteElement.markdown_to_notion("Regular text") is None


def test_match_notion():
    """Test Notion block matching."""
    # Valid quote block
    block = Mock()
    block.type = BlockType.QUOTE
    block.quote = Mock()
    assert QuoteElement.match_notion(block)

    # Invalid - wrong type
    block.type = BlockType.PARAGRAPH
    assert not QuoteElement.match_notion(block)

    # Invalid - no quote content
    block.type = BlockType.QUOTE
    block.quote = None
    assert not QuoteElement.match_notion(block)


def test_markdown_to_notion():
    """Test Markdown -> Notion conversion."""
    result = QuoteElement.markdown_to_notion("[quote](Test quote)")

    assert result is not None
    assert result.type == "quote"
    assert result.quote.color == "default"
    assert len(result.quote.rich_text) == 1
    assert result.quote.rich_text[0].plain_text == "Test quote"


def test_markdown_to_notion_with_formatting():
    """Test conversion with inline formatting."""
    test_cases = [
        "[quote](Quote with **bold** text)",
        "[quote](Quote with *italic* text)",
        "[quote](Quote with `code` text)",
    ]

    for text in test_cases:
        result = QuoteElement.markdown_to_notion(text)
        assert result is not None
        assert result.type == "quote"


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    invalid_cases = [
        "> Standard quote",
        "[quote]()",
        "[quote](   )",
        "Regular text",
        "",
        "[quote](Multi\nline)",
    ]

    for text in invalid_cases:
        assert QuoteElement.markdown_to_notion(text) is None


def test_notion_to_markdown():
    """Test Notion -> Markdown conversion."""
    quote_data = QuoteBlock(rich_text=[create_rich_text("Test quote")], color="default")

    block = Mock()
    block.type = BlockType.QUOTE
    block.quote = quote_data

    result = QuoteElement.notion_to_markdown(block)
    assert result == "[quote](Test quote)"


def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    block = Mock()
    block.type = BlockType.PARAGRAPH
    block.quote = None
    assert QuoteElement.notion_to_markdown(block) is None

    # No quote content
    block.type = BlockType.QUOTE
    block.quote = None
    assert QuoteElement.notion_to_markdown(block) is None

    # Empty text
    quote_data = QuoteBlock(rich_text=[create_rich_text("")], color="default")
    block.quote = quote_data
    assert QuoteElement.notion_to_markdown(block) is None


def test_roundtrip():
    """Test roundtrip conversion."""
    test_cases = [
        "[quote](Simple quote)",
        "[quote](Quote with symbols !@#)",
        "[quote](Quote with numbers 123)",
    ]

    for original in test_cases:
        # Markdown -> Notion
        notion_result = QuoteElement.markdown_to_notion(original)
        assert notion_result is not None

        # Create block for notion_to_markdown
        block = Mock()
        block.type = BlockType.QUOTE
        block.quote = notion_result.quote

        # Notion -> Markdown
        result = QuoteElement.notion_to_markdown(block)
        assert result == original


def test_pattern_regex():
    """Test regex pattern directly."""
    pattern = QuoteElement.PATTERN

    # Valid
    assert pattern.match("[quote](Simple text)")
    assert pattern.match("[quote](Text with spaces)")

    # Invalid
    assert not pattern.match("[quote]()")
    assert not pattern.match("[quote](Multi\nline)")
    assert not pattern.match("> Standard quote")


def test_special_characters():
    """Test with special characters."""
    special_cases = [
        "[quote](Quote with äöü ß)",
        "[quote](Quote with 😀 emojis)",
        "[quote](Quote with symbols: !@#$%)",
        "[quote](Quote with punctuation: .?!)",
    ]

    for text in special_cases:
        assert QuoteElement.markdown_to_notion(text) is not None
        result = QuoteElement.markdown_to_notion(text)
        assert result is not None


def test_whitespace_handling():
    """Test whitespace handling."""
    # Content whitespace should be stripped
    result = QuoteElement.markdown_to_notion("[quote](  text with spaces  )")
    assert result is not None
    assert result.quote.rich_text[0].plain_text == "text with spaces"

    # Whitespace around quote should be handled
    assert QuoteElement.markdown_to_notion("  [quote](text)  ")


def test_empty_content_edge_cases():
    """Test edge cases with empty content."""
    empty_cases = [
        "[quote]()",
        "[quote](   )",
        "[quote](\t)",
        "[quote](\n)",
    ]

    for text in empty_cases:
        assert QuoteElement.markdown_to_notion(text) is None
        assert QuoteElement.markdown_to_notion(text) is None


def test_multiline_not_supported():
    """Test that multiline quotes are rejected."""
    multiline_cases = [
        "[quote](Line one\nLine two)",
        "[quote](Line one\rLine two)",
        "[quote](Line one\r\nLine two)",
    ]

    for text in multiline_cases:
        assert QuoteElement.markdown_to_notion(text) is None
        assert QuoteElement.markdown_to_notion(text) is None
