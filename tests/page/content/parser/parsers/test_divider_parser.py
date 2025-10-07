from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateDividerBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.divider import DividerParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def divider_parser(syntax_registry: SyntaxRegistry) -> DividerParser:
    return DividerParser(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_divider_should_create_divider_block(
    divider_parser: DividerParser,
    context: BlockParsingContext,
) -> None:
    context.line = "---"

    await divider_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateDividerBlock)


@pytest.mark.parametrize(
    "line",
    [
        "---",
        "----",
        "-----",
        "----------",
    ],
)
def test_divider_with_three_or_more_dashes_should_handle(
    divider_parser: DividerParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = divider_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.parametrize(
    "line",
    [
        "---",
        " ---",
        "  ---",
        "--- ",
        "---  ",
        " --- ",
        "\t---",
        "---\t",
    ],
)
def test_divider_with_surrounding_whitespace_should_handle(
    divider_parser: DividerParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = divider_parser._can_handle(context)

    assert can_handle is True


def test_divider_inside_parent_context_should_not_handle(
    divider_parser: DividerParser,
    context: BlockParsingContext,
) -> None:
    context.line = "---"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = divider_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "--",
        "-",
        "- -",
        "- - -",
        "***",
        "___",
        "---text",
        "text---",
        "- --",
        "-- -",
    ],
)
def test_divider_with_invalid_syntax_should_not_handle(
    divider_parser: DividerParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = divider_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_divider_should_append_block_to_result_blocks(
    divider_parser: DividerParser,
    context: BlockParsingContext,
) -> None:
    context.line = "---"
    initial_length = len(context.result_blocks)

    await divider_parser._process(context)

    assert len(context.result_blocks) == initial_length + 1


@pytest.mark.asyncio
async def test_divider_with_many_dashes_should_create_block(
    divider_parser: DividerParser,
    context: BlockParsingContext,
) -> None:
    context.line = "--------------------"

    await divider_parser._process(context)

    assert len(context.result_blocks) == 1
    assert isinstance(context.result_blocks[0], CreateDividerBlock)
