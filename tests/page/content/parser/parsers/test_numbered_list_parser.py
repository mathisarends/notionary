from unittest.mock import Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.blocks.schemas import BlockColor, CreateNumberedListItemBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.numbered_list import NumberedListParser


@pytest.fixture
def numbered_list_parser(mock_rich_text_converter: MarkdownRichTextConverter) -> NumberedListParser:
    return NumberedListParser(rich_text_converter=mock_rich_text_converter)


@pytest.mark.asyncio
async def test_numbered_list_item_should_create_numbered_list_block(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = "1. First item"

    await numbered_list_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateNumberedListItemBlock)
    assert block.numbered_list_item.color == BlockColor.DEFAULT
    mock_rich_text_converter.to_rich_text.assert_called_once_with("First item")


@pytest.mark.parametrize(
    "line,expected_content",
    [
        ("1. First item", "First item"),
        ("2. Second item", "Second item"),
        ("10. Tenth item", "Tenth item"),
        ("99. Ninety-ninth item", "Ninety-ninth item"),
        ("123. One hundred twenty-third item", "One hundred twenty-third item"),
    ],
)
@pytest.mark.asyncio
async def test_numbered_list_with_different_numbers_should_extract_content(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
    line: str,
    expected_content: str,
) -> None:
    context.line = line

    await numbered_list_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with(expected_content)


@pytest.mark.parametrize(
    "line",
    [
        "1. Item",
        "  1. Item with leading spaces",
        "    1. Item with more spaces",
        "\t1. Item with tab",
    ],
)
def test_numbered_list_with_leading_whitespace_should_handle(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = numbered_list_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.asyncio
async def test_numbered_list_with_inline_markdown_should_convert_to_rich_text(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = "1. This is **bold** and *italic*"

    await numbered_list_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("This is **bold** and *italic*")


def test_numbered_list_inside_parent_context_should_not_handle(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
) -> None:
    context.line = "1. Item"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = numbered_list_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "1.Item without space",
        "1 . Item with space before dot",
        "1 Item without dot",
        "Item without number",
        "a. Item with letter",
        "1) Item with parenthesis",
        "(1) Item with parentheses",
        "- Bulleted item",
        "* Bulleted item",
        "1. ",
    ],
)
def test_numbered_list_with_invalid_syntax_should_not_handle(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = numbered_list_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_numbered_list_with_multiple_spaces_after_dot_should_handle(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = "1.   Item with multiple spaces"

    await numbered_list_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("Item with multiple spaces")


@pytest.mark.asyncio
async def test_numbered_list_should_append_block_to_result_blocks(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
) -> None:
    context.line = "1. First item"
    initial_length = len(context.result_blocks)

    await numbered_list_parser._process(context)

    assert len(context.result_blocks) == initial_length + 1


@pytest.mark.asyncio
async def test_numbered_list_with_long_content_should_create_block(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = (
        "1. This is a very long item that contains multiple words and continues for a while to test longer content"
    )

    await numbered_list_parser._process(context)

    assert len(context.result_blocks) == 1
    expected_content = (
        "This is a very long item that contains multiple words and continues for a while to test longer content"
    )
    mock_rich_text_converter.to_rich_text.assert_called_once_with(expected_content)


@pytest.mark.asyncio
async def test_numbered_list_with_special_characters_should_create_block(
    numbered_list_parser: NumberedListParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = "1. Item with special chars: @#$%^&*()"

    await numbered_list_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("Item with special chars: @#$%^&*()")
