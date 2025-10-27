from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.blocks.schemas import Block, BulletedListItemBlock, BulletedListItemData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.bulleted_list import BulletedListRenderer


def _create_bulleted_list_data(rich_text: list[RichText]) -> BulletedListItemData:
    return BulletedListItemData(rich_text=rich_text)


def _create_bulleted_list_block(
    list_data: BulletedListItemData | None,
) -> BulletedListItemBlock:
    mock_obj = Mock(spec=Block)
    bulleted_list_item_block = cast(BulletedListItemBlock, mock_obj)
    bulleted_list_item_block.type = BlockType.BULLETED_LIST_ITEM
    bulleted_list_item_block.bulleted_list_item = list_data
    return bulleted_list_item_block


@pytest.fixture
def bulleted_list_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> BulletedListRenderer:
    return BulletedListRenderer(
        rich_text_markdown_converter=mock_rich_text_markdown_converter
    )


@pytest.mark.asyncio
async def test_bulleted_list_block_should_be_handled(
    bulleted_list_renderer: BulletedListRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.BULLETED_LIST_ITEM

    assert bulleted_list_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_bulleted_list_block_should_not_be_handled(
    bulleted_list_renderer: BulletedListRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not bulleted_list_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_bulleted_list_with_text_should_render_markdown_list(
    bulleted_list_renderer: BulletedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("List item text")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="List item text"
    )

    list_data = _create_bulleted_list_data(rich_text)
    block = _create_bulleted_list_block(list_data)
    render_context.block = block

    await bulleted_list_renderer._process(render_context)

    assert render_context.markdown_result == "- List item text"


@pytest.mark.asyncio
async def test_bulleted_list_with_empty_rich_text_should_render_empty_string(
    bulleted_list_renderer: BulletedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value=None)

    list_data = _create_bulleted_list_data([])
    block = _create_bulleted_list_block(list_data)
    render_context.block = block

    await bulleted_list_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_bulleted_list_with_missing_data_should_render_empty_string(
    bulleted_list_renderer: BulletedListRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_bulleted_list_block(None)
    render_context.block = block

    await bulleted_list_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_bulleted_list_with_indent_level_should_indent_output(
    bulleted_list_renderer: BulletedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Indented item")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Indented item"
    )

    list_data = _create_bulleted_list_data(rich_text)
    block = _create_bulleted_list_block(list_data)
    render_context.block = block
    render_context.indent_level = 1

    await bulleted_list_renderer._process(render_context)

    render_context.indent_text.assert_called_once()
    assert render_context.markdown_result == "  - Indented item"


@pytest.mark.asyncio
async def test_bulleted_list_with_children_should_render_children_with_indent(
    bulleted_list_renderer: BulletedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Parent item")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Parent item"
    )

    list_data = _create_bulleted_list_data(rich_text)
    block = _create_bulleted_list_block(list_data)
    render_context.block = block
    render_context.render_children_with_additional_indent = AsyncMock(
        return_value="  Child content"
    )

    await bulleted_list_renderer._process(render_context)

    render_context.render_children_with_additional_indent.assert_called_once_with(1)
    assert "- Parent item" in render_context.markdown_result
    assert "Child content" in render_context.markdown_result


@pytest.mark.asyncio
async def test_convert_bulleted_list_with_valid_data_should_return_markdown(
    bulleted_list_renderer: BulletedListRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Test content")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Test content"
    )

    list_data = _create_bulleted_list_data(rich_text)
    block = _create_bulleted_list_block(list_data)

    result = await bulleted_list_renderer._convert_bulleted_list_to_markdown(block)

    assert result == "Test content"


@pytest.mark.asyncio
async def test_convert_bulleted_list_without_data_should_return_none(
    bulleted_list_renderer: BulletedListRenderer,
) -> None:
    block = _create_bulleted_list_block(None)

    result = await bulleted_list_renderer._convert_bulleted_list_to_markdown(block)

    assert result is None


@pytest.mark.asyncio
async def test_bulleted_list_with_nested_bulleted_list_child_should_indent_correctly(
    bulleted_list_renderer: BulletedListRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    parent_rich_text = [RichText.from_plain_text("Parent item")]
    child_rich_text = [RichText.from_plain_text("Child item")]

    child_block = _create_bulleted_list_block(
        _create_bulleted_list_data(child_rich_text)
    )

    parent_data = _create_bulleted_list_data(parent_rich_text)
    parent_block = _create_bulleted_list_block(parent_data)
    parent_block.has_children = True
    parent_block.children = [child_block]

    async def mock_converter_side_effect(rich_text_list):
        if rich_text_list == parent_rich_text:
            return "Parent item"
        elif rich_text_list == child_rich_text:
            return "Child item"
        return ""

    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        side_effect=mock_converter_side_effect
    )

    async def render_children_mock(indent_increase):
        # Simulate rendering the child with increased indent
        return "  - Child item"

    render_context.block = parent_block
    render_context.render_children_with_additional_indent = AsyncMock(
        side_effect=render_children_mock
    )

    await bulleted_list_renderer._process(render_context)

    # Assert
    expected = "- Parent item\n  - Child item"
    assert render_context.markdown_result == expected
    render_context.render_children_with_additional_indent.assert_called_once_with(1)
