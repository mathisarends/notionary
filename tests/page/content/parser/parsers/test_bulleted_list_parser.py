from unittest.mock import Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import CreateBulletedListItemBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.bulleted_list import BulletedListParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def bulleted_list_parser(
    mock_rich_text_converter: MarkdownRichTextConverter, syntax_registry: SyntaxRegistry
) -> BulletedListParser:
    return BulletedListParser(syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter)


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
    mock_rich_text_converter: MarkdownRichTextConverter, context: BlockParsingContext, syntax_registry: SyntaxRegistry
) -> None:
    parser = BulletedListParser(rich_text_converter=mock_rich_text_converter, syntax_registry=syntax_registry)
    context.line = "- Item with **bold** and *italic*"

    await parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("Item with **bold** and *italic*")


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
