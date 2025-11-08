from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateFileBlock
from notionary.file_upload.service import NotionFileUpload
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.file import FileParser
from notionary.shared.models.file import FileType


@pytest.fixture
def file_parser(syntax_registry: SyntaxDefinitionRegistry) -> FileParser:
    mock_file_upload = Mock(spec=NotionFileUpload)
    return FileParser(
        syntax_registry=syntax_registry, file_upload_service=mock_file_upload
    )


@pytest.fixture
def make_file_syntax(syntax_registry: SyntaxDefinitionRegistry):
    syntax = syntax_registry.get_file_syntax()

    def _make(url: str) -> str:
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    return _make


@pytest.mark.asyncio
async def test_file_should_create_file_block(
    file_parser: FileParser,
    context: BlockParsingContext,
    make_file_syntax,
) -> None:
    context.line = make_file_syntax("https://example.com/document.zip")

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
    make_file_syntax,
) -> None:
    context.line = make_file_syntax("  https://example.com/file.pdf  ")

    await file_parser._process(context)

    block = context.result_blocks[0]
    assert block.file.external.url == "https://example.com/file.pdf"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/document.zip",
        "https://example.com/archive.tar.gz",
        "https://example.com/data.csv",
        "https://s3.amazonaws.com/bucket/file.xlsx",
    ],
)
def test_file_with_valid_url_should_handle(
    file_parser: FileParser,
    context: BlockParsingContext,
    make_file_syntax,
    url: str,
) -> None:
    context.line = make_file_syntax(url)

    can_handle = file_parser._can_handle(context)

    assert can_handle is True


def test_file_inside_parent_context_should_not_handle(
    file_parser: FileParser,
    context: BlockParsingContext,
    make_file_syntax,
) -> None:
    context.line = make_file_syntax("https://example.com/document.zip")
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
    make_file_syntax,
) -> None:
    context.line = make_file_syntax("")

    await file_parser._process(context)

    assert len(context.result_blocks) == 0
