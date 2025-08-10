"""
Minimale Tests für CalloutElement - nur das Wesentliche.
"""

import pytest
from unittest.mock import Mock

from notionary.blocks.callout.callout_element import CalloutElement
from notionary.blocks.callout.callout_models import CalloutBlock
from notionary.blocks.block_types import BlockType
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.models.icon_types import EmojiIcon


def create_rich_text(content: str) -> RichTextObject:
    """Helper to create RichTextObject."""
    return RichTextObject.from_plain_text(content)


def test_match_markdown():
    """Test Markdown-Erkennung."""
    # Valid
    assert CalloutElement.markdown_to_notion("[callout](Simple text)")
    assert CalloutElement.markdown_to_notion('[callout](Text "🔥")')

    # Invalid
    assert CalloutElement.markdown_to_notion("Regular text") is None
    assert not CalloutElement.markdown_to_notion("[callout]()")


def test_match_notion():
    """Test Notion-Block-Erkennung."""
    # Valid callout block
    block = Mock()
    block.type = BlockType.CALLOUT
    block.callout = Mock()
    assert CalloutElement.match_notion(block)

    # Invalid - wrong type
    block.type = BlockType.PARAGRAPH
    assert not CalloutElement.match_notion(block)

    # Invalid - no callout content
    block.type = BlockType.CALLOUT
    block.callout = None
    assert not CalloutElement.match_notion(block)


def test_markdown_to_notion_simple():
    """Test einfache Markdown -> Notion Konvertierung."""
    result = CalloutElement.markdown_to_notion("[callout](Test content)")

    assert result is not None
    assert result.callout.icon.emoji == "💡"  # Default
    assert result.callout.color == "gray_background"
    assert result.callout.rich_text[0].plain_text == "Test content"


def test_markdown_to_notion_with_emoji():
    """Test Markdown -> Notion mit Custom Emoji."""
    result = CalloutElement.markdown_to_notion('[callout](Warning "⚠️")')

    assert result is not None
    assert result.callout.icon.emoji == "⚠️"
    assert result.callout.rich_text[0].plain_text == "Warning"


def test_markdown_to_notion_invalid():
    """Test ungültige Eingaben."""
    assert CalloutElement.markdown_to_notion("Regular text") is None
    assert CalloutElement.markdown_to_notion("[callout]()") is None


def test_notion_to_markdown_simple():
    """Test einfache Notion -> Markdown Konvertierung."""
    callout_data = CalloutBlock(
        rich_text=[create_rich_text("Test content")],
        icon=EmojiIcon(emoji="💡"),
        color="gray_background",
    )

    block = Mock()
    block.type = BlockType.CALLOUT
    block.callout = callout_data

    result = CalloutElement.notion_to_markdown(block)
    assert result == "[callout](Test content)"


def test_notion_to_markdown_with_emoji():
    """Test Notion -> Markdown mit Custom Emoji."""
    callout_data = CalloutBlock(
        rich_text=[create_rich_text("Warning")],
        icon=EmojiIcon(emoji="⚠️"),
        color="gray_background",
    )

    block = Mock()
    block.type = BlockType.CALLOUT
    block.callout = callout_data

    result = CalloutElement.notion_to_markdown(block)
    assert result == '[callout](Warning "⚠️")'


def test_notion_to_markdown_invalid():
    """Test ungültige Notion-Blöcke."""
    # Wrong type
    block = Mock()
    block.type = BlockType.PARAGRAPH
    block.callout = None
    assert CalloutElement.notion_to_markdown(block) is None

    # No callout content
    block.type = BlockType.CALLOUT
    block.callout = None
    assert CalloutElement.notion_to_markdown(block) is None


def test_roundtrip():
    """Test Roundtrip-Konvertierung."""
    test_cases = [
        "[callout](Simple text)",
        '[callout](Warning "⚠️")',
        '[callout](Success "✅")',
    ]

    for original in test_cases:
        # Markdown -> Notion
        notion_result = CalloutElement.markdown_to_notion(original)
        assert notion_result is not None

        # Create block for notion_to_markdown
        block = Mock()
        block.type = BlockType.CALLOUT
        block.callout = notion_result.callout

        # Notion -> Markdown
        result = CalloutElement.notion_to_markdown(block)
        assert result == original


@pytest.mark.parametrize("emoji", ["🔥", "💡", "⚠️", "✅", "🚀"])
def test_different_emojis(emoji):
    """Test verschiedene Emojis."""
    markdown = f'[callout](Test "{emoji}")'
    result = CalloutElement.markdown_to_notion(markdown)

    assert result is not None
    assert result.callout.icon.emoji == emoji


def test_default_emoji_fallback():
    """Test Default-Emoji wird verwendet wenn keins angegeben."""
    result = CalloutElement.markdown_to_notion("[callout](Test without emoji)")
    assert result.callout.icon.emoji == "💡"


def test_constants():
    """Test dass Konstanten verfügbar sind."""
    assert CalloutElement.DEFAULT_EMOJI == "💡"
    assert CalloutElement.DEFAULT_COLOR == "gray_background"
