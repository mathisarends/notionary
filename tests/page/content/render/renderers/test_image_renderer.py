from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType, FileType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, ExternalFile, ImageBlock, ImageData, NotionHostedFile
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.image import ImageRenderer


def _create_image_data_with_external_url(url: str) -> ImageData:
    return ImageData(type=FileType.EXTERNAL, external=ExternalFile(url=url))


def _create_image_data_with_notion_file(url: str, expiry_time: str) -> ImageData:
    return ImageData(type=FileType.FILE, file=NotionHostedFile(url=url, expiry_time=expiry_time))


def _create_image_data_with_caption(url: str, caption: list[RichText]) -> ImageData:
    return ImageData(type=FileType.EXTERNAL, external=ExternalFile(url=url), caption=caption)


def _create_image_block(image_data: ImageData | None) -> ImageBlock:
    mock_obj = Mock(spec=Block)
    image_block = cast(ImageBlock, mock_obj)
    image_block.type = BlockType.IMAGE
    image_block.image = image_data
    return image_block


@pytest.fixture
def image_renderer(mock_rich_text_markdown_converter: RichTextToMarkdownConverter) -> ImageRenderer:
    return ImageRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_image_block_should_be_handled(image_renderer: ImageRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.IMAGE

    assert image_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_image_block_should_not_be_handled(image_renderer: ImageRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not image_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_image_with_external_url_should_render_markdown_image(
    image_renderer: ImageRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    image_data = _create_image_data_with_external_url("https://example.com/image.png")
    block = _create_image_block(image_data)
    render_context.block = block

    await image_renderer._process(render_context)

    assert render_context.markdown_result == "[image](https://example.com/image.png)"


@pytest.mark.asyncio
async def test_image_with_notion_hosted_file_should_render_markdown_image(
    image_renderer: ImageRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    image_data = _create_image_data_with_notion_file("https://notion.so/image.png", "2025-01-01")
    block = _create_image_block(image_data)
    render_context.block = block

    await image_renderer._process(render_context)

    assert render_context.markdown_result == "[image](https://notion.so/image.png)"


@pytest.mark.asyncio
async def test_image_with_caption_should_include_caption_in_markdown(
    image_renderer: ImageRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    caption_rich_text = [RichText.from_plain_text("Image caption")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Image caption")

    image_data = _create_image_data_with_caption("https://example.com/image.png", caption_rich_text)
    block = _create_image_block(image_data)
    render_context.block = block

    await image_renderer._process(render_context)

    assert "[image](https://example.com/image.png)" in render_context.markdown_result
    assert "[caption] Image caption" in render_context.markdown_result


@pytest.mark.asyncio
async def test_image_without_url_should_render_empty_string(
    image_renderer: ImageRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    image_data = ImageData(type=FileType.EXTERNAL)
    block = _create_image_block(image_data)
    render_context.block = block

    await image_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_image_with_missing_data_should_render_empty_string(
    image_renderer: ImageRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_image_block(None)
    render_context.block = block

    await image_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_extract_image_url_with_external_file_should_return_url(
    image_renderer: ImageRenderer,
) -> None:
    image_data = _create_image_data_with_external_url("https://example.com/image.png")
    block = _create_image_block(image_data)

    url = image_renderer._extract_image_url(block)

    assert url == "https://example.com/image.png"


@pytest.mark.asyncio
async def test_extract_image_url_with_notion_file_should_return_url(
    image_renderer: ImageRenderer,
) -> None:
    image_data = _create_image_data_with_notion_file("https://notion.so/image.png", "2025-01-01")
    block = _create_image_block(image_data)

    url = image_renderer._extract_image_url(block)

    assert url == "https://notion.so/image.png"


@pytest.mark.asyncio
async def test_extract_image_url_without_image_data_should_return_empty_string(
    image_renderer: ImageRenderer,
) -> None:
    block = _create_image_block(None)

    url = image_renderer._extract_image_url(block)

    assert url == ""
