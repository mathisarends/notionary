"""
Minimal tests for ToggleableHeadingElement.
Tests core functionality for collapsible headings with +# syntax.
"""

from unittest.mock import Mock
from notionary.blocks.heading.heading_models import (
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    HeadingBlock,
)
from notionary.blocks.toggleable_heading.toggleable_heading_element import ToggleableHeadingElement


def test_match_markdown_valid():
    """Test recognition of valid toggleable heading formats."""
    assert ToggleableHeadingElement.match_markdown("+# Level 1 Heading")
    assert ToggleableHeadingElement.match_markdown("+## Level 2 Heading")
    assert ToggleableHeadingElement.match_markdown("+### Level 3 Heading")
    assert ToggleableHeadingElement.match_markdown("  +# Indented heading  ")
    assert ToggleableHeadingElement.match_markdown("+# Heading with **bold** text")


def test_match_markdown_invalid():
    """Test rejection of invalid toggleable heading formats."""
    # Regular headings (without +)
    assert not ToggleableHeadingElement.match_markdown("# Regular heading")
    assert not ToggleableHeadingElement.match_markdown("## Regular heading")
    assert not ToggleableHeadingElement.match_markdown("### Regular heading")
    
    # Too many levels
    assert not ToggleableHeadingElement.match_markdown("+#### Level 4")
    assert not ToggleableHeadingElement.match_markdown("+##### Level 5")
    
    # Missing content
    assert not ToggleableHeadingElement.match_markdown("+#")
    assert not ToggleableHeadingElement.match_markdown("+##   ")
    
    # Wrong syntax
    assert not ToggleableHeadingElement.match_markdown("+ # Space before #")
    assert not ToggleableHeadingElement.match_markdown("#+# Wrong order")
    assert not ToggleableHeadingElement.match_markdown("")
    assert not ToggleableHeadingElement.match_markdown("Regular text")


def test_match_notion_valid():
    """Test recognition of valid Notion toggleable heading blocks."""
    # Mock heading content with is_toggleable=True
    mock_heading_content = Mock()
    mock_heading_content.is_toggleable = True
    
    # Mock block
    mock_block = Mock()
    mock_block.type = "heading_1"
    mock_block.get_block_content.return_value = mock_heading_content
    
    assert ToggleableHeadingElement.match_notion(mock_block)
    
    # Test other levels
    for level in ["1", "2", "3"]:
        mock_block.type = f"heading_{level}"
        assert ToggleableHeadingElement.match_notion(mock_block)


def test_match_notion_invalid():
    """Test rejection of invalid Notion blocks."""
    # Non-toggleable heading
    mock_heading_content = Mock()
    mock_heading_content.is_toggleable = False
    
    mock_block = Mock()
    mock_block.type = "heading_1"
    mock_block.get_block_content.return_value = mock_heading_content
    
    assert not ToggleableHeadingElement.match_notion(mock_block)
    
    # Wrong block type
    mock_block.type = "paragraph"
    assert not ToggleableHeadingElement.match_notion(mock_block)
    
    # Invalid heading level
    mock_block.type = "heading_4"
    assert not ToggleableHeadingElement.match_notion(mock_block)
    
    # No content
    mock_block.type = "heading_1"
    mock_block.get_block_content.return_value = None
    assert not ToggleableHeadingElement.match_notion(mock_block)


def test_markdown_to_notion_level_1():
    """Test conversion of level 1 toggleable heading."""
    result = ToggleableHeadingElement.markdown_to_notion("+# Test Heading")
    
    assert result is not None
    assert isinstance(result, CreateHeading1Block)
    assert isinstance(result.heading_1, HeadingBlock)
    assert result.heading_1.is_toggleable is True
    assert result.heading_1.color == "default"
    assert result.heading_1.children == []


def test_markdown_to_notion_level_2():
    """Test conversion of level 2 toggleable heading."""
    result = ToggleableHeadingElement.markdown_to_notion("+## Test Heading")
    
    assert result is not None
    assert isinstance(result, CreateHeading2Block)
    assert result.heading_2.is_toggleable is True


