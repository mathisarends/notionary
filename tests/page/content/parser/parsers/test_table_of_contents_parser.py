from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateTableOfContentsBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.table_of_contents import TableOfContentsParser


@pytest.fixture
def toc_parser() -> TableOfContentsParser:
    return TableOfContentsParser()


@pytest.mark.parametrize(
    "line",
    [
        "[toc]",
        "[TOC]",
        "[Toc]",
        "[ToC]",
    ],
)
@pytest.mark.asyncio
async def test_toc_should_create_table_of_contents_block(
    toc_parser: TableOfContentsParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    await toc_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateTableOfContentsBlock)


@pytest.mark.parametrize(
    "line",
    [
        "[toc]",
        "[TOC]",
        "[Toc]",
    ],
)
def test_toc_should_be_case_insensitive(
    toc_parser: TableOfContentsParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = toc_parser._can_handle(context)

    assert can_handle is True


def test_toc_inside_parent_context_should_not_handle(
    toc_parser: TableOfContentsParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[toc]"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = toc_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "[ toc ]",
        "[toc] ",
        " [toc]",
        "[table of contents]",
        "toc",
        "[TOC",
        "TOC]",
        "[toc]extra",
    ],
)
def test_toc_with_invalid_syntax_should_not_handle(
    toc_parser: TableOfContentsParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = toc_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_toc_should_append_block_to_result_blocks(
    toc_parser: TableOfContentsParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[toc]"
    initial_length = len(context.result_blocks)

    await toc_parser._process(context)

    assert len(context.result_blocks) == initial_length + 1
