from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateVideoBlock, FileType
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.video import VideoParser
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def video_parser(syntax_registry: SyntaxRegistry) -> VideoParser:
    return VideoParser(syntax_registry=syntax_registry)


@pytest.mark.asyncio
async def test_video_with_youtube_url_should_create_block(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "[video](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"

    assert video_parser._can_handle(context)
    await video_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateVideoBlock)
    assert block.video.type == FileType.EXTERNAL
    assert block.video.external.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.mark.asyncio
async def test_video_with_vimeo_url_should_create_block(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "[video](https://vimeo.com/123456789)"

    assert video_parser._can_handle(context)
    await video_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].video.external.url == "https://vimeo.com/123456789"


@pytest.mark.asyncio
async def test_video_with_direct_mp4_url_should_create_block(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "[video](https://example.com/video.mp4)"

    assert video_parser._can_handle(context)
    await video_parser._process(context)

    assert len(context.result_blocks) == 1
    assert context.result_blocks[0].video.external.url == "https://example.com/video.mp4"


@pytest.mark.asyncio
async def test_video_with_text_before_and_after_should_create_block(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "Check out this video: [video](https://youtube.com/watch?v=123) - it's great!"

    assert video_parser._can_handle(context)
    await video_parser._process(context)

    assert len(context.result_blocks) == 1


@pytest.mark.asyncio
async def test_video_caption_should_be_empty_list(video_parser: VideoParser, context: BlockParsingContext) -> None:
    context.line = "[video](https://example.com/video.mp4)"

    await video_parser._process(context)

    block = context.result_blocks[0]
    assert block.video.caption == []


@pytest.mark.asyncio
async def test_video_type_should_be_external(video_parser: VideoParser, context: BlockParsingContext) -> None:
    context.line = "[video](https://example.com/video.mp4)"

    await video_parser._process(context)

    block = context.result_blocks[0]
    assert block.video.type == FileType.EXTERNAL


@pytest.mark.asyncio
async def test_regular_markdown_link_should_not_be_handled(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "[link text](https://example.com)"

    assert not video_parser._can_handle(context)


@pytest.mark.asyncio
async def test_video_without_url_should_not_create_block(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "[video]()"

    if video_parser._can_handle(context):
        await video_parser._process(context)
        assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_malformed_video_syntax_should_not_be_handled(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "[video]https://example.com/video.mp4"

    assert not video_parser._can_handle(context)


@pytest.mark.asyncio
async def test_video_with_missing_closing_bracket_should_not_be_handled(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "[video](https://example.com/video.mp4"

    assert not video_parser._can_handle(context)


@pytest.mark.asyncio
async def test_video_inside_parent_context_should_not_be_handled(
    video_parser: VideoParser, context: BlockParsingContext
) -> None:
    context.line = "[video](https://example.com/video.mp4)"
    context.is_inside_parent_context = Mock(return_value=True)

    assert not video_parser._can_handle(context)


@pytest.mark.asyncio
async def test_extract_url_with_invalid_pattern_should_return_none(video_parser: VideoParser) -> None:
    url = video_parser._extract_url("not a video")

    assert url is None