def test_markdown_to_notion_level_3():
    """Test conversion of level 3 toggleable heading."""
    result = ToggleableHeadingElement.markdown_to_notion("+### Test Heading")
    
    assert result is not None
    assert isinstance(result, CreateHeading3Block)
    assert result.heading_3.is_toggleable is True


def test_markdown_to_notion_invalid():
    """Test that invalid markdown returns None."""
    assert ToggleableHeadingElement.markdown_to_notion("# Regular heading") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#### Too many levels") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#") is None
    assert ToggleableHeadingElement.markdown_to_notion("") is None


def test_notion_to_markdown_level_1():
    """Test conversion from Notion heading_1 to markdown."""
    # Mock heading content
    mock_rich_text = [{"text": {"content": "Test Heading"}}]
    mock_heading_content = Mock()
    mock_heading_content.is_toggleable = True
    mock_heading_content.rich_text = mock_rich_text
    
    # Mock block
    mock_block = Mock()
    mock_block.type = "heading_1"
    mock_block.get_block_content.return_value = mock_heading_content
    
    result = ToggleableHeadingElement.notion_to_markdown(mock_block)
    
    assert result is not None
    assert result.startswith("+# ")


def test_notion_to_markdown_different_levels():
    """Test conversion for different heading levels."""
    test_cases = [
        ("heading_1", "+# "),
        ("heading_2", "+## "),
        ("heading_3", "+### "),
    ]
    
    for block_type, expected_prefix in test_cases:
        # Mock heading content
        mock_rich_text = [{"text": {"content": "Test"}}]
        mock_heading_content = Mock()
        mock_heading_content.is_toggleable = True
        mock_heading_content.rich_text = mock_rich_text
        
        # Mock block
        mock_block = Mock()
        mock_block.type = block_type
        mock_block.get_block_content.return_value = mock_heading_content
        
        result = ToggleableHeadingElement.notion_to_markdown(mock_block)
        
        assert result is not None
        assert result.startswith(expected_prefix)


def test_notion_to_markdown_non_toggleable():
    """Test that non-toggleable headings return None."""
    # Mock non-toggleable heading content
    mock_heading_content = Mock()
    mock_heading_content.is_toggleable = False
    
    # Mock block
    mock_block = Mock()
    mock_block.type = "heading_1"
    mock_block.get_block_content.return_value = mock_heading_content
    
    result = ToggleableHeadingElement.notion_to_markdown(mock_block)
    
    assert result is None


def test_notion_to_markdown_invalid():
    """Test that invalid blocks return None."""
    mock_block = Mock()
    mock_block.type = "paragraph"
    
    assert ToggleableHeadingElement.notion_to_markdown(mock_block) is None
    
    # Invalid heading level
    mock_block.type = "heading_4"
    assert ToggleableHeadingElement.notion_to_markdown(mock_block) is None


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    result = ToggleableHeadingElement.get_llm_prompt_content()
    assert result is not None


def test_pattern_regex_directly():
    """Test the PATTERN regex directly."""
    pattern = ToggleableHeadingElement.PATTERN
    
    # Valid patterns
    match1 = pattern.match("+# Level 1")
    assert match1 is not None
    assert match1.group("level") == "#"
    assert match1.group("content") == "Level 1"
    
    match2 = pattern.match("+## Level 2")
    assert match2 is not None
    assert match2.group("level") == "##"
    assert match2.group("content") == "Level 2"
    
    match3 = pattern.match("+### Level 3")
    assert match3 is not None
    assert match3.group("level") == "###"
    assert match3.group("content") == "Level 3"
    
    # Invalid patterns
    assert not pattern.match("# Regular heading")
    assert not pattern.match("+#### Too many")
    assert not pattern.match("+#")


