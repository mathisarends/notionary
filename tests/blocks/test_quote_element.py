"""
Minimal tests for QuoteElement.
Tests core functionality for quote blocks with [quote](text) syntax.
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.quote.quote_element import QuoteElement
from notionary.blocks.quote.quote_models import (
    CreateQuoteBlock,
    QuoteBlock,
)


def test_match_markdown_valid():
    """Test recognition of valid quote formats."""
    assert QuoteElement.match_markdown("[quote](Simple quote text)")
    assert QuoteElement.match_markdown("[quote](Quote with **bold** text)")
    assert QuoteElement.match_markdown("[quote](Knowledge is power)")
    assert QuoteElement.match_markdown("  [quote](Quote with whitespace)  ")
    assert QuoteElement.match_markdown("[quote](Quote with symbols !@#)")


def test_match_markdown_invalid():
    """Test rejection of invalid quote formats."""
    # Standard markdown quotes should not match
    assert not QuoteElement.match_markdown("> Standard blockquote")
    assert not QuoteElement.match_markdown("> Another blockquote")

    # Invalid custom format
    assert not QuoteElement.match_markdown("[quote]Missing parentheses")
    assert not QuoteElement.match_markdown("quote(Missing brackets)")
    assert not QuoteElement.match_markdown("[quote]()")  # Empty content
    assert not QuoteElement.match_markdown("[quote](   )")  # Whitespace only
    assert not QuoteElement.match_markdown("[quote](Multi\nline)")  # Multiline
    assert not QuoteElement.match_markdown("")
    assert not QuoteElement.match_markdown("Regular text")


def test_match_notion_valid():
    """Test recognition of valid Notion quote blocks."""
    mock_block = Mock()
    mock_block.type = "quote"
    mock_block.quote = Mock()

    assert QuoteElement.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Wrong type
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.quote = Mock()
    assert not QuoteElement.match_notion(mock_block)

    # None content
    mock_block = Mock()
    mock_block.type = "quote"
    mock_block.quote = None
    assert not QuoteElement.match_notion(mock_block)


def test_markdown_to_notion():
    """Test conversion from markdown to Notion."""
    result = QuoteElement.markdown_to_notion("[quote](Test quote)")

    assert result is not None
    assert isinstance(result, CreateQuoteBlock)
    assert isinstance(result.quote, QuoteBlock)
    assert result.quote.color == "default"
    assert isinstance(result.quote.rich_text, list)


def test_markdown_to_notion_with_formatting():
    """Test conversion with inline formatting."""
    test_cases = [
        "[quote](Quote with **bold** text)",
        "[quote](Quote with *italic* text)",
        "[quote](Quote with `code` text)",
        "[quote](Quote with [link](https://example.com))",
    ]

    for text in test_cases:
        result = QuoteElement.markdown_to_notion(text)
        assert result is not None
        assert isinstance(result, CreateQuoteBlock)


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert QuoteElement.markdown_to_notion("> Standard quote") is None
    assert QuoteElement.markdown_to_notion("[quote]()") is None
    assert QuoteElement.markdown_to_notion("[quote](   )") is None
    assert QuoteElement.markdown_to_notion("Regular text") is None
    assert QuoteElement.markdown_to_notion("") is None


def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Create mock rich text
    mock_rich_text = Mock()
    mock_rich_text.model_dump.return_value = {"text": {"content": "Test quote"}}

    # Create mock block
    mock_block = Mock()
    mock_block.type = "quote"
    mock_block.quote = Mock()
    mock_block.quote.rich_text = [mock_rich_text]

    result = QuoteElement.notion_to_markdown(mock_block)

    assert result is not None
    assert result.startswith("[quote](")
    assert result.endswith(")")


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    assert QuoteElement.notion_to_markdown(mock_block) is None

    mock_block.type = "quote"
    mock_block.quote = None
    assert QuoteElement.notion_to_markdown(mock_block) is None


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    result = QuoteElement.get_llm_prompt_content()
    assert result is not None


def test_pattern_regex_directly():
    """Test the PATTERN regex directly."""
    pattern = QuoteElement.PATTERN

    # Valid patterns
    assert pattern.match("[quote](Simple text)")
    assert pattern.match("[quote](Text with spaces)")

    # Invalid patterns
    assert not pattern.match("[quote]()")
    assert not pattern.match("[quote](Multi\nline)")
    assert not pattern.match("> Standard quote")
    assert not pattern.match("[quote]Missing parens")

def test_whitespace_handling():
    """Test handling of whitespace."""
    # Leading/trailing whitespace in quote content should be stripped
    result = QuoteElement.markdown_to_notion("[quote](  text with spaces  )")
    assert result is not None

    # Whitespace around the entire quote should be handled
    assert QuoteElement.match_markdown("  [quote](text)  ")


def test_special_characters():
    """Test with special characters."""
    special_cases = [
        "[quote](Quote with äöü ß)",
        "[quote](Quote with 😀 emojis)",
        "[quote](Quote with symbols: !@#$%)",
        "[quote](Quote with punctuation: .?!)",
        "[quote](Quote with numbers: 123)",
    ]

    for text in special_cases:
        assert QuoteElement.match_markdown(text)
        result = QuoteElement.markdown_to_notion(text)
        assert result is not None


def test_empty_content_handling():
    """Test handling of empty or whitespace-only content."""
    empty_cases = [
        "[quote]()",
        "[quote](   )",
        "[quote](\t)",
        "[quote](\n)",
    ]

    for text in empty_cases:
        assert not QuoteElement.match_markdown(text)
        result = QuoteElement.markdown_to_notion(text)
        assert result is None


def test_roundtrip_conversion():
    """Test that conversion works both ways."""
    original_quotes = [
        "[quote](Simple quote)",
        "[quote](Quote with symbols !@#)",
        "[quote](Quote with numbers 123)",
    ]

    for original in original_quotes:
        # Markdown -> Notion
        notion_block = QuoteElement.markdown_to_notion(original)
        assert notion_block is not None

        # Create mock block for reverse conversion
        mock_block = Mock()
        mock_block.type = "quote"
        mock_block.quote = notion_block.quote

        # Notion -> Markdown
        converted = QuoteElement.notion_to_markdown(mock_block)
        assert converted is not None
        assert converted.startswith("[quote](")
        assert converted.endswith(")")


def test_no_multiline_support():
    """Test that multiline quotes are not supported."""
    multiline_cases = [
        "[quote](Line one\nLine two)",
        "[quote](Line one\rLine two)",
        "[quote](Line one\r\nLine two)",
    ]

    for text in multiline_cases:
        assert not QuoteElement.match_markdown(text)
        result = QuoteElement.markdown_to_notion(text)
        assert result is None
