from typing import cast
from unittest.mock import Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, BreadcrumbBlock
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.breadcrumb import BreadcrumbRenderer


def _create_breadcrumb_block() -> BreadcrumbBlock:
    mock_obj = Mock(spec=Block)
    breadcrumb_block = cast(BreadcrumbBlock, mock_obj)
    breadcrumb_block.type = BlockType.BREADCRUMB
    return breadcrumb_block


@pytest.fixture
def breadcrumb_renderer(
    syntax_registry: SyntaxDefinitionRegistry,
) -> BreadcrumbRenderer:
    return BreadcrumbRenderer(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_breadcrumb_block_should_be_handled(
    breadcrumb_renderer: BreadcrumbRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.BREADCRUMB

    assert breadcrumb_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_breadcrumb_block_should_not_be_handled(
    breadcrumb_renderer: BreadcrumbRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not breadcrumb_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_breadcrumb_should_render_breadcrumb_markdown(
    breadcrumb_renderer: BreadcrumbRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_breadcrumb_block()
    render_context.block = block

    await breadcrumb_renderer._process(render_context)

    assert render_context.markdown_result == "[breadcrumb]"


@pytest.mark.asyncio
async def test_breadcrumb_with_indent_level_should_indent_output(
    breadcrumb_renderer: BreadcrumbRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_breadcrumb_block()
    render_context.block = block
    render_context.indent_level = 1

    await breadcrumb_renderer._process(render_context)

    render_context.indent_text.assert_called_once()
    assert render_context.markdown_result == "  [breadcrumb]"