def test_level_counting():
    """Test that heading levels are correctly counted."""
    test_cases = [
        ("+# Heading", 1),
        ("+## Heading", 2),
        ("+### Heading", 3),
    ]
    
    for markdown_text, expected_level in test_cases:
        result = ToggleableHeadingElement.markdown_to_notion(markdown_text)
        assert result is not None
        
        # Check the correct block type was created
        if expected_level == 1:
            assert isinstance(result, CreateHeading1Block)
        elif expected_level == 2:
            assert isinstance(result, CreateHeading2Block)
        elif expected_level == 3:
            assert isinstance(result, CreateHeading3Block)


def test_whitespace_handling():
    """Test handling of whitespace."""
    # Leading/trailing whitespace
    assert ToggleableHeadingElement.match_markdown("  +# Heading  ")
    
    # Conversion should work
    result = ToggleableHeadingElement.markdown_to_notion("  +## Heading  ")
    assert result is not None


def test_inline_formatting():
    """Test headings with inline formatting."""
    formatting_cases = [
        "+# Heading with **bold** text",
        "+## Heading with *italic* text",
        "+### Heading with `code` text",
        "+# Heading with [link](https://example.com)",
    ]
    
    for text in formatting_cases:
        assert ToggleableHeadingElement.match_markdown(text)
        result = ToggleableHeadingElement.markdown_to_notion(text)
        assert result is not None


def test_special_characters():
    """Test headings with special characters."""
    special_cases = [
        "+# Heading with äöü ß",
        "+## Heading with 😀 emojis",
        "+### Heading with symbols !@#$%",
        "+# Heading with numbers 123",
    ]
    
    for text in special_cases:
        assert ToggleableHeadingElement.match_markdown(text)
        result = ToggleableHeadingElement.markdown_to_notion(text)
        assert result is not None


def test_block_content_access():
    """Test accessing block content with get_block_content()."""
    # Test that the method uses get_block_content() correctly
    mock_heading_content = Mock()
    mock_heading_content.is_toggleable = True
    
    mock_block = Mock()
    mock_block.type = "heading_1"
    mock_block.get_block_content.return_value = mock_heading_content
    
    # Should call get_block_content()
    result = ToggleableHeadingElement.match_notion(mock_block)
    assert result is True
    mock_block.get_block_content.assert_called()


def test_is_toggleable_property():
    """Test the is_toggleable property handling."""
    # Test missing is_toggleable attribute
    mock_heading_content = Mock()
    del mock_heading_content.is_toggleable  # Remove attribute
    
    mock_block = Mock()
    mock_block.type = "heading_1"
    mock_block.get_block_content.return_value = mock_heading_content
    
    # Should handle missing attribute gracefully
    result = ToggleableHeadingElement.match_notion(mock_block)
    assert result is False  # getattr with default False


def test_edge_cases():
    """Test edge cases."""
    edge_cases = [
        ("+# A", True),  # Single character
        ("+## 1", True),  # Single digit
        ("+### !", True),  # Single symbol
    ]
    
    for text, should_match in edge_cases:
        match_result = ToggleableHeadingElement.match_markdown(text)
        assert match_result == should_match
        
        if should_match:
            result = ToggleableHeadingElement.markdown_to_notion(text)
            assert result is not None


def test_roundtrip_conversion():
    """Test that conversion works both ways."""
    original_headings = [
        "+# Main Section",
        "+## Subsection", 
        "+### Details",
    ]
    
    for original in original_headings:
        # Markdown -> Notion
        notion_block = ToggleableHeadingElement.markdown_to_notion(original)
        assert notion_block is not None
        
        # Create mock block for reverse conversion
        level = original.count('#')
        mock_rich_text = [{"text": {"content": original.split(' ', 1)[1]}}]
        mock_heading_content = Mock()
        mock_heading_content.is_toggleable = True
        mock_heading_content.rich_text = mock_rich_text
        
        mock_block = Mock()
        mock_block.type = f"heading_{level}"
        mock_block.get_block_content.return_value = mock_heading_content
        
        # Notion -> Markdown
        converted = ToggleableHeadingElement.notion_to_markdown(mock_block)
        assert converted is not None
        assert converted.startswith("+")
        assert "#" in converted