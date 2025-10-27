from unittest.mock import Mock

import pytest

from notionary.blocks.enums import BlockColor
from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import CreateToDoBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.todo import TodoParser
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


@pytest.fixture
def todo_parser(
    mock_rich_text_converter: MarkdownRichTextConverter,
    syntax_registry: SyntaxDefinitionRegistry,
) -> TodoParser:
    return TodoParser(
        syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter
    )


@pytest.mark.asyncio
async def test_unchecked_todo_should_create_block_with_checked_false(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- [ ] Unchecked todo item"

    assert todo_parser._can_handle(context)
    await todo_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateToDoBlock)
    assert block.to_do.checked is False


@pytest.mark.asyncio
async def test_checked_todo_with_lowercase_x_should_create_block_with_checked_true(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- [x] Checked todo item"

    assert todo_parser._can_handle(context)
    await todo_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].to_do.checked is True


@pytest.mark.asyncio
async def test_checked_todo_with_uppercase_x_should_create_block_with_checked_true(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- [X] Checked todo item"

    assert todo_parser._can_handle(context)
    await todo_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].to_do.checked is True


@pytest.mark.parametrize(
    "marker",
    ["*", "+"],
)
@pytest.mark.asyncio
async def test_todo_with_invalid_markers_should_not_be_handled(
    todo_parser: TodoParser, context: BlockParsingContext, marker: str
) -> None:
    context.line = f"{marker} [ ] Todo with {marker} marker"

    assert not todo_parser._can_handle(context)


@pytest.mark.asyncio
async def test_todo_with_leading_whitespace_should_work(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "  - [ ] Indented todo"

    assert todo_parser._can_handle(context)
    await todo_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_todo_with_inline_markdown_should_convert_rich_text(
    mock_rich_text_converter: MarkdownRichTextConverter,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    parser = TodoParser(
        rich_text_converter=mock_rich_text_converter, syntax_registry=syntax_registry
    )
    context.line = "- [ ] Todo with **bold** and *italic*"

    await parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with(
        "Todo with **bold** and *italic*"
    )


@pytest.mark.asyncio
async def test_todo_with_special_characters_should_work(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- [ ] Todo with äöü and emoji 📝"

    assert todo_parser._can_handle(context)
    await todo_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_todo_inside_parent_context_should_not_be_handled(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- [ ] Todo item"
    context.is_inside_parent_context = Mock(return_value=True)

    assert not todo_parser._can_handle(context)


@pytest.mark.asyncio
async def test_regular_list_item_should_not_be_handled(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- Regular list item"

    assert not todo_parser._can_handle(context)


@pytest.mark.asyncio
async def test_checkbox_without_space_should_not_be_handled(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- []Todo without space"

    assert not todo_parser._can_handle(context)


@pytest.mark.asyncio
async def test_checkbox_with_other_character_should_not_be_handled(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- [y] Invalid checkbox"

    assert not todo_parser._can_handle(context)


@pytest.mark.asyncio
async def test_empty_line_should_not_be_handled(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = ""

    assert not todo_parser._can_handle(context)


@pytest.mark.asyncio
async def test_todo_with_link_should_work(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- [ ] Check [this link](https://example.com)"

    assert todo_parser._can_handle(context)
    await todo_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_todo_with_multiple_spaces_after_marker_should_work(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "-   [ ]   Todo with extra spaces"

    assert todo_parser._can_handle(context)
    await todo_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_todo_with_indented_children_should_parse_children(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    from unittest.mock import AsyncMock

    from notionary.blocks.schemas import CreateToDoBlock, CreateToDoData

    context.line = "- [ ] Parent todo"
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(
        return_value=[
            "    - Child item 1",
            "    - Child item 2",
        ]
    )
    context.strip_indentation_level = Mock(
        return_value=[
            "- Child item 1",
            "- Child item 2",
        ]
    )

    child_block = CreateToDoBlock(
        to_do=CreateToDoData(rich_text=[], checked=False, color=BlockColor.DEFAULT)
    )
    context.parse_nested_markdown = AsyncMock(return_value=[child_block, child_block])

    await todo_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].to_do.children == [child_block, child_block]
    assert context.lines_consumed == 2


@pytest.mark.asyncio
async def test_todo_without_indented_children_should_not_have_children(
    todo_parser: TodoParser, context: BlockParsingContext
) -> None:
    context.line = "- [ ] Simple todo"
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    await todo_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].to_do.children is None
    assert context.lines_consumed == 0
