from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, ColumnBlock, ColumnData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.column import ColumnRenderer


def _create_column_data(width_ratio: float | None = None) -> ColumnData:
    return ColumnData(width_ratio=width_ratio)


def _create_column_block(column_data: ColumnData | None) -> ColumnBlock:
    mock_obj = Mock(spec=Block)
    column_block = cast(ColumnBlock, mock_obj)
    column_block.type = BlockType.COLUMN
    column_block.column = column_data
    return column_block


@pytest.fixture
def column_renderer(mock_rich_text_markdown_converter: RichTextToMarkdownConverter) -> ColumnRenderer:
    return ColumnRenderer()


@pytest.mark.asyncio
async def test_column_block_should_be_handled(column_renderer: ColumnRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.COLUMN

    assert column_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_column_block_should_not_be_handled(column_renderer: ColumnRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not column_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_column_without_width_ratio_should_render_base_marker(
    column_renderer: ColumnRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    column_data = _create_column_data(width_ratio=None)
    block = _create_column_block(column_data)
    render_context.block = block

    await column_renderer._process(render_context)

    assert render_context.markdown_result == "::: column\n:::"


@pytest.mark.asyncio
async def test_column_with_width_ratio_should_include_width_in_marker(
    column_renderer: ColumnRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    column_data = _create_column_data(width_ratio=0.5)
    block = _create_column_block(column_data)
    render_context.block = block

    await column_renderer._process(render_context)

    assert render_context.markdown_result == "::: column 0.5\n:::"


@pytest.mark.asyncio
async def test_column_with_children_should_render_children_between_markers(
    column_renderer: ColumnRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="Column content here")
    column_data = _create_column_data(width_ratio=None)
    block = _create_column_block(column_data)
    render_context.block = block

    await column_renderer._process(render_context)

    assert render_context.markdown_result == "::: column\nColumn content here\n:::"


@pytest.mark.asyncio
async def test_column_with_indentation_should_indent_markers(
    column_renderer: ColumnRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    # Column renderer calls indent_text with spaces parameter for end marker
    # We need a mock that accepts both signatures
    def flexible_indent_text(text, spaces=None):
        return f"  {text}"

    render_context.render_children = AsyncMock(return_value="")
    render_context.indent_level = 1
    render_context.indent_text = Mock(side_effect=flexible_indent_text)
    column_data = _create_column_data(width_ratio=None)
    block = _create_column_block(column_data)
    render_context.block = block

    await column_renderer._process(render_context)

    # Both start and end markers should be indented
    assert render_context.markdown_result == "  ::: column\n  :::"
    # indent_text is called twice - once for start, once for end
    assert render_context.indent_text.call_count >= 1


@pytest.mark.asyncio
async def test_column_without_data_should_render_base_marker(
    column_renderer: ColumnRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    block = _create_column_block(None)
    render_context.block = block

    await column_renderer._process(render_context)

    assert render_context.markdown_result == "::: column\n:::"


@pytest.mark.asyncio
async def test_extract_column_start_with_width_ratio_should_include_width(
    column_renderer: ColumnRenderer,
) -> None:
    column_data = _create_column_data(width_ratio=0.75)
    block = _create_column_block(column_data)

    result = column_renderer._extract_column_start(block)

    assert result == "::: column 0.75"


@pytest.mark.asyncio
async def test_extract_column_start_without_width_ratio_should_return_base_marker(
    column_renderer: ColumnRenderer,
) -> None:
    column_data = _create_column_data(width_ratio=None)
    block = _create_column_block(column_data)

    result = column_renderer._extract_column_start(block)

    assert result == "::: column"


@pytest.mark.asyncio
async def test_extract_column_start_without_data_should_return_base_marker(
    column_renderer: ColumnRenderer,
) -> None:
    block = _create_column_block(None)

    result = column_renderer._extract_column_start(block)

    assert result == "::: column"


@pytest.mark.asyncio
async def test_column_marker_constants_should_be_correct(
    column_renderer: ColumnRenderer,
) -> None:
    assert column_renderer.BASE_START_MARKER == "::: column"
    assert column_renderer.END_MARKER == ":::"
