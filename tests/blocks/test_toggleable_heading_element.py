"""
Minimale Tests für ToggleableHeadingElement - nur das Wesentliche.
"""

import pytest
from unittest.mock import Mock

from notionary.blocks.heading.heading_models import HeadingBlock
from notionary.blocks.block_types import BlockType
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.toggleable_heading.toggleable_heading_element import (
    ToggleableHeadingElement,
)


def create_rich_text(content: str) -> RichTextObject:
    """Helper to create RichTextObject."""
    return RichTextObject.from_plain_text(content)


def test_match_markdown():
    """Test Markdown pattern matching."""
    # Valid patterns
    assert ToggleableHeadingElement.markdown_to_notion("+# Heading 1") is not None
    assert ToggleableHeadingElement.markdown_to_notion("+## Heading 2") is not None
    assert ToggleableHeadingElement.markdown_to_notion("+### Heading 3") is not None
    assert (
        ToggleableHeadingElement.markdown_to_notion("+# Text with spaces") is not None
    )

    # Invalid patterns
    assert ToggleableHeadingElement.markdown_to_notion("# Regular heading") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#### Too many levels") is None
    assert ToggleableHeadingElement.markdown_to_notion("+ Missing hash") is None
    assert not ToggleableHeadingElement.markdown_to_notion("+#")  # No content


def test_match_notion():
    """Test Notion block matching."""
    # Valid toggleable heading 1
    block = Mock()
    block.type = BlockType.HEADING_1
    block.heading_1 = Mock()
    block.heading_1.is_toggleable = True
    block.heading_2 = None
    block.heading_3 = None
    assert ToggleableHeadingElement.match_notion(block)

    # Valid toggleable heading 2
    block.type = BlockType.HEADING_2
    block.heading_1 = None
    block.heading_2 = Mock()
    block.heading_2.is_toggleable = True
    block.heading_3 = None
    assert ToggleableHeadingElement.match_notion(block)

    # Invalid - not toggleable
    block.heading_2.is_toggleable = False
    assert not ToggleableHeadingElement.match_notion(block)

    # Invalid - wrong type
    block.type = BlockType.PARAGRAPH
    assert not ToggleableHeadingElement.match_notion(block)


def test_markdown_to_notion_level1():
    """Test Markdown -> Notion für Level 1."""
    result = ToggleableHeadingElement.markdown_to_notion("+# Test Heading")

    assert result is not None
    assert hasattr(result, "heading_1")
    assert result.heading_1.is_toggleable is True
    assert result.heading_1.rich_text[0].plain_text == "Test Heading"


def test_markdown_to_notion_level2():
    """Test Markdown -> Notion für Level 2."""
    result = ToggleableHeadingElement.markdown_to_notion("+## Test Heading")

    assert result is not None
    assert hasattr(result, "heading_2")
    assert result.heading_2.is_toggleable is True
    assert result.heading_2.rich_text[0].plain_text == "Test Heading"


def test_markdown_to_notion_level3():
    """Test Markdown -> Notion für Level 3."""
    result = ToggleableHeadingElement.markdown_to_notion("+### Test Heading")

    assert result is not None
    assert hasattr(result, "heading_3")
    assert result.heading_3.is_toggleable is True
    assert result.heading_3.rich_text[0].plain_text == "Test Heading"


def test_markdown_to_notion_invalid():
    """Test ungültige Eingaben."""
    assert ToggleableHeadingElement.markdown_to_notion("# Regular heading") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#### Too many levels") is None
    assert ToggleableHeadingElement.markdown_to_notion("+#") is None  # No content


def test_notion_to_markdown_level1():
    """Test Notion -> Markdown für Level 1."""
    heading_data = HeadingBlock(
        rich_text=[create_rich_text("Test Heading")],
        color="default",
        is_toggleable=True,
        children=[],
    )

    block = Mock()
    block.type = BlockType.HEADING_1
    block.heading_1 = heading_data

    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result == "+# Test Heading"


