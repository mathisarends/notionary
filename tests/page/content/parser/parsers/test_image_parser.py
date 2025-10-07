from unittest.mock import Mock

import pytest

from notionary.blocks.schemas import CreateImageBlock, FileType
from notionary.page.content.parser.parsers.base import BlockParsingContext
from notionary.page.content.parser.parsers.image import ImageParser


@pytest.fixture
def image_parser() -> ImageParser:
    return ImageParser()


@pytest.mark.asyncio
async def test_image_should_create_image_block(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[image](https://example.com/photo.jpg)"

    await image_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert isinstance(block, CreateImageBlock)
    assert block.image.type == FileType.EXTERNAL
    assert block.image.external.url == "https://example.com/photo.jpg"
    assert block.image.caption == []


@pytest.mark.asyncio
async def test_image_with_url_containing_special_characters_should_extract_correctly(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[image](https://example.com/path/to/image.png?size=large&quality=high)"

    await image_parser._process(context)

    block = context.result_blocks[0]
    assert block.image.external.url == "https://example.com/path/to/image.png?size=large&quality=high"


@pytest.mark.asyncio
async def test_image_with_whitespace_around_url_should_strip(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[image](  https://example.com/photo.jpg  )"

    await image_parser._process(context)

    block = context.result_blocks[0]
    assert block.image.external.url == "https://example.com/photo.jpg"


@pytest.mark.asyncio
async def test_image_with_text_before_and_after_should_create_block(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "Check out this image: [image](https://example.com/photo.jpg) it's great!"

    await image_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.image.external.url == "https://example.com/photo.jpg"


@pytest.mark.parametrize(
    "line",
    [
        "[image](https://example.com/photo.jpg)",
        "[image](https://example.com/image.png)",
        "[image](https://example.com/picture.gif)",
        "[image](https://example.com/photo.jpeg)",
        "[image](https://example.com/image.webp)",
        "[image](https://s3.amazonaws.com/bucket/image.jpg)",
    ],
)
def test_image_with_valid_url_should_handle(
    image_parser: ImageParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = image_parser._can_handle(context)

    assert can_handle is True


def test_image_inside_parent_context_should_not_handle(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[image](https://example.com/photo.jpg)"
    context.is_inside_parent_context = Mock(return_value=True)

    can_handle = image_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.parametrize(
    "line",
    [
        "[image]",
        "[image]()",
        "[image] (https://example.com/photo.jpg)",
        "[ image ](https://example.com/photo.jpg)",
        "[IMAGE](https://example.com/photo.jpg)",
        "image(https://example.com/photo.jpg)",
        "[image](https://example.com/photo.jpg",
        "[image]https://example.com/photo.jpg)",
        "[video](https://example.com/video.mp4)",
        "![image](https://example.com/photo.jpg)",
    ],
)
def test_image_with_invalid_syntax_should_not_handle(
    image_parser: ImageParser,
    context: BlockParsingContext,
    line: str,
) -> None:
    context.line = line

    can_handle = image_parser._can_handle(context)

    assert can_handle is False


@pytest.mark.asyncio
async def test_image_with_empty_url_should_not_create_block(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[image]()"

    await image_parser._process(context)

    assert len(context.result_blocks) == 0


@pytest.mark.asyncio
async def test_image_should_append_block_to_result_blocks(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[image](https://example.com/photo.jpg)"
    initial_length = len(context.result_blocks)

    await image_parser._process(context)

    assert len(context.result_blocks) == initial_length + 1


@pytest.mark.asyncio
async def test_image_with_relative_url_should_create_block(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[image](/images/photo.jpg)"

    await image_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.image.external.url == "/images/photo.jpg"


@pytest.mark.asyncio
async def test_image_with_data_url_should_create_block(
    image_parser: ImageParser,
    context: BlockParsingContext,
) -> None:
    context.line = "[image](data:image/png;base64,iVBORw0KGgoAAAANS)"

    await image_parser._process(context)

    assert len(context.result_blocks) == 1
    block = context.result_blocks[0]
    assert block.image.external.url == "data:image/png;base64,iVBORw0KGgoAAAANS"
