"""
Minimal tests for ToggleableHeadingElement.
Tests core functionality for toggleable headings (+#, +##, +###).
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.toggleable_heading import ToggleableHeadingElement
from notionary.blocks.heading.heading_models import (
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    HeadingBlock,
)
from notionary.blocks.rich_text.rich_text_models import RichTextObject


def test_match_markdown_valid():
    """Test recognition of valid toggleable heading formats."""
    assert ToggleableHeadingElement.match_markdown("+# Heading 1")
    assert ToggleableHeadingElement.match_markdown("+## Heading 2")
    assert ToggleableHeadingElement.match_markdown("+### Heading 3")
    assert ToggleableHeadingElement.match_markdown("+#  Heading with spaces")


def test_match_markdown_invalid():
    """Test rejection of invalid formats."""
    assert not ToggleableHeadingElement.match_markdown("+#### Too deep")
    assert not ToggleableHeadingElement.match_markdown("# Regular heading")
    assert not ToggleableHeadingElement.match_markdown("+#")  # No content
    assert not ToggleableHeadingElement.match_markdown("+ No level")
    assert not ToggleableHeadingElement.match_markdown("Regular text")
    assert not ToggleableHeadingElement.match_markdown("")


def test_match_notion():
    """Test recognition of Notion toggleable heading blocks."""
    # Valid toggleable heading
    block = Mock()
    block.type = "heading_1"
    heading_content = Mock()
    heading_content.is_toggleable = True
    block.get_block_content.return_value = heading_content
    assert ToggleableHeadingElement.match_notion(block)

    # Non-toggleable heading (should not match)
    heading_content.is_toggleable = False
    assert not ToggleableHeadingElement.match_notion(block)

    # Non-heading block
    block.type = "paragraph"
    assert not ToggleableHeadingElement.match_notion(block)

    # Invalid heading level
    block.type = "heading_4"
    assert not ToggleableHeadingElement.match_notion(block)


@pytest.mark.parametrize(
    "markdown,expected_level,expected_content",
    [
        ("+# Main Section", 1, "Main Section"),
        ("+## Subsection", 2, "Subsection"),
        ("+### Detail", 3, "Detail"),
    ],
)
def test_markdown_to_notion(markdown, expected_level, expected_content):
    """Test conversion from markdown to Notion."""
    result = ToggleableHeadingElement.markdown_to_notion(markdown)

    assert result is not None
    assert result.type == f"heading_{expected_level}"

    # Check heading content
    heading = getattr(result, f"heading_{expected_level}")
    assert isinstance(heading, HeadingBlock)
    assert heading.is_toggleable is True  # Key difference from regular headings
    assert heading.color == "default"
    assert len(heading.rich_text) > 0
    assert heading.rich_text[0].plain_text == expected_content


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    assert ToggleableHeadingElement.markdown_to_notion("+#### Too deep") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#") is None  # No content
    assert ToggleableHeadingElement.markdown_to_notion("# Regular") is None
    assert ToggleableHeadingElement.markdown_to_notion("text") is None


def test_notion_to_markdown():
    """Test conversion from Notion to markdown."""
    # Create mock toggleable heading block
    block = Mock()
    block.type = "heading_2"

    # Mock heading content with real RichTextObject
    heading_content = Mock()
    rich_text = RichTextObject.from_plain_text("Test Section")
    heading_content.rich_text = [rich_text]
    heading_content.is_toggleable = True

    block.get_block_content.return_value = heading_content

    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result == "+## Test Section"

    # Test non-toggleable heading (should return None)
    heading_content.is_toggleable = False
    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result is None


def test_pattern_matching():
    """Test the regex pattern directly."""
    # Valid patterns
    pattern = ToggleableHeadingElement.PATTERN
    assert pattern.match("+# Title")
    assert pattern.match("+## Subtitle")
    assert pattern.match("+### Section")

    # Invalid patterns
    assert not pattern.match("# Regular heading")
    assert not pattern.match("+#### Too deep")
    assert not pattern.match("+ No level")
    assert not pattern.match("+#")  # No content


@pytest.mark.parametrize(
    "markdown,should_match",
    [
        ("+# Section 1", True),
        ("+## Subsection", True),
        ("+### Detail", True),
        ("+#### Too deep", False),
        ("# Regular heading", False),
        ("+# ", False),  # No content
        ("+ No level", False),
        ("Regular text", False),
        ("", False),
    ],
)
def test_markdown_patterns(markdown, should_match):
    """Test various markdown patterns."""
    result = ToggleableHeadingElement.match_markdown(markdown)
    assert result == should_match


def test_roundtrip_conversion():
    """Test that markdown -> notion -> markdown preserves content."""
    test_cases = [
        "+# Main Section",
        "+## Subsection",
        "+### Detail Section",
    ]

    for markdown in test_cases:
        # Convert to notion
        notion_result = ToggleableHeadingElement.markdown_to_notion(markdown)
        assert notion_result is not None

        # Create mock block for notion_to_markdown
        level = markdown.count("#")
        block = Mock()
        block.type = f"heading_{level}"

        heading_content = getattr(notion_result, f"heading_{level}")
        block.get_block_content.return_value = heading_content

        # Convert back to markdown
        result = ToggleableHeadingElement.notion_to_markdown(block)
        assert result == markdown


def test_toggleable_property():
    """Test that created headings are always toggleable."""
    headings = ["+# Level 1", "+## Level 2", "+### Level 3"]

    for heading in headings:
        result = ToggleableHeadingElement.markdown_to_notion(heading)
        assert result is not None

        level = heading.count("#")
        heading_content = getattr(result, f"heading_{level}")
        assert heading_content.is_toggleable is True


def test_content_extraction():
    """Test that content is properly extracted from pattern."""
    markdown = "+## Section with special chars: äöü 🚀"
    result = ToggleableHeadingElement.markdown_to_notion(markdown)

    assert result is not None
    content = result.heading_2.rich_text[0].plain_text
    assert content == "Section with special chars: äöü 🚀"


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = ToggleableHeadingElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, "syntax")
    assert "+#" in content.syntax
    assert "pipe" in content.syntax.lower()  # Mentions pipe prefix for content
