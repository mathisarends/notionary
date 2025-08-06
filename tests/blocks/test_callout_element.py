"""
Pytest tests for CalloutElement.
Tests conversion between Markdown callouts and Notion callout blocks.
"""

import pytest
from unittest.mock import patch, Mock

from notionary.blocks.callout.callout_element import CalloutElement
from notionary.blocks.callout.callout_models import CreateCalloutBlock, CalloutBlock
from notionary.blocks.rich_text.rich_text_models import (
    RichTextObject,
    TextContent,
    TextAnnotations,
)
from notionary.models.icon_types import EmojiIcon  # Fixed import path


@pytest.fixture
def mock_extract_text():
    """Fixture to mock text extraction functionality."""
    with patch(
        "notionary.blocks.rich_text.text_inline_formatter.TextInlineFormatter.extract_text_with_formatting"
    ) as mock:

        def mock_extract_text_func(rich_text_dicts):
            if not rich_text_dicts or len(rich_text_dicts) == 0:
                return ""
            for item in rich_text_dicts:
                if item.get("type") == "text" and item.get("text", {}).get("content"):
                    return item["text"]["content"]
                elif item.get("plain_text"):
                    return item["plain_text"]
            return ""

        mock.side_effect = mock_extract_text_func
        yield mock


def create_rich_text_object(content: str) -> RichTextObject:
    """Helper function to create RichTextObject instances."""
    return RichTextObject(
        type="text",
        text=TextContent(content=content),
        annotations=TextAnnotations(),
        plain_text=content,
    )


def test_match_markdown_valid_formats():
    """Test recognition of valid Markdown callout formats."""
    assert CalloutElement.match_markdown("[callout](Simple callout)")
    assert CalloutElement.match_markdown('[callout](Text with emoji "💡")')
    assert CalloutElement.match_markdown('[callout](Warning text "⚠️")')


def test_match_markdown_invalid_formats():
    """Test rejection of invalid formats."""
    assert not CalloutElement.match_markdown("Regular text")
    assert not CalloutElement.match_markdown("> Blockquote")
    assert not CalloutElement.match_markdown("[link](https://example.com)")
    assert not CalloutElement.match_markdown("[callout]()")  # Empty callout


def test_match_notion():
    """Test recognition of Notion callout blocks."""
    # Create mock Block object
    block = Mock()
    block.type = "callout"
    block.callout = Mock()  # callout content exists
    assert CalloutElement.match_notion(block)

    # Test non-callout block
    paragraph_block = Mock()
    paragraph_block.type = "paragraph"
    paragraph_block.callout = None
    assert not CalloutElement.match_notion(paragraph_block)


def test_markdown_to_notion_simple():
    """Test conversion of simple callout to Notion."""
    result = CalloutElement.markdown_to_notion("[callout](Simple callout)")

    assert result is not None
    assert isinstance(result, CreateCalloutBlock)
    assert result.type == "callout"
    assert isinstance(result.callout, CalloutBlock)
    assert result.callout.color == "gray_background"
    assert result.callout.icon.emoji == "💡"  # Default emoji
    assert len(result.callout.rich_text) == 1
    assert result.callout.rich_text[0].plain_text == "Simple callout"


def test_markdown_to_notion_with_emoji():
    """Test conversion of callout with custom emoji."""
    result = CalloutElement.markdown_to_notion('[callout](Warning text "⚠️")')

    assert result is not None
    assert isinstance(result, CreateCalloutBlock)
    assert result.type == "callout"
    assert result.callout.icon.emoji == "⚠️"
    assert len(result.callout.rich_text) == 1
    assert result.callout.rich_text[0].plain_text == "Warning text"


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = CalloutElement.markdown_to_notion("Regular text")
    assert result is None


def test_notion_to_markdown_simple(mock_extract_text):
    """Test conversion of simple Notion callout to Markdown."""
    # Create mock Block object
    block = Mock()
    block.type = "callout"
    block.callout = Mock()
    block.callout.rich_text = [create_rich_text_object("Simple callout")]

    # Create proper EmojiIcon
    block.callout.icon = EmojiIcon(emoji="💡")

    mock_extract_text.return_value = "Simple callout"
    result = CalloutElement.notion_to_markdown(block)

    assert result == "[callout](Simple callout)"


