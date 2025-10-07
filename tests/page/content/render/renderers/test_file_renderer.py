from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType, FileType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, ExternalFile, FileBlock, FileData, NotionHostedFile
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.file import FileRenderer


def _create_file_data_with_external_url(url: str, name: str | None = None) -> FileData:
    return FileData(type=FileType.EXTERNAL, external=ExternalFile(url=url), name=name)


def _create_file_data_with_notion_file(url: str, expiry_time: str, name: str | None = None) -> FileData:
    return FileData(type=FileType.FILE, file=NotionHostedFile(url=url, expiry_time=expiry_time), name=name)


def _create_file_data_with_caption(url: str, caption: list[RichText], name: str | None = None) -> FileData:
    return FileData(type=FileType.EXTERNAL, external=ExternalFile(url=url), caption=caption, name=name)


def _create_file_block(file_data: FileData | None) -> FileBlock:
    mock_obj = Mock(spec=Block)
    file_block = cast(FileBlock, mock_obj)
    file_block.type = BlockType.FILE
    file_block.file = file_data
    return file_block


@pytest.fixture
def file_renderer(mock_rich_text_markdown_converter: RichTextToMarkdownConverter) -> FileRenderer:
    return FileRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_file_block_should_be_handled(file_renderer: FileRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.FILE

    assert file_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_file_block_should_not_be_handled(file_renderer: FileRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not file_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_file_with_external_url_and_name_should_render_markdown_link(
    file_renderer: FileRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    file_data = _create_file_data_with_external_url("https://example.com/document.pdf", "document.pdf")
    block = _create_file_block(file_data)
    render_context.block = block

    await file_renderer._process(render_context)

    assert render_context.markdown_result == "[document.pdf](https://example.com/document.pdf)"


@pytest.mark.asyncio
async def test_file_with_external_url_without_name_should_use_default_text(
    file_renderer: FileRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    file_data = _create_file_data_with_external_url("https://example.com/file.zip")
    block = _create_file_block(file_data)
    render_context.block = block

    await file_renderer._process(render_context)

    assert render_context.markdown_result == "[file](https://example.com/file.zip)"


@pytest.mark.asyncio
async def test_file_with_notion_hosted_file_should_render_markdown_link(
    file_renderer: FileRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    file_data = _create_file_data_with_notion_file("https://notion.so/file.zip", "2025-01-01", "archive.zip")
    block = _create_file_block(file_data)
    render_context.block = block

    await file_renderer._process(render_context)

    assert render_context.markdown_result == "[archive.zip](https://notion.so/file.zip)"


@pytest.mark.asyncio
async def test_file_with_caption_should_include_caption_in_markdown(
    file_renderer: FileRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    caption_rich_text = [RichText.from_plain_text("Important file")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Important file")

    file_data = _create_file_data_with_caption("https://example.com/file.zip", caption_rich_text, "data.zip")
    block = _create_file_block(file_data)
    render_context.block = block

    await file_renderer._process(render_context)

    assert "[data.zip](https://example.com/file.zip)" in render_context.markdown_result
    assert "[caption] Important file" in render_context.markdown_result


@pytest.mark.asyncio
async def test_file_without_url_should_render_empty_string(
    file_renderer: FileRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    file_data = FileData(type=FileType.EXTERNAL)
    block = _create_file_block(file_data)
    render_context.block = block

    await file_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_file_with_missing_data_should_render_empty_string(
    file_renderer: FileRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_file_block(None)
    render_context.block = block

    await file_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_extract_file_url_with_external_file_should_return_url(
    file_renderer: FileRenderer,
) -> None:
    file_data = _create_file_data_with_external_url("https://example.com/file.zip")
    block = _create_file_block(file_data)

    url = file_renderer._extract_file_url(block)

    assert url == "https://example.com/file.zip"


@pytest.mark.asyncio
async def test_extract_file_url_with_notion_file_should_return_url(
    file_renderer: FileRenderer,
) -> None:
    file_data = _create_file_data_with_notion_file("https://notion.so/file.zip", "2025-01-01")
    block = _create_file_block(file_data)

    url = file_renderer._extract_file_url(block)

    assert url == "https://notion.so/file.zip"


@pytest.mark.asyncio
async def test_extract_file_name_with_name_should_return_name(
    file_renderer: FileRenderer,
) -> None:
    file_data = _create_file_data_with_external_url("https://example.com/file.zip", "document.zip")
    block = _create_file_block(file_data)

    name = file_renderer._extract_file_name(block)

    assert name == "document.zip"


@pytest.mark.asyncio
async def test_extract_file_name_without_name_should_return_empty_string(
    file_renderer: FileRenderer,
) -> None:
    file_data = _create_file_data_with_external_url("https://example.com/file.zip")
    block = _create_file_block(file_data)

    name = file_renderer._extract_file_name(block)

    assert name == ""
