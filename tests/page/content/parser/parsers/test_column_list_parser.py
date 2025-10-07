from unittest.mock import AsyncMock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import (
    CreateColumnBlock,
    CreateColumnData,
    CreateColumnListBlock,
    CreateColumnListData,
    CreateParagraphBlock,
    ParagraphData,
)
from notionary.page.content.parser.context import ParentBlockContext
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.column_list import ColumnListParser


@pytest.fixture
def column_list_parser() -> ColumnListParser:
    return ColumnListParser()


@pytest.fixture
def column_block() -> CreateColumnBlock:
    column_data = CreateColumnData()
    return CreateColumnBlock(column=column_data)


@pytest.fixture
def paragraph_block() -> CreateParagraphBlock:
    paragraph_data = ParagraphData(rich_text=[])
    return CreateParagraphBlock(paragraph=paragraph_data)


@pytest.mark.parametrize(
    "start_line",
    [
        "::: columns",
        "::: column",
        "::: COLUMNS",
        "::: COLUMN",
        "::: Columns",
        "::: Column",
        ":::columns",
        ":::column",
        "::: columns ",
        ":::  columns",
    ],
)
@pytest.mark.asyncio
async def test_column_list_start_should_push_to_parent_stack(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
    start_line: str,
) -> None:
    context.line = start_line
    context.parent_stack = []

    await column_list_parser._process(context)

    assert len(context.parent_stack) == 1
    assert isinstance(context.parent_stack[0].block, CreateColumnListBlock)
    assert context.parent_stack[0].child_lines == []


@pytest.mark.parametrize(
    "start_line",
    [
        "::: columns",
        "::: column",
        "::: COLUMNS",
    ],
)
def test_case_insensitive_column_list_start_should_be_handled(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
    start_line: str,
) -> None:
    context.line = start_line

    can_handle = column_list_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.asyncio
