from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateFileBlock, FileType
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.file import FileParser


@pytest.fixture
def file_parser() -> FileParser:
    return FileParser()


@pytest.mark.asyncio
async def test_file_should_create_file_block(
    file_parser: FileParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[file](https://example.com/document.zip)"

    await file_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateFileBlock)
    assert block.file.type == FileType.EXTERNAL
    assert block.file.external.url == "https://example.com/document.zip"
    assert block.file.caption == []


@pytest.mark.asyncio
async def test_file_with_whitespace_around_url_should_strip(
    file_parser: FileParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[file](  https://example.com/file.pdf  )"

    await file_parser._process(context)

    block = context.result_blocks[0]
    assert block.file.external.url == "https://example.com/file.pdf"


@pytest.mark.parametrize(
    "line",
    [
        "[file](https://example.com/document.zip)",
        "[file](https://example.com/archive.tar.gz)",
        "[file](https://example.com/data.csv)",
        "[file](https://s3.amazonaws.com/bucket/file.xlsx)",
    ],
)
def test_file_with_valid_url_should_handle(
    file_parser: FileParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = file_parser._can_handle(context)

    assert can_handle is True


def test_file_inside_parent_context_should_not_handle(
    file_parser: FileParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[file](https://example.com/document.zip)"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = file_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "[file]",
        "[file]()",
        "[FILE](https://example.com/doc.zip)",
        "file(https://example.com/doc.zip)",
        "[image](https://example.com/photo.jpg)",
    ],
)
def test_file_with_invalid_syntax_should_not_handle(
    file_parser: FileParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = file_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_file_with_empty_url_should_not_create_block(
    file_parser: FileParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[file]()"

    await file_parser._process(context)

    assert len(context.result_blocks) == 0
