from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.schemas import CreateBulletedListItemBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.bulleted_list import BulletedListParser
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)


@pytest.fixture
def bulleted_list_parser(
    mock_rich_text_converter: MarkdownRichTextConverter,
    syntax_registry: SyntaxDefinitionRegistry,
) -> BulletedListParser:
    return BulletedListParser(
        syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter
    )


@pytest.mark.asyncio
async def test_simple_bulleted_list_item_should_create_block(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = "- This is a simple list item"

    assert bulleted_list_parser._can_handle(context)
    await bulleted_list_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateBulletedListItemBlock)


@pytest.mark.asyncio
async def test_bulleted_list_with_inline_markdown_should_convert_rich_text(
    mock_rich_text_converter: MarkdownRichTextConverter,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    parser = BulletedListParser(
        rich_text_converter=mock_rich_text_converter, syntax_registry=syntax_registry
    )
    context.line = "- Item with **bold** and *italic*"

    await parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with(
        "Item with **bold** and *italic*"
    )


@pytest.mark.asyncio
async def test_bulleted_list_with_links_should_work(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = "- Check out [this link](https://example.com)"

    assert bulleted_list_parser._can_handle(context)
    await bulleted_list_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_checkbox_with_capital_x_should_not_be_handled(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = "- [X] Checked todo item"

    assert not bulleted_list_parser._can_handle(context)


@pytest.mark.asyncio
async def test_line_without_dash_should_not_be_handled(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = "Not a list item"

    assert not bulleted_list_parser._can_handle(context)


@pytest.mark.asyncio
async def test_dash_without_space_should_not_be_handled(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = "-No space after dash"

    assert not bulleted_list_parser._can_handle(context)


@pytest.mark.asyncio
async def test_empty_line_should_not_be_handled(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = ""

    assert not bulleted_list_parser._can_handle(context)


@pytest.mark.asyncio
async def test_bulleted_list_inside_parent_context_should_not_be_handled(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = "- List item"
    context.is_inside_parent_context = Mock(return_value=True)

    assert not bulleted_list_parser._can_handle(context)


@pytest.mark.asyncio
async def test_bulleted_list_with_indented_children_should_parse_children(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = "- Parent item"
    context.all_lines = [
        "- Parent item",
        "    - Child item 1",
        "    - Child item 2",
    ]
    context.current_line_index = 0

    # Mock the indentation detection
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

    # Mock child block creation
    from notionary.blocks.schemas import (
        CreateBulletedListItemBlock,
        CreateBulletedListItemData,
    )

    child_block = CreateBulletedListItemBlock(
        bulleted_list_item=CreateBulletedListItemData(rich_text=[])
    )
    context.parse_nested_markdown = AsyncMock(return_value=[child_block, child_block])

    await bulleted_list_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].bulleted_list_item.children == [
        child_block,
        child_block,
    ]
    assert context.lines_consumed == 2


@pytest.mark.asyncio
async def test_bulleted_list_without_indented_children_should_not_have_children(
    bulleted_list_parser: BulletedListParser, context: BlockParsingContext
) -> None:
    context.line = "- Simple item"
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    await bulleted_list_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].bulleted_list_item.children is None
    assert context.lines_consumed == 0
