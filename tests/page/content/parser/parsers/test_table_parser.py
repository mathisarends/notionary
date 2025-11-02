from textwrap import dedent
from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateTableBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.table import TableParser
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)


@pytest.fixture
def table_parser(
    mock_rich_text_converter: MarkdownRichTextConverter,
    syntax_registry: SyntaxDefinitionRegistry,
) -> TableParser:
    return TableParser(
        syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter
    )


@pytest.mark.asyncio
async def test_simple_table_with_header_should_create_block(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    markdown = dedent(
        """
        | Header 1 | Header 2 |
        |----------|----------|
        | Cell 1   | Cell 2   |
        """
    ).strip()

    lines = markdown.split("\n")
    context.line = lines[0]
    context.remaining_lines = lines[1:]
    context.get_remaining_lines = Mock(return_value=lines[1:])

    assert table_parser._can_handle(context)
    await table_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateTableBlock)
    assert block.table.table_width == 2
    assert block.table.has_column_header is True


@pytest.mark.asyncio
async def test_table_without_separator_should_not_have_column_header(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    markdown = dedent(
        """
        | Cell 1 | Cell 2 |
        | Cell 3 | Cell 4 |
        """
    ).strip()

    lines = markdown.split("\n")
    context.line = lines[0]
    context.remaining_lines = lines[1:]
    context.get_remaining_lines = Mock(return_value=lines[1:])

    await table_parser._process(context)

    block = context.result_blocks[0]
    assert block.table.has_column_header is False


@pytest.mark.asyncio
async def test_table_should_consume_correct_number_of_lines(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    markdown = dedent(
        """
        | Header 1 | Header 2 |
        |----------|----------|
        | Cell 1   | Cell 2   |
        """
    ).strip()

    lines = markdown.split("\n")
    context.line = lines[0]
    context.remaining_lines = lines[1:]
    context.get_remaining_lines = Mock(return_value=lines[1:])

    await table_parser._process(context)

    assert context.lines_consumed == 2


@pytest.mark.asyncio
async def test_table_with_three_columns_should_have_correct_width(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    markdown = dedent(
        """
        | Col 1 | Col 2 | Col 3 |
        |-------|-------|-------|
        | A     | B     | C     |
        """
    ).strip()

    lines = markdown.split("\n")
    context.line = lines[0]
    context.get_remaining_lines = Mock(return_value=lines[1:])

    await table_parser._process(context)

    block = context.result_blocks[0]
    assert block.table.table_width == 3


@pytest.mark.asyncio
async def test_table_should_have_correct_number_of_rows(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    markdown = dedent(
        """
        | Header 1 | Header 2 |
        |----------|----------|
        | Row 1    | Data 1   |
        | Row 2    | Data 2   |
        | Row 3    | Data 3   |
        """
    ).strip()

    lines = markdown.split("\n")
    context.line = lines[0]
    context.get_remaining_lines = Mock(return_value=lines[1:])

    await table_parser._process(context)

    block = context.result_blocks[0]
    assert len(block.table.children) == 4


@pytest.mark.asyncio
async def test_table_with_empty_lines_should_stop_at_content(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    markdown = dedent(
        """
        | Header |
        |--------|
        | Cell   |

        Not a table line
        """
    ).strip()

    lines = markdown.split("\n")
    context.line = lines[0]
    context.get_remaining_lines = Mock(return_value=lines[1:])

    await table_parser._process(context)

    assert context.lines_consumed == 3


@pytest.mark.asyncio
async def test_table_with_inline_markdown_should_convert_rich_text(
    mock_rich_text_converter: MarkdownRichTextConverter,
    context: BlockParsingContext,
    syntax_registry: SyntaxDefinitionRegistry,
) -> None:
    parser = TableParser(
        syntax_registry=syntax_registry, rich_text_converter=mock_rich_text_converter
    )

    markdown = "| **Bold** | *Italic* |"
    context.line = markdown
    context.get_remaining_lines = Mock(return_value=[])

    await parser._process(context)

    assert mock_rich_text_converter.to_rich_text.call_count >= 2


@pytest.mark.asyncio
async def test_table_inside_parent_context_should_not_be_handled(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    context.line = "| Header | Data |"
    context.is_inside_parent_context = Mock(return_value=True)

    assert not table_parser._can_handle(context)


@pytest.mark.asyncio
async def test_non_table_line_should_not_be_handled(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    context.line = "Not a table line"

    assert not table_parser._can_handle(context)


@pytest.mark.asyncio
async def test_table_with_leading_whitespace_should_work(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    markdown = "  | Header | Data |"
    context.line = markdown
    context.get_remaining_lines = Mock(return_value=[])

    assert table_parser._can_handle(context)
    await table_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_parse_table_row_should_extract_cells(table_parser: TableParser) -> None:
    cells = table_parser._parse_table_row("| Cell 1 | Cell 2 | Cell 3 |")

    assert len(cells) == 3
    assert cells[0] == " Cell 1 "
    assert cells[1] == " Cell 2 "
    assert cells[2] == " Cell 3 "


@pytest.mark.asyncio
async def test_table_with_alignment_separator_should_work(
    table_parser: TableParser, context: BlockParsingContext
) -> None:
    markdown = dedent(
        """
        | Left | Center | Right |
        |:-----|:------:|------:|
        | A    | B      | C     |
        """
    ).strip()

    lines = markdown.split("\n")
    context.line = lines[0]
    context.get_remaining_lines = Mock(return_value=lines[1:])

    await table_parser._process(context)

    block = context.result_blocks[0]
    assert block.table.has_column_header is True
