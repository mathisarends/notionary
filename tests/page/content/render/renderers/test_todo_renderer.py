from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.blocks.schemas import Block, ToDoBlock, ToDoData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.todo import TodoRenderer


def _create_todo_data(rich_text: list[RichText], checked: bool = False) -> ToDoData:
    return ToDoData(rich_text=rich_text, checked=checked)


def _create_todo_block(todo_data: ToDoData | None) -> ToDoBlock:
    mock_obj = Mock(spec=Block)
    todo_block = cast(ToDoBlock, mock_obj)
    todo_block.type = BlockType.TO_DO
    todo_block.to_do = todo_data
    return todo_block


@pytest.fixture
def todo_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> TodoRenderer:
    return TodoRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_todo_block_should_be_handled(
    todo_renderer: TodoRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.TO_DO

    assert todo_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_todo_block_should_not_be_handled(
    todo_renderer: TodoRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not todo_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_unchecked_todo_should_render_with_empty_checkbox(
    todo_renderer: TodoRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Task to do")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Task to do")

    todo_data = _create_todo_data(rich_text, checked=False)
    block = _create_todo_block(todo_data)
    render_context.block = block

    await todo_renderer._process(render_context)

    assert render_context.markdown_result == "- [ ] Task to do"


@pytest.mark.asyncio
async def test_checked_todo_should_render_with_checked_checkbox(
    todo_renderer: TodoRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Completed task")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Completed task"
    )

    todo_data = _create_todo_data(rich_text, checked=True)
    block = _create_todo_block(todo_data)
    render_context.block = block

    await todo_renderer._process(render_context)

    assert render_context.markdown_result == "- [x] Completed task"


@pytest.mark.asyncio
async def test_todo_with_empty_content_should_render_empty_string(
    todo_renderer: TodoRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="")

    todo_data = _create_todo_data([])
    block = _create_todo_block(todo_data)
    render_context.block = block

    await todo_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_todo_with_missing_data_should_render_empty_string(
    todo_renderer: TodoRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_todo_block(None)
    render_context.block = block

    await todo_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_todo_with_indent_level_should_indent_output(
    todo_renderer: TodoRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Indented task")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Indented task"
    )

    todo_data = _create_todo_data(rich_text)
    block = _create_todo_block(todo_data)
    render_context.block = block
    render_context.indent_level = 1

    await todo_renderer._process(render_context)

    render_context.indent_text.assert_called_once()
    assert render_context.markdown_result == "  - [ ] Indented task"


@pytest.mark.asyncio
async def test_todo_with_children_should_render_children_with_indent(
    todo_renderer: TodoRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Parent task")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Parent task"
    )

    todo_data = _create_todo_data(rich_text)
    block = _create_todo_block(todo_data)
    render_context.block = block
    render_context.render_children_with_additional_indent = AsyncMock(
        return_value="  Child content"
    )

    await todo_renderer._process(render_context)

    render_context.render_children_with_additional_indent.assert_called_once_with(1)
    assert "- [ ] Parent task" in render_context.markdown_result
    assert "Child content" in render_context.markdown_result


@pytest.mark.asyncio
async def test_extract_todo_info_with_checked_todo_should_return_true_and_content(
    todo_renderer: TodoRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Test task")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Test task")

    todo_data = _create_todo_data(rich_text, checked=True)
    block = _create_todo_block(todo_data)

    is_checked, content = await todo_renderer._extract_todo_info(block)

    assert is_checked is True
    assert content == "Test task"


@pytest.mark.asyncio
async def test_extract_todo_info_with_unchecked_todo_should_return_false_and_content(
    todo_renderer: TodoRenderer,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    rich_text = [RichText.from_plain_text("Test task")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Test task")

    todo_data = _create_todo_data(rich_text, checked=False)
    block = _create_todo_block(todo_data)

    is_checked, content = await todo_renderer._extract_todo_info(block)

    assert is_checked is False
    assert content == "Test task"


@pytest.mark.asyncio
async def test_extract_todo_info_without_data_should_return_false_and_empty_string(
    todo_renderer: TodoRenderer,
) -> None:
    block = _create_todo_block(None)

    is_checked, content = await todo_renderer._extract_todo_info(block)

    assert is_checked is False
    assert content == ""
