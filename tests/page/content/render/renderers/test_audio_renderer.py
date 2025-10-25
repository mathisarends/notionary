from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import AudioBlock, Block, ExternalFileWithCaption, NotionHostedFileWithCaption
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.audio import AudioRenderer
from notionary.shared.models.file import ExternalFileData, NotionHostedFileData


def _create_external_audio_data(url: str) -> ExternalFileWithCaption:
    return ExternalFileWithCaption(
        external=ExternalFileData(url=url),
    )


def _create_notion_audio_data(url: str, expiry_time: str) -> NotionHostedFileWithCaption:
    return NotionHostedFileWithCaption(
        file=NotionHostedFileData(url=url, expiry_time=expiry_time),
    )


def _create_external_audio_data_with_caption(url: str, caption: list[RichText]) -> ExternalFileWithCaption:
    return ExternalFileWithCaption(
        external=ExternalFileData(url=url),
        caption=caption,
    )


def _create_empty_external_audio_data() -> ExternalFileWithCaption:
    return ExternalFileWithCaption(external=ExternalFileData(url=""))


def _create_audio_data_with_both_sources(
    external_url: str, notion_url: str, expiry_time: str
) -> ExternalFileWithCaption:
    # Note: This is a special test case - in practice, only one source would be used
    # For testing purposes, we create external file with notion data in additional attributes
    return ExternalFileWithCaption(
        external=ExternalFileData(url=external_url),
    )


def _create_audio_block(audio_data: ExternalFileWithCaption | NotionHostedFileWithCaption | None) -> AudioBlock:
    mock_obj = Mock(spec=AudioBlock)
    audio_block = cast(AudioBlock, mock_obj)
    audio_block.type = BlockType.AUDIO
    audio_block.audio = audio_data
    return audio_block


def _create_audio_block_with_external_url(url: str) -> AudioBlock:
    audio_data = _create_external_audio_data(url)
    return _create_audio_block(audio_data)


def _create_audio_block_with_notion_file(url: str, expiry_time: str) -> AudioBlock:
    audio_data = _create_notion_audio_data(url, expiry_time)
    return _create_audio_block(audio_data)


def _create_audio_block_with_caption(url: str, caption: list[RichText]) -> AudioBlock:
    audio_data = _create_external_audio_data_with_caption(url, caption)
    return _create_audio_block(audio_data)


def _create_audio_block_empty() -> AudioBlock:
    audio_data = _create_empty_external_audio_data()
    return _create_audio_block(audio_data)


def _create_audio_block_with_both_sources(external_url: str, notion_url: str, expiry_time: str) -> AudioBlock:
    audio_data = _create_audio_data_with_both_sources(external_url, notion_url, expiry_time)
    return _create_audio_block(audio_data)


@pytest.fixture
def audio_renderer(mock_rich_text_markdown_converter: RichTextToMarkdownConverter) -> AudioRenderer:
    return AudioRenderer(rich_text_markdown_converter=mock_rich_text_markdown_converter)


@pytest.mark.asyncio
async def test_audio_block_should_be_handled(audio_renderer: AudioRenderer, mock_block: AudioBlock) -> None:
    mock_block.type = BlockType.AUDIO

    assert audio_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_non_audio_block_should_not_be_handled(audio_renderer: AudioRenderer, mock_block: Block) -> None:
    mock_block.type = BlockType.PARAGRAPH

    assert not audio_renderer._can_handle(mock_block)


