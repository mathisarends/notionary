"""
Minimal tests for QuoteElement.
Tests core functionality for custom quote syntax ([quote](text)).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.quote import QuoteElement
from notionary.blocks.quote.quote_models import CreateQuoteBlock, QuoteBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject


def test_match_markdown_valid():
    """Test recognition of valid quote formats."""
    assert QuoteElement.match_markdown("[quote](Simple quote)")
    assert QuoteElement.match_markdown("[quote](Quote with **bold** text)")
    assert QuoteElement.match_markdown("[quote](Knowledge is power)")
    assert QuoteElement.match_markdown("  [quote](Quote with spaces)  ")


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not QuoteElement.match_markdown("> Standard blockquote")
    assert not QuoteElement.match_markdown("[quote]()")  # Empty content
    assert not QuoteElement.match_markdown("[quote]( )")  # Only whitespace
    assert not QuoteElement.match_markdown("[quote](Multi\nline)")  # Multiline
    assert not QuoteElement.match_markdown("[quote](Multi\rline)")  # Carriage return
    assert not QuoteElement.match_markdown("Regular text")
    assert not QuoteElement.match_markdown("")


def test_match_notion():
    """Test recognition of Notion quote blocks."""
    # Valid quote block
    quote_block = Mock()
    quote_block.type = "quote"
    quote_block.quote = Mock()  # Not None
    assert QuoteElement.match_notion(quote_block)

    # Invalid blocks
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.quote = None
    assert not QuoteElement.match_notion(paragraph_block)

    # Quote type but quote is None
    empty_quote_block = Mock()
    empty_quote_block.type = "quote"
    empty_quote_block.quote = None
    assert not QuoteElement.match_notion(empty_quote_block)


def test_markdown_to_notion():
    """Test conversion from markdown to Notion."""
    result = QuoteElement.markdown_to_notion("[quote](This is a quote)")
    
    assert result is not None
    assert isinstance(result, CreateQuoteBlock)
    assert result.type == "quote"
    assert isinstance(result.quote, QuoteBlock)
    assert result.quote.color == "default"
    assert len(result.quote.rich_text) > 0
    assert result.quote.rich_text[0].plain_text == "This is a quote"


def test_markdown_to_notion_with_formatting():
    """Test conversion with inline formatting."""
    result = QuoteElement.markdown_to_notion("[quote](Quote with **bold** text)")
    
    assert result is not None
    # Should have multiple rich text objects for formatting
    assert len(result.quote.rich_text) > 1


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert QuoteElement.markdown_to_notion("[quote]()") is None
    assert QuoteElement.markdown_to_notion("[quote]( )") is None
    assert QuoteElement.markdown_to_notion("> Standard quote") is None
    assert QuoteElement.markdown_to_notion("text") is None


def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Mock quote block
    block = Mock()
    block.type = "quote"
    block.quote = Mock()
    
    # Mock rich text with real RichTextObject
    rich_text = RichTextObject.from_plain_text("Sample quote")
    block.quote.rich_text = [rich_text]
    
    result = QuoteElement.notion_to_markdown(block)
    assert result == "[quote](Sample quote)"


def test_notion_to_markdown_with_whitespace():
    """Test conversion strips whitespace properly."""
    # Mock quote block with whitespace
    block = Mock()
    block.type = "quote"
    block.quote = Mock()
    
    rich_text = RichTextObject.from_plain_text("  Quote with spaces  ")
    block.quote.rich_text = [rich_text]
    
    result = QuoteElement.notion_to_markdown(block)
    assert result == "[quote](Quote with spaces)"  # Stripped


def test_notion_to_markdown_invalid():
    """Test invalid Notion blocks return None."""
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.quote = None
    assert QuoteElement.notion_to_markdown(paragraph_block) is None
    
    # No quote content
    quote_block = Mock()
    quote_block.type = "quote"
    quote_block.quote = None
    assert QuoteElement.notion_to_markdown(quote_block) is None
    
    # Empty rich text
    empty_block = Mock()
    empty_block.type = "quote"
    empty_block.quote = Mock()
    empty_block.quote.rich_text = [RichTextObject.from_plain_text("   ")]  # Only whitespace
    assert QuoteElement.notion_to_markdown(empty_block) is None


def test_find_matches():
    """Test finding multiple quotes in text."""
    text = (
        "Introduction text\n\n"
        "[quote](First quote)\n\n"
        "Some more text\n\n"
        "[quote](Second quote with **bold**)\n\n"
        "Conclusion"
    )
    
    matches = QuoteElement.find_matches(text)
    assert len(matches) == 2
    
    # Check first match
    start1, end1, block1 = matches[0]
    assert text[start1:end1] == "[quote](First quote)"
    assert isinstance(block1, CreateQuoteBlock)
    
    # Check second match  
    start2, end2, block2 = matches[1]
    assert text[start2:end2] == "[quote](Second quote with **bold**)"
    assert isinstance(block2, CreateQuoteBlock)


def test_find_matches_empty():
    """Test find_matches with no quotes."""
    text = "Just regular text without any quotes here."
    matches = QuoteElement.find_matches(text)
    assert matches == []


@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("[quote](Simple quote)", True),
        ("[quote](Quote with **bold**)", True),
        ("[quote](Knowledge is power)", True),
        ("  [quote](With spaces)  ", True),
        ("[quote]()", False),  # Empty
        ("[quote]( )", False),  # Only whitespace
        ("[quote](Multi\nline)", False),  # Multiline
        ("> Standard blockquote", False),
        ("Regular text", False),
        ("", False),
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test various markdown patterns."""
    result = QuoteElement.match_markdown(markdown)
    assert result == should_match


