from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block, EmbedBlock, EmbedData
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.embed import EmbedRenderer
from notionary.rich_text.models import RichText
from notionary.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)


def _create_embed_data(url: str) -> EmbedData:
    return EmbedData(url=url)


def _create_embed_data_with_caption(url: str, caption: list[RichText]) -> EmbedData:
    return EmbedData(url=url, caption=caption)


def _create_embed_block(embed_data: EmbedData | None) -> EmbedBlock:
    mock_obj = Mock(spec=Block)
    embed_block = cast(EmbedBlock, mock_obj)
    embed_block.type = BlockType.EMBED
    embed_block.embed = embed_data
    return embed_block


@pytest.fixture
def embed_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> EmbedRenderer:
    return EmbedRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_embed_block_should_be_handled(
    embed_renderer: EmbedRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.EMBED

    assert embed_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_embed_block_should_not_be_handled(
    embed_renderer: EmbedRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not embed_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_embed_with_url_should_render_markdown_embed(
    embed_renderer: EmbedRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    embed_data = _create_embed_data("https://example.com/embed")
    block = _create_embed_block(embed_data)
    render_context.block = block

    await embed_renderer._process(render_context)

    assert render_context.markdown_result == "[embed](https://example.com/embed)"


@pytest.mark.asyncio
async def test_embed_with_caption_should_include_caption_in_markdown(
    embed_renderer: EmbedRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    caption_rich_text = [RichText.from_plain_text("Embedded content")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Embedded content"
    )

    embed_data = _create_embed_data_with_caption(
        "https://example.com/embed", caption_rich_text
    )
    block = _create_embed_block(embed_data)
    render_context.block = block

    await embed_renderer._process(render_context)

    assert "[embed](https://example.com/embed)" in render_context.markdown_result
    assert "[caption] Embedded content" in render_context.markdown_result


@pytest.mark.asyncio
async def test_embed_without_url_should_render_empty_string(
    embed_renderer: EmbedRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    embed_data = _create_embed_data("")
    block = _create_embed_block(embed_data)
    render_context.block = block

    await embed_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_embed_with_missing_data_should_render_empty_string(
    embed_renderer: EmbedRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_embed_block(None)
    render_context.block = block

    await embed_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_extract_embed_url_with_valid_data_should_return_url(
    embed_renderer: EmbedRenderer,
) -> None:
    embed_data = _create_embed_data("https://example.com/embed")
    block = _create_embed_block(embed_data)

    url = embed_renderer._extract_embed_url(block)

    assert url == "https://example.com/embed"


@pytest.mark.asyncio
async def test_extract_embed_url_without_data_should_return_empty_string(
    embed_renderer: EmbedRenderer,
) -> None:
    block = _create_embed_block(None)

    url = embed_renderer._extract_embed_url(block)

    assert url == ""
