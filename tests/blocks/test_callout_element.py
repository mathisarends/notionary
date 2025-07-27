"""
Pytest tests for CalloutElement.
Tests conversion between Markdown callouts and Notion callout blocks.
"""

import pytest
from unittest.mock import patch, MagicMock
from notionary.blocks import CalloutElement


@pytest.fixture
def mock_extract_text():
    """Fixture to mock text extraction functionality."""
    with patch(
        "notionary.blocks.shared.text_inline_formatter.TextInlineFormatter.extract_text_with_formatting"
    ) as mock:

        def mock_extract_text_func(rich_text):
            if not rich_text or len(rich_text) == 0:
                return ""
            for item in rich_text:
                if item.get("type") == "text" and item.get("text", {}).get("content"):
                    return item["text"]["content"]
            return ""

        mock.side_effect = mock_extract_text_func
        yield mock


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
    assert CalloutElement.match_notion({"type": "callout"})

    assert not CalloutElement.match_notion({"type": "paragraph"})
    assert not CalloutElement.match_notion({"type": "quote"})


def test_markdown_to_notion_simple():
    """Test conversion of simple callout to Notion."""
    result = CalloutElement.markdown_to_notion("[callout](Simple callout)")

    assert result is not None
    assert result["type"] == "callout"
    assert result["callout"]["color"] == "gray_background"
    assert result["callout"]["icon"]["type"] == "emoji"
    assert result["callout"]["icon"]["emoji"] == "💡"  # Default emoji


def test_markdown_to_notion_with_emoji():
    """Test conversion of callout with custom emoji."""
    result = CalloutElement.markdown_to_notion('[callout](Warning text "⚠️")')

    assert result is not None
    assert result["type"] == "callout"
    assert result["callout"]["icon"]["emoji"] == "⚠️"


def test_markdown_to_notion_invalid():
    """Test invalid markdown returns None."""
    result = CalloutElement.markdown_to_notion("Regular text")
    assert result is None


def test_notion_to_markdown_simple(mock_extract_text):
    """Test conversion of simple Notion callout to Markdown."""
    block = {
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": "Simple callout"}}],
            "icon": {"type": "emoji", "emoji": "💡"},
            "color": "gray_background",
        },
    }

    mock_extract_text.return_value = "Simple callout"
    result = CalloutElement.notion_to_markdown(block)

    assert result == "[callout](Simple callout)"


def test_notion_to_markdown_with_custom_emoji(mock_extract_text):
    """Test conversion of Notion callout with custom emoji."""
    block = {
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": "Warning message"}}],
            "icon": {"type": "emoji", "emoji": "⚠️"},
            "color": "gray_background",
        },
    }

    mock_extract_text.return_value = "Warning message"
    result = CalloutElement.notion_to_markdown(block)

    assert result == '[callout](Warning message "⚠️")'


def test_notion_to_markdown_invalid():
    """Test invalid Notion block returns None."""
    result = CalloutElement.notion_to_markdown({"type": "paragraph"})
    assert result is None


def test_is_multiline():
    """Test that callouts are recognized as single-line elements."""
    assert not CalloutElement.is_multiline()


def test_roundtrip_conversion(mock_extract_text):
    """Test that Markdown -> Notion -> Markdown preserves content."""
    test_cases = [
        "[callout](Simple callout)",
        '[callout](Warning message "⚠️")',
        '[callout](Info message "🔔")',
        '[callout](Success message "✅")',
    ]

    for original_markdown in test_cases:
        # Convert to Notion
        notion_block = CalloutElement.markdown_to_notion(original_markdown)
        assert (
            notion_block is not None
        ), f"Failed to convert {original_markdown} to Notion"

        # Extract expected text content
        expected_text = _extract_text_only(original_markdown)
        mock_extract_text.return_value = expected_text

        # Convert back to Markdown
        result_markdown = CalloutElement.notion_to_markdown(notion_block)
        assert result_markdown is not None, "Failed to convert back to Markdown"

        # Check that core content is preserved
        assert "[callout]" in result_markdown
        assert expected_text in result_markdown


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
    assert result["callout"]["icon"]["emoji"] == expected_emoji


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
    block = {"type": block_type}
    result = CalloutElement.match_notion(block)
    assert result == should_match


# Fixtures for common test data
@pytest.fixture
def simple_callout_block():
    """Fixture for simple callout block."""
    return {
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": "Test callout"}}],
            "icon": {"type": "emoji", "emoji": "💡"},
            "color": "gray_background",
        },
    }


@pytest.fixture
def warning_callout_block():
    """Fixture for warning callout block with custom emoji."""
    return {
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": "Warning message"}}],
            "icon": {"type": "emoji", "emoji": "⚠️"},
            "color": "gray_background",
        },
    }


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
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "gray_background",
                },
            },
        },
        {
            "input": '[callout](Fire alert "🔥")',
            "expected": {
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "🔥"},
                    "color": "gray_background",
                },
            },
        },
    ]

    for case in test_cases:
        result = CalloutElement.markdown_to_notion(case["input"])

        # Check basic structure
        assert result["type"] == case["expected"]["type"]

        # Check callout properties (excluding rich_text which is processed separately)
        for key, expected_value in case["expected"]["callout"].items():
            if key != "rich_text":
                assert (
                    result["callout"][key] == expected_value
                ), f"For '{case['input']}': {key} mismatch"


def _extract_text_only(markdown):
    """Helper function to extract pure text content from Markdown callout."""
    # Remove callout prefix and parentheses
    if markdown.startswith("[callout](") and markdown.endswith(")"):
        content = markdown[10:-1]  # Remove [callout]( and )

        # Remove emoji part if present (content in quotes)
        if '"' in content:
            # Split by quotes and take the first part (text before emoji)
            text_part = content.split('"')[0].strip()
            return text_part

        return content.strip()

    return markdown


def test_extract_text_only_helper():
    """Test the helper function for text extraction."""
    test_cases = [
        ("[callout](Simple text)", "Simple text"),
        ('[callout](Warning message "⚠️")', "Warning message"),
        ('[callout](Success "✅")', "Success"),
        ('[callout](Info alert "🔔")', "Info alert"),
    ]

    for markdown, expected_text in test_cases:
        result = _extract_text_only(markdown)
        assert result == expected_text, "Failed to extract text from {markdown}"
