from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import (
    Block,
    SyncedBlockBlock,
    SyncedBlockData,
    SyncedFromBlock,
)
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.synced_block import SyncedBlockRenderer
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


def _create_synced_block_data(
    synced_from: SyncedFromBlock | None = None,
) -> SyncedBlockData:
    return SyncedBlockData(synced_from=synced_from)


def _create_synced_block(
    synced_data: SyncedBlockData | None,
) -> SyncedBlockBlock:
    mock_obj = Mock(spec=Block)
    synced_block = cast(SyncedBlockBlock, mock_obj)
    synced_block.type = BlockType.SYNCED_BLOCK
    synced_block.synced_block = synced_data
    return synced_block


@pytest.fixture
def synced_block_renderer(
    syntax_registry: SyntaxDefinitionRegistry,
) -> SyncedBlockRenderer:
    return SyncedBlockRenderer(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_synced_block_should_be_handled(
    synced_block_renderer: SyncedBlockRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.SYNCED_BLOCK

    assert synced_block_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_synced_block_should_not_be_handled(
    synced_block_renderer: SyncedBlockRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not synced_block_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_original_synced_block_without_children_should_render_with_placeholder(
    synced_block_renderer: SyncedBlockRenderer,
    render_context: MarkdownRenderingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    synced_data = _create_synced_block_data(synced_from=None)
    block = _create_synced_block(synced_data)
    render_context.block = block
    render_context.render_children = AsyncMock(return_value="")

    await synced_block_renderer._process(render_context)

    assert f"{syntax.start_delimiter} Synced Block" in render_context.markdown_result
    assert "no content available" in render_context.markdown_result


@pytest.mark.asyncio
async def test_original_synced_block_with_children_should_render_children(
    synced_block_renderer: SyncedBlockRenderer,
    render_context: MarkdownRenderingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    synced_data = _create_synced_block_data(synced_from=None)
    block = _create_synced_block(synced_data)
    render_context.block = block
    render_context.render_children = AsyncMock(return_value="Child content")

    await synced_block_renderer._process(render_context)

    render_context.render_children.assert_called_once()
    assert f"{syntax.start_delimiter} Synced Block" in render_context.markdown_result
    assert "Child content" in render_context.markdown_result


@pytest.mark.asyncio
async def test_duplicate_synced_block_without_children_should_render_reference_only(
    synced_block_renderer: SyncedBlockRenderer,
    render_context: MarkdownRenderingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    synced_from = SyncedFromBlock(block_id="abc-123-def-456-789")
    synced_data = _create_synced_block_data(synced_from=synced_from)
    block = _create_synced_block(synced_data)
    render_context.block = block
    render_context.render_children = AsyncMock(return_value="")

    await synced_block_renderer._process(render_context)

    assert (
        f"{syntax.start_delimiter} Synced from: abc-123-def-456-789"
        in render_context.markdown_result
    )
    assert "no content available" not in render_context.markdown_result


@pytest.mark.asyncio
async def test_duplicate_synced_block_with_children_should_render_reference_and_children(
    synced_block_renderer: SyncedBlockRenderer,
    render_context: MarkdownRenderingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    syntax = syntax_registry.get_synced_block_syntax()
    synced_from = SyncedFromBlock(block_id="def-456-abc-789-012")
    synced_data = _create_synced_block_data(synced_from=synced_from)
    block = _create_synced_block(synced_data)
    render_context.block = block
    render_context.render_children = AsyncMock(return_value="Synced child content")

    await synced_block_renderer._process(render_context)

    render_context.render_children.assert_called_once()
    assert (
        f"{syntax.start_delimiter} Synced from: def-456-abc-789-012"
        in render_context.markdown_result
    )
    assert "Synced child content" in render_context.markdown_result


@pytest.mark.asyncio
async def test_synced_block_with_missing_data_should_not_render(
    synced_block_renderer: SyncedBlockRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_synced_block(None)
    render_context.block = block

    await synced_block_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_synced_block_with_indent_level_should_indent_marker(
    synced_block_renderer: SyncedBlockRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    synced_data = _create_synced_block_data(synced_from=None)
    block = _create_synced_block(synced_data)
    render_context.block = block
    render_context.indent_level = 1
    render_context.render_children = AsyncMock(return_value="")

    await synced_block_renderer._process(render_context)

    assert render_context.indent_text.call_count >= 1


@pytest.mark.asyncio
async def test_duplicate_synced_block_with_indent_level_should_indent_reference(
    synced_block_renderer: SyncedBlockRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    synced_from = SyncedFromBlock(block_id="abc-def-123-456-789")
    synced_data = _create_synced_block_data(synced_from=synced_from)
    block = _create_synced_block(synced_data)
    render_context.block = block
    render_context.indent_level = 2
    render_context.render_children = AsyncMock(return_value="")

    await synced_block_renderer._process(render_context)

    assert render_context.indent_text.call_count >= 1
