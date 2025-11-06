# tests/page/content/render/renderers/test_column_renderer.py
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, ColumnBlock, ColumnData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.column import ColumnRenderer
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


def _create_column_data(width_ratio: float | None = None) -> ColumnData:
    return ColumnData(width_ratio=width_ratio)


def _create_column_block(column_data: ColumnData | None) -> ColumnBlock:
    mock_obj = Mock(spec=Block)
    column_block = cast(ColumnBlock, mock_obj)
    column_block.type = BlockType.COLUMN
    column_block.column = column_data
    return column_block


@pytest.fixture
def column_renderer(syntax_registry: SyntaxDefinitionRegistry) -> ColumnRenderer:
    return ColumnRenderer(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_column_block_should_be_handled(
    column_renderer: ColumnRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.COLUMN

    assert column_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_column_block_should_not_be_handled(
    column_renderer: ColumnRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not column_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_column_without_width_ratio_should_render_base_marker(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    column_data = _create_column_data(width_ratio=None)
    block = _create_column_block(column_data)
    render_context.block = block
    render_context.indent_level = 0

    await column_renderer._process(render_context)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    assert render_context.markdown_result == delimiter


@pytest.mark.asyncio
async def test_column_with_width_ratio_should_include_width_in_marker(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    column_data = _create_column_data(width_ratio=0.5)
    block = _create_column_block(column_data)
    render_context.block = block
    render_context.indent_level = 0

    await column_renderer._process(render_context)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    expected = f"{delimiter} 0.5"
    assert render_context.markdown_result == expected


@pytest.mark.asyncio
async def test_column_with_children_should_render_children_below_marker(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="Column content here")
    column_data = _create_column_data(width_ratio=None)
    block = _create_column_block(column_data)
    render_context.block = block
    render_context.indent_level = 0

    await column_renderer._process(render_context)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    expected = f"{delimiter}\nColumn content here"
    assert render_context.markdown_result == expected


@pytest.mark.asyncio
async def test_column_with_indentation_should_indent_marker(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    render_context.indent_level = 1
    column_data = _create_column_data(width_ratio=None)
    block = _create_column_block(column_data)
    render_context.block = block

    await column_renderer._process(render_context)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    expected = f"    {delimiter}"
    assert render_context.markdown_result == expected


@pytest.mark.asyncio
async def test_column_without_data_should_render_base_marker(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
    render_context: MarkdownRenderingContext,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    block = _create_column_block(None)
    render_context.block = block
    render_context.indent_level = 0

    await column_renderer._process(render_context)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    assert render_context.markdown_result == delimiter


@pytest.mark.asyncio
async def test_column_should_increase_indent_level_for_children(
    column_renderer: ColumnRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    original_indent = 0
    render_context.indent_level = original_indent

    async def mock_render_children():
        assert render_context.indent_level == original_indent + 1
        return "child content"

    render_context.render_children = AsyncMock(side_effect=mock_render_children)
    column_data = _create_column_data()
    block = _create_column_block(column_data)
    render_context.block = block

    await column_renderer._process(render_context)

    assert render_context.indent_level == original_indent


def test_build_column_start_tag_with_width_ratio_should_include_width(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    column_data = _create_column_data(width_ratio=0.75)
    block = _create_column_block(column_data)

    result = column_renderer._build_column_start_tag(block)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    assert result == f"{delimiter} 0.75"


def test_build_column_start_tag_without_width_ratio_should_return_base_marker(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    column_data = _create_column_data(width_ratio=None)
    block = _create_column_block(column_data)

    result = column_renderer._build_column_start_tag(block)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    assert result == delimiter


def test_build_column_start_tag_without_data_should_return_base_marker(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    block = _create_column_block(None)

    result = column_renderer._build_column_start_tag(block)

    delimiter = syntax_registry.get_column_syntax().start_delimiter
    assert result == delimiter


def test_column_marker_should_be_from_syntax_registry(
    column_renderer: ColumnRenderer,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = column_renderer._syntax_registry.get_column_syntax()
    delimiter = syntax_registry.get_column_syntax().start_delimiter
    assert syntax.start_delimiter == delimiter