def test_notion_to_markdown_with_custom_emoji(mock_extract_text):
    """Test conversion of Notion callout with custom emoji."""
    # Create mock Block object
    block = Mock()
    block.type = "callout"
    block.callout = Mock()
    block.callout.rich_text = [create_rich_text_object("Warning message")]

    # Create proper EmojiIcon
    block.callout.icon = EmojiIcon(emoji="⚠️")

    mock_extract_text.return_value = "Warning message"
    result = CalloutElement.notion_to_markdown(block)

    assert result == '[callout](Warning message "⚠️")'


def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    # Wrong type
    block = Mock()
    block.type = "paragraph"
    block.callout = None
    result = CalloutElement.notion_to_markdown(block)
    assert result is None

    # No callout content
    callout_block = Mock()
    callout_block.type = "callout"
    callout_block.callout = None
    result = CalloutElement.notion_to_markdown(callout_block)
    assert result is None


# REMOVED: test_is_multiline - method doesn't exist anymore


def test_roundtrip_conversion(mock_extract_text):
    """Test that Markdown -> Notion -> Markdown preserves content."""
    test_cases = [
        ("[callout](Simple callout)", "Simple callout", "[callout](Simple callout)"),
        (
            '[callout](Warning message "⚠️")',
            "Warning message",
            '[callout](Warning message "⚠️")',
        ),
        (
            '[callout](Info message "🔔")',
            "Info message",
            '[callout](Info message "🔔")',
        ),
        (
            '[callout](Success message "✅")',
            "Success message",
            '[callout](Success message "✅")',
        ),
    ]

    for original_markdown, expected_text, expected_result in test_cases:
        # Convert to Notion
        notion_result = CalloutElement.markdown_to_notion(original_markdown)
        assert (
            notion_result is not None
        ), f"Failed to convert {original_markdown} to Notion"

        # Create a mock Block object for notion_to_markdown
        block = Mock()
        block.type = "callout"
        block.callout = notion_result.callout

        # Mock the text extraction
        mock_extract_text.return_value = expected_text

        # Convert back to Markdown
        result_markdown = CalloutElement.notion_to_markdown(block)
        assert result_markdown is not None, "Failed to convert back to Markdown"

        # Check exact match
        assert (
            result_markdown == expected_result
        ), f"Expected {expected_result}, got {result_markdown}"


# Parametrized tests for various input formats
@pytest.mark.parametrize(
    "markdown,expected_emoji",
    [
        ("[callout](Simple text)", "💡"),  # Default emoji
        ('[callout](Warning "⚠️")', "⚠️"),
        ('[callout](Success "✅")', "✅"),
        ('[callout](Info "🔔")', "🔔"),
        ('[callout](Fire "🔥")', "🔥"),
    ],
)
def test_emoji_extraction(markdown, expected_emoji):
    """Test emoji extraction from different callout formats."""
    result = CalloutElement.markdown_to_notion(markdown)

    assert result is not None
    assert result.callout.icon.emoji == expected_emoji


@pytest.mark.parametrize(
    "block_type,should_match",
    [
        ("callout", True),
        ("paragraph", False),
        ("quote", False),
        ("heading_1", False),
        ("bulleted_list_item", False),
    ],
)
def test_notion_block_recognition(block_type, should_match):
    """Test recognition of different Notion block types."""
    block = Mock()
    block.type = block_type

    if block_type == "callout":
        block.callout = Mock()  # callout content exists
    else:
        block.callout = None

    result = CalloutElement.match_notion(block)
    assert result == should_match


# Fixtures for common test data
@pytest.fixture
def simple_callout_block():
    """Fixture for simple callout block."""
    block = Mock()
    block.type = "callout"
    block.callout = Mock()
    block.callout.rich_text = [create_rich_text_object("Test callout")]
    block.callout.icon = EmojiIcon(emoji="💡")
    block.callout.color = "gray_background"
    return block


@pytest.fixture
def warning_callout_block():
    """Fixture for warning callout block with custom emoji."""
    block = Mock()
    block.type = "callout"
    block.callout = Mock()
    block.callout.rich_text = [create_rich_text_object("Warning message")]
    block.callout.icon = EmojiIcon(emoji="⚠️")
    block.callout.color = "gray_background"
    return block