async def test_column_list_end_should_pop_from_parent_stack(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    column_list_data = CreateColumnListData()
    column_list_block = CreateColumnListBlock(column_list=column_list_data)
    parent_context = ParentBlockContext(block=column_list_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = ":::"
    context.parse_nested_content = AsyncMock(return_value=[])

    await column_list_parser._process(context)

    assert len(context.parent_stack) == 0
    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_column_list_end_should_add_block_to_result_blocks(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    column_list_data = CreateColumnListData()
    column_list_block = CreateColumnListBlock(column_list=column_list_data)
    parent_context = ParentBlockContext(block=column_list_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = ":::"
    context.parse_nested_content = AsyncMock(return_value=[])

    await column_list_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateColumnListBlock)


@pytest.mark.asyncio
async def test_column_list_with_nested_content_should_parse_child_lines(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
    column_block: CreateColumnBlock,
) -> None:
    column_list_data = CreateColumnListData()
    column_list_block = CreateColumnListBlock(column_list=column_list_data)
    parent_context = ParentBlockContext(
        block=column_list_block,
        child_lines=["line 1", "line 2"],
    )
    context.parent_stack = [parent_context]
    context.line = ":::"
    context.parse_nested_content = AsyncMock(return_value=[column_block])

    await column_list_parser._process(context)

    context.parse_nested_content.assert_called_once_with("line 1\nline 2")


@pytest.mark.asyncio
async def test_column_list_should_filter_only_column_blocks(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
    column_block: CreateColumnBlock,
    paragraph_block: CreateParagraphBlock,
) -> None:
    column_list_data = CreateColumnListData()
    column_list_block = CreateColumnListBlock(column_list=column_list_data)
    parent_context = ParentBlockContext(block=column_list_block, child_lines=[])
    parent_context.child_blocks = [column_block, paragraph_block, column_block]
    context.parent_stack = [parent_context]
    context.line = ":::"
    context.parse_nested_content = AsyncMock(return_value=[])

    await column_list_parser._process(context)

    finalized_block = context.result_blocks[0]
    assert len(finalized_block.column_list.children) == 2
    assert all(isinstance(child, CreateColumnBlock) for child in finalized_block.column_list.children)


def test_filter_column_blocks_should_return_only_column_type(
    column_list_parser: ColumnListParser,
    column_block: CreateColumnBlock,
    paragraph_block: CreateParagraphBlock,
) -> None:
    blocks = [column_block, paragraph_block, column_block]

    filtered = column_list_parser._filter_column_blocks(blocks)

    assert len(filtered) == 2
    assert all(block.type == BlockType.COLUMN for block in filtered)


@pytest.mark.parametrize(
    "invalid_line",
    [
        ":: columns",
        ":::: columns",
        "::: column list",
        "columns :::",
        "::: cols",
        "text ::: columns",
        "",
    ],
)
def test_invalid_column_list_start_should_not_be_handled(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
    invalid_line: str,
) -> None:
    context.line = invalid_line

    can_handle = column_list_parser._can_handle(context)

    assert can_handle is False


def test_end_marker_without_matching_start_should_not_be_handled(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    context.parent_stack = []
    context.line = ":::"

    can_handle = column_list_parser._can_handle(context)

    assert can_handle is False


def test_end_marker_with_different_parent_type_should_not_be_handled(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    paragraph_data = ParagraphData(rich_text=[])
    paragraph_block = CreateParagraphBlock(paragraph=paragraph_data)
    parent_context = ParentBlockContext(block=paragraph_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = ":::"

    can_handle = column_list_parser._can_handle(context)

    assert can_handle is False


def test_is_column_list_start_should_return_true_for_valid_pattern(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    context.line = "::: columns"

    is_start = column_list_parser._is_column_list_start(context)

    assert is_start is True


def test_is_column_list_start_should_return_false_for_invalid_pattern(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    context.line = "not a start"

    is_start = column_list_parser._is_column_list_start(context)

    assert is_start is False


def test_is_column_list_end_should_return_true_for_matching_context(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    column_list_data = CreateColumnListData()
    column_list_block = CreateColumnListBlock(column_list=column_list_data)
    parent_context = ParentBlockContext(block=column_list_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = ":::"

    is_end = column_list_parser._is_column_list_end(context)

    assert is_end is True


def test_is_column_list_end_should_return_false_without_parent_stack(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    context.parent_stack = []
    context.line = ":::"

    is_end = column_list_parser._is_column_list_end(context)

    assert is_end is False


@pytest.mark.asyncio
async def test_nested_column_list_should_add_to_parent_context(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    outer_column_data = CreateColumnData()
    outer_column_block = CreateColumnBlock(column=outer_column_data)
    outer_context = ParentBlockContext(block=outer_column_block, child_lines=[])

    column_list_data = CreateColumnListData()
    column_list_block = CreateColumnListBlock(column_list=column_list_data)
    inner_context = ParentBlockContext(block=column_list_block, child_lines=[])

    context.parent_stack = [outer_context, inner_context]
    context.line = ":::"
    context.parse_nested_content = AsyncMock(return_value=[])

    await column_list_parser._process(context)

    assert len(context.parent_stack) == 1
    assert len(outer_context.child_blocks) == 1
    assert isinstance(outer_context.child_blocks[0], CreateColumnListBlock)


@pytest.mark.asyncio
async def test_column_list_with_both_child_lines_and_blocks_should_combine_all(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
    column_block: CreateColumnBlock,
) -> None:
    second_column_block = CreateColumnBlock(column=CreateColumnData())

    column_list_data = CreateColumnListData()
    column_list_block = CreateColumnListBlock(column_list=column_list_data)
    parent_context = ParentBlockContext(
        block=column_list_block,
        child_lines=["line content"],
    )
    parent_context.child_blocks = [second_column_block]

    context.parent_stack = [parent_context]
    context.line = ":::"
    context.parse_nested_content = AsyncMock(return_value=[column_block])

    await column_list_parser._process(context)

    finalized_block = context.result_blocks[0]
    assert len(finalized_block.column_list.children) == 2


@pytest.mark.asyncio
async def test_start_column_list_should_create_block_with_empty_children(
    column_list_parser: ColumnListParser,
    context: BlockParsingContext,
) -> None:
    context.line = "::: columns"
    context.parent_stack = []

    await column_list_parser._start_column_list(context)

    created_block = context.parent_stack[0].block
    assert isinstance(created_block, CreateColumnListBlock)
    assert hasattr(created_block.column_list, "children")
