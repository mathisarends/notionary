from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, ColumnListBlock
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.column_list import ColumnListRenderer


def _create_column_list_block() -> ColumnListBlock:
    mock_obj = Mock(spec=Block)
    column_list_block = cast(ColumnListBlock, mock_obj)
    column_list_block.type = BlockType.COLUMN_LIST
    column_list_block.column_list = Mock()
    return column_list_block


@pytest.fixture
def column_list_renderer(mock_rich_text_markdown_converter: RichTextToMarkdownConverter) -> ColumnListRenderer:
    return ColumnListRenderer()


@pytest.mark.asyncio
async def test_column_list_block_should_be_handled(column_list_renderer: ColumnListRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.COLUMN_LIST

    assert column_list_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_column_list_block_should_not_be_handled(
    column_list_renderer: ColumnListRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not column_list_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_column_list_without_children_should_render_markers(
    column_list_renderer: ColumnListRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    block = _create_column_list_block()
    render_context.block = block

    await column_list_renderer._process(render_context)

    assert render_context.markdown_result == "::: columns\n:::"


@pytest.mark.asyncio
async def test_column_list_with_children_should_render_children_between_markers(
    column_list_renderer: ColumnListRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="::: column\nColumn 1\n:::\n::: column\nColumn 2\n:::")
    block = _create_column_list_block()
    render_context.block = block

    await column_list_renderer._process(render_context)

    expected = "::: columns\n::: column\nColumn 1\n:::\n::: column\nColumn 2\n:::\n:::"
    assert render_context.markdown_result == expected


@pytest.mark.asyncio
async def test_column_list_with_indentation_should_indent_markers(
    column_list_renderer: ColumnListRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    render_context.indent_level = 1
    block = _create_column_list_block()
    render_context.block = block

    await column_list_renderer._process(render_context)

    # Mock indent_text adds 2 spaces
    assert render_context.markdown_result == "  ::: columns\n  :::"
    assert render_context.indent_text.call_count == 2


@pytest.mark.asyncio
async def test_column_list_marker_constants_should_be_correct(
    column_list_renderer: ColumnListRenderer,
) -> None:
    # The column list syntax is now in SyntaxRegistry, not as a constant on the renderer
    syntax = column_list_renderer._syntax_registry.get_column_list_syntax()
    assert syntax.start_delimiter == "::: columns"
    assert syntax.end_delimiter == ":::"
