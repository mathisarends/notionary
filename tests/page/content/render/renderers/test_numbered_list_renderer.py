from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, NumberedListItemBlock, NumberedListItemData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.numbered_list import NumberedListRenderer
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.schemas import RichText


def _create_numbered_list_item_data(rich_text: list[RichText]) -> NumberedListItemData:
    return NumberedListItemData(rich_text=rich_text)


def _create_numbered_list_item_block(
    list_item_data: NumberedListItemData | None,
) -> NumberedListItemBlock:
    mock_obj = Mock(spec=Block)
    numbered_list_item_block = cast(NumberedListItemBlock, mock_obj)
    numbered_list_item_block.type = BlockType.NUMBERED_LIST_ITEM
    numbered_list_item_block.numbered_list_item = list_item_data
    return numbered_list_item_block


@pytest.fixture
def numbered_list_renderer(
    syntax_registry: SyntaxDefinitionRegistry,
    markdown_grammar: MarkdownGrammar,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> NumberedListRenderer:
    return NumberedListRenderer(
        syntax_registry=syntax_registry,
        rich_text_markdown_converter=mock_rich_text_markdown_converter,
        markdown_grammar=markdown_grammar,
    )


@pytest.fixture
def numbered_list_placeholder() -> str:
    return MarkdownGrammar().numbered_list_placeholder


@pytest.mark.asyncio
async def test_numbered_list_item_block_should_be_handled(
    numbered_list_renderer: NumberedListRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.NUMBERED_LIST_ITEM

    assert numbered_list_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_numbered_list_item_block_should_not_be_handled(
    numbered_list_renderer: NumberedListRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not numbered_list_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_numbered_list_item_without_children_should_render_with_placeholder(
    numbered_list_renderer: NumberedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
    numbered_list_placeholder: str,
) -> None:
    rich_text = [RichText.from_plain_text("First item")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="First item")

    list_item_data = _create_numbered_list_item_data(rich_text)
    block = _create_numbered_list_item_block(list_item_data)
    render_context.block = block

    await numbered_list_renderer._process(render_context)

    # Mock indent_text adds 2 spaces
    assert (
        render_context.markdown_result == f"  {numbered_list_placeholder}. First item"
    )


@pytest.mark.asyncio
async def test_numbered_list_item_with_indentation_should_include_indent(
    numbered_list_renderer: NumberedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
    numbered_list_placeholder: str,
) -> None:
    rich_text = [RichText.from_plain_text("Nested item")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Nested item"
    )

    list_item_data = _create_numbered_list_item_data(rich_text)
    block = _create_numbered_list_item_block(list_item_data)
    render_context.block = block
    render_context.indent_level = 1

    await numbered_list_renderer._process(render_context)

    # Mock indent_text always adds 2 spaces regardless of indent_level
    assert (
        render_context.markdown_result == f"  {numbered_list_placeholder}. Nested item"
    )
    # Verify indent_text was called (real implementation would use indent_level)
    render_context.indent_text.assert_called_once()


@pytest.mark.asyncio
async def test_numbered_list_item_with_children_should_render_with_newline_separator(
    numbered_list_renderer: NumberedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
    numbered_list_placeholder: str,
) -> None:
    rich_text = [RichText.from_plain_text("Parent item")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Parent item"
    )
    render_context.render_children_with_additional_indent = AsyncMock(
        return_value="    Child content"
    )

    list_item_data = _create_numbered_list_item_data(rich_text)
    block = _create_numbered_list_item_block(list_item_data)
    render_context.block = block

    await numbered_list_renderer._process(render_context)

    # Mock indent_text adds 2 spaces
    assert (
        render_context.markdown_result
        == f"  {numbered_list_placeholder}. Parent item\n    Child content"
    )


@pytest.mark.asyncio
async def test_numbered_list_item_with_empty_text_should_render_placeholder_only(
    numbered_list_renderer: NumberedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
    numbered_list_placeholder: str,
) -> None:
    rich_text = [RichText.from_plain_text("")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="")

    list_item_data = _create_numbered_list_item_data(rich_text)
    block = _create_numbered_list_item_block(list_item_data)
    render_context.block = block

    await numbered_list_renderer._process(render_context)

    # Mock indent_text adds 2 spaces
    assert render_context.markdown_result == f"  {numbered_list_placeholder}. "


@pytest.mark.asyncio
async def test_numbered_list_item_without_data_should_render_placeholder_only(
    numbered_list_renderer: NumberedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
    numbered_list_placeholder: str,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="")

    block = _create_numbered_list_item_block(None)
    render_context.block = block

    await numbered_list_renderer._process(render_context)

    # Mock indent_text adds 2 spaces
    assert render_context.markdown_result == f"  {numbered_list_placeholder}. "
