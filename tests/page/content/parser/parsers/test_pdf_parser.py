from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreatePdfBlock
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.pdf import PdfParser
from notionary.page.content.syntax import SyntaxRegistry
from notionary.shared.models.file import FileType


@pytest.fixture
def pdf_parser(syntax_registry: SyntaxRegistry) -> PdfParser:
    return PdfParser(syntax_registry=syntax_registry)


@pytest.fixture
def make_pdf_syntax(syntax_registry: SyntaxRegistry):
    syntax = syntax_registry.get_pdf_syntax()

    def _make(url: str) -> str:
        return f"{syntax.start_delimiter}{url}{syntax.end_delimiter}"

    return _make


@pytest.mark.asyncio
async def test_pdf_should_create_pdf_block(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
) -> None:
    context.line = make_pdf_syntax("https://example.com/document.pdf")

    await pdf_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreatePdfBlock)
    assert block.pdf.type == FileType.EXTERNAL
    assert block.pdf.external.url == "https://example.com/document.pdf"
    assert block.pdf.caption == []


@pytest.mark.asyncio
async def test_pdf_with_url_containing_special_characters_should_extract_correctly(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
) -> None:
    context.line = make_pdf_syntax("https://example.com/path/to/file.pdf?param=value&other=123")

    await pdf_parser._process(context)

    block = context.result_blocks[0]
    assert block.pdf.external.url == "https://example.com/path/to/file.pdf?param=value&other=123"


@pytest.mark.asyncio
async def test_pdf_with_whitespace_around_url_should_strip(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
) -> None:
    context.line = make_pdf_syntax("  https://example.com/document.pdf  ")

    await pdf_parser._process(context)

    block = context.result_blocks[0]
    assert block.pdf.external.url == "https://example.com/document.pdf"


@pytest.mark.asyncio
async def test_pdf_with_text_before_and_after_should_create_block(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
) -> None:
    context.line = f"Check out this document: {make_pdf_syntax('https://example.com/doc.pdf')} for more info"

    await pdf_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.pdf.external.url == "https://example.com/doc.pdf"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/document.pdf",
        "http://example.com/file.pdf",
        "https://example.com/path/to/document.pdf",
        "https://s3.amazonaws.com/bucket/file.pdf",
    ],
)
def test_pdf_with_valid_url_should_handle(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
    url: str,
) -> None:
    context.line = make_pdf_syntax(url)

    can_handle = pdf_parser._can_handle(context)

    assert can_handle is True


def test_pdf_inside_parent_context_should_not_handle(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
) -> None:
    context.line = make_pdf_syntax("https://example.com/document.pdf")
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = pdf_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "[pdf]",
        "[pdf]()",
        "[pdf] (https://example.com/doc.pdf)",
        "[ pdf ](https://example.com/doc.pdf)",
        "[PDF](https://example.com/doc.pdf)",
        "pdf(https://example.com/doc.pdf)",
        "[pdf](https://example.com/doc.pdf",
        "[pdf]https://example.com/doc.pdf)",
        "[video](https://example.com/video.mp4)",
    ],
)
def test_pdf_with_invalid_syntax_should_not_handle(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = pdf_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_pdf_with_empty_url_should_not_create_block(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
) -> None:
    context.line = make_pdf_syntax("")

    await pdf_parser._process(context)

    assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_pdf_should_append_block_to_result_blocks(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
) -> None:
    context.line = make_pdf_syntax("https://example.com/document.pdf")
    initial_length = len(context.result_blocks)

    await pdf_parser._process(context)

    assert len(context.result_blocks) == initial_length + 1


@pytest.mark.asyncio
async def test_pdf_with_relative_url_should_create_block(
    pdf_parser: PdfParser,
    context: BlockParsingContext,
    make_pdf_syntax,
) -> None:
    context.line = make_pdf_syntax("/documents/file.pdf")

    await pdf_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.pdf.external.url == "/documents/file.pdf"
