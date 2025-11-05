from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, ToggleBlock, ToggleData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.toggle import ToggleRenderer
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.schemas import RichText


def _create_toggle_data(rich_text: list[RichText]) -> ToggleData:
    return ToggleData(rich_text=rich_text)


def _create_toggle_block(toggle_data: ToggleData | None) -> ToggleBlock:
    mock_obj = Mock(spec=Block)
    toggle_block = cast(ToggleBlock, mock_obj)
    toggle_block.type = BlockType.TOGGLE
    toggle_block.toggle = toggle_data
    return toggle_block


@pytest.fixture
def toggle_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> ToggleRenderer:
    return ToggleRenderer(
        rich_text_markdown_converter=mock_rich_text_markdown_converter
    )


@pytest.mark.asyncio
async def test_toggle_block_should_be_handled(
    toggle_renderer: ToggleRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.TOGGLE

    assert toggle_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_toggle_block_should_not_be_handled(
    toggle_renderer: ToggleRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not toggle_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_toggle_with_title_should_render_markdown_toggle(
    toggle_renderer: ToggleRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Toggle Title")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Toggle Title"
    )

    toggle_data = _create_toggle_data(rich_text)
    block = _create_toggle_block(toggle_data)
    render_context.block = block

    await toggle_renderer._process(render_context)

    # Should only have start delimiter without end delimiter
    assert "+++ Toggle Title" in render_context.markdown_result
    assert not render_context.markdown_result.strip().endswith("+++")


@pytest.mark.asyncio
async def test_toggle_with_children_should_render_children_between_delimiters(
    toggle_renderer: ToggleRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Toggle with content")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Toggle with content"
    )

    toggle_data = _create_toggle_data(rich_text)
    block = _create_toggle_block(toggle_data)
    render_context.block = block
    render_context.render_children = AsyncMock(return_value="Child content")

    await toggle_renderer._process(render_context)

    render_context.render_children.assert_called_once()
    assert "+++ Toggle with content" in render_context.markdown_result
    assert "Child content" in render_context.markdown_result
    # No end delimiter expected
    assert not render_context.markdown_result.strip().endswith("+++")


@pytest.mark.asyncio
async def test_toggle_with_empty_title_should_not_render(
    toggle_renderer: ToggleRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="")

    toggle_data = _create_toggle_data([])
    block = _create_toggle_block(toggle_data)
    render_context.block = block

    await toggle_renderer._process(render_context)

    # The function returns early, so markdown_result might not be set
    # or might be empty depending on implementation
    assert render_context.markdown_result in ["", None]


@pytest.mark.asyncio
async def test_toggle_with_missing_data_should_not_render(
    toggle_renderer: ToggleRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_toggle_block(None)
    render_context.block = block

    await toggle_renderer._process(render_context)

    assert render_context.markdown_result in ["", None]


@pytest.mark.asyncio
async def test_toggle_with_indent_level_should_indent_delimiters(
    toggle_renderer: ToggleRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Indented toggle")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Indented toggle"
    )

    toggle_data = _create_toggle_data(rich_text)
    block = _create_toggle_block(toggle_data)
    render_context.block = block
    render_context.indent_level = 1

    await toggle_renderer._process(render_context)

    # Should be called once for the start delimiter only
    assert render_context.indent_text.call_count == 1


@pytest.mark.asyncio
async def test_extract_toggle_title_with_valid_data_should_return_markdown(
    toggle_renderer: ToggleRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Test title")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Test title")

    toggle_data = _create_toggle_data(rich_text)
    block = _create_toggle_block(toggle_data)

    title = await toggle_renderer._extract_toggle_title(block)

    assert title == "Test title"


@pytest.mark.asyncio
async def test_extract_toggle_title_without_data_should_return_empty_string(
    toggle_renderer: ToggleRenderer,
) -> None:
    block = _create_toggle_block(None)

    title = await toggle_renderer._extract_toggle_title(block)

    assert title == ""
