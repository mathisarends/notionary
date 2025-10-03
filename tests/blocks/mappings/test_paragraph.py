from unittest.mock import Mock

import pytest

from notionary.blocks.mappings.paragraph import ParagraphElement
from notionary.blocks.schemas import (
    CreateParagraphBlock,
    ParagraphData,
)


@pytest.mark.asyncio
async def test_match_markdown_valid():
    """Test recognition of valid paragraph text."""
    assert await ParagraphElement.markdown_to_notion("Simple text") is not None
    assert await ParagraphElement.markdown_to_notion("Text with **bold** formatting") is not None
    assert await ParagraphElement.markdown_to_notion("Text with [link](https://example.com)")
    assert await ParagraphElement.markdown_to_notion("  Text with leading spaces") is not None
    assert await ParagraphElement.markdown_to_notion("Text with trailing spaces  ") is not None
    assert await ParagraphElement.markdown_to_notion("Multi word paragraph text") is not None


@pytest.mark.asyncio
async def test_match_markdown_invalid():
    """Test rejection of empty or whitespace-only text."""
    assert await ParagraphElement.markdown_to_notion("") is None
    assert await ParagraphElement.markdown_to_notion("   ") is None
    assert await ParagraphElement.markdown_to_notion("\n") is None
    assert await ParagraphElement.markdown_to_notion("\t") is None


def test_match_notion_valid():
    """Test recognition of valid Notion paragraph blocks."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.paragraph = Mock()

    assert ParagraphElement.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Wrong type
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    mock_block.paragraph = Mock()
    assert not ParagraphElement.match_notion(mock_block)

    # None content
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.paragraph = None
    assert not ParagraphElement.match_notion(mock_block)


@pytest.mark.asyncio
async def test_markdown_to_notion():
    """Test conversion from markdown to Notion."""
    result = await ParagraphElement.markdown_to_notion("Test paragraph")

    assert result is not None
    assert isinstance(result, CreateParagraphBlock)
    assert isinstance(result.paragraph, ParagraphData)
    assert result.paragraph.color == "default"
    assert isinstance(result.paragraph.rich_text, list)


@pytest.mark.asyncio
async def test_markdown_to_notion_with_formatting():
    """Test conversion with inline formatting."""
    test_cases = [
        "Text with **bold**",
        "Text with *italic*",
        "Text with `code`",
        "Text with [link](https://example.com)",
        "Mixed **bold** and *italic* text",
    ]

    for text in test_cases:
        result = await ParagraphElement.markdown_to_notion(text)
        assert result is not None
        assert isinstance(result, CreateParagraphBlock)


@pytest.mark.asyncio
async def test_markdown_to_notion_empty():
    """Test that empty text returns None."""
    assert await ParagraphElement.markdown_to_notion("") is None
    assert await ParagraphElement.markdown_to_notion("   ") is None
    assert await ParagraphElement.markdown_to_notion("\n") is None


@pytest.mark.asyncio
async def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Create mock rich text
    mock_rich_text = Mock()
    mock_rich_text.model_dump.return_value = {"text": {"content": "Test content"}}

    # Create mock block
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.paragraph = Mock()
    mock_block.paragraph.rich_text = [mock_rich_text]

    result = await ParagraphElement.notion_to_markdown(mock_block)

    assert result is not None
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "bulleted_list_item"
    assert await ParagraphElement.notion_to_markdown(mock_block) is None

    mock_block.type = "paragraph"
    mock_block.paragraph = None
    assert await ParagraphElement.notion_to_markdown(mock_block) is None


@pytest.mark.asyncio
async def test_accepts_any_text():
    """Test that paragraphs accept any non-empty text."""
    various_texts = [
        "Simple sentence.",
        "Multiple sentences. With periods.",
        "Text with numbers 123 and symbols !@#",
        "Text\nwith\nnewlines",
        "Very long text that spans multiple words and contains various punctuation marks, symbols, and other characters that should all be accepted as valid paragraph content.",
    ]

    for text in various_texts:
        assert await ParagraphElement.markdown_to_notion(text) is not None
        result = await ParagraphElement.markdown_to_notion(text)
        assert result is not None


@pytest.mark.asyncio
async def test_whitespace_handling():
    """Test handling of various whitespace scenarios."""
    # Leading/trailing whitespace should still match
    assert await ParagraphElement.markdown_to_notion("  text  ") is not None
    assert await ParagraphElement.markdown_to_notion("\ttext\t") is not None

    # But should convert successfully
    result = await ParagraphElement.markdown_to_notion("  text  ")
    assert result is not None


@pytest.mark.asyncio
async def test_special_characters():
    """Test with special characters and Unicode."""
    special_cases = [
        "Text with äöü ß",
        "Text with 😀 🎉 emojis",
        "Text with Unicode: ñ é ç",
        "Text with math: π ∑ ∞",
        "Text with symbols: © ® ™",
    ]

    for text in special_cases:
        assert await ParagraphElement.markdown_to_notion(text) is not None
        result = await ParagraphElement.markdown_to_notion(text)
        assert result is not None


@pytest.mark.asyncio
async def test_markdown_formatting_syntax():
    """Test various markdown formatting syntax."""
    formatting_cases = [
        "**Bold text**",
        "*Italic text*",
        "`Inline code`",
        "~~Strikethrough~~",
        "__Underline__",
        "[Link text](https://example.com)",
        "Mixed: **bold** and *italic* and `code`",
        "Text with inline `code` in middle",
    ]

    for text in formatting_cases:
        assert await ParagraphElement.markdown_to_notion(text) is not None
        result = await ParagraphElement.markdown_to_notion(text)
        assert result is not None


@pytest.mark.asyncio
async def test_multiline_text():
    """Test paragraphs with line breaks."""
    multiline_cases = [
        "Line one\nLine two",
        "Line one\n\nLine three",
        "Multiple\nlines\nof\ntext",
    ]

    for text in multiline_cases:
        assert await ParagraphElement.markdown_to_notion(text) is not None
        result = await ParagraphElement.markdown_to_notion(text)
        assert result is not None


@pytest.mark.asyncio
async def test_edge_cases():
    """Test edge cases for paragraph content."""
    edge_cases = [
        "x",  # Single character
        "A",  # Single letter
        "1",  # Single digit
        "!",  # Single symbol
        "  x  ",  # Single char with whitespace
    ]

    for text in edge_cases:
        assert await ParagraphElement.markdown_to_notion(text) is not None
        result = await ParagraphElement.markdown_to_notion(text)
        assert result is not None


@pytest.mark.asyncio
async def test_notion_empty_rich_text():
    """Test handling of empty rich text in Notion blocks."""
    # Mock block with empty rich text
    mock_block = Mock()
    mock_block.type = "paragraph"
    mock_block.paragraph = Mock()
    mock_block.paragraph.rich_text = []

    # Should handle gracefully
    result = await ParagraphElement.notion_to_markdown(mock_block)
    # Result could be None or empty string depending on implementation
    assert result is None or result == ""
