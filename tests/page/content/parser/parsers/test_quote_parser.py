from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import BlockColor, CreateQuoteBlock
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.quote import QuoteParser
from notionary.rich_text.markdown_to_rich_text.converter import (
    MarkdownRichTextConverter,
)


@pytest.fixture
def quote_parser(
    mock_rich_text_converter: MarkdownRichTextConverter,
    syntax_registry: SyntaxDefinitionRegistry,
) -> QuoteParser:
    return QuoteParser(
        rich_text_converter=mock_rich_text_converter, syntax_registry=syntax_registry
    )


@pytest.mark.asyncio
async def test_single_line_quote_should_create_quote_block(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = "> This is a quote"
    context.get_remaining_lines = Mock(return_value=[])

    await quote_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateQuoteBlock)
    assert block.quote.color == BlockColor.DEFAULT
    mock_rich_text_converter.to_rich_text.assert_called_once_with("This is a quote")


@pytest.mark.asyncio
async def test_multi_line_quote_should_join_with_newlines(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = "> First line"
    context.get_remaining_lines = Mock(
        return_value=[
            "> Second line",
            "> Third line",
            "Not a quote",
        ]
    )

    await quote_parser._process(context)

    expected_content = "First line\nSecond line\nThird line"
    mock_rich_text_converter.to_rich_text.assert_called_once_with(expected_content)


@pytest.mark.asyncio
async def test_multi_line_quote_should_consume_correct_number_of_lines(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
) -> None:
    context.line = "> First line"
    context.get_remaining_lines = Mock(
        return_value=[
            "> Second line",
            "> Third line",
            "Not a quote",
        ]
    )
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    await quote_parser._process(context)

    # Should consume 2 additional lines (Second line and Third line)
    # Current line is not counted in lines_consumed
    assert context.lines_consumed == 2


@pytest.mark.asyncio
async def test_quote_should_stop_at_non_quote_line(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = "> Quote line"
    context.get_remaining_lines = Mock(
        return_value=[
            "Regular paragraph",
            "> This should not be included",
        ]
    )
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    await quote_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("Quote line")
    # Should not consume any additional lines (only current line)
    assert context.lines_consumed == 0


@pytest.mark.parametrize(
    "line",
    [
        "> Quote with one space",
        ">Quote without space",
        ">  Quote with multiple spaces",
        ">	Quote with tab",
    ],
)
def test_quote_with_various_whitespace_should_handle(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = quote_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.asyncio
async def test_quote_with_inline_markdown_should_convert_to_rich_text(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = "> This is **bold** and *italic*"
    context.get_remaining_lines = Mock(return_value=[])

    await quote_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with(
        "This is **bold** and *italic*"
    )


def test_quote_inside_parent_context_should_not_handle(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
) -> None:
    context.line = "> Quote"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = quote_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "Not a quote",
        " > Quote with leading space",
        ">> Double quote marker",
        ">",
        "< Reverse bracket",
        "Quote without marker",
    ],
)
def test_quote_with_invalid_syntax_should_not_handle(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = quote_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_quote_with_only_whitespace_content_should_create_block(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = ">   "
    context.get_remaining_lines = Mock(return_value=[])

    await quote_parser._process(context)

    assert len(context.result_blocks) == 1
    mock_rich_text_converter.to_rich_text.assert_called_once_with("")


@pytest.mark.asyncio
async def test_quote_should_strip_content_whitespace(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.line = ">   Content with spaces   "
    context.get_remaining_lines = Mock(return_value=[])

    await quote_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("Content with spaces")


@pytest.mark.asyncio
async def test_single_line_quote_should_consume_one_line(
    quote_parser: QuoteParser,
    context: BlockParsingContext,
) -> None:
    context.line = "> Single quote"
    context.get_remaining_lines = Mock(return_value=[])
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    await quote_parser._process(context)

    # Single line quote doesn't consume additional lines
    assert context.lines_consumed == 0


@pytest.mark.asyncio
async def test_quote_with_indented_children_should_parse_children(
    quote_parser: QuoteParser, context: BlockParsingContext
) -> None:
    from unittest.mock import AsyncMock

    from notionary.blocks.schemas import CreateQuoteBlock, CreateQuoteData

    context.line = "> Quote text"
    context.get_remaining_lines = Mock(return_value=[])
    context.get_line_indentation_level = Mock(return_value=0)
    context.strip_indentation_level = Mock(
        return_value=[
            "- Child item 1",
            "- Child item 2",
        ]
    )

    child_block = CreateQuoteBlock(
        quote=CreateQuoteData(rich_text=[], color=BlockColor.DEFAULT)
    )
    context.parse_nested_markdown = AsyncMock(return_value=[child_block, child_block])

    # Mock the indented child collection for the quote
    def mock_collect_children_after_quote(ctx, last_quote_index):
        return [
            "    - Child item 1",
            "    - Child item 2",
        ]

    # We need to directly test the internal method or adjust our approach
    # For now, let's mock it at the parser level
    original_collect = quote_parser._collect_child_lines_after_quote
    quote_parser._collect_child_lines_after_quote = Mock(
        return_value=[
            "    - Child item 1",
            "    - Child item 2",
        ]
    )

    await quote_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].quote.children == [child_block, child_block]

    # Restore original method
    quote_parser._collect_child_lines_after_quote = original_collect


@pytest.mark.asyncio
async def test_quote_without_indented_children_should_not_have_children(
    quote_parser: QuoteParser, context: BlockParsingContext
) -> None:
    context.line = "> Simple quote"
    context.get_remaining_lines = Mock(return_value=[])
    context.get_line_indentation_level = Mock(return_value=0)
    context.collect_indented_child_lines = Mock(return_value=[])

    await quote_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].quote.children is None
    assert context.lines_consumed == 0