def test_notion_to_markdown_level2():
    """Test Notion -> Markdown für Level 2."""
    heading_data = HeadingBlock(
        rich_text=[create_rich_text("Test Heading")],
        color="default",
        is_toggleable=True,
        children=[],
    )

    block = Mock()
    block.type = BlockType.HEADING_2
    block.heading_2 = heading_data

    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result == "+## Test Heading"


def test_notion_to_markdown_level3():
    """Test Notion -> Markdown für Level 3."""
    heading_data = HeadingBlock(
        rich_text=[create_rich_text("Test Heading")],
        color="default",
        is_toggleable=True,
        children=[],
    )

    block = Mock()
    block.type = BlockType.HEADING_3
    block.heading_3 = heading_data

    result = ToggleableHeadingElement.notion_to_markdown(block)
    assert result == "+### Test Heading"


def test_notion_to_markdown_invalid():
    """Test ungültige Notion blocks."""
    # Wrong type
    block = Mock()
    block.type = BlockType.PARAGRAPH
    assert ToggleableHeadingElement.notion_to_markdown(block) is None

    # Not HeadingBlock instance
    block.type = BlockType.HEADING_1
    block.heading_1 = "not a HeadingBlock"
    assert ToggleableHeadingElement.notion_to_markdown(block) is None


def test_roundtrip():
    """Test Roundtrip-Konvertierung."""
    test_cases = [
        "+# Main Section",
        "+## Subsection",
        "+### Details",
        "+# Section with **bold** text",
    ]

    for original in test_cases:
        # Markdown -> Notion
        notion_result = ToggleableHeadingElement.markdown_to_notion(original)
        assert notion_result is not None

        # Create proper block for notion_to_markdown
        block = Mock()
        if hasattr(notion_result, "heading_1"):
            block.type = BlockType.HEADING_1
            block.heading_1 = notion_result.heading_1
        elif hasattr(notion_result, "heading_2"):
            block.type = BlockType.HEADING_2
            block.heading_2 = notion_result.heading_2
        else:
            block.type = BlockType.HEADING_3
            block.heading_3 = notion_result.heading_3

        # Notion -> Markdown
        result = ToggleableHeadingElement.notion_to_markdown(block)
        # Note: Rich text formatting might be simplified in roundtrip
        assert result.startswith(original.split()[0])  # Check prefix matches


@pytest.mark.parametrize(
    "level,expected_prefix",
    [
        (1, "+#"),
        (2, "+##"),
        (3, "+###"),
    ],
)
def test_different_levels(level, expected_prefix):
    """Test verschiedene Heading-Level."""
    prefix = "#" * level
    markdown = f"+{prefix} Test Content"

    result = ToggleableHeadingElement.markdown_to_notion(markdown)
    assert result is not None

    # Check correct level was created
    if level == 1:
        assert hasattr(result, "heading_1")
        assert result.heading_1.is_toggleable is True
    elif level == 2:
        assert hasattr(result, "heading_2")
        assert result.heading_2.is_toggleable is True
    else:
        assert hasattr(result, "heading_3")
        assert result.heading_3.is_toggleable is True


def test_pattern_regex():
    """Test das Regex Pattern direkt."""
    pattern = ToggleableHeadingElement.PATTERN

    # Valid matches
    assert pattern.match("+# Content")
    assert pattern.match("+## Content")
    assert pattern.match("+### Content")

    # Invalid
    assert not pattern.match("# Content")
    assert not pattern.match("+#### Content")
    assert not pattern.match("+ Content")


def test_empty_content_handling():
    """Test Behandlung von leerem Content."""
    # Empty content should return None
    result = ToggleableHeadingElement.markdown_to_notion("+# ")
    assert result is None

    # Whitespace-only content should work after strip
    result = ToggleableHeadingElement.markdown_to_notion("+#   Content   ")
    assert result is not None
    assert result.heading_1.rich_text[0].plain_text == "Content"
