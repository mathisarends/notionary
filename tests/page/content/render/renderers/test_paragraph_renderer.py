from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, ParagraphBlock, ParagraphData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.paragraph import ParagraphRenderer
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.schemas import RichText


def _create_paragraph_data(rich_text: list[RichText]) -> ParagraphData:
    return ParagraphData(rich_text=rich_text)


def _create_paragraph_block(paragraph_data: ParagraphData | None) -> ParagraphBlock:
    mock_obj = Mock(spec=Block)
    paragraph_block = cast(ParagraphBlock, mock_obj)
    paragraph_block.type = BlockType.PARAGRAPH
    paragraph_block.paragraph = paragraph_data
    return paragraph_block


@pytest.fixture
def paragraph_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> ParagraphRenderer:
    return ParagraphRenderer(
        rich_text_markdown_converter=mock_rich_text_markdown_converter
    )


@pytest.mark.asyncio
async def test_paragraph_block_should_be_handled(
    paragraph_renderer: ParagraphRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert paragraph_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_paragraph_block_should_not_be_handled(
    paragraph_renderer: ParagraphRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.HEADING_1

    assert not paragraph_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_paragraph_with_text_should_render_markdown(
    paragraph_renderer: ParagraphRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("This is a paragraph")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="This is a paragraph"
    )

    paragraph_data = _create_paragraph_data(rich_text)
    block = _create_paragraph_block(paragraph_data)
    render_context.block = block

    await paragraph_renderer._process(render_context)

    assert render_context.markdown_result == "This is a paragraph"


@pytest.mark.asyncio
async def test_paragraph_with_empty_rich_text_should_render_empty_string(
    paragraph_renderer: ParagraphRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value=None)

    paragraph_data = _create_paragraph_data([])
    block = _create_paragraph_block(paragraph_data)
    render_context.block = block

    await paragraph_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_paragraph_with_missing_data_should_render_empty_string(
    paragraph_renderer: ParagraphRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_paragraph_block(None)
    render_context.block = block

    await paragraph_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_paragraph_with_indent_level_should_indent_output(
    paragraph_renderer: ParagraphRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Indented paragraph")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Indented paragraph"
    )

    paragraph_data = _create_paragraph_data(rich_text)
    block = _create_paragraph_block(paragraph_data)
    render_context.block = block
    render_context.indent_level = 1

    await paragraph_renderer._process(render_context)

    # Mock indent_text adds 2 spaces
    assert render_context.markdown_result == "  Indented paragraph"
    render_context.indent_text.assert_called_once_with("Indented paragraph")


@pytest.mark.asyncio
async def test_paragraph_with_children_should_render_children_with_indent(
    paragraph_renderer: ParagraphRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Parent paragraph")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Parent paragraph"
    )
    render_context.render_children_with_additional_indent = AsyncMock(
        return_value="    Child content"
    )

    paragraph_data = _create_paragraph_data(rich_text)
    block = _create_paragraph_block(paragraph_data)
    render_context.block = block

    await paragraph_renderer._process(render_context)

    assert render_context.markdown_result == "Parent paragraph\n    Child content"
    render_context.render_children_with_additional_indent.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_convert_paragraph_with_valid_data_should_return_markdown(
    paragraph_renderer: ParagraphRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Test paragraph")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Test paragraph"
    )

    paragraph_data = _create_paragraph_data(rich_text)
    block = _create_paragraph_block(paragraph_data)

    result = await paragraph_renderer._convert_paragraph_to_markdown(block)

    assert result == "Test paragraph"


@pytest.mark.asyncio
async def test_convert_paragraph_without_data_should_return_none(
    paragraph_renderer: ParagraphRenderer,
) -> None:
    block = _create_paragraph_block(None)

    result = await paragraph_renderer._convert_paragraph_to_markdown(block)

    assert result is None