@pytest.mark.asyncio
async def test_audio_with_external_url_should_render_markdown_audio_link(
    audio_renderer: AudioRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_audio_block_with_external_url("https://example.com/audio.mp3")
    render_context.block = block

    await audio_renderer._process(render_context)

    assert render_context.markdown_result == "[audio](https://example.com/audio.mp3)"


@pytest.mark.asyncio
async def test_audio_with_notion_hosted_file_should_render_markdown_audio_link(
    audio_renderer: AudioRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_audio_block_with_notion_file("https://notion.so/file.mp3", "2025-01-01")
    render_context.block = block

    await audio_renderer._process(render_context)

    assert render_context.markdown_result == "[audio](https://notion.so/file.mp3)"


@pytest.mark.asyncio
async def test_audio_with_caption_should_include_caption_in_markdown(
    audio_renderer: AudioRenderer,
    render_context: MarkdownRenderingContext,
    mock_rich_text_markdown_converter: RichTextToMarkdownConverter,
) -> None:
    caption_rich_text = [RichText.from_plain_text("Audio caption")]
    mock_rich_text_markdown_converter.to_markdown = AsyncMock(return_value="Audio caption")

    block = _create_audio_block_with_caption("https://example.com/audio.mp3", caption_rich_text)
    render_context.block = block

    await audio_renderer._process(render_context)

    assert "[audio](https://example.com/audio.mp3)" in render_context.markdown_result
    assert "[caption] Audio caption" in render_context.markdown_result


@pytest.mark.asyncio
async def test_audio_without_url_should_render_empty_string(
    audio_renderer: AudioRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_audio_block_empty()
    render_context.block = block

    await audio_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_audio_with_missing_audio_data_should_render_empty_string(
    audio_renderer: AudioRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_audio_block(None)
    render_context.block = block

    await audio_renderer._process(render_context)

    assert render_context.markdown_result == ""


@pytest.mark.asyncio
async def test_audio_with_indent_level_should_indent_output(
    audio_renderer: AudioRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_audio_block_with_external_url("https://example.com/audio.mp3")
    render_context.block = block
    render_context.indent_level = 1

    await audio_renderer._process(render_context)

    render_context.indent_text.assert_called_once()
    assert render_context.markdown_result == "  [audio](https://example.com/audio.mp3)"


@pytest.mark.asyncio
async def test_audio_with_children_should_render_children_with_indent(
    audio_renderer: AudioRenderer,
    render_context: MarkdownRenderingContext,
) -> None:
    block = _create_audio_block_with_external_url("https://example.com/audio.mp3")
    render_context.block = block
    render_context.render_children_with_additional_indent = AsyncMock(return_value="  Child content")

    await audio_renderer._process(render_context)

    render_context.render_children_with_additional_indent.assert_called_once_with(1)
    assert "[audio](https://example.com/audio.mp3)" in render_context.markdown_result
    assert "Child content" in render_context.markdown_result


@pytest.mark.asyncio
async def test_extract_audio_url_with_external_file_should_return_url(
    audio_renderer: AudioRenderer,
) -> None:
    block = _create_audio_block_with_external_url("https://example.com/audio.mp3")

    url = audio_renderer._extract_audio_url(block)

    assert url == "https://example.com/audio.mp3"


@pytest.mark.asyncio
async def test_extract_audio_url_with_notion_file_should_return_url(
    audio_renderer: AudioRenderer,
) -> None:
    block = _create_audio_block_with_notion_file("https://notion.so/file.mp3", "2025-01-01")

    url = audio_renderer._extract_audio_url(block)

    assert url == "https://notion.so/file.mp3"


@pytest.mark.asyncio
async def test_extract_audio_url_without_audio_data_should_return_empty_string(
    audio_renderer: AudioRenderer,
) -> None:
    block = _create_audio_block(None)

    url = audio_renderer._extract_audio_url(block)

    assert url == ""


@pytest.mark.asyncio
async def test_extract_audio_url_with_empty_external_url_should_return_empty_string(
    audio_renderer: AudioRenderer,
) -> None:
    audio_data = _create_external_audio_data("")
    block = _create_audio_block(audio_data)

    url = audio_renderer._extract_audio_url(block)

    assert url == ""


@pytest.mark.asyncio
async def test_audio_with_multiple_url_sources_should_prefer_external(
    audio_renderer: AudioRenderer,
) -> None:
    block = _create_audio_block_with_both_sources(
        "https://external.com/audio.mp3", "https://notion.so/file.mp3", "2025-01-01"
    )

    url = audio_renderer._extract_audio_url(block)

    assert url == "https://external.com/audio.mp3"
