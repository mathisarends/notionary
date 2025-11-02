from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, TableOfContentsBlock
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.table_of_contents import (
    TableOfContentsRenderer,
)
from notionary.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)


def _create_table_of_contents_block() -> TableOfContentsBlock:
    mock_obj = Mock(spec=Block)
    table_of_contents_block = cast(TableOfContentsBlock, mock_obj)
    table_of_contents_block.type = BlockType.TABLE_OF_CONTENTS
    table_of_contents_block.table_of_contents = Mock()
    return table_of_contents_block


@pytest.fixture
def table_of_contents_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> TableOfContentsRenderer:
    return TableOfContentsRenderer()


@pytest.mark.asyncio
async def test_table_of_contents_block_should_be_handled(
    table_of_contents_renderer: TableOfContentsRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.TABLE_OF_CONTENTS

    assert table_of_contents_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_table_of_contents_block_should_not_be_handled(
    table_of_contents_renderer: TableOfContentsRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not table_of_contents_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_table_of_contents_should_render_toc_markdown(
    table_of_contents_renderer: TableOfContentsRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_table_of_contents_block()
    render_context.block = block

    await table_of_contents_renderer._process(render_context)

    assert "[toc]" in render_context.markdown_result


@pytest.mark.asyncio
async def test_table_of_contents_without_children_should_render_toc_only(
    table_of_contents_renderer: TableOfContentsRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_table_of_contents_block()
    render_context.block = block
    render_context.indent_level = 0

    await table_of_contents_renderer._process(render_context)

    # TOC with no indentation (but conftest adds 2 spaces anyway when indent_level=0)
    assert render_context.markdown_result == "[toc]"


@pytest.mark.asyncio
async def test_table_of_contents_with_indentation_should_indent_toc(
    table_of_contents_renderer: TableOfContentsRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_table_of_contents_block()
    render_context.block = block
    render_context.indent_level = 1

    await table_of_contents_renderer._process(render_context)

    # Mock indent_text always adds 2 spaces
    assert render_context.markdown_result == "  [toc]"
    render_context.indent_text.assert_called_once_with("[toc]")


@pytest.mark.asyncio
async def test_table_of_contents_with_children_should_render_with_newline_separator(
    table_of_contents_renderer: TableOfContentsRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_table_of_contents_block()
    render_context.block = block
    render_context.render_children_with_additional_indent = AsyncMock(
        return_value="    Child content"
    )

    await table_of_contents_renderer._process(render_context)

    assert render_context.markdown_result == "[toc]\n    Child content"


@pytest.mark.asyncio
async def test_table_of_contents_markdown_constant_should_be_correct(
    table_of_contents_renderer: TableOfContentsRenderer,
) -> None:
    # The TOC syntax is now in SyntaxDefinitionRegistry, not as a constant on the renderer
    syntax = table_of_contents_renderer._syntax_registry.get_table_of_contents_syntax()
    assert syntax.start_delimiter == "[toc]"
