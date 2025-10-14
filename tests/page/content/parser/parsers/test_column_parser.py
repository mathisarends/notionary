from unittest.mock import AsyncMock

import pytest

from notionary.blocks.schemas import (
    CreateColumnBlock,
    CreateColumnData,
    CreateColumnListBlock,
    CreateColumnListData,
    CreateParagraphBlock,
    CreateParagraphData,
)
from notionary.page.content.parser.context import ParentBlockContext
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.column import ColumnParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def syntax_registry() -> SyntaxRegistry:
    return SyntaxRegistry()


@pytest.fixture
def column_delimiter(syntax_registry: SyntaxRegistry) -> str:
    return syntax_registry.MULTI_LINE_BLOCK_DELIMITER


@pytest.fixture
def column_parser(syntax_registry: SyntaxRegistry) -> ColumnParser:
    return ColumnParser(syntax_registry=syntax_registry)


@pytest.fixture
def column_list_context() -> ParentBlockContext:
    column_list_data = CreateColumnListData()
    column_list_block = CreateColumnListBlock(column_list=column_list_data)
    return ParentBlockContext(block=column_list_block, child_lines=[])


@pytest.mark.parametrize(
    "start_line,expected_width_ratio",
    [
        ("{column_delimiter} column", None),
        ("{column_delimiter} column 0.5", 0.5),
        ("{column_delimiter} column 0.33", 0.33),
        ("{column_delimiter} column 0.25", 0.25),
        ("{column_delimiter} column 1.0", 1.0),
        ("{column_delimiter} column 1", 1.0),
        ("{column_delimiter} column .5", 0.5),
        ("{column_delimiter} column 0.1", 0.1),
    ],
)
@pytest.mark.asyncio
async def test_column_start_should_push_to_parent_stack_with_correct_width_ratio(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
    start_line: str,
    expected_width_ratio: float | None,
) -> None:
    context.line = start_line.format(column_delimiter=column_delimiter)
    context.parent_stack = []

    await column_parser._process(context)

    assert len(context.parent_stack) == 1
    assert isinstance(context.parent_stack[0].block, CreateColumnBlock)
    assert context.parent_stack[0].block.column.width_ratio == expected_width_ratio


@pytest.mark.parametrize(
    "start_line",
    [
        "{column_delimiter} column",
        "{column_delimiter} COLUMN",
        "{column_delimiter} Column",
        "{column_delimiter} CoLuMn",
        "{column_delimiter}column",
        "{column_delimiter} column ",
        "{column_delimiter}  column",
    ],
)
def test_case_insensitive_column_start_should_be_handled(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
    start_line: str,
) -> None:
    context.line = start_line.format(column_delimiter=column_delimiter)

    can_handle = column_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.parametrize(
    "invalid_ratio_line",
    [
        "{column_delimiter} column 0",
        "{column_delimiter} column 0.0",
        "{column_delimiter} column -0.5",
        "{column_delimiter} column 1.5",
        "{column_delimiter} column 2.0",
        "{column_delimiter} column abc",
        "{column_delimiter} column 0.5.5",
    ],
)
@pytest.mark.asyncio
async def test_column_start_with_invalid_width_ratio_should_create_column_with_none_ratio(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
    invalid_ratio_line: str,
) -> None:
    context.line = invalid_ratio_line.format(column_delimiter=column_delimiter)
    context.parent_stack = []

    await column_parser._process(context)

    if len(context.parent_stack) > 0:
        assert context.parent_stack[0].block.column.width_ratio is None


