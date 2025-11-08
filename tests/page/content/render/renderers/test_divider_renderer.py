from typing import cast
from unittest.mock import Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, DividerBlock
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.divider import DividerRenderer


def _create_divider_block() -> DividerBlock:
    mock_obj = Mock(spec=Block)
    divider_block = cast(DividerBlock, mock_obj)
    divider_block.type = BlockType.DIVIDER
    return divider_block


@pytest.fixture
def divider_renderer(syntax_registry: SyntaxDefinitionRegistry) -> DividerRenderer:
    return DividerRenderer(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_divider_block_should_be_handled(
    divider_renderer: DividerRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.DIVIDER

    assert divider_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_divider_block_should_not_be_handled(
    divider_renderer: DividerRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not divider_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_divider_should_render_horizontal_rule(
    divider_renderer: DividerRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_divider_block()
    render_context.block = block

    await divider_renderer._process(render_context)

    assert render_context.markdown_result == "---"


@pytest.mark.asyncio
async def test_divider_with_indent_level_should_indent_output(
    divider_renderer: DividerRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_divider_block()
    render_context.block = block
    render_context.indent_level = 1

    await divider_renderer._process(render_context)

    render_context.indent_text.assert_called_once()
    assert render_context.markdown_result == "  ---"
