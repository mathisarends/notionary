from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, QuoteBlock, QuoteData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.quote import QuoteRenderer
from notionary.rich_text.models import RichText
from notionary.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)


def _create_quote_data(rich_text: list[RichText]) -> QuoteData:
    return QuoteData(rich_text=rich_text)


def _create_quote_block(quote_data: QuoteData | None) -> QuoteBlock:
    mock_obj = Mock(spec=Block)
    quote_block = cast(QuoteBlock, mock_obj)
    quote_block.type = BlockType.QUOTE
    quote_block.quote = quote_data
    return quote_block


@pytest.fixture
def quote_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> QuoteRenderer:
    return QuoteRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_quote_block_should_be_handled(
    quote_renderer: QuoteRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.QUOTE

    assert quote_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_quote_block_should_not_be_handled(
    quote_renderer: QuoteRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not quote_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_quote_with_single_line_should_render_blockquote(
    quote_renderer: QuoteRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("This is a quote")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="This is a quote"
    )

    quote_data = _create_quote_data(rich_text)
    block = _create_quote_block(quote_data)
    render_context.block = block

    await quote_renderer._process(render_context)

    assert render_context.markdown_result == "> This is a quote"


@pytest.mark.asyncio
async def test_quote_with_multiple_lines_should_prefix_each_line(
    quote_renderer: QuoteRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Line one\nLine two\nLine three")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Line one\nLine two\nLine three"
    )

    quote_data = _create_quote_data(rich_text)
    block = _create_quote_block(quote_data)
    render_context.block = block

    await quote_renderer._process(render_context)

    assert "> Line one" in render_context.markdown_result
    assert "> Line two" in render_context.markdown_result
    assert "> Line three" in render_context.markdown_result


@pytest.mark.asyncio
async def test_quote_with_empty_rich_text_should_render_empty_string(
    quote_renderer: QuoteRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value=None)

    quote_data = _create_quote_data([])
    block = _create_quote_block(quote_data)
    render_context.block = block

    await quote_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_quote_with_missing_data_should_render_empty_string(
    quote_renderer: QuoteRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_quote_block(None)
    render_context.block = block

    await quote_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_quote_with_indent_level_should_indent_output(
    quote_renderer: QuoteRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Indented quote")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Indented quote"
    )

    quote_data = _create_quote_data(rich_text)
    block = _create_quote_block(quote_data)
    render_context.block = block
    render_context.indent_level = 1

    await quote_renderer._process(render_context)

    render_context.indent_text.assert_called_once()


@pytest.mark.asyncio
async def test_quote_with_children_should_render_children_with_indent(
    quote_renderer: QuoteRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Parent quote")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Parent quote"
    )

    quote_data = _create_quote_data(rich_text)
    block = _create_quote_block(quote_data)
    render_context.block = block
    render_context.render_children_with_additional_indent = AsyncMock(
        return_value="  Child content"
    )

    await quote_renderer._process(render_context)

    render_context.render_children_with_additional_indent.assert_called_once_with(1)
    assert "> Parent quote" in render_context.markdown_result
    assert "Child content" in render_context.markdown_result


@pytest.mark.asyncio
async def test_convert_quote_with_valid_data_should_return_markdown(
    quote_renderer: QuoteRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Test quote")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Test quote")

    quote_data = _create_quote_data(rich_text)
    block = _create_quote_block(quote_data)

    result = await quote_renderer._convert_quote_to_markdown(block)

    assert result == "Test quote"


@pytest.mark.asyncio
async def test_convert_quote_without_data_should_return_none(
    quote_renderer: QuoteRenderer,
) -> None:
    block = _create_quote_block(None)

    result = await quote_renderer._convert_quote_to_markdown(block)

    assert result is None
