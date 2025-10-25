from unittest.mock import Mock

import pytest

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.schemas import (
    BlockCreatePayload,
    BlockType,
    CreateImageBlock,
    CreateParagraphBlock,
    CreateVideoBlock,
    ExternalFileWithCaption,
)
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.caption import CaptionParser
from notionary.page.content.syntax import SyntaxRegistry
from notionary.shared.models.file import ExternalFileData


@pytest.fixture
def caption_parser(
    mock_rich_text_converter: MarkdownRichTextConverter, syntax_registry: SyntaxRegistry
) -> CaptionParser:
    return CaptionParser(rich_text_converter=mock_rich_text_converter, syntax_registry=syntax_registry)


@pytest.fixture
def video_block_with_caption_support() -> CreateVideoBlock:
    video_data = ExternalFileWithCaption(external=ExternalFileData(url="https://youtube.com/watch?v=test"), caption=[])
    block = CreateVideoBlock(type=BlockType.VIDEO, video=video_data)
    return block


@pytest.fixture
def image_block_with_caption_support() -> CreateImageBlock:
    image_data = ExternalFileWithCaption(external=ExternalFileData(url="https://example.com/image.png"), caption=[])
    block = CreateImageBlock(type=BlockType.IMAGE, image=image_data)
    return block


@pytest.fixture
def paragraph_block_without_caption_support() -> CreateParagraphBlock:
    from notionary.blocks.schemas import CreateParagraphData

    paragraph_data = CreateParagraphData(rich_text=[])
    block = CreateParagraphBlock(type=BlockType.PARAGRAPH, paragraph=paragraph_data)
    return block


@pytest.mark.asyncio
async def test_caption_with_valid_previous_block_should_attach_caption(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    video_block_with_caption_support: BlockCreatePayload,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.result_blocks = [video_block_with_caption_support]
    context.line = "[caption] This is a video caption"

    await caption_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("This is a video caption")
    assert video_block_with_caption_support.video.caption == [{"type": "text", "text": {"content": "test"}}]


@pytest.mark.asyncio
async def test_caption_with_inline_markdown_should_convert_to_rich_text(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    image_block_with_caption_support: BlockCreatePayload,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    context.result_blocks = [image_block_with_caption_support]
    context.line = "[caption] **Bold** and *italic* text"

    await caption_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_called_once_with("**Bold** and *italic* text")


@pytest.mark.parametrize(
    "caption_line",
    [
        "[caption] Simple caption",
        "[caption]     Caption with extra spaces",
        "[caption] Caption with numbers 123",
        "[caption] Caption with special chars !@#$%",
    ],
)
@pytest.mark.asyncio
async def test_caption_pattern_matching_should_extract_caption_text(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    video_block_with_caption_support: BlockCreatePayload,
    caption_line: str,
) -> None:
    context.result_blocks = [video_block_with_caption_support]
    context.line = caption_line

    can_handle = caption_parser._can_handle(context)

    assert can_handle is True


@pytest.mark.parametrize(
    "invalid_line",
    [
        "caption] Missing opening bracket",
        "[caption Missing closing bracket",
        "[Caption] Wrong case",
        "[caption]",
        "[caption]   ",
        "Just some text",
        "[image](url)",
    ],
)
def test_invalid_caption_syntax_should_not_be_handled(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    video_block_with_caption_support: BlockCreatePayload,
    invalid_line: str,
) -> None:
    context.result_blocks = [video_block_with_caption_support]
    context.line = invalid_line

    can_handle = caption_parser._can_handle(context)

    assert can_handle is False


def test_caption_without_previous_blocks_should_not_be_handled(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
) -> None:
    context.result_blocks = []
    context.line = "[caption] This is a caption"

    can_handle = caption_parser._can_handle(context)

    assert can_handle is False


def test_caption_with_block_without_caption_support_should_not_be_handled(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    paragraph_block_without_caption_support: BlockCreatePayload,
) -> None:
    context.result_blocks = [paragraph_block_without_caption_support]
    context.line = "[caption] This is a caption"

    can_handle = caption_parser._can_handle(context)

    assert can_handle is False


def test_caption_inside_parent_context_should_not_be_handled(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    video_block_with_caption_support: BlockCreatePayload,
) -> None:
    context.result_blocks = [video_block_with_caption_support]
    context.line = "[caption] This is a caption"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = caption_parser._can_handle(context)

    assert can_handle is False


def test_block_with_caption_attribute_should_support_caption(
    caption_parser: CaptionParser,
    video_block_with_caption_support: BlockCreatePayload,
) -> None:
    supports_caption = caption_parser._block_supports_caption(video_block_with_caption_support)

    assert supports_caption is True


def test_block_without_caption_attribute_should_not_support_caption(
    caption_parser: CaptionParser,
    paragraph_block_without_caption_support: BlockCreatePayload,
) -> None:
    supports_caption = caption_parser._block_supports_caption(paragraph_block_without_caption_support)

    assert supports_caption is False


def test_block_with_nonexistent_type_data_should_not_support_caption(
    caption_parser: CaptionParser,
) -> None:
    # Create a mock block where the video attribute is None
    mock_block = Mock(spec=BlockCreatePayload)
    mock_block.type = BlockType.VIDEO
    mock_block.video = None

    supports_caption = caption_parser._block_supports_caption(mock_block)

    assert supports_caption is False


@pytest.mark.asyncio
async def test_caption_for_image_block_should_attach_caption(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    image_block_with_caption_support: BlockCreatePayload,
) -> None:
    context.result_blocks = [image_block_with_caption_support]
    context.line = "[caption] Image description"

    await caption_parser._process(context)

    assert image_block_with_caption_support.image.caption == [{"type": "text", "text": {"content": "test"}}]


@pytest.mark.asyncio
async def test_caption_should_replace_existing_caption(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    video_block_with_caption_support: BlockCreatePayload,
) -> None:
    video_block_with_caption_support.video.caption = [{"type": "text", "text": {"content": "old"}}]
    context.result_blocks = [video_block_with_caption_support]
    context.line = "[caption] New caption"

    await caption_parser._process(context)

    assert video_block_with_caption_support.video.caption == [{"type": "text", "text": {"content": "test"}}]


@pytest.mark.asyncio
async def test_process_with_non_matching_line_should_do_nothing(
    caption_parser: CaptionParser,
    context: BlockParsingContext,
    video_block_with_caption_support: BlockCreatePayload,
    mock_rich_text_converter: MarkdownRichTextConverter,
) -> None:
    original_caption = [{"type": "text", "text": {"content": "original"}}]
    video_block_with_caption_support.video.caption = original_caption
    context.result_blocks = [video_block_with_caption_support]
    context.line = "Not a caption line"

    await caption_parser._process(context)

    mock_rich_text_converter.to_rich_text.assert_not_called()
    assert video_block_with_caption_support.video.caption == original_caption