def test_specific_notion_structures(
    mock_extract_text, simple_callout_block, warning_callout_block
):
    """Test specific Notion block structures with fixtures."""
    # Test simple callout
    mock_extract_text.return_value = "Test callout"
    result1 = CalloutElement.notion_to_markdown(simple_callout_block)
    assert result1 == "[callout](Test callout)"

    # Test warning callout
    mock_extract_text.return_value = "Warning message"
    result2 = CalloutElement.notion_to_markdown(warning_callout_block)
    assert result2 == '[callout](Warning message "⚠️")'


def test_markdown_to_notion_detailed_structure():
    """Test detailed structure of converted Notion blocks."""
    test_cases = [
        {
            "input": "[callout](Simple callout)",
            "expected": {
                "type": "callout",
                "callout": {
                    "icon": {"emoji": "💡"},
                    "color": "gray_background",
                },
            },
        },
        {
            "input": '[callout](Fire alert "🔥")',
            "expected": {
                "type": "callout",
                "callout": {
                    "icon": {"emoji": "🔥"},
                    "color": "gray_background",
                },
            },
        },
    ]

    for case in test_cases:
        result = CalloutElement.markdown_to_notion(case["input"])

        # Check basic structure
        assert result.type == case["expected"]["type"]

        # Check callout properties (excluding rich_text which is processed separately)
        expected_callout = case["expected"]["callout"]
        if "icon" in expected_callout:
            assert result.callout.icon.emoji == expected_callout["icon"]["emoji"]
        if "color" in expected_callout:
            assert result.callout.color == expected_callout["color"]


def test_markdown_to_notion_empty_content():
    """Test that empty content is handled properly."""
    result = CalloutElement.markdown_to_notion("[callout]()")
    assert result is None


def test_markdown_to_notion_whitespace_handling():
    """Test proper whitespace handling."""
    result = CalloutElement.markdown_to_notion("[callout]( Spaced content )")
    assert result is not None
    # Check that content is properly trimmed
    assert result.callout.rich_text[0].plain_text == "Spaced content"


def test_notion_to_markdown_empty_rich_text(mock_extract_text):
    """Test handling of empty rich_text."""
    block = Mock()
    block.type = "callout"
    block.callout = Mock()
    block.callout.rich_text = []
    block.callout.icon = EmojiIcon(emoji="💡")
    block.callout.color = "gray_background"

    mock_extract_text.return_value = ""
    result = CalloutElement.notion_to_markdown(block)
    assert result is None


def test_pattern_matching():
    """Test the regex pattern directly."""
    assert CalloutElement.PATTERN.match("[callout](Simple text)")
    assert CalloutElement.PATTERN.match('[callout](Text "emoji")')
    assert not CalloutElement.PATTERN.match("[call](Invalid)")
    assert not CalloutElement.PATTERN.match("callout](Missing bracket)")


def test_get_emoji_helper():
    """Test the _get_emoji helper method."""
    # Create EmojiIcon
    emoji_icon = EmojiIcon(emoji="🔥")
    result = CalloutElement._get_emoji(emoji_icon)
    assert result == "🔥"

    # Test with mock icon that doesn't have emoji attribute
    mock_icon = Mock()
    mock_icon.emoji = "💡"
    result = CalloutElement._get_emoji(mock_icon)
    assert result == "💡"


def test_default_emoji_constant():
    """Test that default emoji constant is accessible."""
    assert hasattr(CalloutElement, "DEFAULT_EMOJI")
    assert CalloutElement.DEFAULT_EMOJI == "💡"

    assert hasattr(CalloutElement, "DEFAULT_COLOR")
    assert CalloutElement.DEFAULT_COLOR == "gray_background"


def test_get_llm_prompt_content():
    """Test LLM prompt content generation."""
    content = CalloutElement.get_llm_prompt_content()
    assert content is not None
    assert hasattr(content, "syntax")
    assert "[callout]" in content.syntax
    assert "emoji" in content.syntax.lower() or "icon" in content.syntax.lower()
