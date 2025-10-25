from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, ColumnListBlock
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.column_list import ColumnListRenderer
from notionary.page.content.syntax import SyntaxDefinitionRegistry


def _create_column_list_block() -> ColumnListBlock:
    mock_obj = Mock(spec=Block)
    column_list_block = cast(ColumnListBlock, mock_obj)
    column_list_block.type = BlockType.COLUMN_LIST
    column_list_block.column_list = Mock()
    return column_list_block


@pytest.fixture
def column_list_renderer() -> ColumnListRenderer:
    return ColumnListRenderer()


@pytest.fixture
def syntax_registry() -> SyntaxDefinitionRegistry:
    return SyntaxDefinitionRegistry()


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
async def test_column_list_without_children_should_render_start_marker(
    column_list_renderer: ColumnListRenderer,
    render_context: MarkdownRenderingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    block = _create_column_list_block()
    render_context.block = block
    render_context.indent_level = 0

    await column_list_renderer._process(render_context)

    expected_delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    assert render_context.markdown_result == expected_delimiter


@pytest.mark.asyncio
async def test_column_list_with_children_should_render_children_below_marker(
    column_list_renderer: ColumnListRenderer,
    render_context: MarkdownRenderingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    render_context.render_children = AsyncMock(return_value="::: column\nColumn 1\n::: column\nColumn 2")
    block = _create_column_list_block()
    render_context.block = block
    render_context.indent_level = 0

    await column_list_renderer._process(render_context)

    delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    expected = f"{delimiter}\n::: column\nColumn 1\n::: column\nColumn 2"
    assert render_context.markdown_result == expected


@pytest.mark.asyncio
async def test_column_list_with_indentation_should_indent_start_marker(
    column_list_renderer: ColumnListRenderer,
    render_context: MarkdownRenderingContext,
    syntax_registry: SyntaxDefinitionRegistry,
    indent: str,
) -> None:
    render_context.render_children = AsyncMock(return_value="")
    render_context.indent_level = 1
    block = _create_column_list_block()
    render_context.block = block

    await column_list_renderer._process(render_context)

    delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    assert render_context.markdown_result == f"{indent}{delimiter}"


@pytest.mark.asyncio
async def test_column_list_should_increase_indent_level_for_children(
    column_list_renderer: ColumnListRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    original_indent = 0
    render_context.indent_level = original_indent

    async def mock_render_children():
        assert render_context.indent_level == original_indent + 1
        return "child content"

    render_context.render_children = AsyncMock(side_effect=mock_render_children)
    block = _create_column_list_block()
    render_context.block = block

    await column_list_renderer._process(render_context)

    assert render_context.indent_level == original_indent