@pytest.mark.asyncio
async def test_column_end_should_pop_from_parent_stack(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = column_delimiter
    context.parse_nested_content = AsyncMock(return_value=[])

    await column_parser._process(context)

    assert len(context.parent_stack) == 0


@pytest.mark.asyncio
async def test_column_end_without_column_list_parent_should_add_to_result_blocks(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = column_delimiter
    context.parse_nested_content = AsyncMock(return_value=[])

    await column_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateColumnBlock)


@pytest.mark.asyncio
async def test_column_end_with_column_list_parent_should_add_to_parent_child_blocks(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
    column_list_context: ParentBlockContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    column_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [column_list_context, column_context]
    context.line = column_delimiter
    context.parse_nested_content = AsyncMock(return_value=[])

    await column_parser._process(context)

    assert len(context.parent_stack) == 1
    assert len(column_list_context.child_blocks) == 1
    assert isinstance(column_list_context.child_blocks[0], CreateColumnBlock)


@pytest.mark.asyncio
async def test_column_content_should_be_added_to_child_lines(
    column_parser: ColumnParser,
    context: BlockParsingContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = "Some content line"

    await column_parser._process(context)

    assert len(parent_context.child_lines) == 1
    assert parent_context.child_lines[0] == "Some content line"


@pytest.mark.asyncio
async def test_column_with_nested_content_should_parse_child_lines(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    paragraph_data = CreateParagraphData(rich_text=[])
    paragraph_block = CreateParagraphBlock(paragraph=paragraph_data)

    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(
        block=column_block,
        child_lines=["line 1", "line 2"],
    )
    context.parent_stack = [parent_context]
    context.line = column_delimiter
    context.parse_nested_content = AsyncMock(return_value=[paragraph_block])

    await column_parser._process(context)

    context.parse_nested_content.assert_called_once_with("line 1\nline 2")
    assert len(context.result_blocks[0].column.children) == 1


@pytest.mark.asyncio
async def test_column_with_both_child_lines_and_blocks_should_combine_all(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    paragraph_block = CreateParagraphBlock(paragraph=CreateParagraphData(rich_text=[]))
    nested_column_block = CreateColumnBlock(column=CreateColumnData())

    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(
        block=column_block,
        child_lines=["line content"],
    )
    parent_context.child_blocks = [nested_column_block]

    context.parent_stack = [parent_context]
    context.line = column_delimiter
    context.parse_nested_content = AsyncMock(return_value=[paragraph_block])

    await column_parser._process(context)

    assert len(context.result_blocks[0].column.children) == 2


def test_is_column_start_should_return_true_for_valid_pattern(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    context.line = f"{column_delimiter} column"

    is_start = column_parser._is_column_start(context)

    assert is_start is True


def test_is_column_start_with_ratio_should_return_true(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    context.line = f"{column_delimiter} column 0.5"

    is_start = column_parser._is_column_start(context)

    assert is_start is True


def test_is_column_end_should_return_true_for_matching_context(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = column_delimiter

    is_end = column_parser._is_column_end(context)

    assert is_end is True


def test_is_column_end_without_parent_stack_should_return_false(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    context.parent_stack = []
    context.line = column_delimiter

    is_end = column_parser._is_column_end(context)

    assert is_end is False


def test_is_column_end_with_different_parent_type_should_return_false(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    paragraph_data = CreateParagraphData(rich_text=[])
    paragraph_block = CreateParagraphBlock(paragraph=paragraph_data)
    parent_context = ParentBlockContext(block=paragraph_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = column_delimiter

    is_end = column_parser._is_column_end(context)

    assert is_end is False


def test_is_column_content_should_return_true_for_content_inside_column(
    column_parser: ColumnParser,
    context: BlockParsingContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = "Some content"

    is_content = column_parser._is_column_content(context)

    assert is_content is True


def test_is_column_content_without_parent_stack_should_return_false(
    column_parser: ColumnParser,
    context: BlockParsingContext,
) -> None:
    context.parent_stack = []
    context.line = "Some content"

    is_content = column_parser._is_column_content(context)

    assert is_content is False


def test_is_column_content_with_column_start_marker_should_return_false(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = f"{column_delimiter} column"

    is_content = column_parser._is_column_content(context)

    assert is_content is False


def test_is_column_content_with_end_marker_should_return_false(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [parent_context]
    context.line = column_delimiter

    is_content = column_parser._is_column_content(context)

    assert is_content is False


@pytest.mark.parametrize(
    "ratio_str,expected_ratio",
    [
        ("0.5", 0.5),
        ("0.33", 0.33),
        ("1.0", 1.0),
        ("1", 1.0),
        (".5", 0.5),
        ("0.1", 0.1),
    ],
)
def test_parse_width_ratio_should_return_valid_ratio(
    column_parser: ColumnParser,
    ratio_str: str,
    expected_ratio: float,
) -> None:
    parsed_ratio = column_parser._parse_width_ratio(ratio_str)

    assert parsed_ratio == expected_ratio


@pytest.mark.parametrize(
    "invalid_ratio_str",
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
def test_parse_width_ratio_with_invalid_value_should_return_none(
    column_parser: ColumnParser,
    invalid_ratio_str: str,
) -> None:
    parsed_ratio = column_parser._parse_width_ratio(invalid_ratio_str)

    assert parsed_ratio is None


def test_parse_width_ratio_with_none_should_return_none(
    column_parser: ColumnParser,
) -> None:
    parsed_ratio = column_parser._parse_width_ratio(None)

    assert parsed_ratio is None


def test_has_column_list_parent_should_return_true_when_parent_is_column_list(
    column_parser: ColumnParser,
    context: BlockParsingContext,
    column_list_context: ParentBlockContext,
) -> None:
    context.parent_stack = [column_list_context]

    has_parent = column_parser._has_column_list_parent(context)

    assert has_parent is True


def test_has_column_list_parent_should_return_false_without_parent_stack(
    column_parser: ColumnParser,
    context: BlockParsingContext,
) -> None:
    context.parent_stack = []

    has_parent = column_parser._has_column_list_parent(context)

    assert has_parent is False


def test_has_column_list_parent_should_return_false_with_different_parent_type(
    column_parser: ColumnParser,
    context: BlockParsingContext,
) -> None:
    column_data = CreateColumnData()
    column_block = CreateColumnBlock(column=column_data)
    parent_context = ParentBlockContext(block=column_block, child_lines=[])
    context.parent_stack = [parent_context]

    has_parent = column_parser._has_column_list_parent(context)

    assert has_parent is False


def test_create_column_block_should_return_block_with_correct_ratio(
    column_parser: ColumnParser,
    column_delimiter: str,
) -> None:
    block = column_parser._create_column_block(f"{column_delimiter} column 0.5")

    assert isinstance(block, CreateColumnBlock)
    assert block.column.width_ratio == pytest.approx(0.5)


def test_create_column_block_without_ratio_should_return_block_with_none_ratio(
    column_parser: ColumnParser,
    column_delimiter: str,
) -> None:
    block = column_parser._create_column_block(f"{column_delimiter} column")

    assert isinstance(block, CreateColumnBlock)
    assert block.column.width_ratio is None


def test_create_column_block_with_invalid_line_should_return_none(
    column_parser: ColumnParser,
) -> None:
    block = column_parser._create_column_block("not a column")

    assert block is None


def test_invalid_column_start_should_not_be_handled(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    # Generate invalid variations based on the actual delimiter
    invalid_variations = [
        column_delimiter[:-1] + " column",  # Missing one character (e.g., ":: column")
        column_delimiter + ": column",  # One too many (e.g., ":::: column")
        f"{column_delimiter} col",  # Wrong keyword
        f"{column_delimiter} columns",  # Wrong keyword (plural)
        f"column {column_delimiter}",  # Wrong order
        f"text {column_delimiter} column",  # Prefixed text
        "",  # Empty string
    ]

    for invalid_line in invalid_variations:
        context.line = invalid_line
        context.parent_stack = []
        can_handle = column_parser._can_handle(context)
        assert can_handle is False, f"Should not handle: {invalid_line}"


@pytest.mark.asyncio
async def test_column_block_should_have_correct_structure(
    column_parser: ColumnParser,
    column_delimiter: str,
    context: BlockParsingContext,
) -> None:
    context.line = f"{column_delimiter} column 0.5"
    context.parent_stack = []

    await column_parser._start_column(context)

    created_block = context.parent_stack[0].block
    assert isinstance(created_block, CreateColumnBlock)
    assert hasattr(created_block, "column")
    assert hasattr(created_block.column, "width_ratio")
    assert hasattr(created_block.column, "children")
