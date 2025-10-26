from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.blocks.schemas import (
    Block,
    ExternalFileWithCaption,
    NotionHostedFileWithCaption,
    PdfBlock,
)
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.pdf import PdfRenderer
from notionary.shared.models.file import ExternalFileData, NotionHostedFileData


def _create_pdf_data_with_external_url(url: str) -> ExternalFileWithCaption:
    return ExternalFileWithCaption(external=ExternalFileData(url=url))


def _create_pdf_data_with_notion_file(
    url: str, expiry_time: str
) -> NotionHostedFileWithCaption:
    return NotionHostedFileWithCaption(
        file=NotionHostedFileData(url=url, expiry_time=expiry_time)
    )


def _create_pdf_data_with_caption(
    url: str, caption: list[RichText]
) -> ExternalFileWithCaption:
    return ExternalFileWithCaption(external=ExternalFileData(url=url), caption=caption)


def _create_pdf_block(
    pdf_data: ExternalFileWithCaption | NotionHostedFileWithCaption | None,
) -> PdfBlock:
    mock_obj = Mock(spec=Block)
    pdf_block = cast(PdfBlock, mock_obj)
    pdf_block.type = BlockType.PDF
    pdf_block.pdf = pdf_data
    return pdf_block


@pytest.fixture
def pdf_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> PdfRenderer:
    return PdfRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_pdf_block_should_be_handled(
    pdf_renderer: PdfRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PDF

    assert pdf_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_pdf_block_should_not_be_handled(
    pdf_renderer: PdfRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not pdf_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_pdf_with_external_url_should_render_markdown_link(
    pdf_renderer: PdfRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    pdf_data = _create_pdf_data_with_external_url("https://example.com/document.pdf")
    block = _create_pdf_block(pdf_data)
    render_context.block = block

    await pdf_renderer._process(render_context)

    assert render_context.markdown_result == "[pdf](https://example.com/document.pdf)"


@pytest.mark.asyncio
async def test_pdf_with_notion_hosted_file_should_render_markdown_link(
    pdf_renderer: PdfRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    pdf_data = _create_pdf_data_with_notion_file(
        "https://notion.so/document.pdf", "2025-01-01"
    )
    block = _create_pdf_block(pdf_data)
    render_context.block = block

    await pdf_renderer._process(render_context)

    assert render_context.markdown_result == "[pdf](https://notion.so/document.pdf)"


@pytest.mark.asyncio
async def test_pdf_with_caption_should_include_caption_in_markdown(
    pdf_renderer: PdfRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    caption_rich_text = [RichText.from_plain_text("Important document")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Important document"
    )

    pdf_data = _create_pdf_data_with_caption(
        "https://example.com/document.pdf", caption_rich_text
    )
    block = _create_pdf_block(pdf_data)
    render_context.block = block

    await pdf_renderer._process(render_context)

    assert "[pdf](https://example.com/document.pdf)" in render_context.markdown_result
    assert "[caption] Important document" in render_context.markdown_result


@pytest.mark.asyncio
async def test_pdf_without_url_should_render_empty_string(
    pdf_renderer: PdfRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    pdf_data = ExternalFileWithCaption(external=ExternalFileData(url=""))
    block = _create_pdf_block(pdf_data)
    render_context.block = block

    await pdf_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_pdf_with_missing_data_should_render_empty_string(
    pdf_renderer: PdfRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_pdf_block(None)
    render_context.block = block

    await pdf_renderer._process(render_context)

    assert render_context.markdown_result == ""
