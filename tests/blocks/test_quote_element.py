"""
Minimale Tests für QuoteElement - nur das Wesentliche.
"""

from unittest.mock import Mock

import pytest

from notionary.blocks.quote.quote_element import QuoteElement
from notionary.blocks.quote.quote_models import QuoteBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.types import BlockType


def create_rich_text(content: str) -> RichTextObject:
    """Helper to create RichTextObject."""
    return RichTextObject.from_plain_text(content)


@pytest.mark.asyncio
async def test_match_markdown():
    """Test Markdown pattern matching."""
    # Valid
    assert await QuoteElement.markdown_to_notion("> Simple quote text")
    assert await QuoteElement.markdown_to_notion("> Quote with **bold** text")
    assert await QuoteElement.markdown_to_notion(">Quote with no space")
    assert await QuoteElement.markdown_to_notion(">   Quote with multiple spaces")

    # Invalid
    assert await QuoteElement.markdown_to_notion("[quote](Old syntax)") is None
    assert not await QuoteElement.markdown_to_notion(">")  # Empty
    assert not await QuoteElement.markdown_to_notion("> ")  # Whitespace only
    assert not await QuoteElement.markdown_to_notion(
        "> Multi\nline"
    )  # Multiline
    assert await QuoteElement.markdown_to_notion("Regular text") is None


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


@pytest.mark.asyncio
async def test_markdown_to_notion():
    """Test Markdown -> Notion conversion."""
    result = await QuoteElement.markdown_to_notion("> Test quote")

    assert result is not None
    assert result.type == "quote"
    assert result.quote.color == "default"
    assert len(result.quote.rich_text) == 1
    assert result.quote.rich_text[0].plain_text == "Test quote"


@pytest.mark.asyncio
async def test_markdown_to_notion_with_formatting():
    """Test conversion with inline formatting."""
    test_cases = [
        "> Quote with **bold** text",
        "> Quote with *italic* text",
        "> Quote with `code` text",
    ]

    for text in test_cases:
        result = await QuoteElement.markdown_to_notion(text)
        assert result is not None
        assert result.type == "quote"


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    invalid_cases = [
        "[quote](Old syntax)",
        ">",
        "> ",
        "Regular text",
        "",
        "> Multi\nline",
    ]

    for text in invalid_cases:
        assert await QuoteElement.markdown_to_notion(text) is None


@pytest.mark.asyncio
async def test_notion_to_markdown():
    """Test Notion -> Markdown conversion."""
    quote_data = QuoteBlock(rich_text=[create_rich_text("Test quote")], color="default")

    block = Mock()
    block.type = BlockType.QUOTE
    block.quote = quote_data

    result = await QuoteElement.notion_to_markdown(block)
    assert result == "> Test quote"


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    block = Mock()
    block.type = BlockType.PARAGRAPH
    block.quote = None
    assert await QuoteElement.notion_to_markdown(block) is None

    # No quote content
    block.type = BlockType.QUOTE
    block.quote = None
    assert await QuoteElement.notion_to_markdown(block) is None

    # Empty text
    quote_data = QuoteBlock(rich_text=[create_rich_text("")], color="default")
    block.quote = quote_data
    assert await QuoteElement.notion_to_markdown(block) is None


@pytest.mark.asyncio
async def test_roundtrip():
    """Test roundtrip conversion."""
    test_cases = [
        "> Simple quote",
        "> Quote with symbols !@#",
        "> Quote with numbers 123",
    ]

    for original in test_cases:
        # Markdown -> Notion
        notion_result = await QuoteElement.markdown_to_notion(original)
        assert notion_result is not None

        # Create block for notion_to_markdown
        block = Mock()
        block.type = BlockType.QUOTE
        block.quote = notion_result.quote

        # Notion -> Markdown
        result = await QuoteElement.notion_to_markdown(block)
        assert result == original


def test_pattern_regex():
    """Test regex pattern directly."""
    pattern = QuoteElement.PATTERN

    # Valid
    assert pattern.match("> Simple text")
    assert pattern.match("> Text with spaces")
    assert pattern.match(">Text without space")

    # Invalid
    assert not pattern.match(">")
    assert not pattern.match("> Multi\nline")
    assert not pattern.match("[quote](Old syntax)")


@pytest.mark.asyncio
async def test_special_characters():
    """Test with special characters."""
    special_cases = [
        "> Quote with äöü ß",
        "> Quote with 😀 emojis",
        "> Quote with symbols: !@#$%",
        "> Quote with punctuation: .?!",
    ]

    for text in special_cases:
        assert await QuoteElement.markdown_to_notion(text) is not None
        result = await QuoteElement.markdown_to_notion(text)
        assert result is not None


@pytest.mark.asyncio
async def test_whitespace_handling():
    """Test whitespace handling."""
    # Content whitespace should be stripped
    result = await QuoteElement.markdown_to_notion(">  text with spaces  ")
    assert result is not None
    assert result.quote.rich_text[0].plain_text == "text with spaces"

    # Different spacing after >
    assert await QuoteElement.markdown_to_notion("> text")
    assert await QuoteElement.markdown_to_notion(">text")
    assert await QuoteElement.markdown_to_notion(">  text")


@pytest.mark.asyncio
async def test_empty_content_edge_cases():
    """Test edge cases with empty content."""
    empty_cases = [
        ">",
        "> ",
        ">\t",
        ">\n",
    ]

    for text in empty_cases:
        assert await QuoteElement.markdown_to_notion(text) is None


@pytest.mark.asyncio
async def test_multiline_not_supported():
    """Test that multiline quotes are rejected."""
    multiline_cases = [
        "> Line one\nLine two",
        "> Line one\rLine two", 
        "> Line one\r\nLine two",
    ]

    for text in multiline_cases:
        assert await QuoteElement.markdown_to_notion(text) is None
