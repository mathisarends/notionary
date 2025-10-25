from unittest.mock import AsyncMock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import (
    CreateColumnBlock,
    CreateColumnData,
    CreateColumnListBlock,
    CreateParagraphBlock,
    CreateParagraphData,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.column_list import ColumnListParser
from notionary.page.content.syntax.definition import MarkdownGrammar, SyntaxDefinitionRegistry


@pytest.fixture
def column_list_parser(syntax_registry: SyntaxDefinitionRegistry) -> ColumnListParser:
    return ColumnListParser(syntax_registry=syntax_registry)


@pytest.fixture
def column_delimiter(markdown_grammar: MarkdownGrammar) -> str:
    return markdown_grammar.column_delimiter


@pytest.fixture
def context() -> BlockParsingContext:
    context = BlockParsingContext(
        line="",
        all_lines=[],
        current_line_index=0,
        result_blocks=[],
        parent_stack=[],
        lines_consumed=0,
    )
    context.parse_nested_markdown = AsyncMock(return_value=[])
    return context


@pytest.fixture
def column_block() -> CreateColumnBlock:
    column_data = CreateColumnData()
    return CreateColumnBlock(column=column_data)


@pytest.fixture
def paragraph_block() -> CreateParagraphBlock:
    paragraph_data = CreateParagraphData(rich_text=[])
    return CreateParagraphBlock(paragraph=paragraph_data)


def test_can_handle_valid_column_list_start(
    column_list_parser: ColumnListParser,
    syntax_registry: SyntaxDefinitionRegistry,
    context: BlockParsingContext,
) -> None:
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    context.line = delimiter

    assert column_list_parser._can_handle(context) is True


@pytest.mark.parametrize(
    "column_list_line",
    [
        "{delimiter}",
        "{delimiter} ",
        " {delimiter}",
    ],
)
def test_can_handle_column_list_with_whitespace(
    column_list_parser: ColumnListParser,
    syntax_registry: SyntaxDefinitionRegistry,
    context: BlockParsingContext,
    column_list_line: str,
) -> None:
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    context.line = column_list_line.format(delimiter=delimiter).strip()

    result = column_list_parser._can_handle(context)

    assert result is True


def test_cannot_handle_invalid_line(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    context.line = "Just some text"

    assert column_list_parser._can_handle(context) is False


def test_cannot_handle_wrong_keyword(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
    column_delimiter: str,
) -> None:
    invalid_variations = [
        f"{column_delimiter} column list",
        f"{column_delimiter} cols",
        f"columns {column_delimiter}",
        f"text {column_delimiter} columns",
    ]

    for invalid_line in invalid_variations:
        context.line = invalid_line
        assert column_list_parser._can_handle(context) is False


@pytest.mark.asyncio
async def test_process_column_list_without_children(
    column_list_parser: ColumnListParser,
    syntax_registry: SyntaxDefinitionRegistry,
    context: BlockParsingContext,
) -> None:
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    context.line = delimiter
    context.all_lines = [delimiter]
    context.current_line_index = 0

    await column_list_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateColumnListBlock)
    assert context.result_blocks[0].column_list.children == []


@pytest.mark.asyncio
async def test_process_column_list_with_indented_columns(
    column_list_parser: ColumnListParser,
    syntax_registry: SyntaxDefinitionRegistry,
    context: BlockParsingContext,
    column_block: CreateColumnBlock,
    column_delimiter: str,
) -> None:
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter

    context.line = delimiter
    context.all_lines = [
        delimiter,
        f"    {column_delimiter}",
        f"    {column_delimiter} 0.5",
    ]
    context.current_line_index = 0
    context.parse_nested_markdown = AsyncMock(return_value=[column_block, column_block])

    await column_list_parser._process(context)

    assert len(context.result_blocks) == 1
    assert len(context.result_blocks[0].column_list.children) == 2
    context.parse_nested_markdown.assert_called_once()


@pytest.mark.asyncio
async def test_process_column_list_filters_only_column_blocks(
    column_list_parser: ColumnListParser,
    syntax_registry: SyntaxDefinitionRegistry,
    context: BlockParsingContext,
    column_block: CreateColumnBlock,
    paragraph_block: CreateParagraphBlock,
) -> None:
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter

    context.line = delimiter
    context.all_lines = [delimiter, "    content"]
    context.current_line_index = 0
    context.parse_nested_markdown = AsyncMock(return_value=[column_block, paragraph_block, column_block])

    await column_list_parser._process(context)

    finalized_block = context.result_blocks[0]
    assert len(finalized_block.column_list.children) == 2
    assert all(isinstance(child, CreateColumnBlock) for child in finalized_block.column_list.children)


@pytest.mark.asyncio
async def test_process_column_list_consumes_indented_lines(
    column_list_parser: ColumnListParser,
    syntax_registry: SyntaxDefinitionRegistry,
    context: BlockParsingContext,
) -> None:
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter

    context.line = delimiter
    context.all_lines = [
        delimiter,
        "    Child line 1",
        "    Child line 2",
        "Next block",
    ]
    context.current_line_index = 0
    context.parse_nested_markdown = AsyncMock(return_value=[])

    await column_list_parser._process(context)

    assert context.lines_consumed == 2


def test_create_column_list_block(
    column_list_parser: ColumnListParser,
) -> None:
    block = column_list_parser._create_column_list_block()

    assert isinstance(block, CreateColumnListBlock)
    assert hasattr(block.column_list, "children")
    assert block.column_list.children == []


def test_extract_column_blocks_filters_only_columns(
    column_list_parser: ColumnListParser,
    column_block: CreateColumnBlock,
    paragraph_block: CreateParagraphBlock,
) -> None:
    blocks = [column_block, paragraph_block, column_block]

    filtered = column_list_parser._extract_column_blocks(blocks)

    assert len(filtered) == 2
    assert all(block.type == BlockType.COLUMN for block in filtered)


def test_extract_column_blocks_with_empty_list(
    column_list_parser: ColumnListParser,
) -> None:
    blocks = []

    filtered = column_list_parser._extract_column_blocks(blocks)

    assert filtered == []


def test_extract_column_blocks_with_only_non_columns(
    column_list_parser: ColumnListParser,
    paragraph_block: CreateParagraphBlock,
) -> None:
    blocks = [paragraph_block, paragraph_block]

    filtered = column_list_parser._extract_column_blocks(blocks)

    assert filtered == []


def test_is_column_list_start_with_valid_pattern(
    column_list_parser: ColumnListParser,
    syntax_registry: SyntaxDefinitionRegistry,
    context: BlockParsingContext,
) -> None:
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter
    context.line = delimiter

    assert column_list_parser._is_column_list_start(context) is True


def test_is_column_list_start_with_invalid_pattern(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    context.line = "not a column list start"

    assert column_list_parser._is_column_list_start(context) is False


def test_column_list_block_structure(
    column_list_parser: ColumnListParser,
) -> None:
    block = column_list_parser._create_column_list_block()

    assert isinstance(block, CreateColumnListBlock)
    assert hasattr(block, "column_list")
    assert hasattr(block.column_list, "children")
    assert isinstance(block.column_list.children, list)


@pytest.mark.asyncio
async def test_column_list_with_mixed_content(
    column_list_parser: ColumnListParser,
    syntax_registry: SyntaxDefinitionRegistry,
    context: BlockParsingContext,
    column_block: CreateColumnBlock,
    paragraph_block: CreateParagraphBlock,
) -> None:
    delimiter = syntax_registry.get_column_list_syntax().start_delimiter

    context.line = delimiter
    context.all_lines = [delimiter, "    mixed content"]
    context.current_line_index = 0

    mixed_blocks = [column_block, paragraph_block, column_block, paragraph_block]
    context.parse_nested_markdown = AsyncMock(return_value=mixed_blocks)

    await column_list_parser._process(context)

    result_block = context.result_blocks[0]
    assert len(result_block.column_list.children) == 2
    assert all(child.type == BlockType.COLUMN for child in result_block.column_list.children)


def test_is_valid_column_block(
    column_list_parser: ColumnListParser,
    column_block: CreateColumnBlock,
) -> None:
    assert column_list_parser._is_valid_column_block(column_block) is True


def test_is_valid_column_block_with_paragraph(
    column_list_parser: ColumnListParser,
    paragraph_block: CreateParagraphBlock,
) -> None:
    assert column_list_parser._is_valid_column_block(paragraph_block) is False