def test_pattern_matching():
    """Test the regex pattern directly."""
    pattern = QuoteElement.PATTERN
    
    # Valid patterns
    assert pattern.match("[quote](Simple text)")
    assert pattern.match("[quote](Text with symbols !@#)")
    
    # Invalid patterns
    assert not pattern.match("[quote]()")
    assert not pattern.match("[quote](Multi\nline)")
    assert not pattern.match("> Standard quote")


def test_roundtrip_conversion():
    """Test that markdown -> notion -> markdown preserves content."""
    test_cases = [
        "[quote](Simple quote)",
        "[quote](Quote with **bold** text)",
        "[quote](Knowledge is power)",
        "[quote](Quote with special chars: äöü 🚀)",
    ]
    
    for original_markdown in test_cases:
        # Convert to notion
        notion_result = QuoteElement.markdown_to_notion(original_markdown)
        assert notion_result is not None
        
        # Create mock block for notion_to_markdown
        block = Mock()
        block.type = "quote"
        block.quote = notion_result.quote
        
        # Convert back to markdown
        result_markdown = QuoteElement.notion_to_markdown(block)
        
        # Should preserve the content (but might normalize whitespace)
        assert result_markdown is not None
        assert result_markdown.startswith("[quote](")
        assert result_markdown.endswith(")")
        
        # Extract and compare content
        original_content = original_markdown[8:-1]  # Remove [quote]( and )
        result_content = result_markdown[8:-1]
        assert result_content.strip() == original_content.strip()


def test_content_extraction():
    """Test that content is properly extracted from pattern."""
    test_cases = [
        ("[quote](Simple content)", "Simple content"),
        ("[quote](Content with **bold**)", "Content with **bold**"),
        ("[quote](Special chars: äöü 🚀)", "Special chars: äöü 🚀"),
        ("[quote](Quote with numbers 123)", "Quote with numbers 123"),
    ]
    
    for markdown, expected_content in test_cases:
        result = QuoteElement.markdown_to_notion(markdown)
        assert result is not None
        actual_content = result.quote.rich_text[0].plain_text
        assert expected_content in actual_content  # May have formatting differences


def test_single_line_restriction():
    """Test that multiline content is rejected."""
    multiline_quotes = [
        "[quote](First line\nSecond line)",
        "[quote](Line with\rcarriage return)",
        "[quote](Multiple\n\nlines)",
    ]
    
    for quote in multiline_quotes:
        assert not QuoteElement.match_markdown(quote)
        assert QuoteElement.markdown_to_notion(quote) is None


def test_with_special_characters():
    """Test quotes with various special characters."""
    special_quotes = [
        "[quote](Quote with émoji 🎯)",
        "[quote](Chinese text: 这是引用)",
        "[quote](Math symbols: ∑ ∆ π)",
        "[quote](Punctuation: !@#$%^&*())]",
        "[quote](URLs work: https://example.com)",
    ]
    
    for quote in special_quotes:
        assert QuoteElement.match_markdown(quote)
        result = QuoteElement.markdown_to_notion(quote)
        assert result is not None
        assert result.type == "quote"


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = QuoteElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, 'syntax')
    assert "[quote]" in content.syntax
    assert "blockquote" in content.syntax.lower() or "quote" in content.syntax.lower()