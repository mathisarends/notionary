"""
Pytest tests for ToggleElement.
Tests conversion between Markdown toggles and Notion toggle blocks.
"""

import pytest
from unittest.mock import Mock
from notionary.blocks.toggle.toggle_element import ToggleElement
from notionary.blocks.toggle.toggle_models import CreateToggleBlock, ToggleBlock
from notionary.blocks.rich_text.rich_text_models import RichTextObject


@pytest.mark.parametrize(
    "text,expected",
    [
        ("+++ This is a toggle", True),
        ("+++   Another one", True),
        ("++ Not a toggle", False),
        ("> Blockquote", False),
        ("+++", False),
        ("", False),
        ("+++    ", False),
        ("Some text", False),
    ],
)
def test_match_markdown(text, expected):
    assert ToggleElement.match_markdown(text) == expected


@pytest.mark.parametrize(
    "block_type,expected",
    [
        ("toggle", True),
        ("paragraph", False),
        ("callout", False),
        ("heading_1", False),
    ],
)
def test_match_notion(block_type, expected):
    # Create proper Mock Block object
    block = Mock()
    block.type = block_type
    if block_type == "toggle":
        block.toggle = Mock()  # toggle content exists
    else:
        block.toggle = None

    assert ToggleElement.match_notion(block) == expected


def test_markdown_to_notion_valid():
    markdown = "+++ My Toggle Title"
    result = ToggleElement.markdown_to_notion(markdown)

    assert result is not None
    assert isinstance(result, CreateToggleBlock)
    assert result.type == "toggle"
    assert isinstance(result.toggle, ToggleBlock)
    assert result.toggle.color == "default"
    assert result.toggle.children == []

    # Check rich text content
    assert len(result.toggle.rich_text) == 1
    assert result.toggle.rich_text[0].plain_text == "My Toggle Title"


@pytest.mark.parametrize(
    "invalid",
    [
        "+++",  # No title
        "This is just text",
        "++ No toggle",
        "",
    ],
)
def test_markdown_to_notion_invalid(invalid):
    assert ToggleElement.markdown_to_notion(invalid) is None


def test_notion_to_markdown_simple():
    # Create mock Block object with proper structure
    notion_block = Mock()
    notion_block.type = "toggle"

    # Create mock toggle content with real RichTextObject
    toggle_content = Mock()
    rich_text = RichTextObject.from_plain_text("My Toggle Title")
    toggle_content.rich_text = [rich_text]
    toggle_content.children = []

    notion_block.toggle = toggle_content

    result = ToggleElement.notion_to_markdown(notion_block)
    assert result == "+++ My Toggle Title"


def test_notion_to_markdown_with_children():
    # Create mock Block with children
    notion_block = Mock()
    notion_block.type = "toggle"

    # Create mock toggle content
    toggle_content = Mock()
    rich_text = RichTextObject.from_plain_text("Parent")
    toggle_content.rich_text = [rich_text]

    # Mock child block
    child_block = Mock()
    child_block.type = "paragraph"
    toggle_content.children = [child_block]

    notion_block.toggle = toggle_content

    result = ToggleElement.notion_to_markdown(notion_block)
    assert result.startswith("+++ Parent")
    assert "[Nested content]" in result


def test_notion_to_markdown_invalid():
    # Wrong type
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.toggle = None
    assert ToggleElement.notion_to_markdown(paragraph_block) is None

    # No toggle content
    toggle_block = Mock()
    toggle_block.type = "toggle"
    toggle_block.toggle = None
    assert ToggleElement.notion_to_markdown(toggle_block) is None


# REMOVED: test_is_multiline - method doesn't exist anymore


@pytest.mark.parametrize(
    "md",
    [
        "+++ Toggle mit Umlauten äöüß",
        "+++ Toggle mit Emoji 🙂",
        "+++    Spaces vorne und hinten   ",
    ],
)
def test_unicode_content_and_whitespace(md):
    block = ToggleElement.markdown_to_notion(md)
    assert block is not None
    assert isinstance(block, CreateToggleBlock)

    # Check that the content is properly extracted
    text = block.toggle.rich_text[0].plain_text
    # The content should be trimmed
    expected_content = md.lstrip("+").strip()
    assert text == expected_content


def test_roundtrip():
    cases = [
        "+++ Einfache Überschrift",
        "+++ Toggle mit Emoji 🚀",
        "+++   Mit mehreren   Spaces   ",
    ]
    for md in cases:
        # Convert to notion
        notion_result = ToggleElement.markdown_to_notion(md)
        assert notion_result is not None

        # Create proper mock Block for notion_to_markdown
        mock_block = Mock()
        mock_block.type = "toggle"
        mock_block.toggle = notion_result.toggle

        # Convert back to markdown
        md2 = ToggleElement.notion_to_markdown(mock_block)
        assert md2 is not None
        assert md2.startswith("+++")

        # Content should be trimmed, so compare the trimmed versions
        original_content = md.lstrip("+").strip()
        result_content = md2.lstrip("+").strip()
        assert result_content == original_content


def test_pattern_matching():
    """Test the regex pattern directly."""
    assert ToggleElement.TOGGLE_PATTERN.match("+++ Valid toggle")
    assert ToggleElement.TOGGLE_PATTERN.match("+++   With spaces")
    assert not ToggleElement.TOGGLE_PATTERN.match("++ Invalid")
    assert not ToggleElement.TOGGLE_PATTERN.match("++++Too many plus")


def test_extract_text_content_method():
    """Test the _extract_text_content helper method."""
    # Create some rich text objects
    rich_text_objects = [
        RichTextObject.from_plain_text("Hello "),
        RichTextObject.from_plain_text("World"),
    ]

    result = ToggleElement._extract_text_content(rich_text_objects)
    assert result == "Hello World"


def test_empty_toggle_content():
    """Test handling of empty toggle content."""
    # Should fail on empty content
    assert ToggleElement.markdown_to_notion("+++ ") is None
    assert ToggleElement.markdown_to_notion("+++") is None


def test_whitespace_normalization():
    """Test that whitespace is properly handled."""
    md = "+++    Title with many spaces    "
    result = ToggleElement.markdown_to_notion(md)

    assert result is not None
    # Content should be trimmed
    assert result.toggle.rich_text[0].plain_text == "Title with many spaces"


def test_special_characters():
    """Test handling of special characters."""
    special_cases = [
        '+++ Title with "quotes"',
        "+++ Title with 'single quotes'",
        "+++ Title with & ampersand",
        "+++ Title with < > brackets",
        "+++ Title with | pipes",
    ]

    for md in special_cases:
        result = ToggleElement.markdown_to_notion(md)
        assert result is not None
        # Just verify it doesn't crash


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = ToggleElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, "syntax")
    assert "+++" in content.syntax
    assert "pipe" in content.syntax.lower()
