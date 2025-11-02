from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import (
    Block,
    ExternalFileWithCaption,
    NotionHostedFileWithCaption,
    VideoBlock,
)
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.video import VideoRenderer
from notionary.rich_text.rich_text_to_markdown.service import (
    RichTextToMarkdownConverter,
)
from notionary.rich_text.schemas import RichText
from notionary.shared.models.file import ExternalFileData, NotionHostedFileData


def _create_video_data_with_external_url(url: str) -> ExternalFileWithCaption:
    return ExternalFileWithCaption(external=ExternalFileData(url=url))


def _create_video_data_with_notion_file(
    url: str, expiry_time: str
) -> NotionHostedFileWithCaption:
    return NotionHostedFileWithCaption(
        file=NotionHostedFileData(url=url, expiry_time=expiry_time)
    )


def _create_video_data_with_caption(
    url: str, caption: list[RichText]
) -> ExternalFileWithCaption:
    return ExternalFileWithCaption(external=ExternalFileData(url=url), caption=caption)


def _create_video_block(
    video_data: ExternalFileWithCaption | NotionHostedFileWithCaption | None,
) -> VideoBlock:
    mock_obj = Mock(spec=Block)
    video_block = cast(VideoBlock, mock_obj)
    video_block.type = BlockType.VIDEO
    video_block.video = video_data
    return video_block


@pytest.fixture
def video_renderer(
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> VideoRenderer:
    return VideoRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_video_block_should_be_handled(
    video_renderer: VideoRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.VIDEO

    assert video_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_video_block_should_not_be_handled(
    video_renderer: VideoRenderer, mock_block: Block
) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not video_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_video_with_external_url_should_render_markdown_video(
    video_renderer: VideoRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    video_data = _create_video_data_with_external_url("https://example.com/video.mp4")
    block = _create_video_block(video_data)
    render_context.block = block

    await video_renderer._process(render_context)

    assert render_context.markdown_result == "[video](https://example.com/video.mp4)"


@pytest.mark.asyncio
async def test_video_with_notion_hosted_file_should_render_markdown_video(
    video_renderer: VideoRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    video_data = _create_video_data_with_notion_file(
        "https://notion.so/video.mp4", "2025-01-01"
    )
    block = _create_video_block(video_data)
    render_context.block = block

    await video_renderer._process(render_context)

    assert render_context.markdown_result == "[video](https://notion.so/video.mp4)"


@pytest.mark.asyncio
async def test_video_with_caption_should_include_caption_in_markdown(
    video_renderer: VideoRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    caption_rich_text = [RichText.from_plain_text("Video caption")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(
        return_value="Video caption"
    )

    video_data = _create_video_data_with_caption(
        "https://example.com/video.mp4", caption_rich_text
    )
    block = _create_video_block(video_data)
    render_context.block = block

    await video_renderer._process(render_context)

    assert "[video](https://example.com/video.mp4)" in render_context.markdown_result
    assert "[caption] Video caption" in render_context.markdown_result


@pytest.mark.asyncio
async def test_video_without_url_should_render_empty_string(
    video_renderer: VideoRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    video_data = ExternalFileWithCaption(external=ExternalFileData(url=""))
    block = _create_video_block(video_data)
    render_context.block = block

    await video_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_video_with_missing_data_should_render_empty_string(
    video_renderer: VideoRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_video_block(None)
    render_context.block = block

    await video_renderer._process(render_context)

    assert render_context.markdown_result == ""
