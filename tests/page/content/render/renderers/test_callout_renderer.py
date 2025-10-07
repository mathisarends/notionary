from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, CalloutBlock, CalloutData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.callout import CalloutRenderer
from notionary.shared.models.icon_models import EmojiIcon


def _create_emoji_icon(emoji: str) -> EmojiIcon:
    return EmojiIcon(emoji=emoji)


def _create_callout_data(rich_text: list[RichText], icon: EmojiIcon | None = None) -> CalloutData:
    return CalloutData(rich_text=rich_text, icon=icon)


def _create_callout_block(callout_data: CalloutData | None) -> CalloutBlock:
    mock_obj = Mock(spec=Block)
    callout_block = cast(CalloutBlock, mock_obj)
    callout_block.type = BlockType.CALLOUT
    callout_block.callout = callout_data
    return callout_block


@pytest.fixture
def callout_renderer(mock_rich_text_markdown_converter: RichTextToMarkdownConverter) -> CalloutRenderer:
    return CalloutRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_callout_block_should_be_handled(callout_renderer: CalloutRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.CALLOUT

    assert callout_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_callout_block_should_not_be_handled(callout_renderer: CalloutRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not callout_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_callout_with_text_should_render_markdown_callout(
    callout_renderer: CalloutRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Important note")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Important note")

    callout_data = _create_callout_data(rich_text)
    block = _create_callout_block(callout_data)
    render_context.block = block

    await callout_renderer._process(render_context)

    assert "::: callout" in render_context.markdown_result
    assert "Important note" in render_context.markdown_result
    assert ":::" in render_context.markdown_result


@pytest.mark.asyncio
async def test_callout_with_emoji_should_include_emoji_in_markdown(
    callout_renderer: CalloutRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Warning message")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Warning message")
    emoji_icon = _create_emoji_icon("⚠️")

    callout_data = _create_callout_data(rich_text, emoji_icon)
    block = _create_callout_block(callout_data)
    render_context.block = block

    await callout_renderer._process(render_context)

    assert "::: callout ⚠️" in render_context.markdown_result
    assert "Warning message" in render_context.markdown_result


@pytest.mark.asyncio
async def test_callout_with_empty_content_should_render_empty_string(
    callout_renderer: CalloutRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="")

    callout_data = _create_callout_data([])
    block = _create_callout_block(callout_data)
    render_context.block = block

    await callout_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_callout_with_missing_data_should_render_empty_string(
    callout_renderer: CalloutRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_callout_block(None)
    render_context.block = block

    await callout_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_callout_with_children_should_render_children(
    callout_renderer: CalloutRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Parent content")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Parent content")

    callout_data = _create_callout_data(rich_text)
    block = _create_callout_block(callout_data)
    render_context.block = block
    render_context.render_children = AsyncMock(return_value="Child content")

    await callout_renderer._process(render_context)

    render_context.render_children.assert_called_once()
    assert "::: callout" in render_context.markdown_result
    assert "Parent content" in render_context.markdown_result
    assert "Child content" in render_context.markdown_result
    assert ":::" in render_context.markdown_result


@pytest.mark.asyncio
async def test_extract_callout_icon_with_emoji_should_return_emoji(
    callout_renderer: CalloutRenderer,
) -> None:
    emoji_icon = _create_emoji_icon("🔥")
    callout_data = _create_callout_data([RichText.from_plain_text("Test")], emoji_icon)
    block = _create_callout_block(callout_data)

    icon = await callout_renderer._extract_callout_icon(block)

    assert icon == "🔥"


@pytest.mark.asyncio
async def test_extract_callout_icon_without_icon_should_return_empty_string(
    callout_renderer: CalloutRenderer,
) -> None:
    callout_data = _create_callout_data([RichText.from_plain_text("Test")])
    block = _create_callout_block(callout_data)

    icon = await callout_renderer._extract_callout_icon(block)

    assert icon == ""


@pytest.mark.asyncio
async def test_extract_callout_content_with_valid_data_should_return_markdown(
    callout_renderer: CalloutRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Test content")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Test content")

    callout_data = _create_callout_data(rich_text)
    block = _create_callout_block(callout_data)

    content = await callout_renderer._extract_callout_content(block)

    assert content == "Test content"


@pytest.mark.asyncio
async def test_extract_callout_content_without_data_should_return_empty_string(
    callout_renderer: CalloutRenderer,
) -> None:
    block = _create_callout_block(None)

    content = await callout_renderer._extract_callout_content(block)

    assert content == ""
