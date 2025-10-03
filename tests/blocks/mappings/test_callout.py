from unittest.mock import Mock

import pytest

from notionary.blocks.mappings.callout import (
    CalloutElement,
)
from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import BlockType, CalloutData
from notionary.shared.models.icon_models import EmojiIcon


def create_rich_text(content: str) -> RichText:
    """Helper to create RichText."""
    return RichText.from_plain_text(content)


@pytest.mark.asyncio
async def test_match_markdown():
    assert await CalloutElement.markdown_to_notion("[callout](Simple text)")
    assert await CalloutElement.markdown_to_notion('[callout](Text "🔥")')

    assert await CalloutElement.markdown_to_notion("Regular text") is None
    assert not await CalloutElement.markdown_to_notion("[callout]()")


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


@pytest.mark.asyncio
async def test_markdown_to_notion_simple():
    """Test einfache Markdown -> Notion Konvertierung."""
    result = await CalloutElement.markdown_to_notion("[callout](Test content)")

    assert result is not None
    assert result.callout.icon.emoji == "💡"  # Default
    assert result.callout.color == "gray_background"
    assert result.callout.rich_text[0].plain_text == "Test content"


@pytest.mark.asyncio
async def test_markdown_to_notion_with_emoji():
    """Test Markdown -> Notion mit Custom Emoji."""
    result = await CalloutElement.markdown_to_notion('[callout](Warning "⚠️")')

    assert result is not None
    assert result.callout.icon.emoji == "⚠️"
    assert result.callout.rich_text[0].plain_text == "Warning"


@pytest.mark.asyncio
async def test_markdown_to_notion_invalid():
    """Test ungültige Eingaben."""
    assert await CalloutElement.markdown_to_notion("Regular text") is None
    assert await CalloutElement.markdown_to_notion("[callout]()") is None


@pytest.mark.asyncio
async def test_notion_to_markdown_simple():
    """Test einfache Notion -> Markdown Konvertierung."""
    callout_data = CalloutData(
        rich_text=[create_rich_text("Test content")],
        icon=EmojiIcon(emoji="💡"),
        color="gray_background",
    )

    block = Mock()
    block.type = BlockType.CALLOUT
    block.callout = callout_data

    result = await CalloutElement.notion_to_markdown(block)
    assert result == "[callout](Test content)"


@pytest.mark.asyncio
async def test_notion_to_markdown_with_emoji():
    """Test Notion -> Markdown mit Custom Emoji."""
    callout_data = CalloutData(
        rich_text=[create_rich_text("Warning")],
        icon=EmojiIcon(emoji="⚠️"),
        color="gray_background",
    )

    block = Mock()
    block.type = BlockType.CALLOUT
    block.callout = callout_data

    result = await CalloutElement.notion_to_markdown(block)
    assert result == '[callout](Warning "⚠️")'


@pytest.mark.asyncio
async def test_notion_to_markdown_invalid():
    """Test ungültige Notion-Blöcke."""
    # Wrong type
    block = Mock()
    block.type = BlockType.PARAGRAPH
    block.callout = None
    assert await CalloutElement.notion_to_markdown(block) is None

    # No callout content
    block.type = BlockType.CALLOUT
    block.callout = None
    assert await CalloutElement.notion_to_markdown(block) is None


@pytest.mark.asyncio
async def test_roundtrip():
    """Test Roundtrip-Konvertierung."""
    test_cases = [
        "[callout](Simple text)",
        '[callout](Warning "⚠️")',
        '[callout](Success "✅")',
    ]

    for original in test_cases:
        # Markdown -> Notion
        notion_result = await CalloutElement.markdown_to_notion(original)
        assert notion_result is not None

        # Create block for notion_to_markdown
        block = Mock()
        block.type = BlockType.CALLOUT
        block.callout = notion_result.callout

        # Notion -> Markdown
        result = await CalloutElement.notion_to_markdown(block)
        assert result == original


@pytest.mark.asyncio
@pytest.mark.parametrize("emoji", ["🔥", "💡", "⚠️", "✅", "🚀"])
async def test_different_emojis(emoji):
    """Test verschiedene Emojis."""
    markdown = f'[callout](Test "{emoji}")'
    result = await CalloutElement.markdown_to_notion(markdown)

    assert result is not None
    assert result.callout.icon.emoji == emoji


@pytest.mark.asyncio
async def test_default_emoji_fallback():
    """Test Default-Emoji wird verwendet wenn keins angegeben."""
    result = await CalloutElement.markdown_to_notion("[callout](Test without emoji)")
    assert result.callout.icon.emoji == "💡"


def test_constants():
    """Test dass Konstanten verfügbar sind."""
    assert CalloutElement.DEFAULT_EMOJI == "💡"
    assert CalloutElement.DEFAULT_COLOR == "gray_background"
