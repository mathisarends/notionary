from unittest.mock import AsyncMock

import pytest

from notionary.blocks.schemas import (
    CreateColumnBlock,
    CreateParagraphBlock,
    CreateParagraphData,
)
from notionary.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.column import ColumnParser


@pytest.fixture
def syntax_registry() -> SyntaxDefinitionRegistry:
    return SyntaxDefinitionRegistry()


@pytest.fixture
def column_parser(syntax_registry: SyntaxDefinitionRegistry) -> ColumnParser:
    return ColumnParser(syntax_registry=syntax_registry)


@pytest.fixture
def column_delimiter(markdown_grammar: MarkdownGrammar) -> str:
    return markdown_grammar.column_delimiter


@pytest.fixture
def context() -> BlockParsingContext:
    lines = []
    context = BlockParsingContext(
        line="",
        all_lines=lines,
        current_line_index=0,
        result_blocks=[],
        parent_stack=[],
        lines_consumed=0,
    )
    context.parse_nested_markdown = AsyncMock(return_value=[])
    return context


def test_can_handle_valid_column_start(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    column_delimiter: str,
) -> None:
    context.line = f"{column_delimiter} column"

    assert column_parser._can_handle(context) is True


@pytest.mark.parametrize(
    "column_line",
    [
        "{delimiter} column",
        "{delimiter} COLUMN",
        "{delimiter} Column",
        "{delimiter} CoLuMn",
        "{delimiter}column",
        "{delimiter} column ",
        "{delimiter}  column",
    ],
)
def test_can_handle_case_insensitive_column_start(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    column_line: str,
    column_delimiter: str,
) -> None:
    context.line = column_line.format(delimiter=column_delimiter)

    assert column_parser._can_handle(context) is True


def test_cannot_handle_invalid_line(
    column_parser: ColumnParser,
    context: BlockParsingContext,
) -> None:
    context.line = "Just some text"

    assert column_parser._can_handle(context) is False


def test_cannot_handle_wrong_keyword(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    column_delimiter: str,
) -> None:
    invalid_variations = [
        f"{column_delimiter} col",
        f"{column_delimiter} columns",
        f"column {column_delimiter}",
        f"text {column_delimiter} column",
    ]

    for invalid_line in invalid_variations:
        context.line = invalid_line
        assert column_parser._can_handle(context) is False


@pytest.mark.asyncio
async def test_process_column_without_children(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    column_delimiter: str,
) -> None:
    context.line = f"{column_delimiter} column"
    context.all_lines = [f"{column_delimiter} column"]

    await column_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateColumnBlock)


@pytest.mark.asyncio
async def test_process_column_with_width_ratio(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    column_delimiter: str,
) -> None:
    context.line = f"{column_delimiter} column 0.5"
    context.all_lines = [f"{column_delimiter} column 0.5"]

    await column_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].column.width_ratio == 0.5


@pytest.mark.asyncio
async def test_process_column_with_indented_children(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    column_delimiter: str,
) -> None:
    paragraph_block = CreateParagraphBlock(paragraph=CreateParagraphData(rich_text=[]))

    context.line = f"{column_delimiter} column"
    context.all_lines = [
        f"{column_delimiter} column",
        "    Child content line 1",
        "    Child content line 2",
    ]
    context.parse_nested_markdown = AsyncMock(return_value=[paragraph_block])

    await column_parser._process(context)

    assert len(context.result_blocks) == 1
    assert len(context.result_blocks[0].column.children) == 1
    context.parse_nested_markdown.assert_called_once()


@pytest.mark.asyncio
async def test_process_column_consumes_indented_lines(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    column_delimiter: str,
) -> None:
    context.line = f"{column_delimiter} column"
    context.all_lines = [
        f"{column_delimiter} column",
        "    Child line 1",
        "    Child line 2",
        "Next block",
    ]
    context.parse_nested_markdown = AsyncMock(return_value=[])

    await column_parser._process(context)

    assert context.lines_consumed == 2


def test_create_column_block_with_width_ratio(
    column_parser: ColumnParser,
    column_delimiter: str,
) -> None:
    block = column_parser._create_column_block(f"{column_delimiter} column 0.5")

    assert isinstance(block, CreateColumnBlock)
    assert block.column.width_ratio == pytest.approx(0.5)


def test_create_column_block_without_width_ratio(
    column_parser: ColumnParser,
    syntax_registry: SyntaxDefinitionRegistry,
    column_delimiter: str,
) -> None:
    block = column_parser._create_column_block(f"{column_delimiter} column")

    assert isinstance(block, CreateColumnBlock)
    assert block.column.width_ratio is None


def test_create_column_block_with_invalid_line(
    column_parser: ColumnParser,
) -> None:
    block = column_parser._create_column_block("not a column")

    assert block is None


@pytest.mark.parametrize(
    "ratio_str,expected",
    [
        ("0.5", 0.5),
        ("0.33", 0.33),
        ("1.0", 1.0),
        ("1", 1.0),
        (".5", 0.5),
        ("0.1", 0.1),
    ],
)
def test_parse_width_ratio_valid_values(
    column_parser: ColumnParser,
    ratio_str: str,
    expected: float,
) -> None:
    result = column_parser._parse_width_ratio(ratio_str)

    assert result == expected


@pytest.mark.parametrize(
    "invalid_ratio",
    [
        "0",
        "0.0",
        "-0.5",
        "1.5",
        "2.0",
        "abc",
        "0.5.5",
        "1.00001",
    ],
)
def test_parse_width_ratio_invalid_values(
    column_parser: ColumnParser,
    invalid_ratio: str,
) -> None:
    result = column_parser._parse_width_ratio(invalid_ratio)

    assert result is None


def test_parse_width_ratio_none_input(
    column_parser: ColumnParser,
) -> None:
    result = column_parser._parse_width_ratio(None)

    assert result is None


@pytest.mark.parametrize(
    "ratio_line,expected_ratio",
    [
        ("{delimiter} column", None),
        ("{delimiter} column 0.5", 0.5),
        ("{delimiter} column 0.33", 0.33),
        ("{delimiter} column 1.0", 1.0),
        ("{delimiter} column 1", 1.0),
        ("{delimiter} column .5", 0.5),
    ],
)
@pytest.mark.asyncio
async def test_process_various_width_ratios(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    ratio_line: str,
    expected_ratio: float | None,
    column_delimiter: str,
) -> None:
    context.line = ratio_line.format(delimiter=column_delimiter)
    context.all_lines = [context.line]

    await column_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].column.width_ratio == expected_ratio


@pytest.mark.parametrize(
    "invalid_ratio_line",
    [
        "{delimiter} column 0",
        "{delimiter} column -0.5",
        "{delimiter} column 1.5",
        "{delimiter} column 2.0",
        "{delimiter} column abc",
    ],
)
@pytest.mark.asyncio
async def test_process_invalid_width_ratio_creates_no_block(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    invalid_ratio_line: str,
    column_delimiter: str,
) -> None:
    context.line = invalid_ratio_line.format(delimiter=column_delimiter)
    context.all_lines = [context.line]

    await column_parser._process(context)

    # Invalid ratio should result in no block being created
    assert len(context.result_blocks) == 0


def test_column_block_structure(
    column_parser: ColumnParser,
    column_delimiter: str,
) -> None:
    block = column_parser._create_column_block(f"{column_delimiter} column 0.5")

    assert isinstance(block, CreateColumnBlock)
    assert hasattr(block, "column")
    assert hasattr(block.column, "width_ratio")
    assert hasattr(block.column, "children")
    assert block.column.children == []
