from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BookmarkBlock, BookmarkData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.bookmark import BookmarkRenderer


def _create_bookmark_data(url: str) -> BookmarkData:
    return BookmarkData(url=url)


def _create_bookmark_data_with_caption(url: str, caption: list[RichText]) -> BookmarkData:
    return BookmarkData(url=url, caption=caption)


def _create_bookmark_block(bookmark_data: BookmarkData | None) -> BookmarkBlock:
    block = Mock(spec=BookmarkBlock)
    block.type = BlockType.BOOKMARK
    block.bookmark = bookmark_data
    return block


@pytest.fixture
def bookmark_renderer(mock_rich_text_markdown_converter: RichTextToMarkdownConverter) -> BookmarkRenderer:
    return BookmarkRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_bookmark_block_should_be_handled(bookmark_renderer: BookmarkRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.BOOKMARK

    assert bookmark_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_bookmark_block_should_not_be_handled(bookmark_renderer: BookmarkRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not bookmark_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_bookmark_with_url_should_render_markdown_bookmark(
    bookmark_renderer: BookmarkRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    bookmark_data = _create_bookmark_data("https://example.com")
    block = _create_bookmark_block(bookmark_data)
    render_context.block = block

    await bookmark_renderer._process(render_context)

    assert render_context.markdown_result == "[bookmark](https://example.com)"


@pytest.mark.asyncio
async def test_bookmark_with_caption_should_include_caption_in_markdown(
    bookmark_renderer: BookmarkRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    caption_rich_text = [RichText.from_plain_text("Useful resource")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Useful resource")

    bookmark_data = _create_bookmark_data_with_caption("https://example.com", caption_rich_text)
    block = _create_bookmark_block(bookmark_data)
    render_context.block = block

    await bookmark_renderer._process(render_context)

    assert "[bookmark](https://example.com)" in render_context.markdown_result
    assert "[caption] Useful resource" in render_context.markdown_result


@pytest.mark.asyncio
async def test_bookmark_without_url_should_render_empty_string(
    bookmark_renderer: BookmarkRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    bookmark_data = _create_bookmark_data("")
    block = _create_bookmark_block(bookmark_data)
    render_context.block = block

    await bookmark_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_bookmark_with_missing_bookmark_data_should_render_empty_string(
    bookmark_renderer: BookmarkRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_bookmark_block(None)
    render_context.block = block

    await bookmark_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_extract_bookmark_url_with_valid_data_should_return_url(
    bookmark_renderer: BookmarkRenderer,
) -> None:
    bookmark_data = _create_bookmark_data("https://example.com")
    block = _create_bookmark_block(bookmark_data)

    url = bookmark_renderer._extract_bookmark_url(block)

    assert url == "https://example.com"


@pytest.mark.asyncio
async def test_extract_bookmark_url_without_bookmark_data_should_return_empty_string(
    bookmark_renderer: BookmarkRenderer,
) -> None:
    block = _create_bookmark_block(None)

    url = bookmark_renderer._extract_bookmark_url(block)

    assert url == ""


@pytest.mark.asyncio
async def test_extract_bookmark_url_with_empty_url_should_return_empty_string(
    bookmark_renderer: BookmarkRenderer,
) -> None:
    bookmark_data = _create_bookmark_data("")
    block = _create_bookmark_block(bookmark_data)

    url = bookmark_renderer._extract_bookmark_url(block)

    assert url == ""
